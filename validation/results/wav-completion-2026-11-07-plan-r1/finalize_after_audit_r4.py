"""User-authorized finalization after successful automatic audit; fail closed."""
import json
import os
from pathlib import Path
import subprocess
import time
ROOT=Path('/home/alexandre/projetos/emulador_tube_screamer')
OUT=Path('/mnt/f/ts808-validation/wav-completion-20261108-r4')
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
    while not OUT.exists():
        time.sleep(2)
    record(status='waiting_for_audit')
    wait('ts808-wav-completion-20261108-r4.service')
    wait('ts808-wav-completion-monitor-20261108-r4.service')
    status=json.loads((OUT/'status.json').read_text())
    assert status['status']=='completed', 'Executor did not complete: '+str(status)
    audit=json.loads((OUT/'qualification/qualification.json').read_text())
    assert audit['assessment_completion']=='completed' and audit['entry_count']==128, 'Incomplete audit'
    approved = audit['automatic_qualification']=='passed' and audit['failed_entry_count']==0
    assert (ROOT/'validation/results/wav-completion-2026-11-08-r4/provenance.json').is_file(), 'Missing final snapshot'
    record(status='checking')
    run([str(ROOT/'.venv/bin/python'),'-m','pytest','validation/tests','-q'],env=dict(os.environ,PYTHONPATH='validation'))
    run(['git','diff','--check'])
    branch=run(['git','branch','--show-current'],capture_output=True,text=True).stdout.strip()
    assert branch=='main', 'Unexpected branch'
    assert not run(['git','diff','--cached','--name-only'],capture_output=True,text=True).stdout.strip(), 'Unexpected staged changes'
    allowed=['SESSION_HANDOFF.md','docs/designs/ts808_wav_reference_revision.md','validation/scripts/requalify_wav_references.py','validation/scripts/complete_wav_requalification.py','validation/tests/test_complete_wav_requalification.py','validation/results/wav-completion-2026-11-07-plan-r1','validation/results/wav-tight-pilot-2026-11-06-r1','validation/results/wav-tight-pilot-2026-11-07-r2','validation/results/wav-tight-pilot-2026-11-07-r3','validation/results/wav-completion-2026-11-07-r1','validation/results/wav-completion-2026-11-08-r2','validation/results/wav-completion-2026-11-08-r3','validation/results/wav-completion-2026-11-08-r4','validation/ts808_validation/simulator.py','validation/tests/test_native_timeout.py']
    changed=run(['git','status','--porcelain','--untracked-files=all'],capture_output=True,text=True).stdout.splitlines()
    assert all(any(line[3:]==p or line[3:].startswith(p+'/') for p in allowed) for line in changed), 'Unexpected workspace changes'
    prepend(f"Auditoria automática concluída: {audit['entry_count']} entradas, resultado {audit['automatic_qualification']}, {audit['failed_entry_count']} entradas reprovadas. Testes Python aprovados.\nUsuário pediu commit e push após auditoria mesmo com reprovações registradas.\nEscuta humana/ABX e aceitação do MVP permanecem pendentes.\nDesligamento só se qualificação automática aprovada e push confirmado.\nRegistro operacional: "+str(STATE)+'.')
    run(['git','add','--',*allowed])
    run(['git','diff','--cached','--check'])
    run(['git','commit','-m','Record WAV requalification results and complete 128-entry audit'])
    sha=run(['git','rev-parse','HEAD'],capture_output=True,text=True).stdout.strip()
    record(status='pushing',commit=sha)
    run(['git','push','origin','HEAD:refs/heads/main'])
    remote=run(['git','ls-remote','origin','refs/heads/main'],capture_output=True,text=True).stdout.split()[0]
    assert remote==sha, 'Remote SHA mismatch'
    assert not run(['git','status','--porcelain'],capture_output=True,text=True).stdout.strip(), 'Workspace not clean'
    if not approved:
        record(status='push_verified_no_shutdown',commit=sha,remote_commit=remote,automatic_qualification=audit['automatic_qualification'],failed_entry_count=audit['failed_entry_count'],mvp_accepted=False)
        raise SystemExit(0)
    record(status='push_verified_shutdown_requested',commit=sha,remote_commit=remote,mvp_accepted=False)
    run(['/mnt/c/Windows/System32/shutdown.exe','/s','/t','120','/c','TS808: auditoria aprovada, commit e push verificados. Desligamento autorizado pelo usuario.'])
except Exception as error:
    record(status='blocked_no_shutdown',reason=str(error))
    prepend('Finalização interrompida; computador mantido ligado. Motivo: '+str(error)+'.\nConsulte '+str(STATE)+'.')
    raise
