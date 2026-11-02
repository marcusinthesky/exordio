{ pkgs, lean4-nix }:
let
  manifest = {
    tag = "v4.35.0";
    toolchain = {
      x86_64-linux = {
        url = "https://github.com/leanprover/lean4/releases/download/v4.35.0/lean-4.35.0-linux.tar.zst";
        hash = "sha256-colZekRUMkbJInuMrlAXZ+CVzhf21Ei5X8So3Jcmj20=";
      };
      aarch64-linux = {
        url = "https://github.com/leanprover/lean4/releases/download/v4.35.0/lean-4.35.0-linux_aarch64.tar.zst";
        hash = "sha256-yPD4o5IOg5cYsTQ+Z4H9gKPpsQJPvNcHjrMPVOgGsCg=";
      };
    };
  };
in
(pkgs.callPackage (lean4-nix + "/lib/toolchain.nix") { inherit pkgs; }).fetchBinaryLean manifest
