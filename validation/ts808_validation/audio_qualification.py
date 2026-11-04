"""Native export and common-FIR qualification bound to numerical reports."""
from pathlib import Path
import uuid
import re
import numpy as np
from .artifacts import ROOT,load_json,atomic_json
from .cli import make_deck
from .simulator import prepare_request,run_request,sha256,windows_path
from .persist import consume_reference,check,validate_schema,publish_report
from .reconstruct import pchip
from .wave_audio import qualify_native,listening_pair


def qualify_audio(case_path,run_dir,nominal_dir,refined_dir,report_dir,config):
    case=load_json(case_path);report=load_json(report_dir/'report.json')
    if case['analysis_kind']!='transient':return report
    if any(report['outcomes'][k]!='passed' for k in ('reference','numerical')):return report
    rate=case['execution']['rate_Hz'];duration=case['analysis']['time']['duration_s'];frames=round(duration*rate)
    if rate not in (192000,384000):raise ValueError('Listening/audio qualification uses target rates only')
    nm,nq,n=consume_reference(nominal_dir,config);rm,rq,r=consume_reference(refined_dir,config)
    expression=next(t['native_expression'] for t in nm['selection']['traces'] if t['quantity_id']=='output')
    t=np.arange(frames+1)/rate;nv=pchip(n['axis'],n['traces'][expression],t);rv=pchip(r['axis'],r['traces'][expression],t)
    wav_settings=dict(rate_Hz=rate,encoding='signed PCM32 mono',frame_count=frames,origin_s=0,duration_s=duration,transient_stop_s=duration-.5/rate,scale_V_per_FS=8)
    settings=dict(nq['reference_settings'],wav=wav_settings)
    deck=re.sub(r'^\.tran .*$',f'.tran 0 {duration-.5/rate:.17g} 0 {nq["reference_settings"]["maxstep_s"]:.17g}',make_deck(case),flags=re.MULTILINE)
    # Preserve effective numerical producer options, including its actual solver.
    source_deck=Path(nm['source']['request']['locator']['wsl_path']).parent/'deck.cir'
    option_lines=[line for line in source_deck.read_text().splitlines() if line.startswith('.options ')]
    deck='\n'.join(line for line in deck.splitlines() if not line.startswith(('.options ','.save ','.end','* Comparison domain ends')))+'\n'
    deck+='\n'.join(option_lines)+'\nBwav wav_export 0 V={V(output)/8}\n.save V(output) V(wav_export)\n'+f'.wave audio.wav 32 {rate} V(wav_export)\n.end\n'
    destination=Path(config['workspace']['wsl_root'])/(case['case_id']+'-wav-'+str(rate)+'-'+uuid.uuid4().hex)
    request=prepare_request(ROOT/'reference/ts808',case_path,destination,request_id=destination.name,settings=settings,deck=deck)
    for filename in ('models.lib','component_map.json','device_spec.md'):
        if next(e['sha256'] for e in request['inputs'] if e['path']==filename)!=next(e['sha256'] for e in nq['inputs'] if e['path']==filename):
            raise ValueError('Audio producer model differs from qualified reference')
    request['expected_outputs'].append('audio.wav');validate_schema('reference_request',request);atomic_json(destination/'request.json',request)
    result=run_request(destination,Path(config['tools']['ltspice']['path']))
    source=dict(request_id=request['request_id'],request_sha256=sha256(destination/'request.json'),result_sha256=sha256(destination/'reference_result.json'),settings=settings,files={e['path']:dict(locator=dict(windows_path=windows_path(destination/e['path']),wsl_path=str((destination/e['path']).resolve())),size_bytes=e['size_bytes'],sha256=e['sha256']) for e in result['files']})
    atomic_json(report_dir/'native-wav-source.json',source)
    checks=qualify_native(destination/'audio.wav',nv[:-1],rv[:-1],rate)
    uc=[c for c in checks if c['id'].startswith('wav_reference_uncertainty')]
    checks.append(check('wav_reference_uncertainty',0 if all(c['status']=='passed' for c in uc) else 1,0))
    report['artifacts'].append(dict(path='native-wav-source.json',sha256=sha256(report_dir/'native-wav-source.json'),status='generated',reason='Immutable original native WAV/RAW/log producer identities'))
    if case['case_id']=='listen_high':
        run=load_json(run_dir/'run.json');data=np.memmap(run_dir/'traces.f64le',mode='r',dtype='<f8',shape=tuple(run['trace']['shape']))
        column=case['trace_columns'].index('output');audio_checks,metadata=listening_pair(data[:,column],nv,rate,report_dir/'listening')
        checks.extend(audio_checks);report['reconstruction']['wav']=metadata
        fir=[c for c in audio_checks if c['id'].startswith('wav_filter_')]
        checks.append(check('wav_filter_response',0 if all(c['status']=='passed' for c in fir) else 1,0))
        for name in ('cpp.wav','reference.wav'):
            path=report_dir/'listening'/name;report['artifacts'].append(dict(path=str(path.relative_to(report_dir)),sha256=sha256(path),status='generated',reason='Common calibration and exact T18 FIR support'))
    report['checks']=[c for c in report['checks'] if not c['id'].startswith('wav_')]+checks
    report['outcomes']['wav']='failed' if any(c['status']=='failed' for c in checks) else 'pending' if any(c['status']=='not_evaluated' for c in checks) else 'passed'
    report['outcomes']['combined']='failed' if report['outcomes']['wav']=='failed' else 'pending' if case['case_id']=='listen_high' or report['outcomes']['wav']=='pending' else 'passed'
    publish_report(report_dir,report);return report
