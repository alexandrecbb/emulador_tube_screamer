"""Record the pilot outcome and growth without starting additional producers."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

ROOT=Path('/home/alexandre/projetos/emulador_tube_screamer')
OUT=Path('/mnt/f/ts808-validation/wav-tight-pilot-20261106-r1')
UNIT='ts808-wav-tight-pilot-20261106-r1.service'
while True:
    state=subprocess.run(['systemctl','--user','show',UNIT,'-p','ActiveState','--value'],capture_output=True,text=True,check=True).stdout.strip()
    if state not in ('active','activating','reloading'):break
    time.sleep(30)
status=json.loads((OUT/'status.json').read_text())
snapshot=ROOT/'validation/results/wav-tight-pilot-2026-11-06-r1'
snapshot.mkdir(exist_ok=False)
provenance={}
for source in (OUT/'status.json',OUT/'plan.json',OUT/'matrix/summary.json',Path(__file__)):
    if source.is_file():
        shutil.copyfile(source,snapshot/source.name)
        with source.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
        provenance[source.name]=dict(original=str(source),sha256=digest)
(snapshot/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
summary=json.loads((OUT/'matrix/summary.json').read_text()) if (OUT/'matrix/summary.json').exists() else {}
rows=[]
for entry in summary.get('entries',[]):
    if entry['report']:
        source=OUT/'matrix'/entry['report']['path']
        report=json.loads(source.read_text())
        rows.append(dict(case_id=entry['case_id'],rate_Hz=entry['rate_Hz'],outcomes=report['outcomes'],
                         metrics=[c for c in report['checks'] if c['id'] in ('wav_native_rms','wav_native_peak','wav_reference_uncertainty_rms','wav_reference_uncertainty_peak')]))
        target=snapshot/f"report-{entry['rate_Hz']}.json"
        shutil.copyfile(source,target)
        with source.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
        provenance[target.name]=dict(original=str(source),sha256=digest)
(snapshot/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
(snapshot/'metrics.json').write_text(json.dumps(rows,indent=2)+'\n')
message=(f"Piloto de tolerâncias nativas100x: {status}.\n"
         f"Métricas: {snapshot.relative_to(ROOT)}/metrics.json.\n"
         'Correção dos11casos e auditoria128entradas ainda pendentes; MVPnãoaceito.\n'
         'Gate da execução completa bloqueado por espaço; não iniciar novos produtores\n'
         'sem reavaliar orçamento real do piloto e espaço em F:.\n'
         f'Evidências originais: {OUT}/.\n')
(snapshot/'README.md').write_text(message)
p=ROOT/'SESSION_HANDOFF.md'
p.write_text('## RESULTADO DO PILOTO WAV100x — 2026-11-06\n\n'+message+'Histórico abaixo.\n\n'+p.read_text())
