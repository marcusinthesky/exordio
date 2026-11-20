"""Exercise the optional benchmark without Docker, upstream assets or model calls."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import pytest

from bench.run import configuration, instruction, render_seed, schedule, seed_workspace, summarize
from tests.support import ROOT, answers, git


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    data = json.loads((ROOT / "bench/config.example.json").read_text())
    data.update(model="model-snapshot", codex_version="0.100.0")
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data))
    return path


def test_configuration_resolves_upstream_relative_to_its_file(config_file: Path) -> None:
    config = configuration(config_file)
    assert Path(config["zero2repo"]) == config_file.parent / "zero2repo"
    assert config["cases"] == ["case001", "case002", "case003", "case012"]
    assert config["model"] == "model-snapshot"
    assert config["codex_version"] == "0.100.0"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("model", "SET_ME"),
        ("model", ""),
        ("model", 1),
        ("codex_version", "latest"),
        ("codex_version", "SET_ME"),
        ("codex_version", "0.100.0-beta"),
        ("template_ref", "main"),
        ("template_ref", "f" * 39),
        ("reasoning_effort", "ultra"),
        ("cases", []),
        ("cases", ["case001", "case001"]),
        ("cases", ["case043"]),
        ("cases", "case001"),
        ("repetitions", 0),
        ("repetitions", True),
        ("agent_timeout_sec", -1),
        ("test_timeout_sec", "7200"),
        ("seed", -1),
        ("seed", True),
        ("stall_window_sec", -1),
    ],
)
def test_configuration_rejects_unfrozen_or_invalid_settings(
    config_file: Path, field: str, value: object
) -> None:
    data = json.loads(config_file.read_text())
    data[field] = value
    config_file.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        configuration(config_file)


def test_schedule_contains_every_paired_repetition_once() -> None:
    cases = ["case001", "case002", "case003", "case012"]
    jobs = schedule(cases, 3, 42)
    assert jobs == schedule(cases, 3, 42)
    assert jobs != schedule(cases, 3, 43)
    assert len(jobs) == len({job["id"] for job in jobs}) == 24
    assert Counter((job["case"], job["repetition"], job["arm"]) for job in jobs) == {
        (case, repetition, arm): 1
        for case in cases
        for repetition in range(1, 4)
        for arm in ("blank", "exordio")
    }
    for job in jobs:
        assert job["id"] == f"{job['case']}-{job['repetition']:02d}-{job['arm']}"


NATIVE_INSTRUCTION = (
    "Implement the product, from scratch, in /app. It starts empty.\n"
    "Read the public interface. Submit explicitly. Hidden tests decide the score.\n"
)


def test_instruction_changes_only_the_initial_workspace_assumption() -> None:
    assert instruction(NATIVE_INSTRUCTION) == (
        "Implement the product, in /app. "
        "Use any existing starter files, adapting them to the interface contract.\n"
        "Read the public interface. Submit explicitly. Hidden tests decide the score.\n"
    )


@pytest.mark.parametrize(
    "text",
    [
        NATIVE_INSTRUCTION.replace(", from scratch,", ","),
        NATIVE_INSTRUCTION.replace("It starts empty.", "It is empty."),
        NATIVE_INSTRUCTION + "It starts empty.",
        NATIVE_INSTRUCTION + ", from scratch,",
    ],
)
def test_instruction_rejects_upstream_prompt_drift(text: str) -> None:
    with pytest.raises(ValueError):
        instruction(text)


class Container:
    def __init__(self, exit_code: int = 0) -> None:
        self.exit_code = exit_code
        self.events: list[tuple] = []

    def exec(self, command: object, **kwargs: object) -> SimpleNamespace:
        self.events.append(("exec", command))
        return SimpleNamespace(exit_code=self.exit_code, tail="setup failed", timed_out=False)

    def cp_to(self, source: Path, destination: str) -> None:
        self.events.append(("copy", Path(source), destination))


def test_blank_workspace_is_initialized_without_copied_files() -> None:
    container = Container()
    seed_workspace(container, None)
    assert all(event[0] == "exec" for event in container.events)
    assert "git" in str(container.events[-1]) and "init" in str(container.events[-1])


def test_exordio_seed_includes_dotfiles_before_git_initialization(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "README.md").write_text("Starter.\n")
    (tmp_path / ".copier-answers.yml").write_text("languages: [python]\n")
    container = Container()
    seed_workspace(container, tmp_path)
    copied = [event for event in container.events if event[0] == "copy"]
    assert copied == [("copy", path, "/app/") for path in sorted(tmp_path.iterdir())]
    assert container.events[0][0] == "exec"
    assert container.events[-1][0] == "exec"
    assert "git" in str(container.events[-1]) and "init" in str(container.events[-1])


def test_workspace_failure_is_not_treated_as_a_successful_seed() -> None:
    with pytest.raises(RuntimeError):
        seed_workspace(Container(exit_code=1), None)


def test_seed_cannot_import_repository_history(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    with pytest.raises((ValueError, RuntimeError)):
        seed_workspace(Container(), tmp_path)


@pytest.mark.parametrize("language", ["python", "typescript"])
def test_rendered_starter_selects_only_the_task_language(
    template_source: Path, tmp_path: Path, language: str
) -> None:
    destination = tmp_path / "starter"
    render_seed(template_source, git(template_source, "rev-parse", "HEAD"), destination, language)
    saved = answers(destination)
    assert saved["languages"] == [language]
    assert saved["workflows"] == saved["agents"] == []
    assert saved["secrets"] is False
    assert saved["project_slug"] == "benchmark-project"
    assert (destination / "src" / language).is_dir()
    assert (destination / "devenv.nix").is_file()
    assert not any(
        (destination / path).exists() for path in (".git", ".context", ".agents", "bench")
    )


def trial(reward: int, **changes: object) -> dict:
    return {
        "run_valid": True,
        "setup_ok": True,
        "reward": reward,
        "solve_seconds": 10,
        "token_usage": {"complete": True, "total_tokens": 100, "cost_usd": 0.1},
    } | changes


def test_summary_compares_complete_paired_plans() -> None:
    plan = schedule(["case001", "case002"], 1, 42)
    results = {
        job["id"]: trial(int(job["arm"] == "exordio" or job["case"] == "case001")) for job in plan
    }
    summary = summarize(plan, results)
    assert summary["complete"] is True
    assert summary["valid_pairs"] == 2
    assert summary["paired_pass_rate_difference"] == 0.5
    assert summary["arms"]["blank"]["pass_rate"] == 0.5
    assert summary["arms"]["exordio"]["pass_rate"] == 1.0
    for arm in summary["arms"].values():
        assert arm["total_tokens"] == 200
        assert arm["cost_usd"] == 0.2
        assert arm["solve_seconds"] == 20


def test_summary_retains_agent_failures_and_separates_missing_and_invalid_attempts() -> None:
    plan = schedule(["case001"], 2, 42)
    summary = summarize(
        plan,
        {
            "case001-01-blank": trial(0, error="No submit file", terminal_status="no_submit"),
            "case001-02-blank": trial(0, run_valid=False, setup_ok=False, token_usage={}),
            "case001-01-exordio": trial(1),
        },
    )
    assert summary["complete"] is False
    assert summary["valid_pairs"] == 1
    assert summary["paired_pass_rate_difference"] is None
    blank, exordio = (summary["arms"][arm] for arm in ("blank", "exordio"))
    assert (blank["planned"], blank["completed"], blank["failed"], blank["invalid"]) == (2, 2, 1, 1)
    assert blank["observed_pass_rate"] == 0
    assert exordio["missing"] == 1
    for arm in (blank, exordio):
        assert arm["pass_rate"] is arm["total_tokens"] is arm["cost_usd"] is None
    assert exordio["solve_seconds"] is None


@pytest.mark.parametrize(
    "usage",
    [
        {"complete": False, "total_tokens": 99, "cost_usd": 0.1},
        {"complete": True, "total_tokens": None, "cost_usd": None},
    ],
)
def test_summary_does_not_treat_partial_or_unknown_usage_as_complete(usage: dict) -> None:
    plan = schedule(["case001"], 1, 42)
    summary = summarize(plan, {job["id"]: trial(1, token_usage=usage) for job in plan})
    assert summary["complete"] is True
    for arm in summary["arms"].values():
        assert arm["pass_rate"] == 1.0
        assert arm["total_tokens"] is arm["cost_usd"] is None


def test_native_collection_failure_remains_a_scored_failure() -> None:
    plan = schedule(["case001"], 1, 42)
    summary = summarize(
        plan,
        {
            "case001-01-blank": trial(0, judge_error="no tests collected"),
            "case001-01-exordio": trial(1),
        },
    )
    blank = summary["arms"]["blank"]
    assert (blank["failed"], blank["invalid"], blank["judge_errors"]) == (1, 0, 1)
    assert blank["pass_rate"] == 0
    assert summary["complete"] is True
    assert summary["paired_pass_rate_difference"] == 1
