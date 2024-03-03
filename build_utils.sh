cd build/utils
cabal build
cd ../../
cp $(find . -name utils-0.1.0.0)/x/prep_onto/build/prep_onto/prep_onto ./
cp $(find . -name utils-0.1.0.0)/x/simple_parse/build/simple_parse/simple_parse ./