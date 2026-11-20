"""Exercise a generated project in its own environment, as runtime CI does."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from tests.support import (
    LANGUAGES,
    WORKFLOWS,
    clean_environment,
    commit_all,
    git,
    render,
    snapshot_template,
)


def runtime(
    repo: Path,
    *command: str,
    offline: bool = False,
    capture_output: bool = False,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = clean_environment()
    if offline:
        env.update(
            UV_OFFLINE="1",
            CARGO_NET_OFFLINE="true",
            GOTOOLCHAIN="local",
            GOPROXY="off",
            NO_PROXY="",
            no_proxy="",
        )
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
    env.update(extra_env or {})
    return subprocess.run(
        ["devenv", "shell", "--", "just", *command],
        cwd=repo,
        env=env,
        check=True,
        text=True,
        capture_output=capture_output,
    )


def source_snapshot(repo: Path) -> dict[str, bytes]:
    """Include untracked source so a newly created go.sum cannot escape drift checks."""
    return {
        name: (repo / name).read_bytes()
        for name in git(repo, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split(
            "\0"
        )
        if name and (repo / name).is_file()
    }


def reject_go_defect(repo: Path, target: Path, fault: str, command: str, diagnostic: str) -> None:
    """Require a meaningful tool failure and verify it did not repair the bad source."""
    original = target.read_bytes() if target.exists() else None
    try:
        target.write_bytes((original or b"") + fault.encode())
        before = source_snapshot(repo)
        try:
            runtime(repo, command, offline=True, capture_output=True)
        except subprocess.CalledProcessError as error:
            output = (error.stdout or "") + (error.stderr or "")
            assert diagnostic in output, f"{command} failed for an unexpected reason:\n{output}"
        else:
            raise AssertionError(f"{command} accepted the injected Go defect")
        assert source_snapshot(repo) == before, f"{command} rewrote source while rejecting a defect"
    finally:
        if original is None:
            target.unlink(missing_ok=True)
        else:
            target.write_bytes(original)


def check_go_quality(repo: Path) -> None:
    go = repo / "src/go"
    for filename, fault, command, diagnostic in (
        (
            "quality_probe.go",
            "package greet\n\nvar qualityProbe string = 123\n",
            "go::typecheck",
            "cannot use 123",
        ),
        (
            "quality_probe.go",
            'package greet\n\nimport "os"\n\nfunc QualityProbe() {\n\tos.Chdir(".")\n}\n',
            "go::lint",
            "errcheck",
        ),
        (
            "quality_probe.go",
            'package greet\n\nfunc QualityFormatProbe() string {return "probe"}\n',
            "go::lint",
            "gofumpt",
        ),
        (
            "quality_probe_test.go",
            'package greet\n\nimport "testing"\n\n'
            'func TestQualityProbe(t *testing.T) { t.Fatal("exordio-go-failing-test-probe") }\n',
            "go::test",
            "exordio-go-failing-test-probe",
        ),
    ):
        reject_go_defect(repo, go / "greet" / filename, fault, command, diagnostic)

    # A local unused dependency makes tidy fail without needing any registry access.
    (go / "build").mkdir(exist_ok=True)
    with TemporaryDirectory(prefix="quality-dependency-", dir=go / "build") as temporary:
        dependency = Path(temporary)
        (dependency / "go.mod").write_text("module example.com/exordio-quality-dependency\n")
        reject_go_defect(
            repo,
            go / "go.mod",
            "\nrequire example.com/exordio-quality-dependency v0.0.0\n"
            f"replace example.com/exordio-quality-dependency => {json.dumps(temporary)}\n",
            "go::modules",
            "-require example.com/exordio-quality-dependency",
        )
    check_go_setup_preserves_source(repo)


def check_go_setup_preserves_source(repo: Path) -> None:
    """Populate an isolated file proxy, then prove setup refuses to repair missing sums."""
    go = repo / "src/go"
    manifest = go / "go.mod"
    original = manifest.read_bytes()
    probe = go / "greet/setup_probe.go"
    module = "example.com/exordio-setup-probe"
    version = "v0.0.1"
    with TemporaryDirectory(prefix="setup-probe-", dir=go / "build") as temporary:
        fixture = Path(temporary)
        proxy = fixture / "proxy"
        versions = proxy / module / "@v"
        versions.mkdir(parents=True)
        dependency = {"go.mod": f"module {module}\n", "probe.go": "package dependency\n"}
        (versions / f"{version}.mod").write_text(dependency["go.mod"])
        (versions / f"{version}.info").write_text(
            json.dumps({"Version": version, "Time": "2020-01-01T00:00:00Z"})
        )
        with ZipFile(versions / f"{version}.zip", "w") as archive:
            for name, content in dependency.items():
                archive.writestr(f"{module}@{version}/{name}", content)
        environment = {
            "GOPROXY": proxy.as_uri(),
            "GOSUMDB": "off",
            "GONOPROXY": "none",
            "GOMODCACHE": str(fixture / "cache"),
        }
        try:
            manifest.write_bytes(original + f"\nrequire {module} {version}\n".encode())
            probe.write_text(f'package greet\n\nimport _ "{module}"\n')
            before = source_snapshot(repo)
            try:
                runtime(repo, "go::setup", offline=True, capture_output=True, extra_env=environment)
            except subprocess.CalledProcessError as error:
                output = (error.stdout or "") + (error.stderr or "")
                assert "go.sum" in output, output
            else:
                raise AssertionError("go::setup accepted missing checksums")
            assert (fixture / "cache" / f"{module}@{version}" / "probe.go").exists()
            assert source_snapshot(repo) == before, "Go setup repaired missing source checksums"

            # The alternate modfile must still resolve replacements relative to the real module.
            local = fixture / "dependency"
            local.mkdir()
            for name, content in dependency.items():
                (local / name).write_text(content)
            relative = "./" + str(local.relative_to(go))
            manifest.write_text(manifest.read_text() + f"replace {module} => {relative}\n")
            before = source_snapshot(repo)
            runtime(repo, "go::setup", offline=True, capture_output=True, extra_env=environment)
            runtime(repo, "go::typecheck", offline=True, capture_output=True, extra_env=environment)
            assert source_snapshot(repo) == before, "Go setup rewrote a relative replacement"
        finally:
            manifest.write_bytes(original)
            probe.unlink(missing_ok=True)


def reject_rust_defect(repo: Path, command: str, diagnostic: str) -> None:
    """A failed command must diagnose the fixture without repairing its source."""
    before = git(repo, "diff", "--binary", "HEAD")
    try:
        runtime(repo, command, offline=True, capture_output=True)
    except subprocess.CalledProcessError as error:
        output = error.stdout + error.stderr
        assert diagnostic in output, f"{command} failed for an unexpected reason:\n{output}"
    else:
        raise AssertionError(f"{command} accepted the injected Rust defect")
    assert git(repo, "diff", "--binary", "HEAD") == before, f"{command} rewrote source files"


def exercise_rust(repo: Path) -> None:
    """Prove the generated Rust gates reject defects, including lockfile drift."""
    for name in ("Ada", "two words", "café"):
        result = runtime(repo, "rust::run", name, offline=True, capture_output=True)
        assert result.stdout.strip() == f"Hello, {name}!"
    binary = repo / "src/rust/target/release/example-app"
    result = subprocess.run([str(binary), "Ada"], check=True, capture_output=True, text=True)
    assert result.stdout.strip() == "Hello, Ada!"

    library = repo / "src/rust/src/lib.rs"
    original = library.read_bytes()
    for fault, command, diagnostic in (
        (
            '\npub fn quality_type_probe() -> i32 { "wrong type" }\n',
            "rust::typecheck",
            "mismatched types",
        ),
        (
            "\npub fn quality_borrow_probe() -> usize {\n"
            '    let value = String::from("moved");\n'
            "    let _owner = value;\n    value.len()\n}\n",
            "rust::typecheck",
            "borrow of moved value",
        ),
        (
            "\npub fn quality_lint_probe(value: bool) -> bool { value == true }\n",
            "rust::lint",
            "bool_comparison",
        ),
        (
            "\npub fn quality_format_probe()->u8{1}\n",
            "rust::fmt-check",
            "Diff in",
        ),
        (
            "\n#[cfg(test)] mod quality_test_probe {\n"
            "    #[test] fn fails() { assert_eq!(1, 2); }\n}\n",
            "rust::test",
            "quality_test_probe::fails",
        ),
        (
            "\n/// ```\n/// assert_eq!(1, 2);\n/// ```\npub fn quality_doctest_probe() {}\n",
            "rust::test",
            "doctest failed",
        ),
        (
            "\n/// See [exordio_missing_documentation_item].\n"
            "pub fn quality_documentation_probe() {}\n",
            "rust::doc",
            "unresolved link",
        ),
    ):
        try:
            library.write_bytes(original + fault.encode())
            reject_rust_defect(repo, command, diagnostic)
        finally:
            library.write_bytes(original)

    lock = repo / "src/rust/Cargo.lock"
    original_lock = lock.read_bytes()
    try:
        lock.unlink()
        for command in ("rust::setup", "rust::dependencies"):
            reject_rust_defect(repo, command, "Cargo.lock")
            assert not lock.exists(), f"{command} created a missing Cargo.lock"
    finally:
        lock.write_bytes(original_lock)
    try:
        lock.write_bytes(original_lock.replace(b'"0.1.0"', b'"0.0.0"'))
        for command in ("rust::setup", "rust::dependencies"):
            reject_rust_defect(repo, command, "lock file")
    finally:
        lock.write_bytes(original_lock)

    # A real local dependency exercises cargo-shear without registry access.
    manifest = repo / "src/rust/Cargo.toml"
    original_manifest = manifest.read_bytes()
    dependency = repo / "src/rust/quality-probe"
    dependency.mkdir()
    (dependency / "src").mkdir()
    (dependency / "Cargo.toml").write_text(
        '[package]\nname = "exordio-quality-probe"\nversion = "0.1.0"\nedition = "2024"\n'
    )
    (dependency / "src/lib.rs").write_text("pub const UNUSED: usize = 1;\n")
    try:
        manifest.write_bytes(
            original_manifest + b'\n[dependencies.exordio-quality-probe]\npath = "quality-probe"\n'
        )
        lock.write_text(
            'version = 4\n\n[[package]]\nname = "example-app"\nversion = "0.1.0"\n'
            'dependencies = ["exordio-quality-probe"]\n\n'
            '[[package]]\nname = "exordio-quality-probe"\nversion = "0.1.0"\n'
        )
        runtime(repo, "rust::dependencies", offline=True)
        reject_rust_defect(repo, "rust::deadcode", "exordio-quality-probe")
    finally:
        manifest.write_bytes(original_manifest)
        lock.write_bytes(original_lock)
        shutil.rmtree(dependency)


def exercise(
    directory: Path, workflows: list[str], languages: list[str], agents: list[str] | None = None
) -> None:
    source = snapshot_template(directory / "catalog")
    repo = directory / "project"
    maximal = set(workflows) == set(WORKFLOWS) and set(languages) == set(LANGUAGES)
    render(
        source,
        repo,
        {
            "workflows": workflows,
            "languages": languages,
            "agents": agents if agents is not None else ["codex", "claude"] if maximal else [],
            "secrets": maximal,
            **(
                {"go_module": "github.com/example/runtime-fixture/src/go"}
                if "go" in languages
                else {}
            ),
        },
    )
    git(repo, "init", "--quiet", "--initial-branch=main")
    commit_all(repo, "feat(project): initialize runtime fixture")
    initial_source = source_snapshot(repo)
    runtime(repo, "setup")
    assert not git(repo, "status", "--porcelain=v1", "--untracked-files=no"), (
        "Setup rewrote tracked content"
    )
    if "go" in languages:
        assert source_snapshot(repo) == initial_source, (
            "Setup changed source or created untracked files"
        )
        output = runtime(repo, "go::run", "Ada", offline=True, capture_output=True)
        assert output.stdout.strip() == "Hello, Ada!", output.stdout
    if "planning" in workflows:
        runtime(repo, "plan-new", "project", "Project plan")
        runtime(repo, "task-new", ".context/plan/project", "first", "First task")
    if "reference" in workflows:
        runtime(repo, "reference-new", "paper", "Useful paper")
    if workflows:
        runtime(repo, "sync")
        commit_all(repo, "docs(project): create records and refresh views")
    before = git(repo, "diff", "--binary", "HEAD")
    source_before = source_snapshot(repo)
    runtime(repo, "check", offline=True)
    assert git(repo, "diff", "--binary", "HEAD") == before, "Checks rewrote tracked content"
    if "go" in languages:
        assert source_snapshot(repo) == source_before, "Checks changed or created source files"
        check_go_quality(repo)
        # Rerun the complete Go gate after restoring every defect.
        runtime(repo, "go::check", offline=True)
        assert source_snapshot(repo) == source_before, "Go quality probes changed source"

    if "rust" in languages:
        exercise_rust(repo)
    # Exercise the *generated commands* with deliberate defects, not just clean fixtures.
    # Each probe is restored, then the no-mutation invariant is checked again.
    for language, target, fault, command in (
        (
            "python",
            repo / "src/python/packages/example_core/src/example_core/__init__.py",
            "\\nimport exordio_unused_quality_probe\\n",
            "python::lint",
        ),
        (
            "typescript",
            repo / "src/typescript/packages/core/src/index.ts",
            "\\nconst exordioTypeProbe: string = 123;\\n",
            "typescript::typecheck",
        ),
        (
            "typescript",
            repo / "src/typescript/packages/core/src/index.ts",
            "\\nexport function exordioDeadExportProbe(): number { return 7; }\\n",
            "typescript::knip",
        ),
    ):
        if language not in languages:
            continue
        original = target.read_bytes()
        try:
            target.write_bytes(original + fault.replace("\\n", "\n").encode())
            try:
                runtime(repo, command, offline=True)
            except subprocess.CalledProcessError:
                pass
            else:
                raise AssertionError(f"{command} accepted the injected {language} defect")
        finally:
            target.write_bytes(original)
    assert git(repo, "diff", "--binary", "HEAD") == before, "Quality probes changed tracked content"


def main() -> None:
    workflows = json.loads(os.environ.get("PROJECT_WORKFLOWS", "[]"))
    languages = json.loads(os.environ.get("PROJECT_LANGUAGES", "[]"))
    assert isinstance(workflows, list) and set(workflows) <= set(WORKFLOWS)
    assert isinstance(languages, list) and set(languages) <= set(LANGUAGES)
    agents = json.loads(os.environ.get("PROJECT_AGENTS", "null"))
    assert agents is None or isinstance(agents, list) and set(agents) <= {"codex", "claude"}
    with TemporaryDirectory(prefix="catalog-runtime-") as temporary:
        exercise(Path(temporary), workflows, languages, agents)


if __name__ == "__main__":
    main()
