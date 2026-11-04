"""Blinded artifacts and statistics; human responses are never synthesized."""
import secrets,shutil,struct
from pathlib import Path
import numpy as np
from scipy.stats import binomtest
from .artifacts import atomic_json,load_json
from .simulator import sha256,confined
from .persist import validate_schema
from .wave_audio import wav_header


def prepare_session(report_path,cpp,reference,output,listener_id,*,seed=None,family_id='primary'):
    report=load_json(report_path)
    if report['case_id']!='listen_high' or report['execution_config']['rate_Hz']!=384000 or any(report['outcomes'][k]!='passed' for k in ('reference','numerical','wav')):
        raise ValueError('ABX requires all automatic gates and the predeclared 384 kHz-derived pair')
    for path in (cpp,reference):
        h=wav_header(path)
        if h['format']!=3 or h['bits']!=32 or h['channels']!=1 or h['rate_Hz']!=48000 or h['data_bytes']!=167872*4:raise ValueError('Wrong listening artifact')
        if sha256(path) not in {a['sha256'] for a in report['artifacts'] if a['status']=='generated'}:raise ValueError('Unbound listening artifact')
    output.mkdir(parents=True,exist_ok=False);blind=output/'blinded';blind.mkdir();private=output/'private';private.mkdir()
    seed=secrets.randbits(128) if seed is None else seed;generator=np.random.Generator(np.random.PCG64(seed));swap=bool(generator.integers(2))
    paths=(reference,cpp) if swap else (cpp,reference)
    for name,path in zip(('A','B'),paths):shutil.copyfile(path,blind/(name+'.wav'))
    assignments=[];trials=[]
    for index in range(20):
        trial_id=f'trial_{index+1:02}';answer=('A','B')[generator.integers(2)];x='X'+str(index+1).zfill(2)
        # A private RIFF JUNK nonce prevents session-level file hashes from
        # revealing X=A/B; the audio payload is copied without re-encoding.
        payload=bytearray((blind/(answer+'.wav')).read_bytes())
        payload.extend(b'JUNK'+struct.pack('<I',32)+secrets.token_bytes(32))
        struct.pack_into('<I',payload,4,len(payload)-8)
        (blind/(x+'.wav')).write_bytes(payload)
        trials.append(dict(trial_id=trial_id,presented_file_ids=['A','B',x],response=None));assignments.append(dict(trial_id=trial_id,answer=answer))
    artifacts=[dict(path=p.name,sha256=sha256(p)) for p in sorted(blind.glob('*.wav'))]
    session=dict(schema_version=1,kind='session',session_id=output.name,physical_case_sha256=report['physical_case_sha256'],condition_id='listen_high',family_id=family_id,trial_count=20,artifacts=artifacts,listener_id=listener_id,trials=trials,completion='pending')
    key=dict(schema_version=1,kind='key',session_id=output.name,physical_case_sha256=report['physical_case_sha256'],condition_id='listen_high',family_id=family_id,trial_count=20,artifacts=artifacts,seed=str(seed),generator='NumPy PCG64',mapping={'A':'reference' if swap else 'cpp','B':'cpp' if swap else 'reference'},assignments=assignments)
    validate_schema('abx_session',session);validate_schema('abx_session',key);atomic_json(private/'key.json',key);atomic_json(blind/'session.json',session)
    return session


def evaluate_family(pairs,family_id):
    results=[]
    for session_path,key_path in pairs:
        s=load_json(session_path);k=load_json(key_path);validate_schema('abx_session',s);validate_schema('abx_session',k)
        if s['family_id']!=family_id or k['family_id']!=family_id:raise ValueError('Different predeclared confirmatory family')
        if s['session_id']!=k['session_id'] or s['physical_case_sha256']!=k['physical_case_sha256'] or s['artifacts']!=k['artifacts']:raise ValueError('Wrong ABX key')
        if s['completion']!='completed' or any(t['response'] not in ('A','B') for t in s['trials']):raise ValueError('Human responses incomplete')
        for a in s['artifacts']:
            if sha256(confined(session_path.parent,a['path']))!=a['sha256']:raise ValueError('Changed ABX audio')
        if [t['trial_id'] for t in s['trials']]!=[t['trial_id'] for t in k['assignments']]:raise ValueError('Wrong trial order')
        correct=sum(t['response']==a['answer'] for t,a in zip(s['trials'],k['assignments']))
        results.append(dict(session_id=s['session_id'],correct=correct,p_value=float(binomtest(correct,20,.5,alternative='greater').pvalue),session_sha256=sha256(session_path),key_sha256=sha256(key_path)))
    if not results:raise ValueError('Empty confirmatory family')
    reject=True
    for order,i in enumerate(sorted(range(len(results)),key=lambda i:results[i]['p_value'])):
        reject=reject and results[i]['p_value']<=.05/(len(results)-order)
        results[i]['above_chance_holm']=reject
    return dict(family_id=family_id,alpha=.05,correction='Holm',results=results,listening='failed' if any(r['above_chance_holm'] for r in results) else 'pending',reason='Above chance opens discrepancy; nonsignificance does not establish equivalence')
