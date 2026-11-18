---
description: One Cargo package with a library boundary and a thin executable adapter.
---

# Rust architecture

`src/lib.rs` owns reusable logic. `src/main.rs` translates command-line arguments
into a library call and propagates output errors. `tests/cli.rs` verifies the
compiled program through its public process interface. Library unit tests and
doctests keep behavior close to the API.

`Cargo.toml` owns package metadata and lint policy. `Cargo.lock` owns application
dependency resolution, including the dependency-free starter. Add modules within
this package first; introduce multiple packages or a workspace only when they
represent independent boundaries. Rust visibility and module privacy enforce
the initial boundary without a separate architecture framework.

Nix owns executable tool versions, including compatible LLVM coverage tools.
Just exposes the common language commands and forwards work to native Cargo
tools. Setup prepares caches with locked resolution; validation uses frozen
inputs. Explicit formatting and Cargo dependency edits are separate writes.
All generated compilation, test and coverage output belongs under `target/`.

The offline gate covers formatting, compilation, Clippy, dependency hygiene,
Nextest, doctests, documentation and a release build. Security refreshes online
advisory data separately. Coverage is an explicit diagnostic rather than an
arbitrary default percentage requirement.
