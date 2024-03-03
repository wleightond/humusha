{
  inputs = {
    utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, utils }: utils.lib.eachDefaultSystem (system:
    let
      pkgs = nixpkgs.legacyPackages.${system};
      inputList = with pkgs; [ cabal-install ghc git gnumake python3 ];
    in
    {
      devShell = pkgs.mkShell {
        buildInputs = inputList;
      };
    }
  );
}
