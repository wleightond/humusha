# Humusha: Ontology Design Pattern Substitution in FOL Ontologies Proof-of-Concept Tool

A proof-of-concept tool for substituting ontology design patterns in first-order logic ontologies encoded in clif.

It includes pattern specifications in `config.json`, test ontologies in `test_files/`, and the raw result data in `/output/`

## Usage

To get a shell environment with the required packages (requires [nix](https://nixos.org/)):

    nix develop
    make utils

To make the binaries that find satisfied formulae

    ./humusha build-instance-finders


To run the full process for a given pattern, once instance finders and utils are built:

    ./humusha normalise-ontology  [ontology]
    ./humusha find-axiom-instances [pattern] [ontology]
    ./humusha make-substitutions [pattern] [ontology]
    ./humusha apply-substitutions [pattern] [ontology]


./humusha build-instance-finders
./humusha normalise-ontology  [ontology]
./humusha find-axiom-instances [pattern] [ontology]
./humusha make-substitutions [pattern] [ontology]
./humusha apply-substitutions [pattern] [ontology]
