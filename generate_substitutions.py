#!/usr/bin/env python

import json
from os import listdir
from sys import stdin, stderr
import sys
from typing import *
from dataclasses import dataclass
from itertools import chain, combinations, product

from models import (
    PatternInstance,
    Substitution,
    CDP,
    COP,
    COP_B,
    CRA,
    PATTERNS,
    PCOP,
    QDP,
    RR,
    deserialize,
)

DEBUG = True


def sub_cops(cops: Sequence[PatternInstance]) -> List[Substitution]:
    sub_cop = lambda e, d, _, f: [
        f"(forall (x) (forall (y) (if (has{e} x y) (and ({d} x) ({f} y)))))"
    ]
    return [Substitution((axioms, sub_cop(*tuple(objs)))) for (_, objs, axioms) in cops]


def sub_copbs(cops: Sequence[PatternInstance]) -> List[Substitution]:
    sub_cop = lambda e, d, f: [
        f"(forall (x) (forall (y) (if (has{e} x y) (and ({d} x) ({f} y)))))"
    ]
    return [Substitution((axioms, sub_cop(*tuple(objs)))) for (_, objs, axioms) in cops]


def sub_pcops(pcops: Sequence[PatternInstance]) -> List[Substitution]:
    sub_cop = lambda e, d, _, f: [
        f"(forall (x) (forall (y) (if (has{e} x y) (and ({d} x) ({f} y)))))"
    ]
    return [
        Substitution((axioms, sub_cop(*tuple(objs)))) for (_, objs, axioms) in pcops
    ]


def sub_cdps(cdps: Sequence[PatternInstance]) -> List[Substitution]:
    "∀x,y(D(x)→∃y(E(y)∧ATT(x,y))"
    sub_cdp = lambda d, e: [
        f"(forall (x) (if ({d} x) (exists (y) (and ({e} y) (hasDataValue x y)))))"
    ]
    return [
        Substitution((axioms, sub_cdp(*tuple(objs[:2]))))
        for (name, objs, axioms) in cdps
    ]


def sub_qdps(qdps: Sequence[PatternInstance]) -> List[Substitution]:
    sub_qdp = lambda a, b: [
        f"(forall (x) (if ({a} x) (exists (y) (and ({b} y) (hasDataValue x y)))))"
    ]
    return [
        Substitution((axioms, sub_qdp(*tuple(objs[:2]))))
        for (name, objs, axioms) in qdps
    ]


def sub_rrs(rrs: Sequence[PatternInstance]) -> List[Substitution]:
    sub_rr = lambda a, b: [f"(forall (x) (if ({a} x) ({b} x)))"]
    return [
        Substitution((axioms, sub_rr(*tuple(objs)))) for (name, objs, axioms) in rrs
    ]


def sub_cras(cras: Sequence[PatternInstance]) -> List[Substitution]:
    sub_cra = lambda d: [f"(forall (x) (if ({d} x) (exists (y) (hasDataValue x y))))"]
    return [Substitution((axioms, sub_cra(objs[0]))) for (name, objs, axioms) in cras]


def generate_substitution(
    pattern_instance: PatternInstance, config: dict
) -> Substitution:
    substitution_templates = config["patterns"][pattern_instance.pattern][
        "substitution"
    ]
    all_variables = {
        f"{obj.formula_name}_{obj.object_name}": obj.object_value
        for obj in pattern_instance.objs
    }
    return Substitution(
        axioms_to_delete=[axiom.sentence for axiom in pattern_instance.axioms],
        axioms_to_add=[
            template.format(**all_variables) for template in substitution_templates
        ],
    )


CUSTOM_SUBSTITUTION_FUNCTIONS = {
    COP: sub_cops,
    COP_B: sub_copbs,
    PCOP: sub_pcops,
    CDP: sub_cdps,
    QDP: sub_qdps,
    # RR: sub_rrs,
    CRA: sub_cras,
}
