# This attribute set defines the default package: the project and its locked dependencies
{ pkgs, flake, ... }:
let
  inherit (flake.lib.mkPythonSet { inherit pkgs; }) workspace pythonSet;
in
pkgs.lib.addMetaAttrs { mainProgram = "mgc"; } (
  pythonSet.mkVirtualEnv "music-genre-classifier-env" workspace.deps.default
)
