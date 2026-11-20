"""Run the complete generated TypeScript application independently of TeX CI."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from tests.support import clean_environment, commit_all, git, render, snapshot_template


def runtime(
    repo: Path, *command: str, offline: bool = False, check: bool = True, capture: bool = False
) -> subprocess.CompletedProcess[str]:
    env = clean_environment()
    if offline:
        env.update(UV_OFFLINE="1", CARGO_NET_OFFLINE="true")
        # Browser tests intentionally reach local app, Storybook and mail services.
        env.update(NO_PROXY="localhost,127.0.0.1,::1", no_proxy="localhost,127.0.0.1,::1")
        env.update(
            {
                name: "http://127.0.0.1:9"
                for name in (
                    "HTTP_PROXY",
                    "HTTPS_PROXY",
                    "ALL_PROXY",
                    "http_proxy",
                    "https_proxy",
                    "all_proxy",
                )
            }
        )
    return subprocess.run(
        ["devenv", "shell", "--", "just", *command],
        cwd=repo,
        env=env,
        check=check,
        capture_output=capture,
        text=True,
        timeout=1800,
    )


def reject(repo: Path, command: str, diagnostic: str) -> None:
    result = runtime(repo, command, offline=True, check=False, capture=True)
    assert result.returncode != 0, f"{command} accepted the injected defect"
    output = result.stdout + result.stderr
    assert diagnostic in output, (
        f"{command} failed for an unexpected reason; expected {diagnostic!r}:\n{output[-8000:]}"
    )
    print(f"Verified {command} rejects {diagnostic!r}.", flush=True)


def preserve_artifacts(repo: Path) -> None:
    destination = os.environ.get("COMPONENTS_ARTIFACT_DIR")
    if not destination:
        return
    target = Path(destination)
    for name in ("test-results", "playwright-report"):
        source = repo / "src/typescript" / name
        if source.exists():
            shutil.copytree(source, target / name, dirs_exist_ok=True)


def exercise(directory: Path) -> None:
    source = snapshot_template(directory / "catalog")
    repo = directory / "project"
    render(source, repo, {"languages": ["typescript"], "typescript_components": True})
    workspace = repo / "src/typescript"
    git(repo, "init", "--quiet", "--initial-branch=main")
    commit_all(repo, "feat(project): initialize complete TypeScript fixture")
    try:
        runtime(repo, "setup")
        runtime(repo, "typescript::browser-setup")
        assert not git(repo, "status", "--porcelain"), (
            "Setup changed source or created unignored files"
        )
        runtime(repo, "services-up")
        runtime(repo, "typescript::db-migrate")
        before = git(repo, "diff", "--binary", "HEAD")
        try:
            runtime(repo, "check", offline=True)
        except subprocess.CalledProcessError:
            # Keep the original gate failure while gathering reviewable visual evidence.
            # The visual command uses updateSnapshots: "none" and writes only reports.
            if (workspace / "packages/ui/storybook-static/index.html").is_file() and not (
                workspace / "test-results/visual"
            ).exists():
                print("Collecting visual diagnostics after the failed check.", flush=True)
                try:
                    runtime(repo, "typescript::test-visual", offline=True, check=False)
                except (subprocess.TimeoutExpired, OSError) as error:
                    print(f"Visual diagnostics could not finish: {error}", flush=True)
            raise
        assert git(repo, "diff", "--binary", "HEAD") == before, "Checks rewrote tracked content"
        assert not git(repo, "status", "--porcelain"), "Checks left unignored generated files"

        schema = workspace / "apps/web/src/features/projects/schema.ts"
        original = schema.read_bytes()
        for fault, command, diagnostic in (
            (
                "\nexport const exordioTypeProbe: string = 123;\n",
                "typescript::typecheck",
                "TS2322",
            ),
            (
                "\nexport function exordioUnusedProbe(): number { return 7; }\n",
                "typescript::knip",
                "exordioUnusedProbe",
            ),
        ):
            try:
                schema.write_bytes(original + fault.encode())
                reject(repo, command, diagnostic)
            finally:
                schema.write_bytes(original)

        boundary = workspace / "packages/ui/src/exordio-boundary-probe.ts"
        try:
            boundary.write_text('export { redirect } from "next/navigation";\n')
            reject(repo, "typescript::boundaries", "UI must be independent")
        finally:
            boundary.unlink(missing_ok=True)

        lock = workspace / "bun.lock"
        contents = lock.read_bytes()
        try:
            lock.unlink()
            reject(repo, "typescript::setup", "Restore the committed bun.lock")
            assert not lock.exists(), "Setup recreated the missing lock"
        finally:
            lock.write_bytes(contents)
        assert git(repo, "diff", "--binary", "HEAD") == before, (
            "Quality probes changed tracked files"
        )
        assert not git(repo, "status", "--porcelain"), "Quality probes left untracked files"
    finally:
        preserve_artifacts(repo)
        # Always tear down only this generated project's services, including on failure.
        runtime(repo, "services-down", check=False)


def main() -> None:
    with TemporaryDirectory(prefix="exordio-components-runtime-") as temporary:
        exercise(Path(temporary))


if __name__ == "__main__":
    main()
