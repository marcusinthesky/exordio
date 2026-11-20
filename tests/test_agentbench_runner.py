"""Exercise runner orchestration without Docker or model calls."""

from __future__ import annotations

import fcntl
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from bench import run as bench


@pytest.fixture
def campaign(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    native_prompt = "Build, from scratch, in /app. It starts empty. Follow the public contract."
    seed = tmp_path / "seeds/python"
    seed.mkdir(parents=True)
    (seed / "README.md").write_text("Starter\n")
    (seed / ".gitignore").write_text(".venv/\n")
    hidden = tmp_path / "tests/final"
    hidden.mkdir(parents=True)
    (hidden / "acceptance.py").write_text("# hidden from the agent\n")
    image = {
        "case_id": "case001",
        "deliverable_image": "sha256:deliverable",
        "agent_image": "sha256:agent",
        "agent_image_id": "sha256:agent",
        "tests_cache_dir": str(hidden.parent),
    }
    data = {
        "config": {
            "zero2repo": str(tmp_path / "upstream"),
            "model": "model-snapshot",
            "codex_version": "0.100.0",
            "reasoning_effort": "high",
            "agent_timeout_sec": 7200,
            "test_timeout_sec": 7200,
            "stall_window_sec": 2100,
        },
        "plan": bench.schedule(["case001"], 1, 42),
        "prompts": {"case001": bench.instruction(native_prompt)},
        "seeds": {"python": bench.tree_identity(seed)},
        "images": {
            "case001": {
                "image": image,
                "prepared_agent_image": "sha256:prepared",
                "tests": bench.tree_identity(hidden.parent),
            }
        },
        "implementation": bench.implementation_identity(),
        "host_arch": bench.platform.machine(),
    }
    bench.write_json(tmp_path / "campaign.json", data)
    (tmp_path / "campaign.sha256").write_text(bench.digest(data))
    (tmp_path / "case001.prompt.md").write_text(data["prompts"]["case001"])
    container = SimpleNamespace(
        exec=Mock(return_value=SimpleNamespace(exit_code=0, tail="")),
        cp_to=Mock(),
    )
    runner = SimpleNamespace(
        Container=SimpleNamespace(build_run_argv=Mock()),
        _run_solve=Mock(),
        AgentImage=SimpleNamespace,
        ensure_agent_image=Mock(side_effect=AssertionError("must reuse the frozen image")),
        build_instruction=Mock(return_value=native_prompt),
        _run_agent_setup=Mock(return_value=None),
        image_identity=lambda reference: {"id": reference},
        resolve_limits=lambda **kw: kw,
    )
    calls = []

    def native_trial(case, **kwargs):
        kwargs["out_dir"].mkdir(parents=True, exist_ok=False)
        container.cp_to.reset_mock()
        prompt = runner.build_instruction(agent_timeout_sec=kwargs["limits"]["agent_timeout_sec"])
        frozen_image = runner.ensure_agent_image()
        setup = runner._run_agent_setup(container, object(), out_dir=kwargs["out_dir"])
        calls.append((case, kwargs, prompt, frozen_image, list(container.cp_to.call_args_list)))
        return SimpleNamespace(
            to_dict=lambda: {
                "run_valid": True,
                "setup_ok": setup is None or setup.exit_code == 0,
                "reward": 0,
                "error": "missing submission",
                "terminal_status": "exited",
            }
        )

    runner.run_trial = Mock(side_effect=native_trial)
    monkeypatch.setattr(bench, "load_upstream", lambda path: runner)
    monkeypatch.setenv("OPENAI_API_KEY", "benchmark-test-placeholder")
    return tmp_path, data, runner, calls


def test_both_arms_reuse_native_runner_and_differ_only_in_seed(campaign) -> None:
    destination, data, runner, calls = campaign
    native_setup, native_prompt, image_builder = (
        runner._run_agent_setup,
        runner.build_instruction,
        runner.ensure_agent_image,
    )
    bench.run(destination, execute=True)
    assert len(calls) == native_setup.call_count == 2
    for case, kwargs, prompt, image, copied in calls:
        assert case == Path(data["config"]["zero2repo"]) / "benchmark/cases/case001"
        assert (
            kwargs["agent_spec_path"] == bench.ROOT / "bench/agent.json"
            and kwargs["model"] == "model-snapshot"
        )
        assert kwargs["limits"] == {
            "agent_timeout_sec": 7200,
            "test_timeout_sec": 7200,
            "stall_window_sec": 2100,
        }
        assert prompt == data["prompts"]["case001"]
        expected = (
            "sha256:prepared" if kwargs["out_dir"].name.endswith("exordio") else "sha256:agent"
        )
        assert image.agent_image_id == expected
        assert not copied
        result = bench.read_json(kwargs["out_dir"] / "trial.json")
        assert result["reward"] == 0 and result["error"] == "missing submission"
        assert bench.valid(result)
    assert runner._run_agent_setup is native_setup and runner.build_instruction is native_prompt
    assert runner.ensure_agent_image is image_builder
    image_builder.assert_not_called()
    bench.run(destination, execute=True)
    assert len(calls) == 2  # Completed failed attempts are preserved, never retried.


def test_runner_exception_is_retained_and_patches_are_restored(campaign) -> None:
    destination, data, runner, _ = campaign
    runner.run_trial.side_effect = RuntimeError("Docker stopped")
    setup, prompt, images = (
        runner._run_agent_setup,
        runner.build_instruction,
        runner.ensure_agent_image,
    )
    result = bench.execute_trial(runner, data, data["plan"][0], destination, {})
    assert result["run_valid"] is False and result["reward"] is None
    assert "Docker stopped" in result["error"]
    assert runner._run_agent_setup is setup and runner.build_instruction is prompt
    assert runner.ensure_agent_image is images


def test_native_setup_failure_is_not_a_model_failure(campaign) -> None:
    destination, _, runner, calls = campaign
    runner._run_agent_setup.return_value = SimpleNamespace(exit_code=1, tail="auth setup failed")
    with pytest.raises(ValueError, match="invalid attempt"):
        bench.run(destination, execute=True)
    assert len(calls) == 1
    assert all(not copied for _, _, _, _, copied in calls)
    summary = bench.read_json(destination / "summary.json")
    assert sum(arm["invalid"] for arm in summary["arms"].values()) == 1
    assert sum(arm["missing"] for arm in summary["arms"].values()) == 1


def test_default_run_needs_no_credentials_or_execution(campaign, monkeypatch, capsys) -> None:
    destination, data, runner, _ = campaign
    monkeypatch.delenv("OPENAI_API_KEY")
    bench.run(destination)
    output = capsys.readouterr().out
    assert all(job["id"] in output for job in data["plan"])
    runner.run_trial.assert_not_called()
    assert not (destination / "runs").exists()


def test_interrupted_attempt_stops_without_overwriting(campaign) -> None:
    destination, data, runner, _ = campaign
    output = destination / "runs" / data["plan"][-1]["id"]
    output.mkdir(parents=True)
    log = output / "agent.log"
    log.write_text("partial output")
    with pytest.raises(ValueError, match="unfinished attempt"):
        bench.run(destination, execute=True)
    runner.run_trial.assert_not_called()
    assert log.read_text() == "partial output" and not (output / "trial.json").exists()
    assert bench.report(destination)["interrupted"] == [data["plan"][-1]["id"]]


def test_modified_campaign_is_rejected_before_execution(campaign) -> None:
    destination, data, runner, _ = campaign
    data["config"]["model"] = "another-model"
    bench.write_json(destination / "campaign.json", data)
    with pytest.raises(ValueError, match="campaign changed"):
        bench.run(destination, execute=True)
    runner.run_trial.assert_not_called()


def test_campaign_lock_rejects_concurrent_execution(campaign) -> None:
    destination, _, runner, _ = campaign
    with (destination / "run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(ValueError, match="already running"):
            bench.run(destination, execute=True)
    runner.run_trial.assert_not_called()


def test_subscription_uses_prepared_image_and_host_agent_spec(campaign, monkeypatch) -> None:
    destination, data, runner, _ = campaign
    config = data["config"]
    config.update(
        protocol="prepared-subscription", model="openai-codex:gpt-6-luna", reasoning_effort="medium"
    )
    monkeypatch.delenv("OPENAI_API_KEY")
    data["images"]["case001"]["prepared_agent_image"] = "sha256:prepared"
    runner.Container = SimpleNamespace(build_run_argv=lambda image: ["docker", "run", image])
    runner._run_solve = Mock()

    def trial(case, **kwargs):
        assert kwargs["agent_spec_path"] == bench.ROOT / "bench/agent.json"
        assert kwargs["model"] == config["model"]
        image = runner.ensure_agent_image()
        assert image.agent_image_id == "sha256:prepared"
        assert runner.Container.build_run_argv(image.agent_image_id) == [
            "docker",
            "run",
            "--label",
            "ai.pydantic.workspace=true",
            "sha256:prepared",
        ]
        assert runner.Container.build_run_argv(image.deliverable_image) == [
            "docker",
            "run",
            "sha256:deliverable",
        ]
        return SimpleNamespace(to_dict=lambda: {"run_valid": True, "setup_ok": True, "reward": 0})

    runner.run_trial.side_effect = trial
    job = next(job for job in data["plan"] if job["arm"] == "exordio")
    assert bench.valid(bench.execute_trial(runner, data, job, destination, {}))
