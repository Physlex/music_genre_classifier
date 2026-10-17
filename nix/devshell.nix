# Development shell: Nix provides the interpreter and tooling, uv manages Python packages
{ pkgs, ... }:
let
  python = pkgs.python313;
in
  pkgs.mkShell {
    packages = [ python ] ++ (with pkgs; [ uv basedpyright ruff nixd ]);

    env = {
      # Use the Nix interpreter rather than letting uv download one
      UV_PYTHON = python.interpreter;
      UV_PYTHON_DOWNLOADS = "never";

      # PyPI manylinux wheels (numpy, scipy, numba, soxr) expect these on the system path
      LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath (with pkgs; [ stdenv.cc.cc.lib zlib ]);
    };

    shellHook = ''
      uv sync --quiet
      source .venv/bin/activate
    '';
  }
