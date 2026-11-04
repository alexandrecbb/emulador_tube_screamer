"""Implemented process boundaries; unavailable comparison stages are not advertised."""
import argparse
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
from jsonschema import Draft202012Validator, ValidationError
from .artifacts import load_json, validate_case
from .simulator import sha256, windows_path, prepare_request, run_request

ROOT = Path(__file__).resolve().parents[2]


def doctor(toolchain: Path) -> dict:
    config = load_json(toolchain)
    Draft202012Validator(load_json(ROOT / "schemas/toolchain.schema.json")).validate(config)
    errors = []
    if config['execution_profile'] != 'wsl2-windows-native-v1':
        errors.append('Unexpected execution profile')
    if platform.python_version() != '3.14.4':
        errors.append('Python 3.14.4 required')
    for name, expected in config['linux']['python_packages'].items():
        try:
            if importlib.metadata.version(name) != expected:
                errors.append(f'{name}: expected {expected}')
        except importlib.metadata.PackageNotFoundError:
            errors.append(f'{name}: missing')
    for name, tool in config['tools'].items():
        path = Path(tool['path'])
        if not path.is_file() or sha256(path) != tool['sha256']:
            errors.append(f'{name}: missing or changed executable')
    for name in ('gcc', 'cmake', 'ninja'):
        tool = config['tools'][name]
        value = subprocess.check_output([tool['path'], '--version'], text=True)
        if tool['version'] not in value.splitlines()[0]:
            errors.append(f'{name}: version mismatch')
    if 'microsoft' not in platform.release().lower():
        errors.append('WSL kernel required')
    paired = Path(config['workspace']['wsl_root'])
    if windows_path(paired).lower() != config['workspace']['windows_root'].lower():
        errors.append('Shared path mismatch')
    executable = config['tools']['ltspice']['path']
    # A -Command probe is setup only; numerical runs use the staged -File helper.
    escaped = windows_path(Path(executable)).replace("'", "''")
    value = subprocess.check_output(['powershell.exe', '-NoProfile', '-NonInteractive',
                                     '-Command', f"(Get-Item -LiteralPath '{escaped}').VersionInfo.ProductVersion"], text=True).strip()
    if value != '26.1.1.0':
        errors.append('LTspice 26.1.1 required')
    return dict(schema_version=1, status='failed' if errors else 'passed', errors=errors,
                qualification='environment_only', toolchain_sha256=sha256(toolchain))


def make_deck(case: dict, refinement=False) -> str:
    base = (ROOT / 'reference/ts808/ts808.cir').read_text().splitlines()
    controls = case['circuit']['controls']
    mapping = load_json(ROOT / 'reference/ts808/component_map.json')
    segments = {s['current_id'][2:]: (definition['total_Ohm'] *
                 (controls[name] if s['factor'] == 'fraction' else 1-controls[name]))
                for name, definition in mapping['controls'].items() for s in definition['segments']}
    lines = []
    for line in base:
        if line.startswith(('.op', '.save', '.end', '.nodeset')) and not line.startswith('.options'):
            continue
        words = line.split()
        if words and words[0].startswith('R_') and words[0][2:] in segments:
            name = words[0][2:]; r = segments[name]
            words[0] = ('V_' if r == 0 else 'R_')+name
            words[-1] = format(r, '.17g')
            line = ' '.join(words)
        if refinement and line.startswith('.options '):
            line = line.replace('reltol=1e-6', 'reltol=1e-7').replace('abstol=1e-12', 'abstol=1e-13').replace('vntol=1e-9', 'vntol=1e-10').replace('chgtol=1e-16', 'chgtol=1e-17')
        lines.append(line)
    kind = case['analysis_kind']
    if kind == 'dc':
        lines.append('.op')
    elif kind == 'ac':
        lines.append('.ac dec 100 20 20000')
    else:
        source = case['stimulus']
        def ramp(u, duration):
            return f'if(({u})<=0,0,if(({u})>={duration:.17g},1,(1-cos(pi*({u})/{duration:.17g}))/2))'
        source_type = source['type']
        if source_type == 'dc':
            expression = '0'
        elif source_type in ('tone', 'overload'):
            u = f'(time-{source["onset_s"]:.17g})'
            envelope = ramp(u, source['rise_s'])
            if source_type == 'overload':
                envelope += '*'+ramp(f'({source["duration_s"]:.17g}-{u})', source['fall_s'])
            expression = f'{source["peak_V"]:.17g}*({envelope})*sin(2*pi*{source["frequency_Hz"]:.17g}*time)'
        elif source_type == 'listening':
            notes = []
            for onset, frequency in zip(source['onsets_s'], source['frequencies_Hz']):
                u = f'(time-{onset:.17g})'
                harmonics = '+'.join(f'{a:.17g}*sin(2*pi*{frequency*h:.17g}*{u})'
                                     for h, a in enumerate(source['harmonic_coefficients'], 1))
                release = ramp(f'({source["note_duration_s"]:.17g}-{u})', source['fall_s'])
                notes.append(f'if(({u})>=0,if(({u})<={source["note_duration_s"]:.17g},'
                    f'{source["coefficient_V"]:.17g}*exp(-{u}/{source["decay_s"]:.17g})*'
                    f'({ramp(u,source["rise_s"])})*'
                    f'({release})*'
                    f'({harmonics}),0),0)')
            expression = '+'.join(notes)
        else:
            raise ValueError('Unknown native stimulus')
        lines = [f'Bgenerator generator 0 V={{{expression}}}' if line.startswith('Vgenerator ') else line for line in lines]
        duration = case['analysis']['time']['duration_s']
        maxstep = 1/(384000*8*(2 if refinement else 1))
        lines.append(f'* Comparison domain ends at {duration:.17g}; one native maxstep guard ensures endpoint coverage')
        lines.append(f'.tran 0 {duration+maxstep:.17g} 0 {maxstep:.17g}')
    traces = []
    for name, trace in mapping['trace_map'].items():
        expression = trace['expression']
        if name.startswith('i_') and segments[name[2:]] == 0:
            expression = trace['zero_resistance_expression']
        traces.append(expression)
    return '\n'.join(lines+['.save '+' '.join(traces), '.end', ''])


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest='command', required=True)
    env = commands.add_parser('doctor'); env.add_argument('--toolchain', type=Path, required=True)
    prep = commands.add_parser('prepare-reference')
    prep.add_argument('--case', type=Path, required=True); prep.add_argument('--toolchain', type=Path, required=True)
    prep.add_argument('--output', type=Path, required=True); prep.add_argument('--refined', action='store_true')
    run = commands.add_parser('run-reference')
    run.add_argument('--request', type=Path, required=True); run.add_argument('--toolchain', type=Path, required=True)
    run.add_argument('--output', type=Path, required=True)
    imp = commands.add_parser('import-reference')
    imp.add_argument('--case', type=Path, required=True); imp.add_argument('--raw', type=Path, required=True)
    imp.add_argument('--log', type=Path, required=True); imp.add_argument('--output', type=Path, required=True)
    imp.add_argument('--toolchain', type=Path, default=ROOT/'validation/toolchain.json')
    cmp = commands.add_parser('compare')
    for name in ('case','run','reference','output'):
        cmp.add_argument('--'+name, type=Path, required=True)
    cmp.add_argument('--refined-reference',type=Path)
    cmp.add_argument('--toolchain', type=Path, default=ROOT/'validation/toolchain.json')
    su = commands.add_parser('suite')
    su.add_argument('--cases',type=Path,required=True);su.add_argument('--toolchain',type=Path,required=True)
    su.add_argument('--model-executable',type=Path,required=True);su.add_argument('--rates',type=int,nargs='+',required=True)
    su.add_argument('--output',type=Path,required=True);su.add_argument('--pilot-summary',type=Path,required=True)
    args = parser.parse_args(argv)
    try:
        if args.command=='compare' and args.refined_reference is None:
            print('Explicit refined reference is required',file=sys.stderr);return 31
        report = doctor(args.toolchain)
        if report['status'] != 'passed':
            print(json.dumps(report)); return 10
        if args.command == 'doctor':
            print(json.dumps(report, indent=2)); return 0
        config = load_json(args.toolchain)
        if args.command == 'suite':
            from .suite import suite
            return suite(args.cases,args.toolchain,args.model_executable.resolve(),args.rates,args.output,args.pilot_summary)
        elif args.command == 'import-reference':
            from .persist import import_reference
            if args.raw.name!='deck.raw' or args.log.name!='deck.log' or args.raw.parent.resolve()!=args.log.parent.resolve():
                raise ValueError('Expected original paired deck RAW/log')
            if sha256(args.case)!=sha256(args.raw.parent/'case.json'): raise ValueError('Different source case bytes')
            import_reference(args.raw.parent,args.output,config)
        elif args.command == 'compare':
            from .compare import compare
            if sha256(args.case)!=sha256(args.run.parent/'case.json'): raise ValueError('Different run case bytes')
            report=compare(args.run,args.reference,args.refined_reference,args.output,config)
            return 0 if report['outcomes']['numerical']=='passed' else 31 if report['outcomes']['reference']!='passed' else 50 if report['outcomes']['numerical']=='pending' else 40
        elif args.command == 'prepare-reference':
            case = load_json(args.case); validate_case(case)
            if not args.output.resolve().is_relative_to(Path(config['workspace']['wsl_root']).resolve()):
                raise ValueError('Reference requests must use the declared shared Windows root')
            prepare_request(ROOT / 'reference/ts808', args.case, args.output,
                            request_id=args.output.name, settings=dict(level='refined' if args.refined else 'nominal',
                            maxstep_s=1/(384000*8*(2 if args.refined else 1)),
                            dc_protocol='gminsteps=0 srcsteps=0; native log must be audited'),
                            deck=make_deck(case, args.refined))
        elif args.command == 'run-reference':
            if args.output.exists():
                raise ValueError('Output already exists')
            result = run_request(args.request, Path(config['tools']['ltspice']['path']))
            args.output.mkdir(parents=True, exist_ok=False)
            # Original native files stay in the shared request; this is an index only.
            (args.output / 'result.json').write_text(json.dumps(dict(
                request_directory=str(args.request.resolve()), request_sha256=sha256(args.request/'request.json'),
                result_sha256=sha256(args.request/'reference_result.json'), result=result,
                reference_qualification='not_evaluated'), indent=2)+'\n')
        return 0
    except (ValueError, KeyError, ValidationError) as error:
        print(str(error), file=sys.stderr); return 30 if args.command=='import-reference' else 31 if args.command=='compare' else 10
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr); return 30 if args.command == 'run-reference' else 50
