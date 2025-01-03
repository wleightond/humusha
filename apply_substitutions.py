from io import TextIOWrapper


def get_commands(instr):
    commands = instr.split("COMMAND: ")[1:]
    deletes, adds = [], []
    for comm in commands:
        if "ADD" in comm:
            if comm.index("ADD") == 0:
                add = comm[comm.index("\n") + 1 :].strip()
                adds.append(add)
        elif "DELETE" in comm:
            if comm.index("DELETE") == 0:
                delete = comm[comm.index("\n") + 1 :].strip()
                deletes.append(delete)
    return adds, deletes


def apply(
    adds: list[str], deletes: list[str], ontology: str, log: TextIOWrapper
) -> str:
    log.write(f"\nReceived {len(deletes)} axioms to delete.\n")
    for axiom_to_delete in deletes:
        log.write(f"\nDeleting axiom:\n")
        log.write(f"{axiom_to_delete}\n")
        try:
            assert axiom_to_delete in ontology
        except Exception as e:
            log.write(f"Axiom text not found:\n{axiom_to_delete}")
            log.write("This might happen if the ontology was not normalised first.")
            exit(1)
        ontology = ontology.replace(axiom_to_delete, "", 1)
    # log.write(adds)
    log.write(f"\nReceived {len(adds)} axioms to add.\n")
    for axiom_to_add in adds:
        log.write(f"\nAdding axiom:\n")
        log.write(f"{axiom_to_add}\n")
        ontology += (
            "" if not ontology or ontology.endswith("\n") else "\n"
        ) + axiom_to_add
    while "\n\n" in ontology:
        ontology = ontology.replace("\n\n", "\n")
    return ontology.strip()+'\n'
