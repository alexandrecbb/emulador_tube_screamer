"""Finalize the resumed assessment without publishing or shutting down the host."""
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path('/home/alexandre/projetos/emulador_tube_screamer')
OUT = Path('/mnt/f/ts808-validation/settling-requalification-20261106-r4')
STATE = OUT.parent / (OUT.name + '-finalization-state.json')
SNAPSHOT = ROOT / 'validation/results/settling-requalification-2026-11-06-r4'
UNIT = 'ts808-settling-resume-20261106-r4.service'

def read(path):
    return json.loads(path.read_text())

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def save_state(status, **fields):
    data = dict(status=status, output=str(OUT), updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), **fields)
    tmp = STATE.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2) + '\n')
    tmp.replace(STATE)

def run(command, log):
    print('Running:', ' '.join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), cwd=ROOT, check=True, stdout=log, stderr=subprocess.STDOUT)

def main():
    save_state('waiting_for_assessment', pid=os.getpid())
    while True:
        result = subprocess.run(['systemctl', '--user', 'show', UNIT, '-p', 'ActiveState', '--value'], capture_output=True, text=True, check=True)
        if result.stdout.strip() not in ('active', 'activating', 'reloading'):
            break
        time.sleep(30)
    status = read(OUT / 'status.json')
    q = read(OUT / 'qualification/qualification.json')
    if (status['status'] != 'completed' or q['assessment_completion'] != 'completed'
            or q['entry_count'] != 128 or q['physical_case_count'] != 91):
        raise ValueError('Complete assessment of 91 cases/128 entries required')
    save_state('checking', automatic_qualification=q['automatic_qualification'])
    checks = OUT / 'finalization-checks.log'
    with checks.open('x') as log:
        run([sys.executable, '-m', 'pytest', 'validation/tests', 'scripts/test_codex_jev.py', '-q'], log)
        for preset in ('offline-checks', 'offline-release'):
            run([ROOT / '.tools/cmake-4.4.5-linux-x86_64/bin/cmake', '--build', '--preset', preset], log)
            run([ROOT / '.tools/cmake-4.4.5-linux-x86_64/bin/ctest', '--preset', preset], log)
    SNAPSHOT.mkdir(exist_ok=False)
    provenance = {}
    for source in (OUT/'status.json', OUT/'qualification/qualification.json', OUT/'qualification/qualification.md', OUT/'qualification/integrity.json', checks, Path(__file__)):
        shutil.copyfile(source, SNAPSHOT/source.name)
        provenance[source.name] = dict(original=str(source), sha256=digest(source))
    (SNAPSHOT/'provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    counts = {key:dict(collections.Counter(e['outcomes'][key] for e in q['entries'])) for key in ('reference', 'numerical', 'wav')}
    (SNAPSHOT/'outcomes.json').write_text(json.dumps(counts, indent=2)+'\n')
    message = (f"Avaliação concluída: 91 casos físicos, 128 entradas. Qualificação automática: {q['automatic_qualification']}; entradas reprovadas: {q['failed_entry_count']}.\n"
               f"Resultados por categoria: {counts}.\n"
               "Critérios e circuito preservados. MVP não aceito.\n"
               "ABX humano anterior: 10/20, p=0,588099; listening permanece pendente pelo protocolo.\n"
               f"Evidências: {OUT}/qualification/.\n")
    (SNAPSHOT/'README.md').write_text(message)
    handoff = ROOT/'SESSION_HANDOFF.md'
    heading = ('## REQUALIFICAÇÃO R4 CONCLUÍDA — 2026-11-06\n\n'+message+
               f'Python/build/CTest checked e release aprovados; logs: {checks}.\n'
               f'Snapshot com hashes/proveniência: {SNAPSHOT.relative_to(ROOT)}/.\n'
               f'Estado externo da finalização: {STATE}.\n'
               'Nenhum commit/push/desligamento executado nesta retomada.\n'
               'As seções inferiores preservam histórico.\n\n')
    handoff.write_text(heading+handoff.read_text())
    report = ROOT/'docs/mvp_validation_report.md'
    report.write_text('# Resultado da requalificação R4 — 2026-11-06\n\n'+message+'\nAs seções seguintes preservam o histórico.\n\n'+report.read_text())
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    save_state('completed', automatic_qualification=q['automatic_qualification'], snapshot=str(SNAPSHOT), mvp_accepted=False)

if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        save_state('failed', reason=str(error))
        raise
