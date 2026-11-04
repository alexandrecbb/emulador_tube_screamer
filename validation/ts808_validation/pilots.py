"""Resource-measured pilots. Full matrix is forbidden until pilot gates pass."""
import argparse,copy,json,shutil,subprocess,time,uuid
from pathlib import Path
from .artifacts import ROOT,load_json,atomic_json,finalize_run
from .cli import make_deck,doctor
from .simulator import prepare_request,run_request
from .persist import import_reference,consume_reference,validate_schema
from .compare import compare,validator_hash


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--toolchain',type=Path,default=ROOT/'validation/toolchain.json')
    parser.add_argument('--case-ids',nargs='+',default=['tone_center_f1000_a100mv','tone_high_f1000_a500mv','overload_high'])
    parser.add_argument('--refresh-comparisons',action='store_true')
    parser.add_argument('--solver',choices=['normal','alternate'],default='normal');args=parser.parse_args();native_solver={'normal':'norm','alternate':'alt'}[args.solver]
    cfg=load_json(args.toolchain)
    if doctor(args.toolchain)['status']!='passed':raise RuntimeError('Toolchain failed')
    args.output.mkdir(parents=True,exist_ok=True);catalog=load_json(ROOT/'reference/ts808/cases.json')['cases'];catalog.extend(r['case'] for r in load_json(ROOT/'reference/ts808/case_revisions.json')['revisions']);summary=[];prior_summary=load_json(args.output/'pilots.json') if (args.output/'pilots.json').exists() else {'pilots':[]}
    for case_id in args.case_ids:
        base=next(c for c in catalog if c['case_id']==case_id);physical=args.output/case_id;physical.mkdir(exist_ok=True);cp=physical/'case.json';atomic_json(cp,base);refs={};resources=[];saved=load_json(physical/'resources.json').get('measurements',[]) if (physical/'resources.json').exists() else []
        for refined in (False,True):
            level='refined' if refined else 'nominal';pointer=physical/(level+'-request.json')
            start=time.monotonic()
            if pointer.exists():
                dest=Path(load_json(pointer)['directory'])
            else:
                dest=Path(cfg['workspace']['wsl_root'])/(case_id+'-'+level+'-'+uuid.uuid4().hex)
                prepare_request(ROOT/'reference/ts808',cp,dest,request_id=dest.name,settings=dict(level=level,maxstep_s=1/(384000*8*(2 if refined else 1)),dc_protocol='solver='+native_solver+'; gminsteps=0 srcsteps=0; native pseudo-transient audited'),deck=make_deck(base,refined).replace('.temp 25','.temp 25\n.options solver='+native_solver))
                atomic_json(pointer,dict(directory=str(dest)))
            result=load_json(dest/'reference_result.json') if (dest/'reference_result.json').exists() else run_request(dest,Path(cfg['tools']['ltspice']['path']))
            refs[level]=physical/level
            manifest=load_json(refs[level]/'reference.json') if refs[level].exists() else import_reference(dest,refs[level],cfg)
            resources.append(dict(level=level,elapsed_s=time.monotonic()-start,native_elapsed_s=result['invocation']['elapsed_s'],point_count=manifest['validation']['point_count'],bytes=sum(e['size_bytes'] for e in result['files']),directory=str(dest)))
            atomic_json(physical/'resources.json',dict(reference=resources));print(case_id,level,resources[-1],flush=True)
        reused_sources_checked=False
        for rate in (192000,384000,768000):
            case=copy.deepcopy(base);case['execution']['rate_Hz']=rate;case['execution']['purpose']='pilot';case['analysis']['time']['sample_count']=round(case['analysis']['time']['duration_s']*rate)+1
            target=physical/str(rate);target.mkdir(exist_ok=True);cp=target/'case.json';atomic_json(cp,case)
            start=time.monotonic()
            previous=next((m for p in prior_summary.get('pilots',[]) if p['case_id']==case_id for m in p['measurements'] if m.get('rate_Hz')==rate),None) if prior_summary['pilots'] else None
            if previous is None:previous=next((m for m in saved if m.get('rate_Hz')==rate),None)
            if previous is None and (target/'execution-measurement.json').exists():previous=load_json(target/'execution-measurement.json')
            state=load_json(target/'run/run.json') if (target/'run/run.json').exists() else None
            if state and state['completion']['state']=='completed':
                p=subprocess.CompletedProcess([],0,b'',b'')
            elif state and state['completion']['state']=='failed':
                p=subprocess.CompletedProcess([],20 if state['completion']['written_samples']==0 else 21,b'',state['diagnostics']['reason'].encode())
            else:
                if (target/'run').exists():(target/'run').rename(target/('run-interrupted-'+uuid.uuid4().hex))
                p=subprocess.run([str(ROOT/'build/offline-release/ts808_offline'),'--case',str(cp),'--output',str(target/'run')],capture_output=True)
            resource=dict(rate_Hz=rate,elapsed_s=previous['elapsed_s'] if previous else None if (target/'run/run.json').exists() and p.args==[] else time.monotonic()-start,exit_code=p.returncode)
            if resource['elapsed_s'] is not None:atomic_json(target/'execution-measurement.json',resource)
            if p.returncode:resource['error']=p.stderr.decode()
            else:
                finalize_run(target/'run',cp,ROOT/'build/offline-release/ts808_offline')
                recorded=Path(previous['comparison_directory']) if previous and previous.get('comparison_directory') and not args.refresh_comparisons else None
                if recorded is not None and (recorded/'report.json').exists():
                    if not recorded.resolve().is_relative_to(target.resolve()):raise ValueError('Recorded comparison escapes target')
                    if not reused_sources_checked:
                        for reference in refs.values():
                            verified=consume_reference(reference,cfg);del verified
                        reused_sources_checked=True
                    prior=load_json(recorded/'report.json');validate_schema('report',prior)
                    from .simulator import sha256
                    if prior['inputs']['run_sha256']!=sha256(target/'run/run.json'):raise ValueError('Recorded comparison run changed')
                    comparison=recorded
                else:
                    comparison=target/('comparison-'+validator_hash()[:10] if args.refresh_comparisons else 'comparison')
                report=load_json(comparison/'report.json') if (comparison/'report.json').exists() else compare(target/'run',refs['nominal'],refs['refined'],comparison,cfg)
                resource['comparison_directory']=str(comparison)
                resource['outcomes']=report['outcomes'];resource['bytes']=sum(f.stat().st_size for f in (target/'run').iterdir())
            resources.append(resource);atomic_json(physical/'resources.json',dict(measurements=resources));print(case_id,rate,resource,flush=True)
        summary.append(dict(case_id=case_id,measurements=resources));atomic_json(args.output/'pilots.json',dict(pilots=summary,full_matrix_authorized=len(summary)==3 and all(m.get('outcomes',{}).get('numerical')=='passed' for p in summary for m in p['measurements'] if 'rate_Hz' in m)))
    return 0 if load_json(args.output/'pilots.json')['full_matrix_authorized'] else 40

if __name__=='__main__':raise SystemExit(main())
