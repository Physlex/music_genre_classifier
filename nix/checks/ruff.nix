# Lints the Python sources and checks their formatting with ruff
{ pkgs, flake, ... }:
pkgs.runCommandLocal "ruff" { nativeBuildInputs = [ pkgs.ruff ]; } ''
  cd ${flake}
  ruff check --no-cache .
  ruff format --no-cache --check .
  touch $out
''
