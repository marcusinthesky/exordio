set shell := ["bash", "-euo", "pipefail", "-c"]
set positional-arguments
uv := "env -u PYTHONPATH -u PYTHONHOME -u VIRTUAL_ENV uv run --frozen"

# Discover maintainer commands.
default:
    @just --list

# Install frozen dependencies and Git hooks.
setup:
    env -u PYTHONPATH -u PYTHONHOME -u VIRTUAL_ENV uv sync --frozen --all-groups
    bash template/infra/nix/prepare-runtime.sh .venv/bin/insitu
    prek install

# Run tests, optionally selecting a file or pytest options.
test *args:
    {{ uv }} pytest "$@"

# Validate sources, generated projects and documentation.
check:
    bash template/infra/nix/check.sh
    schematter validate --schema template/infra/schemas/documents/budget.document-schema.yaml README.md AGENTS.md
    just test
    just site

# Format maintainer sources.
fmt:
    ruff check --fix .
    ruff format .
    nixfmt devenv.nix template/infra/nix/pkgs/*.nix
    rumdl fmt .

# Render local changes into a NEW directory; pass Copier options after it.
render destination="/tmp/exordio-preview" *options:
    test ! -e "$1" && test ! -L "$1" || { echo 'Choose a new destination.' >&2; exit 1; }
    {{ uv }} copier copy --defaults --vcs-ref HEAD "${@:2}" . "$1"

# Build the searchable creator guides.
site:
    {{ uv }} zensical build --strict

# Preview at http://127.0.0.1:8000.
site-serve:
    {{ uv }} zensical serve --dev-addr 127.0.0.1:8000
