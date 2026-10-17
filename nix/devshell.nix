# Development shell: Nix provides the interpreter and tooling, uv manages Python packages
{ pkgs, ... }:
  pkgs.mkShell { }
