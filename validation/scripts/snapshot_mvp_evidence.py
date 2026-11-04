"""Small versionable evidence snapshots; large original payloads stay local."""
from pathlib import Path
import copy,shutil,datetime
from ts808_validation.artifacts import ROOT,load_json,atomic_json
from ts808_validation.simulator import sha256,native_options
from ts808_validation.compare import validate_native_refinement
out=ROOT/'validation/results/mvp-2026-11-04';out.mkdir(parents=True,exist_ok=True)
revised=load_json(ROOT/'runs/mvp-revised-pilots-norm/pilots.json')['pilots'];overload=load_json(ROOT/'runs/mvp-pilots-02/overload_high/qualified-pilot.json');pilots=copy.deepcopy(revised+[overload]);snapshots=[];audits=[]
for pilot in pilots:
    case_id=pilot['case_id']
    for measured in pilot['measurements']:
        if 'level' in measured:
            if 'elapsed_s' in measured:measured['import_or_reuse_elapsed_s']=measured.pop('elapsed_s')
            continue
        rate=measured['rate_Hz'];original=Path(measured['comparison_directory'])
        if not original.is_absolute():original=ROOT/original
        original=original.resolve()
        if not original.is_relative_to(ROOT/'runs'):raise ValueError('Unexpected comparison source')
        target=original.parent
        timing=target/'execution-measurement.json'
        if timing.exists():
            t=load_json(timing)
            if t['elapsed_s'] is not None:
                measured['elapsed_s']=t['elapsed_s'];measured['measurement_kind']=t.get('measurement_kind','original monotonic execution timer')
        report=load_json(original/'report.json');destination=out/case_id/str(rate);destination.mkdir(parents=True,exist_ok=True)
        files={}
        for source,name in [(original/'report.json','report.json'),(original/'report.md','report.md'),(target/'case.json','case.json'),(target/'run/run.json','run.json')]:
            shutil.copyfile(source,destination/name);files[name]=sha256(destination/name)
        for artifact in report['artifacts']:
            if artifact['status']=='generated' and artifact['path']=='residual.png':
                shutil.copyfile(original/'residual.png',destination/'residual.png');files['residual.png']=sha256(destination/'residual.png')
        pair_options={}
        for level in ('nominal','refined'):
            meta=report['reference_qualification'][level];manifest_path=Path(meta['manifest_path']['wsl_path'])
            if sha256(manifest_path)!=meta['manifest_sha256']:raise ValueError('Changed imported reference manifest')
            ref=load_json(manifest_path);request_path=Path(ref['source']['request']['locator']['wsl_path']);result_path=Path(ref['source']['result']['locator']['wsl_path'])
            if sha256(request_path)!=meta['request_sha256'] or sha256(result_path)!=meta['result_sha256']:raise ValueError('Changed native producer metadata')
            request=load_json(request_path)
            for entry in request['inputs']:
                if sha256(request_path.parent/entry['path'])!=entry['sha256']:raise ValueError('Changed native staged input')
            pair_options[level]=native_options((request_path.parent/'deck.cir').read_text())
            for source,name in [(manifest_path,level+'-reference.json'),(request_path,level+'-request.json'),(result_path,level+'-result.json'),(Path(ref['source']['log']['locator']['wsl_path']),level+'.log')]:
                shutil.copyfile(source,destination/name);files[name]=sha256(destination/name)
        validate_native_refinement(pair_options['nominal'],pair_options['refined'])
        audit=dict(status='passed',report_sha256=files['report.json'],native_options=pair_options,scope='Independent audit of actual hashed producer options; waveform metrics remain from the closed original report')
        atomic_json(destination/'native-option-audit.json',audit);audits.append(dict(case_id=case_id,rate_Hz=rate,**audit))
        snapshots.append(dict(case_id=case_id,rate_Hz=rate,physical_case_sha256=report['physical_case_sha256'],path=str(destination.relative_to(out)),files=files,outcomes=report['outcomes']))
        measured['evidence_path']=str(destination.relative_to(out))
checks=[m for p in pilots for m in p['measurements'] if 'rate_Hz' in m]
atomic_json(out/'pilots.json',dict(pilots=pilots,completion='completed',full_matrix_authorized=all(m['outcomes']['numerical']=='passed' for m in checks),scope='Two explicitly revised settling pilots plus overload; all three rates are retained, 768 kHz is diagnostic only'))
small=['dc-audit.json','scaled-normal-audit.json','opamp-qualification.json','opamp-ac-qualification.json','fir-checks.json','native-wav-qualified.json','lifecycle.json','path-roundtrip.json','resource-gate.json','rejected-raw-archive.json']
for name in small:shutil.copyfile(ROOT/'runs/mvp-qualification'/name,out/name)
shutil.copyfile(ROOT/'runs/mvp-qualification/overload-192000-tighter10/diagnosis.json',out/'overload-tolerance-diagnosis.json')
shutil.copyfile(ROOT/'validation/toolchain.json',out/'toolchain-c.json');shutil.copyfile(ROOT/'validation/toolchain-pilot-f.json',out/'toolchain-f.json')
case=load_json(ROOT/'reference/ts808/cases.json');revisions=load_json(ROOT/'reference/ts808/case_revisions.json');active=copy.deepcopy(case);replacement={r['base_case_id']:r['case'] for r in revisions['revisions']}
active['cases']=[copy.deepcopy(replacement.get(c['case_id'],c)) for c in active['cases']]
for c in active['cases']:c['execution']['purpose']='target'
atomic_json(out/'active-cases.json',active)
source_hashes={}
for folder in ('src','include','app','schemas','reference/ts808','validation/ts808_validation','validation/scripts'):
    for source in sorted((ROOT/folder).rglob('*')):
        if source.is_file() and '__pycache__' not in source.parts and source.suffix!='.pyc':source_hashes[str(source.relative_to(ROOT))]=sha256(source)
atomic_json(out/'evidence.json',dict(schema_version=1,recorded_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='blocked',scope='Automatic MVP validation attempt; not accepted model/audio/real-time performance',full_native_matrix_executed=False,abx_pairs_released=False,human_responses_collected=False,outcomes=dict(reference='pending',numerical='failed',wav='pending',listening='pending',combined='failed'),snapshots=snapshots,source_hashes=source_hashes,availability='Original large RAW and C++ trace payloads remain on this machine, outside Git. Copied run/reference metadata alone cannot substitute for those payloads. Rejected/cancelled archived RAWs are not acceptance evidence.'))
print('Recorded',len(snapshots),'closed rate-specific reports; numerical acceptance remains failed',flush=True)
