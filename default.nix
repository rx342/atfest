{
  source ? import ./npins,
  system ? builtins.currentSystem,
  pkgs ? import source.nixpkgs {
    overlays = [ ];
    config = { };
    inherit system;
  },
}:

{
  shell = pkgs.mkShellNoCC {
    name = "atfest";
    packages = [
      pkgs.uv
      pkgs.python3
    ];
  };
}
