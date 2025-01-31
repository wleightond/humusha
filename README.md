# Humusha: Ontology Pattern Substitution in FOL Ontologies Proof-of-Concept Tool

[![DOI](https://zenodo.org/badge/824579063.svg)](https://doi.org/10.5281/zenodo.13983309)

A proof-of-concept tool for substituting ontology design patterns in first-order logic ontologies encoded in clif.

It includes pattern specifications in `config.json`, test ontologies in `test_files/`, and the raw result data in `/output/`

## Usage

To get a shell environment with the required packages (requires [nix](https://nixos.org/)):

    nix develop
    make utils

To make the binaries that find satisfied formulae

    ./humusha build-instance-finders


To run the full process for a given pattern, once instance finders and utils are built:

    ./humusha build-instance-finders
    ./humusha normalise-ontology  [ontology]
    ./humusha find-axiom-instances [pattern] [ontology]
    ./humusha make-substitutions [pattern] [ontology]
    ./humusha apply-substitutions [pattern] [ontology]

## Licenses
Software is licensed under the GPL v2.0 (source code from HETS is a critical component and is itself licensed this way); ontologies retain their original licenses.

## Preferred Citation
If you would like to cite this project, please cite the original publication:
> Dawson, W.L., Keet, C.M. Ontology Pattern Substitution: Toward their use for domain ontologies. FOIS'24 Demonstrations Track. Enschede, The Netherlands, 15-19 July 2024. CEUR-WS (in print)
