"""Diagnose native DC/AC initialization with independently fixed bias guesses."""
import uuid
from pathlib import Path

import numpy as np

from ts808_validation.artifacts import ROOT,atomic_json,load_json
from ts808_validation.cli import make_deck
from ts808_validation.persist import import_reference,consume_reference
from ts808_validation.simulator import prepare_request,run_request


def main():
    output=Path('/mnt/f/ts808-validation/substeps-20261104/ac-bias-diagnosis')
    output.mkdir(exist_ok=False)
    cfg=load_json(ROOT/'validation/toolchain-pilot-f.json')
    catalog=load_json(ROOT/'reference/ts808/cases.json')['cases']
    matrix=output.parent/'matrix'
    rows=[]
    for solver,nodeset in [('norm',False),('alt',False),('norm',True),('alt',True)]:
        for kind in ('dc','ac'):
            case=next(c for c in catalog if c['case_id']==kind+'_d000_t000_v050')
            target=output/(kind+'-'+solver+('-nodeset' if nodeset else ''));target.mkdir()
            cp=target/'case.json';atomic_json(cp,case)
            deck=make_deck(case).replace('.temp 25','.temp 25\n.options solver='+solver)
            if nodeset:
                # T22's fixed physical bias guess; never imported from a C++ solution.
                zeros={'input','tone_rc','output','z_clip','z_tone'}
                emitters={'input_emitter','output_emitter','output_cap'}
                guesses=[]
                for name in case['trace_columns'][1:]:
                    if name.startswith('i_'):continue
                    native={'z_clip':'xclip:z','z_tone':'xtone:z'}.get(name,name)
                    value=0 if name in zeros else 3.85 if name in emitters else 4.5
                    guesses.append(f'V({native})={value}')
                deck=deck.replace('.end','.nodeset '+' '.join(guesses)+'\n.end')
            dest=Path(cfg['workspace']['wsl_root'])/(target.name+'-'+uuid.uuid4().hex)
            prepare_request(ROOT/'reference/ts808',cp,dest,request_id=dest.name,
                            settings=dict(level='nominal',maxstep_s=1/(384000*8),dc_protocol=f'solver={solver}; independently fixed T22 bias guess={nodeset}'),deck=deck)
            try:
                run_request(dest,Path(cfg['tools']['ltspice']['path']))
                imported=target/'reference';import_reference(dest,imported,cfg)
                manifest,_,native=consume_reference(imported,cfg)
                actual=np.array([native['traces'][t['native_expression']][0] for t in manifest['selection']['traces']])
                cpp=np.fromfile(matrix/'ac_d000_t000_v050/192000/run/traces.f64le',dtype='<f8').reshape(-1,32)[0,1:]
                row=dict(kind=kind,solver=solver,nodeset=nodeset,directory=str(dest),dc_solver=native['dc_solver'])
                if kind=='dc':
                    indices=[i for i,n in enumerate(case['trace_columns'][1:]) if not n.startswith('i_')]
                    row['max_voltage_difference_V']=float(np.max(abs(actual[indices]-cpp[indices])))
                    row['input_base_V']=float(actual[case['trace_columns'].index('input_base')-1])
                else:
                    output_exp=next(t['native_expression'] for t in manifest['selection']['traces'] if t['quantity_id']=='output')
                    row['output_peak_gain']=float(np.max(abs(native['traces'][output_exp])))
            except (RuntimeError,ValueError) as error:
                row=dict(kind=kind,solver=solver,nodeset=nodeset,directory=str(dest),error=str(error))
            rows.append(row);atomic_json(output/'diagnosis.json',dict(measurements=rows));print(row,flush=True)


if __name__=='__main__':
    main()
