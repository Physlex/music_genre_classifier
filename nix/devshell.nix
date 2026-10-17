# Development shell: an editable uv2nix virtualenv, so source changes apply without a rebuild
{ pkgs, flake, ... }:
let
  inherit (flake.lib.mkPythonSet { inherit pkgs; }) workspace pythonSet;

  editableOverlay = workspace.mkEditablePyprojectOverlay {
    # Use environment variable pointing to editable root directory
    root = "$REPO_ROOT";
  };

  editablePythonSet = pythonSet.overrideScope editableOverlay;

  virtualenv = editablePythonSet.mkVirtualEnv "music-genre-classifier-dev-env" workspace.deps.all;
in
pkgs.mkShell {
  packages = [
    virtualenv
  ]
  ++ (with pkgs; [
    uv
    basedpyright
    ruff
    nixd
  ]);

  env = {
    # Prevent uv from managing a virtualenv, uv2nix does that
    UV_NO_SYNC = "1";
    # Use the Nix interpreter for all uv operations
    UV_PYTHON = editablePythonSet.python.interpreter;
    # Prevent uv from downloading its own Python builds
    UV_PYTHON_DOWNLOADS = "never";
  };

  shellHook = ''
    # Eliminate PYTHONPATH side-effects from nixpkgs Python builders
    unset PYTHONPATH
    # Directory editable packages are relative to
    export REPO_ROOT=$(git rev-parse --show-toplevel)
  '';
}
