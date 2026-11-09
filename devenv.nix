{ pkgs, lib, ... }:
{
  name = "exordio";
  packages = with pkgs; [
    git
    actionlint
    shellcheck
    just
    prek
    uv
    python313
    patchelf
    ruff
    ripgrep
    bun
    rumdl
    lychee
    nixfmt
    statix
    pandoc
    (callPackage ./template/infra/nix/pkgs/schematter.nix { })
    (callPackage ./template/infra/nix/pkgs/agentsync.nix { })
  ];
  env = {
    UV_PYTHON_DOWNLOADS = "never";
    UV_PYTHON = "${pkgs.python313}/bin/python3";
    PROJECT_RUNTIME_LINKER = pkgs.stdenv.cc.bintools.dynamicLinker;
    PROJECT_RUNTIME_LIBRARIES = lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.glibc
      pkgs.zlib
    ];
  };
  enterShell = "unset PYTHONPATH PYTHONHOME VIRTUAL_ENV";
  enterTest = "just check";
}
