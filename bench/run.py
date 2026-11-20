"""Paired scaffold experiment using Zero2Repo's pinned native runner."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib
import json
import math
import os
import platform
import random
import re
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
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
        "reasoning_effort": "high",
        "cases": list(CASES),
        "repetitions": 3,
        "seed": 42,
        "agent_timeout_sec": 7200,
        "test_timeout_sec": 7200,
        "stall_window_sec": 2100,
    }
    supplied = read_json(path)
    required = {"zero2repo", "template_ref", "model", "codex_version"}
    if not isinstance(supplied, dict) or supplied.keys() - defaults.keys() - required:
        raise ValueError("config must be an object containing only documented fields")
    config = defaults | supplied
    for key in required:
        value = config.get(key)
        if not isinstance(value, str) or not value.strip() or "SET_ME" in value:
            raise ValueError(f"set {key} explicitly in the config")
    if not re.fullmatch(r"[0-9a-f]{40}", config["template_ref"]):
        raise ValueError("template_ref must be a full commit SHA")
    if not re.fullmatch(r"\d+\.\d+\.\d+", config["codex_version"]):
        raise ValueError("codex_version must be an exact release, e.g. 0.123.0")
    if config["reasoning_effort"] not in ("minimal", "low", "medium", "high", "xhigh"):
        raise ValueError("unsupported Codex reasoning_effort")
    cases = config["cases"]
    if (
        not isinstance(cases, list)
        or not cases
        or any(not isinstance(case, str) or case not in CASES for case in cases)
        or len(cases) != len(set(cases))
    ):
        raise ValueError("cases must be a nonempty, unique subset of the pilot cases")
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
        for name in ("bench/run.py", "pyproject.toml", "uv.lock")
    } | {"python": sys.version}


def provider_identity() -> str:
    # Credentials never enter the manifest; endpoint/transport changes still invalidate a resume.
    return digest(
        {
            key: os.environ.get(key)
            for key in (
                "OPENAI_BASE_URL",
                "CBRUN_CODEX_GATEWAY_WEBSOCKETS",
            )
        }
    )


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
            "CBRUN_CODEX_VERSION": config["codex_version"],
            "CBRUN_CODEX_REASONING_EFFORT": config["reasoning_effort"],
            "CBRUN_PLATFORM": "linux/amd64",
        }
    )
    if "CBRUN_CODEX_GATEWAY_WEBSOCKETS" in os.environ:
        env["CBRUN_CODEX_GATEWAY_WEBSOCKETS"] = os.environ["CBRUN_CODEX_GATEWAY_WEBSOCKETS"]
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


def seed_workspace(container, seed: Path | None) -> None:
    checked_exec(container, 'test -d /app && test -z "$(find /app -mindepth 1 -print -quit)"')
    if seed is not None:
        if (seed / ".git").exists():
            raise ValueError("starter must not contain a Git repository")
        for child in sorted(seed.iterdir()):
            container.cp_to(child, "/app/")
    checked_exec(container, "git -C /app init --quiet --initial-branch=main")


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
        seeds = {}
        for language in sorted({CASES[case] for case in config["cases"]}):
            seed = destination / "seeds" / language
            render_seed(ROOT, config["template_ref"], seed, language)
            seeds[language] = tree_identity(seed)
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
            for seed in (None, destination / "seeds" / CASES[case_id]):
                container = runner.Container.start(image.agent_image_id, network="none")
                try:
                    version = runner._probe_cli_version(container, "codex")
                    if version != f"codex-cli {config['codex_version']}":
                        raise ValueError(f"CLI pin mismatch: {version!r}")
                    checked_exec(
                        container,
                        "test ! -e /tests/final && test -s /environment/prd/Full_PRD.md "
                        "&& test -s /environment/Interface_Contract.md",
                    )
                    seed_workspace(container, seed)
                finally:
                    container.remove()
            images[case_id] = {"image": frozen, "tests": tree_identity(image.tests_cache_dir)}
            (destination / f"{case_id}.prompt.md").write_text(prompts[case_id])
        write_json(
            destination / "campaign.json",
            {
                "schema": 1,
                "config": config,
                "upstream_commit": UPSTREAM_COMMIT,
                "implementation": implementation_identity(),
                "provider": provider_identity(),
                "host_arch": platform.machine(),
                "seeds": seeds,
                "images": images,
                "prompts": prompts,
                "plan": schedule(config["cases"], config["repetitions"], config["seed"]),
                "prepared_at": runner.utc_now(),
                "preparation_seconds": time.monotonic() - started,
            },
        )
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
    if not os.environ.get("OPENAI_API_KEY", "").strip():
        raise ValueError("OPENAI_API_KEY is required; host Codex login is not mounted")
    if campaign["implementation"] != implementation_identity():
        raise ValueError("adapter, lockfile or Python changed; prepare a new campaign")
    if campaign["provider"] != provider_identity() or campaign["host_arch"] != platform.machine():
        raise ValueError("provider settings or host architecture changed; prepare a new campaign")
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
        for case, text in campaign["prompts"].items():
            if (destination / f"{case}.prompt.md").read_text() != text:
                raise ValueError(f"prompt changed: {case}")
        for language, identity in campaign["seeds"].items():
            if tree_identity(destination / "seeds" / language) != identity:
                raise ValueError(f"starter changed: {language}")
        for record in campaign["images"].values():
            image = record["image"]
            if tree_identity(Path(image["tests_cache_dir"])) != record["tests"]:
                raise ValueError("hidden test cache changed; prepare a new campaign")
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
            write_json(
                output / "trial.json", execute_trial(runner, campaign, job, destination, limits)
            )
            report(destination)


def execute_trial(runner, campaign: dict, job: dict, destination: Path, limits) -> dict:
    config = campaign["config"]
    image_data = campaign["images"][job["case"]]["image"]
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
            if outcome is None or outcome.exit_code == 0:
                seed_workspace(
                    container,
                    destination / "seeds" / CASES[job["case"]] if job["arm"] == "exordio" else None,
                )
            return outcome
        finally:
            preparation_seconds = time.monotonic() - start

    def prompt(**kwargs):
        text = instruction(native_prompt(**kwargs))
        if text != campaign["prompts"][job["case"]]:
            raise ValueError("instruction differs from prepared campaign")
        return text

    print(f"Running {job['id']}", flush=True)
    try:
        with (
            patch.object(runner, "ensure_agent_image", return_value=image),
            patch.object(runner, "build_instruction", prompt),
            patch.object(runner, "_run_agent_setup", setup),
        ):
            result = runner.run_trial(
                Path(config["zero2repo"]) / "benchmark/cases" / job["case"],
                backend="codex",
                model=config["model"],
                out_dir=destination / "runs" / job["id"],
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
    result["preparation_seconds"] = preparation_seconds
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
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
