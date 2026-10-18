# Nix attribute set defining known libraries for the nix build system
{ inputs, ... }:
let
  inherit (inputs)
    pyproject-nix
    uv2nix
    pyproject-build-systems
    git-hooks
    ;
in
{
  # Python package set generated from uv.lock, shared by the package and devshell
  mkPythonSet =
    { pkgs }:
    let
      inherit (pkgs) lib;

      workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ../..; };

      python = pkgs.python313;

      pythonBase = pkgs.callPackage pyproject-nix.build.packages { inherit python; };

      overlay = workspace.mkPyprojectOverlay { sourcePreference = "wheel"; };

      hacks = pkgs.callPackage pyproject-nix.build.hacks { };

      pyprojectOverrides = _final: prev: {
        # Numba's wheel links against libtbb, which the wheel does not bundle
        numba = prev.numba.overrideAttrs (old: {
          buildInputs = (old.buildInputs or [ ]) ++ [ pkgs.tbb ];
        });

        # The PyPI wheel uv2nix selects does not bundle libsndfile, nixpkgs' build is
        # already patched to find it
        soundfile = hacks.nixpkgsPrebuilt {
          from = python.pkgs.soundfile;
          prev = prev.soundfile;
        };
      };

      pythonSet = pythonBase.overrideScope (
        lib.composeManyExtensions [
          pyproject-build-systems.overlays.wheel
          overlay
          pyprojectOverrides
        ]
      );
    in
    {
      inherit workspace pythonSet;
    };

  # Git hooks for the devshell to install: checks on commit, formatting on push
  mkGitHooks =
    { pkgs, virtualenv }:
    git-hooks.lib.${pkgs.stdenv.hostPlatform.system}.run {
      src = ../..;
      hooks = {
        ruff = {
          enable = true;
          entry = "${pkgs.ruff}/bin/ruff check";
        };

        basedpyright = {
          enable = true;
          name = "basedpyright";
          entry = "${pkgs.basedpyright}/bin/basedpyright --pythonpath ${virtualenv}/bin/python";
          types = [ "python" ];
          pass_filenames = false;
        };

        ruff-format = {
          enable = true;
          stages = [ "pre-push" ];
        };

        nixfmt = {
          enable = true;
          stages = [ "pre-push" ];
        };
      };
    };
}
