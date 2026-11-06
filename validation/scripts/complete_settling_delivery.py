"""Explicitly authorized run, evidence snapshot, commit, verified push and Windows shutdown.

No delivery occurs if execution/audit/checks/push fail. Qualification may be
rejected: the committed report records that result without accepting the MVP.
"""
import argparse
import datetime
import os
from pathlib import Path
import shutil
import subprocess
import sys

from ts808_validation.artifacts import ROOT, atomic_json, load_json
from ts808_validation.simulator import sha256


def delivery_gate(status, qualification):
    if (status['status'] != 'completed'
            or qualification['assessment_completion'] != 'completed'
            or qualification['entry_count'] != 128
            or qualification['physical_case_count'] != 91):
        raise ValueError('Complete 91-case/128-entry assessment required before delivery')


def run(command, **kwargs):
    print('Running:', ' '.join(map(str, command)), flush=True)
    return subprocess.run(list(map(str, command)), cwd=ROOT, check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--resume-from', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--authorize-commit-push-shutdown', action='store_true', required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(Path('/mnt/f/ts808-validation')):
        raise ValueError('New F: output required')
    state_path = output.parent/(output.name+'-delivery-state.json')
    state = dict(status='running', authorization='User request 2026-11-06: continue, commit, push, shutdown Windows',
                 output=str(output), pid=os.getpid())
    atomic_json(state_path, state)
    try:
        run([sys.executable, '-u', ROOT/'validation/scripts/run_settling_requalification.py',
             '--prepared', args.prepared, '--resume-from', args.resume_from, '--output', output])
        qualification = load_json(output/'qualification/qualification.json')
        delivery_gate(load_json(output/'status.json'), qualification)
        state.update(status='checking', automatic_qualification=qualification['automatic_qualification'])
        atomic_json(state_path, state)
        checks = output/'delivery-checks.log'
        with checks.open('w') as log:
            run([sys.executable, '-m', 'pytest', 'validation/tests', 'scripts/test_codex_jev.py', '-q'], stdout=log, stderr=subprocess.STDOUT)
            cmake = ROOT/'.tools/cmake-4.4.5-linux-x86_64/bin/cmake'
            ctest = ROOT/'.tools/cmake-4.4.5-linux-x86_64/bin/ctest'
            for preset in ('offline-checks', 'offline-release'):
                run([cmake, '--build', '--preset', preset], stdout=log, stderr=subprocess.STDOUT)
                run([ctest, '--preset', preset], stdout=log, stderr=subprocess.STDOUT)
        snapshot = ROOT/'validation/results/settling-requalification-2026-11-06'
        snapshot.mkdir(exist_ok=False)
        provenance = {}
        for source in [output/'status.json', output/'qualification/qualification.json',
                       output/'qualification/qualification.md', output/'qualification/integrity.json', checks]:
            shutil.copyfile(source, snapshot/source.name)
            provenance[source.name] = dict(original=str(source), sha256=sha256(source))
        atomic_json(snapshot/'provenance.json', provenance)
        from collections import Counter
        counts = {key:dict(Counter(e['outcomes'][key] for e in qualification['entries']))
                  for key in ('reference','numerical','wav')}
        atomic_json(snapshot/'outcomes.json', counts)
        message = (f"Avaliação concluída: 91 casos físicos, 128 entradas. Qualificação automática: "
                   f"{qualification['automatic_qualification']}; entradas reprovadas: {qualification['failed_entry_count']}.\n"
                   f"Resultados por categoria: {counts}.\n"
                   "Critérios e circuito preservados; reprovações não foram promovidas. MVP não aceito.\n"
                   "ABX humano anterior: 10/20, p=0,588099; listening pendente pelo protocolo.\n"
                   f"Evidências: {output}/qualification/.\n")
        (snapshot/'README.md').write_text(message)
        handoff = ROOT/'SESSION_HANDOFF.md'
        heading = ('## REQUALIFICAÇÃO E ENTREGA FINAL — 2026-11-06\n\n'+message+
                   f'Verificações Python/CTest e build checked/release aprovados; logs em {checks}.\n'
                   'Usuário autorizou commit/push e desligamento do Windows após conclusão.\n'
                   f'Estado externo de entrega: {state_path}.\n'
                   'O serviço confirma o SHA remoto antes de solicitar desligamento.\n'
                   'O estado externo registra sucesso/falha dessas ações após este commit.\n'
                   'As seções inferiores preservam histórico.\n\n')
        handoff.write_text(heading+handoff.read_text())
        report = ROOT/'docs/mvp_validation_report.md'
        report.write_text('# Resultado da requalificação — 2026-11-06\n\n'+message+'\n'+report.read_text())
        run(['git','diff','--check'])
        branch = run(['git','branch','--show-current'], capture_output=True, text=True).stdout.strip()
        if branch != 'main':
            raise ValueError('Expected main branch for the authorized delivery')
        run(['git','add','-A'])
        run(['git','commit','-m','Complete DC settling requalification and preserve validation evidence'])
        commit = run(['git','rev-parse','HEAD'], capture_output=True, text=True).stdout.strip()
        state.update(status='committed', commit=commit)
        atomic_json(state_path, state)
        run(['git','push','origin','main'])
        remote = run(['git','ls-remote','origin','refs/heads/main'], capture_output=True, text=True).stdout.split()
        if not remote or remote[0] != commit:
            raise ValueError('Remote commit differs; shutdown blocked')
        if run(['git','status','--porcelain'], capture_output=True, text=True).stdout.strip():
            raise ValueError('Worktree changed after commit; shutdown blocked')
        state.update(status='push_verified', remote_commit=remote[0], shutdown_target='Windows host',
                     shutdown_requested_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
        atomic_json(state_path, state)
        run(['/mnt/c/Windows/System32/shutdown.exe','/s','/t','60',
             '/c','TS808: requalification finished; commit and remote push verified.'])
        state.update(status='shutdown_scheduled', shutdown_delay_seconds=60)
        atomic_json(state_path, state)
    except BaseException as error:
        state.update(status='failed', reason=str(error))
        atomic_json(state_path, state)
        raise


if __name__ == '__main__':
    main()
