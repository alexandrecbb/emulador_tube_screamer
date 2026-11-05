import copy,os,shutil,subprocess,traceback
from pathlib import Path
from ts808_validation.artifacts import ROOT,atomic_json,load_json,configure_substeps,finalize_run
from ts808_validation.suite import suite,validate_summary,file_ref
from ts808_validation.compare import compare
from ts808_validation.audio_qualification import qualify_audio
from ts808_validation.persist import ReferenceSession,import_reference
from ts808_validation.simulator import sha256
from ts808_validation.qualification import consolidate
job=Path(__file__).parent;root=job.parent
source=root/'qualification-resume-r10-20261104/matrix';seed=job/'seed'
cfg=load_json(ROOT/'validation/toolchain-pilot-f.json');exe=ROOT/'build/offline-release/ts808_offline'
def cp(src,dst):
    if str(src).endswith('.f64le'):os.link(src,dst);return dst
    return shutil.copy2(src,dst)
atomic_json(job/'status.json',dict(status='running',pid=os.getpid()))
try:
    print('Preserving source; recovering completed native refined import',flush=True)
    shutil.copytree(source,seed,copy_function=cp)
    physical=seed/'tone_high_f5000_a010mv'
    partial=physical/'refined'
    if partial.exists():partial.rename(physical/'refined-incomplete-preserved')
    dest=Path('/mnt/f/ts808-reference/runs/tone_high_f5000_a010mv-refined-2035339bb21c4452b789564d64e22054')
    result=load_json(dest/'reference_result.json')
    if result['completion']!='completed':raise ValueError('Native request not completed')
    import_reference(dest,physical/'refined',cfg)
    atomic_json(physical/'refined-request.json',dict(directory=str(dest),request_sha256=sha256(dest/'request.json')))
    attempts=load_json(physical/'refined-attempts.json')
    attempts['attempts'][-1].update(status='completed',recovered_import=True)
    atomic_json(physical/'refined-attempts.json',attempts)
    summary=load_json(seed/'summary.json');session=ReferenceSession()
    case=load_json(physical/'case.json')
    for rate in (192000,384000):
        target=physical/str(rate);target.mkdir()
        c=copy.deepcopy(case);configure_substeps(c,rate)
        c['analysis']['time']['sample_count']=round(c['analysis']['time']['duration_s']*rate)+1
        atomic_json(target/'case.json',c)
        subprocess.run([str(exe),'--case',str(target/'case.json'),'--output',str(target/'run')],check=True)
        finalize_run(target/'run',target/'case.json',exe)
        report=compare(target/'run',physical/'nominal',physical/'refined',target/'comparison',cfg,reference_session=session)
        report=qualify_audio(target/'case.json',target/'run',physical/'nominal',physical/'refined',target/'comparison',cfg,reference_session=session)
        e=next(e for e in summary['entries'] if e['case_id']==case['case_id'] and e['rate_Hz']==rate)
        for key,p in {'case':target/'case.json','run':target/'run/run.json','report':target/'comparison/report.json','nominal':physical/'nominal/reference.json','refined':physical/'refined/reference.json'}.items():e[key]=file_ref(seed,p)
        required=[report['outcomes'][k] for k in ('reference','numerical','wav') if report['outcomes'][k]!='not_applicable']
        ok=all(v=='passed' for v in required);failed='failed' in required
        e.update(status='passed' if ok else 'failed' if failed else 'not_evaluated',exit_code=0 if ok else 40 if failed else 50,reason='Recovered completed native import; measured gates preserved')
        print('Recovered case',rate,report['outcomes'],flush=True)
    session.verify()
    validate_summary(summary,load_json(seed/'cases.json')['cases']);atomic_json(seed/'summary.json',summary)
    print('Resuming remaining matrix',flush=True)
    code=suite(seed/'cases.json',ROOT/'validation/toolchain-pilot-f.json',exe,[192000,384000],job/'matrix',root/'pilots.json',native_solver='alt',resume_from=seed,native_tolerance_scale=1.,native_solver_fallback=False,native_topology_nodeset=True,continue_native_failures=True,native_solver_overrides={'tone_edge_t000_f5000_a100mv':'norm'})
    atomic_json(job/'partition-status.json',dict(exit_code=code))
    print('Starting complete assessment, preserving rejected gates',flush=True)
    result=consolidate(root,job/'qualification',job/'matrix/summary.json',require_passed=False)
    atomic_json(job/'status.json',dict(status='completed',exit_code=0,partition_exit_code=code,automatic_qualification=result['automatic_qualification'],assessment_completion=result['assessment_completion'],pid=os.getpid()))
except BaseException as e:
    atomic_json(job/'status.json',dict(status='failed',error=str(e),pid=os.getpid()));traceback.print_exc();raise
