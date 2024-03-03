#!/usr/bin/env python

from os import listdir
from sys import stdin, stderr
import sys
from typing import *
from itertools import chain, combinations

DEBUG = True

COP = 'cop'
COP_B = 'cop_b'
PCOP = 'pcop'
CDP = 'cdp'
QDP = 'qdp'
RR = 'rr'
CRA = 'cra_e'

PATTERNS = [COP, COP_B, PCOP, CDP, QDP, RR, CRA]

# Axiom instances have a formula name, list of variables, and the axiom
AxiomInstance = NewType("AxiomInstance", Tuple[str, Sequence[str], str])

# Pattern instances have a pattern name, list of variables, and *list* of axioms
PatternInstance = NewType("PatternInstance", Tuple[str, Sequence[str], Sequence[str]])

# Substitutions are made of a list of axioms to remove and a list of axioms to add
Substitution = NewType("Substitution", Tuple[Sequence[str], Sequence[str]])


def valid_cops(matches: Sequence[AxiomInstance]) -> Sequence[PatternInstance]:
    cops: MutableSequence[PatternInstance] = []
    # cop_f1s, cop_f2s = [], []
    for (name, objs, axiom) in matches:
        if name.startswith("COP_f1"):
            cops.append(PatternInstance(("COP", objs, [axiom])))
    return cops
    #         cop_f1s.append((name, objs, axiom))
    #     elif name == 'COP_f2':
    #         cop_f2s.append((name, objs, axiom))
    # for (_, f1_objs, f1_axiom) in cop_f1s:
    #     for (_, f2_objs, f2_axiom) in cop_f2s:
    #         if f1_objs[1] == f2_objs[1]:
    #             cops.append(('COP', [f1_objs[0], f2_objs[0]], [f1_axiom, f2_axiom]))

def sub_cops(cops: Sequence[PatternInstance]) -> List[Substitution]:
    sub_cop = lambda e, d, _, f: [
        f"(forall (x) (forall (y) (if (has{e} x y) (and ({d} x) ({f} y)))))"
    ]
    return [Substitution((axioms, sub_cop(*tuple(objs)))) for (_, objs, axioms) in cops]

def valid_copbs(matches: Sequence[AxiomInstance]) -> Sequence[PatternInstance]:
    cops: MutableSequence[PatternInstance] = []
    cop_f1s: MutableSequence[PatternInstance] = []
    # cop_f1s, cop_f2s = [], []
    # bookloan book   participant person
    # e        d      _           f
    # bookloan book   participant
    # e        d      _
    # bookloan person participant
    # e        f      _
    for (name, objs, axiom) in matches:
        if name == "COP_b_f1":
            cop_f1s.append((name, objs, axiom))
    for (
        (_, f1_objs, f1_axiom),
        (_, f2_objs, f2_axiom)
     ) in combinations(cop_f1s, 2):
            if f1_objs[0] == f2_objs[0]:
                cops.append(('COP_b', [f1_objs[0], f1_objs[1], f2_objs[1]], [f1_axiom, f2_axiom]))
    return cops


def sub_copbs(cops: Sequence[PatternInstance]) -> List[Substitution]:
    sub_cop = lambda e, d, f: [
        f"(forall (x) (forall (y) (if (has{e} x y) (and ({d} x) ({f} y)))))"
    ]
    return [Substitution((axioms, sub_cop(*tuple(objs)))) for (_, objs, axioms) in cops]


def valid_pcops(matches: Sequence[AxiomInstance]) -> Sequence[PatternInstance]:
    cops: Sequence[PatternInstance] = valid_cops(matches)
    pcops: MutableSequence[PatternInstance] = []
    # breakpoint()
    for (_, cop_objs, cop_axioms) in cops:
        d, f, _, e = cop_objs
        f1_axiom, f2_axiom, f3_axiom = "", "", ""
        for (name, objs, axiom) in matches:
            if name.startswith("PCOP_f2") and objs[0] == d:
                f1_axiom = axiom
            elif name.startswith("PCOP_f1") and objs[0] == f:
                f2_axiom = axiom
            elif name.startswith("PCOP_f1") and objs[0] == e:
                f3_axiom = axiom
            if f1_axiom and f2_axiom and f3_axiom:
                pcops.append(
                    PatternInstance(("PCOP", cop_objs, [f1_axiom, f2_axiom, f3_axiom]+cop_axioms))
                )
    return pcops


#  { ∀x(D(x) → ED(x)),
#    ∀x(F(x) → ED(x)),
#    ∀x(E(x) → PD(x)) }
#           ||          but replicate COP as well
#           \/
#  {                  }



def sub_pcops(pcops: Sequence[PatternInstance]) -> List[Substitution]:
    sub_cop = lambda e, d, _, f: [
        f"(forall (x) (forall (y) (if (has{e} x y) (and ({d} x) ({f} y)))))"
    ]
    return [Substitution((axioms, sub_cop(*tuple(objs)))) for (_, objs, axioms) in pcops]


def valid_cdps(matches: Sequence[AxiomInstance]) -> Sequence[PatternInstance]:
    cdps: MutableSequence[PatternInstance] = []
    for (name, objs, axiom) in matches:
        if name.startswith("CDP_f1"):
            cdps.append(PatternInstance(("CDP", objs[:2], [axiom])))
    return cdps


def sub_cdps(cdps: Sequence[PatternInstance]) -> List[Substitution]:
    "∀x,y(D(x)→∃y(E(y)∧ATT(x,y))"
    sub_cdp = lambda d, e: [
        f"(forall (x) (if ({d} x) (exists (y) (and ({e} y) (hasDataValue x y)))))"
    ]
    return [
        Substitution((axioms, sub_cdp(*tuple(objs[:2]))))
        for (name, objs, axioms) in cdps
    ]


def valid_qdps(matches: Sequence[AxiomInstance]) -> Sequence[PatternInstance]:
    qdps: MutableSequence[PatternInstance] = []
    for (name, objs, axiom) in matches:
        if name.startswith("QDP_f1"):
            qdps.append(PatternInstance(("QDP", objs, [axiom])))
    return qdps


def sub_qdps(qdps: Sequence[PatternInstance]) -> List[Substitution]:
    sub_qdp = lambda a, b: [
        f"(forall (x) (if ({a} x) (exists (y) (and ({b} y) (hasDataValue x y)))))"
    ]
    return [
        Substitution((axioms, sub_qdp(*tuple(objs[:2]))))
        for (name, objs, axioms) in qdps
    ]


# RR_f1: A -> POB                                   |-> A
# RR_f2: B -> SOB                                   |-> B
# RR_f3a: forall x,y ((A(x) and B(y)) -> OD(x, y)   |-> A B
# RR_f3b: forall x,y ((A(x) and B(y)) -> OGD(x, y)  |-> A B

# So, given RR_f3* on A and B we need to find an RR_f1 on A and RR_f2 on B


def valid_rrs(matches: Sequence[AxiomInstance]) -> Sequence[PatternInstance]:
    rrs: MutableSequence[PatternInstance] = []
    rrf3s = [
        (name, objs, axiom) for (name, objs, axiom) in matches if name[:5] == "RR_f3"
    ]
    for f3 in rrf3s:
        _, objs, f3_axiom = f3
        a, b = objs[0], objs[1]
        f1_axiom, f2_axiom = "", ""
        for (name, objs, axiom) in matches:
            if name.startswith("RR_f1") and objs[0] == b:
                f1_axiom = axiom
            if name.startswith("RR_f2") and objs[0] == a:
                f2_axiom = axiom
            if f1_axiom and f2_axiom:
                break
        if f1_axiom and f2_axiom:
            rrs.append(PatternInstance(("RR", [a, b], [f1_axiom, f2_axiom, f3_axiom])))
    return rrs


def sub_rrs(rrs: Sequence[PatternInstance]) -> List[Substitution]:
    sub_rr = lambda a, b: [f"(forall (x) (if ({a} x) ({b} x)))"]
    return [
        Substitution((axioms, sub_rr(*tuple(objs)))) for (name, objs, axioms) in rrs
    ]


def valid_cras(matches: Sequence[AxiomInstance]) -> Sequence[PatternInstance]:
    cra_as: List[PatternInstance] = []
    cra_es: List[PatternInstance] = []
    for (name, objs, axiom) in matches:
        if name.startswith("CRA_a_f1"):
            cra_as.append(PatternInstance(("CRA_a", objs, [axiom])))
        if name.startswith("CRA_a_f2"):
            cra_as.append(PatternInstance(("CRA_a", objs, [axiom])))
        if name.startswith("CRA_e_f1"):
            cra_as.append(PatternInstance(("CRA_e", objs, [axiom])))
    return cra_as + cra_es


#  { forall x (C(x) -> exists y (R(x, y) and exists z (D(y, z))))                                       }
#                   ||
#                   \/
#  { forall x (C(x) -> exists y (hasDataValue(x, y))) }
def sub_cras(cras: Sequence[PatternInstance]) -> List[Substitution]:
    sub_cra = lambda d: [f"(forall (x) (if ({d} x) (exists (y) (hasDataValue x y))))"]
    return [Substitution((axioms, sub_cra(objs[0]))) for (name, objs, axioms) in cras]



def get_matches(instr: str) -> Sequence[AxiomInstance]:
    # print(instr)
    instances = instr.split("INSTANCE\n")
    matches = []
    for inst in instances:
        if inst:
            # print(inst)
            name, objs = eval(inst[: inst.index("\n")].replace("Just ", ""))
            axiom = inst[inst.index("\n") + 1 :]
            matches.append(AxiomInstance((name, objs, axiom)))
    return matches


if __name__ == "__main__":
    funcs = {
        COP: (valid_cops, sub_cops), 
        COP_B: (valid_copbs, sub_copbs), 
        PCOP: (valid_pcops, sub_pcops), 
        CDP: (valid_cdps, sub_cdps), 
        QDP: (valid_qdps, sub_qdps), 
        RR: (valid_rrs, sub_rrs), 
        CRA: (valid_cras, sub_cras),
    }

    active_patterns = list(filter(
        lambda s: s in PATTERNS,
        sys.argv
    ))

    matches = get_matches(stdin.read().strip())
    # matches: Sequence[AxiomInstance] = [AxiomInstance(match) for match in raw_matches]
    stderr.write(f"matches:")
    for match in matches:
        stderr.write(f"\t{match}\n")
    
    subd: dict[str, list[Substitution]] = {}

    for patt in PATTERNS:
        if patt in active_patterns:
            get_valid, substitute = funcs[patt]
            valids = get_valid(matches)
            stderr.write(f"valid_{patt}s(matches): {valids}\n")
            stderr.write(f"sub_{patt}s({patt}s) {substitute(valids)}\n")
            subd[patt] = substitute(valids)

    subs = list(chain.from_iterable(subd.values()))
    subs = list(map(
        eval, 
        set(
            map(repr, subs)
        )))
    stderr.write("\n\nsubs:")
    stderr.write("\n".join(map(repr, subs)))
    stderr.write("\n\n")
    out_str = ""
    if subs:
        stderr.write(f"{len(subs)} substitution{'' if len(subs) == 1 else 's'} generated.\n\n")
        for sub in subs:
            in_axiom_ls, out_axiom_ls = sub
            for axiom in in_axiom_ls:
                out_str += f"COMMAND: DELETE\n{axiom}\n"
            for axiom in out_axiom_ls:
                out_str += f"COMMAND: ADD\n{axiom}\n"
    else:
        stderr.write("No substitutions generated.\n\n")
    print(out_str)

