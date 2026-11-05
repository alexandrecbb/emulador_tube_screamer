"""Diagnose hold initialization independently; never promote matrix evidence."""
import argparse
import copy
import subprocess
import uuid
from pathlib import Path

from ts808_validation.artifacts import ROOT, atomic_json, configure_substeps, finalize_run, load_json
from ts808_validation.cli import doctor, make_deck
from ts808_validation.compare import compare
from ts808_validation.persist import ReferenceSession, import_reference
from ts808_validation.simulator import prepare_request, run_request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not args.output.resolve().is_relative_to(Path('/mnt/f/ts808-validation')):
        raise ValueError('Diagnostic payloads must remain on F:')
    toolchain = ROOT/'validation/toolchain-pilot-f.json'
    if doctor(toolchain)['status'] != 'passed':
        raise ValueError('Toolchain check failed')
    cfg = load_json(toolchain)
    executable = ROOT/'build/offline-release/ts808_offline'
    case = next(c for c in load_json(Path('/mnt/f/ts808-validation/substeps-20261104/cases.json'))['cases']
                if c['case_id'] == 'hold_center')
    args.output.mkdir(exist_ok=False)
    summary = dict(scope='Initialization diagnosis only; no matrix promotion', attempts=[])
    for solver, nodeset in [('norm', False), ('alt', True)]:
        target = args.output/(solver + ('-nodeset' if nodeset else ''))
        target.mkdir()
        base = target/'case.json'
        atomic_json(base, case)
        row = dict(solver=solver, nodeset=nodeset, requests=[], measurements=[])
        summary['attempts'].append(row)
        try:
            refs = {}
            for refined in (False, True):
                level = 'refined' if refined else 'nominal'
                deck = make_deck(case, refined).replace('.temp 25', '.temp 25\n.options solver='+solver)
                if nodeset:
                    # Independent topology-based T22 guess, never C++ solution data.
                    zeros = {'input', 'tone_rc', 'output', 'z_clip', 'z_tone'}
                    emitters = {'input_emitter', 'output_emitter', 'output_cap'}
                    guesses = []
                    for name in case['trace_columns'][1:]:
                        if name.startswith('i_'):
                            continue
                        native = {'z_clip': 'xclip:z', 'z_tone': 'xtone:z'}.get(name, name)
                        value = 0 if name in zeros else 3.85 if name in emitters else 4.5
                        guesses.append(f'V({native})={value}')
                    deck = deck.replace('.end', '.nodeset '+' '.join(guesses)+'\n.end')
                dest = Path(cfg['workspace']['wsl_root'])/('hold-diagnosis-'+solver+'-'+level+'-'+uuid.uuid4().hex)
                prepare_request(ROOT/'reference/ts808', base, dest, request_id=dest.name,
                                settings=dict(level=level, maxstep_s=1/(384000*8*(2 if refined else 1)),
                                              dc_protocol=f'Diagnostic solver={solver}; independent T22 nodeset={nodeset}'), deck=deck)
                row['requests'].append(str(dest))
                atomic_json(args.output/'diagnosis.json', summary)
                run_request(dest, Path(cfg['tools']['ltspice']['path']))
                refs[level] = target/level
                import_reference(dest, refs[level], cfg)
            session = ReferenceSession()
            for rate in (192000, 384000):
                c = configure_substeps(copy.deepcopy(case), rate)
                output = target/str(rate)
                output.mkdir()
                cp = output/'case.json'
                atomic_json(cp, c)
                subprocess.run([str(executable), '--case', str(cp), '--output', str(output/'run')], check=True)
                finalize_run(output/'run', cp, executable)
                report = compare(output/'run', refs['nominal'], refs['refined'], output/'comparison', cfg,
                                 reference_session=session)
                row['measurements'].append(dict(rate_Hz=rate, outcomes=report['outcomes']))
            row['status'] = 'completed'
        except (RuntimeError, ValueError, subprocess.SubprocessError) as exc:
            row.update(status='failed', error=str(exc))
        atomic_json(args.output/'diagnosis.json', summary)
        print(row, flush=True)


if __name__ == '__main__':
    main()
