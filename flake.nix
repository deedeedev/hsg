{
  description = "hsg — Chinese text coverage analysis and comprehensible sentence mining";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python312;
      in
      {
        packages.hsg = python.pkgs.buildPythonPackage rec {
          pname = "hsg";
          version = "1.0.0";
          src = self;
          pyproject = true;
          build-system = [ python.pkgs.hatchling ];
          dependencies = with python.pkgs; [
            click
            rich
            tabulate
            pypinyin
            requests
          ];
        };
        defaultPackage = self.packages.${system}.hsg;
      }
    );
}
