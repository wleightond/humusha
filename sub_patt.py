#!/usr/bin/env python
from sys import argv, stdin

def get_comms(instr):
    comms = instr.split('COMMAND: ')[1:]
    deletes, adds = [], []
    for comm in comms:
        if 'ADD' in comm:
            if comm.index('ADD') == 0:
                add = comm[comm.index('\n')+1:]
                adds.append(add.strip())
        elif 'DELETE' in comm:
            if comm.index('DELETE') == 0:
                delete = comm[comm.index('\n')+1:].strip()
                deletes.append(delete)
    return adds, deletes

if __name__ == '__main__':
    if len(argv) > 2:
        comms_file = argv[-2]
        with open(comms_file) as f: in_str = f.read()
        in_file = argv[-1]
    elif len(argv) == 2:
        in_str = stdin.read()
        in_file = argv[-1]
    else:
        print('Usage: sub_patt.py comm_file input_ontology > output_ontology')
        exit(0)
    
    with open(in_file) as f: out_str = f.read()
    # print(out_str.__repr__())
    adds, deletes = get_comms(in_str)
    # print(deletes)
    for delete in deletes:
        try:
            assert delete in out_str
        except Exception as e:
            print(f'Axiom text not found:\n{delete}')
            print('This might happen if the ontology was not passed through `prep_onto` first.')
            exit(1)
        out_str = out_str.replace(delete, '')
    # print(adds)
    for add in adds:
        out_str += ('' if not out_str or out_str.endswith('\n') else '\n') + add
    while '\n\n' in out_str:
        out_str = out_str.replace('\n\n', '\n')
    print(out_str)
    