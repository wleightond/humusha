# Humusha: Ontology Design Pattern Substitution in FOL Ontologies Proof-of-Concept Tool

A proof-of-concept tool for substituting ontology design patterns in first-order logic ontologies encoded in clif.

It includes pattern specifications in `config.json`, test ontologies in `test_files/`, and the raw result data in `/output/`

## Usage

To get a shell environment with the required packages (requires [nix](https://nixos.org/)):

    nix develop
    make utils

To make the binaries that find satisfied formulae

    ./build_instance_finders.py
    # OR
    make finders


To run the full process for a given pattern, once instance finders and prep_onto are built:

    ./odpsub [pattern] [ontology]

To test the patterns currently working:

    for i in {cdp,cop,pcop,rr}; do ./odpsub $i test_$i.clif; done

To manually perform a step of the process:

for a given formula

    cat ontofile | ./bin/[formula] > [formula]_instances

for a given pattern

    cat [instance files] | ./make_subs.py > subs
    cat ontofile | ./prep_onto > outputonto
    ./sub_patt.py subs output_onto
