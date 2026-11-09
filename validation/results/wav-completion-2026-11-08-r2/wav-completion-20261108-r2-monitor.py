"""Persist final qualification and service outcome; never start producers."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
ROOT = Path('/home/alexandre/projetos/emulador_tube_screamer')
OUT = Path('/mnt/f/ts808-validation/wav-completion-20261108-r2')
UNIT = 'ts808-wav-completion-20261108-r2.service'
while True:
    state = subprocess.run(['systemctl', '--user', 'show', UNIT, '-p', 'ActiveState', '--value'], capture_output=True, text=True, check=True).stdout.strip()
    if state not in ('active', 'activating', 'reloading'):
        break
    time.sleep(30)
service = subprocess.run(['systemctl', '--user', 'show', UNIT, '-p', 'Result', '-p', 'ExecMainStatus'], capture_output=True, text=True, check=True).stdout
status = json.loads((OUT/'status.json').read_text()) if (OUT/'status.json').exists() else {}
if status.get('status') in ('running', 'auditing') or not status:
    status.update(status='interrupted', reason='Service exited without a final result', service_result=service, mvp_accepted=False)
    (OUT/'status.json').write_text(json.dumps(status, indent=2)+'\n')
snapshot = ROOT/'validation/results/wav-completion-2026-11-08-r2'
snapshot.mkdir(exist_ok=False)
provenance = {}
for source in (OUT/'status.json', OUT/'plan.json', OUT/'qualification/qualification.json', OUT/'qualification/qualification.md', OUT/'qualification/integrity.json', OUT/'qualification/progress.json', Path(__file__)):
    if source.is_file():
        shutil.copyfile(source, snapshot/source.name)
        with source.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        provenance[source.name] = dict(original=str(source), sha256=digest)
(snapshot/'provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
message = f'Estado final do executor: {status}.\nServiço: {service}\nEvidências: {OUT}/.\nSnapshot: {snapshot.relative_to(ROOT)}/.\nQualificação automática e aceitação do MVP são distintas; escuta humana permanece sujeita ao protocolo.\nSem commit/push/desligamento.\n'
(snapshot/'README.md').write_text(message)
p = ROOT/'SESSION_HANDOFF.md'
p.write_text('## RESULTADO DA CONCLUSÃO WAV E AUDITORIA — 2026-11-08\n\n'+message+'Histórico abaixo.\n\n'+p.read_text())
