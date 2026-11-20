"""Paired scaffold experiment using Zero2Repo's pinned native runner."""

from __future__ import annotations

import argparse
import asyncio
import fcntl
import hashlib
import importlib
import importlib.metadata
import json
import math
import os
import platform
import random
import re
import shlex
import subprocess
import sys
import tempfile
import time
from contextlib import ExitStack, contextmanager
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_COMMIT = "c10b60ca3f2d9498a7e2dfea6b4a881037a0cccc"
CASES = {"case001": "python", "case002": "python", "case003": "typescript", "case012": "typescript"}
ARMS = ("blank", "exordio")


def read_json(path: Path):
    return json.loads(path.read_text())


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def read_campaign(destination: Path) -> dict:
    campaign = read_json(destination / "campaign.json")
    if digest(campaign) != (destination / "campaign.sha256").read_text().strip():
        raise ValueError("campaign changed; prepare a new campaign")
    return campaign


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def tree_identity(root: Path) -> dict:
    """Include executable bits and links, without following links outside the tree."""
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            content = "link:" + os.readlink(path)
        elif path.is_file():
            content = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            continue
        result[path.relative_to(root).as_posix()] = [path.lstat().st_mode & 0o777, content]
    return result


def configuration(path: Path) -> dict:
    defaults = {
        "seed": 42,
        "agent_timeout_sec": 7200,
        "test_timeout_sec": 7200,
        "stall_window_sec": 2100,
    }
    supplied = read_json(path)
    required = {"zero2repo", "template_ref"}
    if not isinstance(supplied, dict) or supplied.keys() - defaults.keys() - required:
        raise ValueError("config must be an object containing only documented fields")
    config = defaults | supplied
    for key in required:
        value = config.get(key)
        if not isinstance(value, str) or not value.strip() or "SET_ME" in value:
            raise ValueError(f"set {key} explicitly in the config")
    if not re.fullmatch(r"[0-9a-f]{40}", config["template_ref"]):
        raise ValueError("template_ref must be a full commit SHA")
    config.update(
        model="openai-codex:gpt-6-luna", reasoning_effort="medium", cases=list(CASES), repetitions=3
    )
    for key in ("repetitions", "seed", "agent_timeout_sec", "test_timeout_sec", "stall_window_sec"):
        value = config[key]
        minimum = 0 if key in ("seed", "stall_window_sec") else 1
        if type(value) is not int or value < minimum:
            raise ValueError(f"{key} must be an integer >= {minimum}")
    config["zero2repo"] = str((path.resolve().parent / config["zero2repo"]).resolve())
    return config


def schedule(cases: list[str], repetitions: int, seed: int) -> list[dict]:
    jobs = [
        {"id": f"{case}-{rep:02d}-{arm}", "case": case, "repetition": rep, "arm": arm}
        for case in cases
        for rep in range(1, repetitions + 1)
        for arm in ARMS
    ]
    random.Random(seed).shuffle(jobs)
    return jobs


def instruction(text: str) -> str:
    for old, new in (
        (", from scratch,", ","),
        (
            "It starts empty.",
            "Use any existing starter files, adapting them to the interface contract.",
        ),
    ):
        if text.count(old) != 1:
            raise ValueError(f"upstream prompt changed: expected exactly one {old!r}")
        text = text.replace(old, new)
    return text


def git(path: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def load_upstream(path: Path):
    if git(path, "rev-parse", "HEAD") != UPSTREAM_COMMIT:
        raise ValueError(f"Zero2Repo must be checked out at {UPSTREAM_COMMIT}")
    if git(path, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("Zero2Repo checkout must be clean")
    sys.path.insert(0, str(path / "benchmark"))
    runner = importlib.import_module("cbrun.run_case")
    if Path(runner.__file__).resolve() != path / "benchmark/cbrun/run_case.py":
        raise ValueError("another cbrun installation shadows the pinned checkout")
    return runner


def implementation_identity() -> dict:
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in (
            "bench/run.py",
            "bench/subscription.py",
            "bench/agent.json",
            "bench/prepared.Dockerfile",
            "pyproject.toml",
            "uv.lock",
        )
    } | {"python": sys.version}


@contextmanager
def runtime_environment(config: dict):
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("CBRUN_", "CODINGBENCH_", "CODING_BENCH_"))
        and key != "DOCKER_DEFAULT_PLATFORM"
    }
    env.update(
        {
            "CBRUN_CODEX_VERSION": "0.123.0",
            "CBRUN_CODEX_REASONING_EFFORT": config["reasoning_effort"],
            "CBRUN_PLATFORM": "linux/amd64",
        }
    )
    with patch.dict(os.environ, env, clear=True):
        yield


def render_seed(source: Path, ref: str, destination: Path, language: str) -> None:
    from copier import run_copy

    run_copy(
        str(source),
        destination,
        vcs_ref=ref,
        defaults=True,
        quiet=True,
        data={
            "project_name": "Benchmark project",
            "project_slug": "benchmark-project",
            "languages": [language],
            "workflows": [],
            "agents": [],
            "secrets": False,
        },
    )


def checked_exec(container, command: str) -> None:
    result = container.exec(command, timeout_sec=60)
    if result.exit_code != 0:
        raise RuntimeError(f"workspace preparation failed: {result.tail}")


def initialize_blank(container) -> None:
    checked_exec(container, 'test -d /app && test -z "$(find /app -mindepth 1 -print -quit)"')
    checked_exec(container, "git -C /app init --quiet --initial-branch=main")


def prepared_image(
    runner, base: str, seed: Path, language: str, destination: Path, upstream: Path, case_id: str
) -> str:
    """Build the treatment in /app and check it offline before accepting the image."""
    tag = "exordio-base:" + base.removeprefix("sha256:")
    subprocess.run(["docker", "tag", base, tag], check=True)
    image_id = destination / f"{language}.iid"
    subprocess.run(
        [
            "docker",
            "build",
            "--build-arg",
            f"BASE_IMAGE={tag}",
            "--iidfile",
            str(image_id),
            "-f",
            str(ROOT / "bench/prepared.Dockerfile"),
            str(seed),
        ],
        check=True,
    )
    image = image_id.read_text().strip()
    validate_prepared_image(runner, image, language, upstream, case_id)
    return image


def validate_prepared_image(
    runner, image: str, language: str, upstream: Path, case_id: str
) -> None:
    container = runner.Container.start(image, network="none")
    try:
        checked_exec(container, "tar -C /app -xf /opt/exordio-starter.tar")
        checked_exec(container, "test ! -e /tests/final && git -C /app rev-parse --git-dir")
        checked_exec(
            container,
            f'cd /app && PATH="$(cat /etc/exordio-profile)/bin:$PATH" just {language}::test',
        )
        if language == "python":
            # Create a harmless protected file even in images stripped of every banned package.
            module = runner.load_denylist(upstream / "benchmark/cases" / case_id).import_ban[0]
            location = container.exec("python3 -c 'import site; print(site.getsitepackages()[0])'")
            if location.exit_code:
                raise RuntimeError("cannot locate the native Python package directory")
            target = f"{location.tail.strip()}/bench_audit_fixture/_vendor/{module}/probe.txt"
            container.write_file(target, b"audit fixture")
            monitor = runner.AccessMonitor(container.container_id)
            monitor.start()
            try:
                python = "/app/src/python/.venv/bin/python"
                checked_exec(container, f"{python} -I -S -c 'import json'")
                if monitor.violated.is_set():
                    raise ValueError("ordinary Python import triggered the case audit")
                protected = monitor.reconciler.protected
                if target not in protected:
                    raise ValueError("native monitor did not register the audit fixture")
                probe = f"open({target!r}, 'rb').close()"
                checked_exec(container, f"{python} -I -S -c {shlex.quote(probe)}")
                monitor.violated.wait(10)
            finally:
                events = monitor.stop()
            if monitor.infra_error or not any(
                event.get("opener") == "python" and target in event.get("paths", [])
                for event in events
            ):
                raise ValueError("native monitor could not attribute the controlled Python access")
        else:
            hooks = upstream / "benchmark/coding_bench_harbor"
            for name in (
                "_cb_import_block.cjs",
                "_cb_import_block_esm.mjs",
                "_cb_import_block_hooks.mjs",
            ):
                container.cp_to(hooks / name, "/tmp/")
            denylist = runner.load_denylist(upstream / "benchmark/cases" / case_id)
            package = denylist.import_ban[0]
            container.write_file(f"/app/node_modules/{package}/index.js", b"module.exports = 123;")
            for extension, statement in (
                ("mjs", f"await import({json.dumps(package)})"),
                ("cjs", f"require({json.dumps(package)})"),
            ):
                container.write_file(
                    f"/app/audit-probe.{extension}",
                    f"try {{ {statement}; }} catch (e) {{ "
                    "if (process.env.CODING_BENCH_IMPORT_BAN && "
                    "e.code === 'CODING_BENCH_IMPORT_BAN') process.exit(0); throw e; } "
                    "if (process.env.CODING_BENCH_IMPORT_BAN) "
                    "throw Error('prepared Bun lacks Zero2Repo import protection');".encode(),
                )
                for banned in ("", package):
                    checked_exec(
                        container,
                        f"cd /app && CODING_BENCH_IMPORT_BAN={shlex.quote(banned)} "
                        'NODE_OPTIONS="--require /tmp/_cb_import_block.cjs '
                        '--import /tmp/_cb_import_block_esm.mjs" '
                        f'"$(cat /etc/exordio-profile)/bin/bun" audit-probe.{extension}',
                    )
    finally:
        container.remove()


def prepare(config_path: Path, destination: Path) -> None:
    started = time.monotonic()
    config = configuration(config_path)
    if git(ROOT, "rev-parse", f"{config['template_ref']}^{{commit}}") != config["template_ref"]:
        raise ValueError("template_ref must identify a commit in this checkout")
    runner = load_upstream(Path(config["zero2repo"]))
    with runtime_environment(config):
        prompts = {}
        for case_id in config["cases"]:
            case = runner.load_case(Path(config["zero2repo"]) / "benchmark/cases" / case_id)
            steps = runner.discover_steps(case)
            if len(steps) != 1:
                raise ValueError("this experiment requires a single final milestone")
            runner.require_native_or_allowed(
                allow_emulated=False, test_manifest=steps[0].test_manifest
            )
            runner._check_public_leakage(case, allow_leakage=False)
            merged = runner.merge_runner(case, steps[0])
            prompts[case_id] = instruction(
                runner.build_instruction(
                    has_hardware=bool((case.hardware_text or "").strip()),
                    agent_timeout_sec=config["agent_timeout_sec"],
                    build_command=case.build_command,
                    workdir=merged["workdir"],
                    test_env=runner.test_command_env(merged["test_command"]),
                )
            )
        destination.mkdir(parents=True, exist_ok=False)
        for language in sorted({CASES[case] for case in config["cases"]}):
            seed = destination / "seeds" / language
            render_seed(ROOT, config["template_ref"], seed, language)
        images = {}
        for case_id in config["cases"]:
            print(f"Preparing {case_id} (no model calls)", flush=True)
            image = runner.ensure_agent_image(
                case_id,
                cache_root=destination / "cache",
                backend="codex",
                case_dir=Path(config["zero2repo"]) / "benchmark/cases" / case_id,
            )
            frozen = asdict(image)
            frozen["tests_cache_dir"] = str(image.tests_cache_dir)
            frozen["deliverable_image"] = runner.image_identity(image.deliverable_image)["id"]
            frozen["agent_image"] = image.agent_image_id
            images[case_id] = {"image": frozen, "tests": tree_identity(image.tests_cache_dir)}
            language = CASES[case_id]
            setup_start = time.monotonic()
            images[case_id]["prepared_agent_image"] = prepared_image(
                runner,
                image.agent_image_id,
                destination / "seeds" / language,
                language,
                destination,
                Path(config["zero2repo"]),
                case_id,
            )
            images[case_id]["prepared_image_seconds"] = time.monotonic() - setup_start
        campaign = {
            "schema": 3,
            "agent": {
                "provider": "openai-codex",
                "harness": importlib.metadata.version("pydantic-ai-harness"),
                "pydantic_ai": importlib.metadata.version("pydantic-ai-slim"),
                "workspace": "/app",
                "sub_agents": False,
                "container_filesystem": "unrestricted",
            },
            "review_rubric": (ROOT / "bench/rubric.md").read_text(),
            "config": config,
            "upstream_commit": UPSTREAM_COMMIT,
            "implementation": implementation_identity(),
            "host_arch": platform.machine(),
            "images": images,
            "prompts": prompts,
            "plan": schedule(config["cases"], config["repetitions"], config["seed"]),
            "prepared_at": runner.utc_now(),
            "preparation_seconds": time.monotonic() - started,
        }
        limits = runner.resolve_limits(
            **{
                key: config[key]
                for key in ("agent_timeout_sec", "test_timeout_sec", "stall_window_sec")
            }
        )
        for job in schedule(config["cases"], 1, config["seed"]):
            result = execute_trial(runner, campaign, job, destination, limits, smoke=True)
            if not valid(result) or result["reward"] != 0 or result.get("judge_exit_code") is None:
                raise ValueError(
                    f"native judge smoke failed for {job['id']}: {result.get('error')}"
                )
        write_json(destination / "campaign.json", campaign)
        (destination / "campaign.sha256").write_text(
            digest(read_json(destination / "campaign.json")) + "\n"
        )
    print(f"Prepared {destination}; review campaign.json and the prompts before running.")


def valid(result: dict) -> bool:
    return (
        result.get("run_valid") is True
        and result.get("setup_ok") is True
        and not result.get("emulated")
        and result.get("reward") in (0, 1)
    )


def summarize(plan: list[dict], results: dict[str, dict]) -> dict:
    summary = {}
    for arm in ARMS:
        jobs = [job for job in plan if job["arm"] == arm]
        rows = [results[job["id"]] for job in jobs if job["id"] in results]
        scored = [row for row in rows if valid(row)]
        passed = sum(row["reward"] == 1 for row in scored)
        usage = [row.get("token_usage", {}) for row in rows]
        tokens = [row.get("total_tokens") if row.get("complete") else None for row in usage]
        costs = [row.get("cost_usd") if row.get("complete") else None for row in usage]
        summary[arm] = {
            "planned": len(jobs),
            "completed": len(rows),
            "missing": len(jobs) - len(rows),
            "invalid": len(rows) - len(scored),
            "passed": passed,
            "failed": len(scored) - passed,
            "needs_review": sum(bool(row.get("needs_review")) for row in rows),
            "judge_errors": sum(bool(row.get("judge_error")) for row in rows),
            "pass_rate": passed / len(scored) if len(scored) == len(jobs) and jobs else None,
            "observed_pass_rate": passed / len(scored) if scored else None,
            "solve_seconds": sum_known([row.get("solve_seconds") for row in rows])
            if len(rows) == len(jobs)
            else None,
            "total_tokens": sum_known(tokens) if len(rows) == len(jobs) else None,
            "cost_usd": sum_known(costs) if len(rows) == len(jobs) else None,
            "usage_complete": sum(bool(row.get("complete")) for row in usage),
        }
    by_case = {}
    for case in sorted({job["case"] for job in plan}):
        repetitions = {}
        differences = []
        for job in (job for job in plan if job["case"] == case):
            row = results.get(job["id"])
            pair = repetitions.setdefault(job["repetition"], {})
            pair[job["arm"]] = (
                row["reward"] if row and valid(row) else "missing" if row is None else "invalid"
            )
        for pair in repetitions.values():
            if all(isinstance(pair.get(arm), (float, int)) for arm in ARMS):
                differences.append(pair["exordio"] - pair["blank"])
        by_case[case] = {
            "repetitions": repetitions,
            "passes": {
                arm: sum(pair.get(arm) == 1 for pair in repetitions.values()) for arm in ARMS
            },
            "paired_difference": sum(differences) / len(repetitions)
            if len(differences) == len(repetitions)
            else None,
        }
    paired = []
    for job in plan:
        if job["arm"] == "blank":
            a = results.get(job["id"], {})
            b = results.get(job["id"].removesuffix("blank") + "exordio", {})
            if valid(a) and valid(b):
                paired.append(b["reward"] - a["reward"])
    complete = len(paired) * 2 == len(plan) and bool(plan)
    return {
        "arms": summary,
        "cases": by_case,
        "valid_pairs": len(paired),
        "complete": complete,
        "paired_pass_rate_difference": sum(paired) / len(paired) if complete else None,
    }


def sum_known(values: list) -> float | None:
    if not values or any(
        type(value) not in (int, float) or not math.isfinite(value) for value in values
    ):
        return None
    return sum(values)


def report(destination: Path) -> dict:
    campaign = read_campaign(destination)
    results = {}
    interrupted = []
    for job in campaign["plan"]:
        path = destination / "runs" / job["id"] / "trial.json"
        if path.is_file():
            results[job["id"]] = read_json(path)
        elif path.parent.exists():
            interrupted.append(job["id"])
    summary = summarize(campaign["plan"], results)
    summary["interrupted"] = interrupted
    summary["prepared_image_seconds"] = {
        case: record.get("prepared_image_seconds") for case, record in campaign["images"].items()
    }
    write_json(destination / "summary.json", summary)
    print(json.dumps(summary, indent=2))
    return summary


def run(destination: Path, *, execute: bool = False) -> None:
    campaign = read_campaign(destination)
    if not execute:
        for job in campaign["plan"]:
            print(job["id"])
        print("No model calls made. Add --execute to run the prepared campaign.")
        return
    with (destination / "run.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("this campaign is already running") from exc
        execute_campaign(destination, campaign)


def execute_campaign(destination: Path, campaign: dict) -> None:
    if campaign["implementation"] != implementation_identity():
        raise ValueError("adapter, lockfile or Python changed; prepare a new campaign")
    if campaign["host_arch"] != platform.machine():
        raise ValueError("host architecture changed; prepare a new campaign")
    pending = []
    for job in campaign["plan"]:
        output = destination / "runs" / job["id"]
        if (output / "trial.json").is_file():
            if not isinstance(read_json(output / "trial.json"), dict):
                raise ValueError(f"invalid attempt record at {output}")
        elif output.exists():
            raise ValueError(
                f"unfinished attempt at {output}; preserve it and start a new campaign"
            )
        else:
            pending.append(job)
    config = campaign["config"]
    runner = load_upstream(Path(config["zero2repo"]))
    with runtime_environment(config):
        for record in campaign["images"].values():
            image = record["image"]
            if tree_identity(Path(image["tests_cache_dir"])) != record["tests"]:
                raise ValueError("hidden test cache changed; prepare a new campaign")
            prepared = record.get("prepared_agent_image")
            if prepared and runner.image_identity(prepared)["id"] != prepared:
                raise ValueError("frozen prepared image is unavailable")
            for key in ("agent_image_id", "deliverable_image"):
                if runner.image_identity(image[key])["id"] != image[key]:
                    raise ValueError("frozen image is unavailable")
        limits = runner.resolve_limits(
            **{
                key: config[key]
                for key in (
                    "agent_timeout_sec",
                    "test_timeout_sec",
                    "stall_window_sec",
                )
            }
        )
        for job in pending:
            output = destination / "runs" / job["id"]
            result = execute_trial(runner, campaign, job, destination, limits)
            write_json(output / "trial.json", result)
            report(destination)
            if not valid(result):
                raise ValueError(
                    f"invalid attempt at {output}; inspect diagnostics before resuming"
                )


def execute_trial(
    runner, campaign: dict, job: dict, destination: Path, limits, *, smoke=False
) -> dict:
    config = campaign["config"]
    image_data = campaign["images"][job["case"]]["image"]
    prepared = job["arm"] == "exordio"
    if prepared:
        prepared_id = campaign["images"][job["case"]]["prepared_agent_image"]
        image_data = image_data | {"agent_image": prepared_id, "agent_image_id": prepared_id}
    image = runner.AgentImage(
        **(
            image_data
            | {
                "tests_cache_dir": Path(image_data["tests_cache_dir"]),
            }
        )
    )
    native_setup, native_prompt = runner._run_agent_setup, runner.build_instruction
    preparation_seconds = None

    def setup(container, invocation, *, out_dir):
        nonlocal preparation_seconds
        start = time.monotonic()
        try:
            outcome = native_setup(container, invocation, out_dir=out_dir)
            if (outcome is None or outcome.exit_code == 0) and prepared:
                checked_exec(container, "tar -C /app -xf /opt/exordio-starter.tar")
            elif outcome is None or outcome.exit_code == 0:
                initialize_blank(container)
            if outcome is None or outcome.exit_code == 0:
                checked_exec(container, "install -d -m 0700 /run/pydantic-ai")
            return outcome
        finally:
            preparation_seconds = time.monotonic() - start

    def prompt(**kwargs):
        text = instruction(native_prompt(**kwargs))
        if text != campaign["prompts"][job["case"]]:
            raise ValueError("instruction differs from prepared campaign")
        return text

    usage = []

    def host_solve(container, invocation, **kwargs):
        if smoke:
            container.write_file(runner.CONTAINER_SUBMIT_PATH, b"CODINGBENCH_SUBMIT\n")
            return runner.ExecResult(0)
        from bench.subscription import solve

        env = None
        if prepared:
            path = container.exec(
                'printf "%s/bin:%s" "$(cat /etc/exordio-profile)" "$PATH"', timeout_sec=10
            )
            if path.exit_code:
                raise RuntimeError("could not resolve the prepared environment")
            env = {"PATH": path.tail.strip()}
        return asyncio.run(
            solve(
                runner,
                config["model"],
                config["reasoning_effort"],
                container,
                usage=usage,
                env=env,
                **kwargs,
            )
        )

    print(f"Running {job['id']}", flush=True)
    try:
        with (
            ExitStack() as hooks,
            patch.object(runner, "ensure_agent_image", return_value=image),
            patch.object(runner, "build_instruction", prompt),
            patch.object(runner, "_run_agent_setup", setup),
        ):
            build_argv = runner.Container.build_run_argv

            def labeled_argv(reference, **kwargs):
                args = build_argv(reference, **kwargs)
                if reference == image.agent_image_id:
                    args[2:2] = ["--label", "ai.pydantic.workspace=true"]
                return args

            hooks.enter_context(
                patch.object(runner.Container, "build_run_argv", staticmethod(labeled_argv))
            )
            hooks.enter_context(patch.object(runner, "_run_solve", host_solve))
            result = runner.run_trial(
                Path(config["zero2repo"]) / "benchmark/cases" / job["case"],
                agent_spec_path=ROOT / "bench/agent.json",
                model=config["model"],
                out_dir=destination / ("smoke" if smoke else "runs") / job["id"],
                cache_root=destination / "cache",
                limits=limits,
            ).to_dict()
    except Exception as exc:
        # An infrastructure exception is a retained attempt, never an implicit retry.
        result = {
            "run_valid": False,
            "reward": None,
            "terminal_status": "error",
            "error": f"{type(exc).__name__}: {exc}",
        }
    total_tokens = sum_known(usage)
    result["token_usage"] = {
        "complete": total_tokens is not None,
        "total_tokens": total_tokens,
        "cost_usd": None,
    }
    result["preparation_seconds"] = preparation_seconds
    return result


def subscription_smoke() -> None:
    """Exercise the pilot's exact model and effort using host subscription credentials."""
    from pydantic_ai import Agent

    agent = Agent("openai-codex:gpt-6-luna", model_settings={"openai_reasoning_effort": "medium"})
    result = agent.run_sync("Reply with OK.")
    if result.output.strip() != "OK":
        raise ValueError("subscription smoke returned an unexpected response")
    print("Subscription model call succeeded.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("subscription-smoke", help="make one local subscription model call")
    prepare_parser = commands.add_parser(
        "prepare", help="freeze inputs and smoke-test images; no API calls"
    )
    prepare_parser.add_argument("config", type=Path)
    prepare_parser.add_argument("destination", type=Path)
    run_parser = commands.add_parser("run", help="show the plan, or explicitly execute it")
    run_parser.add_argument("destination", type=Path)
    run_parser.add_argument("--execute", action="store_true")
    commands.add_parser("report").add_argument("destination", type=Path)
    args = parser.parse_args()
    if args.command == "subscription-smoke":
        subscription_smoke()
        return
    destination = args.destination.resolve()
    try:
        if args.command == "prepare":
            prepare(args.config, destination)
        elif args.command == "run":
            run(destination, execute=args.execute)
        else:
            report(destination)
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"agentbench: {exc}\n")


if __name__ == "__main__":
    main()
