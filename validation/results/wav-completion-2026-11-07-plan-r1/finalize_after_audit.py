"""User-authorized finalization after successful automatic audit; fail closed."""
import json
import os
from pathlib import Path
import subprocess
import time
ROOT=Path('/home/alexandre/projetos/emulador_tube_screamer')
OUT=Path('/mnt/f/ts808-validation/wav-completion-20261107-r1')
STATE=OUT/'finalization.json'
os.chdir(ROOT)
def run(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)
def record(**data):
    STATE.write_text(json.dumps(data, indent=2)+'\n')
def wait(unit):
    while True:
        value=run(['systemctl','--user','show',unit,'-p','ActiveState','--value'],capture_output=True,text=True).stdout.strip()
        if value not in ('active','activating','reloading'): return
        time.sleep(30)
def prepend(message):
    p=ROOT/'SESSION_HANDOFF.md'
    p.write_text('## FINALIZAÇÃO AUTORIZADA — 2026-11-07\n\n'+message+'\n\n'+p.read_text())
try:
    record(status='waiting_for_audit')
    wait('ts808-wav-completion-20261107-r1.service')
    wait('ts808-wav-completion-monitor-20261107-r1.service')
    status=json.loads((OUT/'status.json').read_text())
    audit=json.loads((OUT/'qualification/qualification.json').read_text())
    assert status['status']=='completed', 'Executor did not complete'
    assert audit['assessment_completion']=='completed' and audit['entry_count']==128, 'Incomplete audit'
    assert audit['automatic_qualification']=='passed' and audit['failed_entry_count']==0, 'Audit not approved'
    assert (ROOT/'validation/results/wav-completion-2026-11-07-r1/provenance.json').is_file(), 'Missing final snapshot'
    record(status='checking')
    run([str(ROOT/'.venv/bin/python'),'-m','pytest','validation/tests','-q'],env=dict(os.environ,PYTHONPATH='validation'))
    run(['git','diff','--check'])
    branch=run(['git','branch','--show-current'],capture_output=True,text=True).stdout.strip()
    assert branch=='main', 'Unexpected branch'
    assert not run(['git','diff','--cached','--name-only'],capture_output=True,text=True).stdout.strip(), 'Unexpected staged changes'
    allowed=['SESSION_HANDOFF.md','docs/designs/ts808_wav_reference_revision.md','validation/scripts/requalify_wav_references.py','validation/scripts/complete_wav_requalification.py','validation/tests/test_complete_wav_requalification.py','validation/results/wav-completion-2026-11-07-plan-r1','validation/results/wav-tight-pilot-2026-11-06-r1','validation/results/wav-tight-pilot-2026-11-07-r2','validation/results/wav-tight-pilot-2026-11-07-r3','validation/results/wav-completion-2026-11-07-r1']
    changed=run(['git','status','--porcelain','--untracked-files=all'],capture_output=True,text=True).stdout.splitlines()
    assert all(any(line[3:]==p or line[3:].startswith(p+'/') for p in allowed) for line in changed), 'Unexpected workspace changes'
    prepend('Auditoria automática das 128 entradas concluída e aprovada; testes Python aprovados.\nUsuário autorizou commit, push e desligamento após estas etapas.\nEscuta humana/ABX e aceitação do MVP continuam pendentes conforme protocolo.\nFinalizador fará push, verificará SHA remoto e só então solicitará desligamento do Windows.\nRegistro operacional: '+str(STATE)+'.')
    run(['git','add','--',*allowed])
    run(['git','diff','--cached','--check'])
    run(['git','commit','-m','Complete WAV reference requalification and 128-entry audit'])
    sha=run(['git','rev-parse','HEAD'],capture_output=True,text=True).stdout.strip()
    record(status='pushing',commit=sha)
    run(['git','push','origin','HEAD:refs/heads/main'])
    remote=run(['git','ls-remote','origin','refs/heads/main'],capture_output=True,text=True).stdout.split()[0]
    assert remote==sha, 'Remote SHA mismatch'
    assert not run(['git','status','--porcelain'],capture_output=True,text=True).stdout.strip(), 'Workspace not clean'
    record(status='push_verified_shutdown_requested',commit=sha,remote_commit=remote,mvp_accepted=False)
    run(['/mnt/c/Windows/System32/shutdown.exe','/s','/t','120','/c','TS808: auditoria aprovada, commit e push verificados. Desligamento autorizado pelo usuario.'])
except BaseException as error:
    record(status='blocked_no_shutdown',reason=str(error))
    prepend('Finalização interrompida; computador mantido ligado. Motivo: '+str(error)+'.\nConsulte '+str(STATE)+'.')
    raise
