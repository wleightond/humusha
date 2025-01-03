from dataclasses import asdict, dataclass
import json

COP = "cop"
COP_B = "cop_b"
PCOP = "pcop"
CDP = "cdp"
QDP = "qdp"
RR = "rr"
CRA = "cra_e"

PATTERNS = [COP, COP_B, PCOP, CDP, QDP, RR, CRA]


@dataclass
class PatternObject:
    formula_name: str
    object_name: str
    object_value: str


# Axiom instances have a formula name, list of variables, and the axiom
@dataclass
class AxiomInstance:
    formula_name: str
    objs: list[PatternObject]
    sentence: str


# Pattern instances have a pattern name, list of variables, and *list* of axioms
# PatternInstance = NewType("PatternInstance", Tuple[str, list[str], list[str]])
@dataclass
class PatternInstance:
    pattern: str
    objs: list[PatternObject]
    axioms: tuple[AxiomInstance, ...]

# Substitutions are made of a list of axioms to remove and a list of axioms to add
@dataclass
class Substitution:
    axioms_to_delete: list[str]
    axioms_to_add: list[str]


def deserialize_object_list(input_list: list[dict]) -> list[PatternObject]:
    return [PatternObject(**obj) for obj in input_list]


def deserialize_axiom_list(input_list: list[dict]) -> list[AxiomInstance]:
    return [AxiomInstance(**axiom) for axiom in input_list]


def serialize(pattern_instances: list[PatternInstance]) -> str:
    return json.dumps([asdict(instance) for instance in pattern_instances])


def deserialize(input_text: str) -> list[PatternInstance]:
    pattern_instance_dicts = json.loads(input_text)
    pattern_instances = []
    for item in pattern_instance_dicts:
        instance = PatternInstance(**item)
        instance.objs = deserialize_object_list(instance.objs)
        instance.axioms = deserialize_axiom_list(instance.axioms)
        for axiom in instance.axioms:
            axiom.objs = deserialize_object_list(axiom.objs)
        pattern_instances.append(instance)
    return pattern_instances
