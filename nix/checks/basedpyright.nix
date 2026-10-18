# Type checks the Python sources against the project's locked dependencies
{
  pkgs,
  flake,
  perSystem,
  ...
}:
pkgs.runCommandLocal "basedpyright" { nativeBuildInputs = [ pkgs.basedpyright ]; } ''
  export HOME=$TMPDIR
  cd ${flake}
  basedpyright --pythonpath ${perSystem.self.default}/bin/python
  touch $out
''
