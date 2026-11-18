---
description: A native Go module with explicit toolchain and dependency ownership.
---

# Go module

One module contains the reusable `greet` package and its executable consumer in
`cmd/example-app`. Packages share one module identity and dependency graph.
Tests live beside the code they exercise. Additional commands can live under
`cmd/`; supporting implementation packages can use `internal/` when they should
remain private to this module.

| Concern | Owner |
| --- | --- |
| Module identity | The `go_module` Copier answer and `go.mod` |
| Application dependencies | `go.mod` and `go.sum` when needed |
| Compiler, lint and security tools | The pinned Nix environment |
| Formatting and static analysis | golangci-lint with the committed configuration |
| Tests and race detection | The Go toolchain and its `testing` package |
| Executable output | Ignored `build/` |
| Cross-language commands | The root justfile |

The `go` directive establishes Go 1.26.0 as the module's minimum version; Nix
pins the development toolchain. `GOTOOLCHAIN=local` keeps commands on that
toolchain. `GOWORK=off` isolates checks from an unrelated workspace file.
Tool versions belong to Nix rather than a second Go tool-dependency manifest.

Setup prepares dependencies explicitly. Checks validate module consistency
before static analysis, tests and builds, using local inputs without repairing
source or manifests. Formatting is an explicit write. The separate security
command uses govulncheck's current database and call analysis; its findings can
change as new vulnerabilities are published.

The starter uses ordinary packages within a single module. Add another module or
a `go.work` file only when independently versioned modules need to be developed
together. See the [Go layout guide](https://go.dev/doc/modules/layout) for ways
to grow the package and command structure.
