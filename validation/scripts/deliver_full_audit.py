"""Deliver the audited revision and shut down the host, as authorized 2026-11-09."""
import os
from pathlib import Path
import subprocess
import time
from ts808_validation.artifacts import ROOT, atomic_json, load_json
from ts808_validation.compare import validator_hash

OUT=Path('/mnt/f/ts808-validation/full-audit-20261109-r1')
SNAPSHOT=ROOT/'validation/results/full-audit-2026-11-09-r1'
PATHS=['SESSION_HANDOFF.md','docs/designs/ts808_wav_reference_revision.md',
       'validation/ts808_validation/compare.py','validation/ts808_validation/reconstruct.py',
       'validation/ts808_validation/reference.py','validation/tests/test_bounded_pchip.py',
       'validation/tests/test_remaining_wav.py',
       *['validation/scripts/'+n+'.py' for n in ('repair_remaining_wav','resume_memory_requalification','refresh_full_audit','finish_full_audit_refresh','deliver_full_audit')],
       *['validation/results/'+n for n in ('memory-fix-2026-11-09','memory-requalification-2026-11-09-r1','wav-repair-2026-11-09-r1','wav-repair-2026-11-09-r2','wav-repair-2026-11-09-r3','full-audit-2026-11-09-r1')]]

def run(args,**kwargs):return subprocess.run(args,cwd=ROOT,check=True,**kwargs)

def wait_service(name):
    while True:
        state=run(['systemctl','--user','show',name,'--property=ActiveState','--value'],capture_output=True,text=True).stdout.strip()
        if state not in ('active','activating'):return
        time.sleep(30)

def main():
    # Durable lock prevents duplicate commits, pushes and shutdown scheduling.
    descriptor=os.open(ROOT/'.git/full-audit-delivery-20261109-r1.lock',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    os.close(descriptor)
    status=dict(status='waiting_for_audit',shutdown_authorized=True,authorization='User request after audit, 2026-11-09',mvp_accepted=False)
    atomic_json(OUT/'delivery-status.json',status)
    try:
        wait_service('ts808-full-audit-finalize-20261109-r1.service')
        result=load_json(OUT/'qualification/qualification.json')
        finalization=load_json(SNAPSHOT/'finalization.json')
        if (result['assessment_completion']!='completed' or result['automatic_qualification']!='passed'
            or result['entry_count']!=128 or result['failed_entry_count']!=0
            or result['validator_sha256']!=validator_hash() or finalization['status']!='completed'
            or not finalization['pilots_verified']):
            raise ValueError('Complete passing audit and verified pilots required before delivery/shutdown')
        status['status']='checking';atomic_json(OUT/'delivery-status.json',status)
        with (OUT/'delivery-tests.log').open('w') as log:
            run([str(ROOT/'.venv/bin/python'),'-m','pytest','validation/tests','-q'],stdout=log,stderr=subprocess.STDOUT)
        run(['git','diff','--check'])
        if run(['git','branch','--show-current'],capture_output=True,text=True).stdout.strip()!='main':raise ValueError('Unexpected branch')
        if run(['git','diff','--cached','--name-only'],capture_output=True,text=True).stdout.strip():raise ValueError('Unrelated staged changes')
        p=ROOT/'SESSION_HANDOFF.md'
        p.write_text('## ENTREGA APROVADA E DESLIGAMENTO AUTORIZADO — 2026-11-09\n\nAuditoria automática128/128 aprovada, zero reprovações; pilotos verificados\ne testes Python aprovados. Usuário voltou a autorizar desligar o Windows\napós commit e push. Executor validation/scripts/deliver_full_audit.py fará\ncommit dos arquivos listados, push main e confirmação do SHA remoto.\nSomente depois agenda desligamento sem /f. Em qualquer falha, não desliga.\nResultado operacional em '+str(OUT/'delivery-status.json')+'.\nQualificação automática não equivale a ABX humano nem aceitação MVP.\nHistórico abaixo.\n\n'+p.read_text())
        run(['git','add','--',*PATHS])
        run(['git','diff','--cached','--check'])
        run(['git','commit','-m','Fix bounded-memory validation and complete 128-entry TS808 audit'])
        head=run(['git','rev-parse','HEAD'],capture_output=True,text=True).stdout.strip()
        status.update(status='pushing',commit=head);atomic_json(OUT/'delivery-status.json',status)
        run(['git','push','origin','HEAD:refs/heads/main'])
        remote=run(['git','ls-remote','--exit-code','origin','refs/heads/main'],capture_output=True,text=True).stdout.split()[0]
        if remote!=head:raise ValueError('Remote commit does not match local delivery')
        if run(['git','status','--porcelain'],capture_output=True,text=True).stdout.strip():raise ValueError('Working tree changed; retain host for inspection')
        status.update(status='push_verified_shutdown_pending',remote_commit=remote)
        atomic_json(OUT/'delivery-status.json',status)
        run(['systemd-run','--user','--unit=ts808-host-shutdown-20261109-r1','--on-active=60s',
             '--setenv=WSL_INTEROP='+os.environ['WSL_INTEROP'],
             '/mnt/c/Windows/System32/shutdown.exe','/s','/t','0'])
        status.update(status='shutdown_scheduled',delay_s=60,force=False)
    except BaseException as error:
        status.update(status='interrupted',reason=str(error));raise
    finally:atomic_json(OUT/'delivery-status.json',status)

if __name__=='__main__':main()
