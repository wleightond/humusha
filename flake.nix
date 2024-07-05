{
  inputs = {
    utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, utils }: utils.lib.eachDefaultSystem (system:
    let
      pkgs = nixpkgs.legacyPackages.${system};
      inputList = with pkgs; [ cabal-install ghc git gnumake python311Full python311Packages.click ];
    in
    {
      devShell = pkgs.mkShell {
        buildInputs = inputList;
      };
    }
  );
}
