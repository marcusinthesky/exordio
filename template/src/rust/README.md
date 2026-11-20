---
description: A native Rust package with a reusable library, CLI and strict quality gates.
---

# Rust

One Cargo package provides a library in `src/lib.rs` and a thin executable in
`src/main.rs`. Unit tests, an integration test of the real CLI, and executable
documentation examples use only the standard library. The stable `example-app`
name keeps the committed lock reusable across generated projects; rename the
package, library imports and lock together when adopting your domain vocabulary.

Run from the repository root:

```bash
just rust::setup
just rust::run Ada
just rust::check
```

Nix supplies the compiler, Cargo, rustfmt, Clippy, Nextest and analysis tools.
`rust-version` in the manifest records the supported minimum, while the Nix lock
pins the actual toolchain. There is no additional rustup toolchain pin.

Setup fetches dependencies using the committed `Cargo.lock`. Ordinary checks run
offline with frozen resolution, fail if the lock is missing or stale, and never
repair it. Add dependencies or update the lock explicitly with Cargo from this
directory, then commit the manifest and lock together and rerun setup. Build and
test output stays under ignored `target/`; the release CLI is
`target/release/example-app`.

## Quality gates

| Command | Checks |
| --- | --- |
| `just rust::fmt-check` | Canonical rustfmt formatting |
| `just rust::typecheck` | Types, ownership and borrowing across all targets |
| `just rust::lint` | Clippy correctness and pedantic rules; warnings are errors |
| `just rust::dependencies` | Frozen dependency resolution |
| `just rust::deadcode` | cargo-shear dependency hygiene |
| `just rust::test` | Nextest unit/integration tests followed by doctests |
| `just rust::doc` | rustdoc documentation, with warnings treated as errors |
| `just rust::build` | Release compilation |
| `just rust::check` | All of the above |
| `just rust::fmt` | Explicit formatting repairs |

Nextest uses the CI profile for a complete run without retries. Its timeout
policy stops runaway tests, and JUnit results go to `target/nextest/ci/junit.xml`.
The manifest forbids unsafe code and denies unfinished/debugging macros. Tune
pedantic lint exceptions individually when the domain needs them. All-feature
checks cover this starter; projects with mutually exclusive features should
replace them with an explicit feature matrix.

## Extended checks

`just rust::security` uses cargo-deny and the current online advisory database.
It also checks licenses, prohibited crates and dependency sources. Review
`deny.toml` when adding dependencies or choosing a distribution license; the
unpublished starter is excluded from license checks, not its public dependencies.
This changing online data is deliberately separate from `rust::check`.

`just rust::coverage` writes an HTML coverage report to
`target/llvm-cov/html/index.html` using the matching Nix LLVM tools. It measures
unit and integration tests; stable Rust doctest coverage is not included. There
is no minimum percentage until the project defines a useful coverage policy.

Miri, fuzzing and mutation testing are useful additions for unsafe code, parsers
and critical algorithms. Introduce their toolchains and targeted tests when
those needs arise, rather than adding nightly or empty test targets by default.

See [ARCHITECTURE.md](ARCHITECTURE.md) for package ownership.
