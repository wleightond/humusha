#!/usr/bin/env python

from dataclasses import dataclass, asdict
import json
from os import listdir
from sys import stdin, stderr
import sys
from typing import *
from itertools import chain, combinations, product
from models import (
    AxiomInstance,
    PatternInstance,
    PatternObject,
    CDP,
    COP,
    COP_B,
    CRA,
    PATTERNS,
    PCOP,
    QDP,
    RR,
    serialize,
)

DEBUG = True


def get_instances(instr: str, config: dict) -> list[AxiomInstance]:
    # print(instr)
    instances = instr.split("INSTANCE\n")
    matches = []
    for inst in instances:
        if inst:
            # print(inst)
            formula, raw_objs = eval(inst[: inst.index("\n")].replace("Just ", ""))
            axiom = inst[inst.index("\n") + 1 :]
            objs = [
                PatternObject(formula, obj_name, obj_value)
                for obj_name, obj_value in zip(
                    config["formulae"][formula]["objs"], raw_objs
                )
            ]
            matches.append(AxiomInstance(formula, objs, axiom))
    return matches


def filter_axioms(formula: str, matches: list[AxiomInstance]) -> list[AxiomInstance]:
    return [
        axiom_instance
        for axiom_instance in matches
        if axiom_instance.formula_name == formula
    ]


def segregate_matches(
    pattern: str, matches: list[AxiomInstance], config: dict
) -> dict[str, list[AxiomInstance]]:
    return {
        formula: filter_axioms(formula, matches)
        for formula in config["patterns"][pattern]["formulae"]
    }


def get_object_from_combination(
    ref: list[str], combination: tuple[AxiomInstance, ...]
) -> PatternObject:
    formula, obj_name, *_ = ref
    for axiom_instance in combination:
        if axiom_instance.formula_name == formula:
            for obj in axiom_instance.objs:
                if obj.object_name == obj_name:
                    return obj
    raise ValueError(
        f"Combination did not have object '{obj_name}' for formula '{formula}': {combination}"
    )


CONSTRAINT_OPS = {"EQUALS": lambda a, b: a == b}


def check_combination(
    combination: tuple[AxiomInstance, ...], pattern: str, config: dict
) -> bool:
    constraints: list[list[list[str]]] = config["patterns"][pattern]["constraints"]
    for [op, left_ref, right_ref] in constraints:
        left_obj = get_object_from_combination(left_ref, combination)
        right_obj = get_object_from_combination(right_ref, combination)
        if not CONSTRAINT_OPS[op](left_obj.object_value, right_obj.object_value):
            return False
    return True


def valid_matches(
    pattern: str, matches: list[AxiomInstance], config: dict
) -> list[PatternInstance]:
    pattern_instances: list[PatternInstance] = []
    segregated_matches = segregate_matches(pattern, matches, config)

    for combination in product(*segregated_matches.values()):
        if check_combination(combination, pattern, config):
            objs = chain(*(axiom_instance.objs for axiom_instance in combination))
            instance = PatternInstance(
                pattern=pattern, objs=list(objs), axioms=combination
            )
            pattern_instances.append(instance)
    return pattern_instances


def valid_cops(
    pattern: str, matches: list[AxiomInstance], config: dict
) -> list[PatternInstance]:
    cops: list[PatternInstance] = []
    # cop_f1s, cop_f2s = [], []
    for name, objs, axiom in matches:
        if name.startswith("COP_f1"):
            cops.append(PatternInstance(("COP", objs, [axiom])))
    return cops


def valid_copbs(
    pattern: str, matches: list[AxiomInstance], config: dict
) -> list[PatternInstance]:
    cops: list[PatternInstance] = []
    cop_f1s: list[PatternInstance] = []
    # cop_f1s, cop_f2s = [], []
    # bookloan book   participant person
    # e        d      _           f
    # bookloan book   participant
    # e        d      _
    # bookloan person participant
    # e        f      _
    for name, objs, axiom in matches:
        if name == "COP_b_f1":
            cop_f1s.append((name, objs, axiom))
    for (_, f1_objs, f1_axiom), (_, f2_objs, f2_axiom) in combinations(cop_f1s, 2):
        if f1_objs[0] == f2_objs[0]:
            cops.append(
                ("COP_b", [f1_objs[0], f1_objs[1], f2_objs[1]], [f1_axiom, f2_axiom])
            )
    return cops


def valid_pcops(
    pattern: str, matches: list[AxiomInstance], config: dict
) -> list[PatternInstance]:
    cops: list[PatternInstance] = valid_cops(matches)
    pcops: list[PatternInstance] = []
    # breakpoint()
    for _, cop_objs, cop_axioms in cops:
        d, f, _, e = cop_objs
        f1_axiom, f2_axiom, f3_axiom = "", "", ""
        for name, objs, axiom in matches:
            if name.startswith("PCOP_f2") and objs[0] == d:
                f1_axiom = axiom
            elif name.startswith("PCOP_f1") and objs[0] == f:
                f2_axiom = axiom
            elif name.startswith("PCOP_f1") and objs[0] == e:
                f3_axiom = axiom
            if f1_axiom and f2_axiom and f3_axiom:
                pcops.append(
                    PatternInstance(
                        ("PCOP", cop_objs, [f1_axiom, f2_axiom, f3_axiom] + cop_axioms)
                    )
                )
    return pcops


def valid_cdps(
    pattern: str, matches: list[AxiomInstance], config: dict
) -> list[PatternInstance]:
    cdps: list[PatternInstance] = []
    for name, objs, axiom in matches:
        if name.startswith("CDP_f1"):
            cdps.append(PatternInstance(("CDP", objs[:2], [axiom])))
    return cdps


def valid_qdps(
    pattern: str, matches: list[AxiomInstance], config: dict
) -> list[PatternInstance]:
    qdps: list[PatternInstance] = []
    for name, objs, axiom in matches:
        if name.startswith("QDP_f1"):
            qdps.append(PatternInstance(("QDP", objs, [axiom])))
    return qdps


# def valid_rrs(pattern: str, matches: list[AxiomInstance], config: dict) -> list[PatternInstance]:
#     rrs: list[PatternInstance] = []
#     rrf3s = [
#         (name, objs, axiom) for (name, objs, axiom) in matches if name[:5] == "RR_f3"
#     ]
#     for f3 in rrf3s:
#         _, objs, f3_axiom = f3
#         a, b = objs[0], objs[1]
#         f1_axiom, f2_axiom = "", ""
#         for name, objs, axiom in matches:
#             if name.startswith("RR_f1") and objs[0] == b:
#                 f1_axiom = axiom
#             if name.startswith("RR_f2") and objs[0] == a:
#                 f2_axiom = axiom
#             if f1_axiom and f2_axiom:
#                 break
#         if f1_axiom and f2_axiom:
#             rrs.append(PatternInstance(("RR", [a, b], [f1_axiom, f2_axiom, f3_axiom])))
#     return rrs


def valid_cras(
    pattern: str, matches: list[AxiomInstance], config: dict
) -> list[PatternInstance]:
    cra_as: List[PatternInstance] = []
    cra_es: List[PatternInstance] = []
    for name, objs, axiom in matches:
        if name.startswith("CRA_a_f1"):
            cra_as.append(PatternInstance(("CRA_a", objs, [axiom])))
        if name.startswith("CRA_a_f2"):
            cra_as.append(PatternInstance(("CRA_a", objs, [axiom])))
        if name.startswith("CRA_e_f1"):
            cra_as.append(PatternInstance(("CRA_e", objs, [axiom])))
    return cra_as + cra_es


CUSTOM_PATTERN_FUNCTIONS = {
    # COP: valid_cops,
    COP_B: valid_copbs,
    # PCOP: valid_pcops,
    # CDP: valid_cdps,
    # QDP: valid_qdps,
    # RR: valid_rrs,
    # CRA: valid_cras,
}
