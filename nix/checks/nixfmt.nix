# Checks the Nix sources are formatted the way `nix fmt` would leave them
{ pkgs, flake, ... }:
pkgs.runCommandLocal "nixfmt" { nativeBuildInputs = [ pkgs.nixfmt ]; } ''
  nixfmt --check $(find ${flake} -name '*.nix')
  touch $out
''
