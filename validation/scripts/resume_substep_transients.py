"""Resume retained transient work into a new evidence directory."""
import argparse
import os
from pathlib import Path
import shutil

from ts808_validation.artifacts import ROOT, atomic_json
from ts808_validation.simulator import sha256
from ts808_validation.suite import suite


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resume-from', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not args.output.resolve().is_relative_to(Path('/mnt/f/ts808-validation')):
        raise ValueError('New evidence must remain on F:')
    args.output.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(args.resume_from/'cases.json', args.output/'cases.json')
    atomic_json(args.output/'scope.json', dict(
        scope='Remaining transient partition; DC/AC and hold remain separate',
        resume_directory=str(args.resume_from), source_summary_sha256=sha256(args.resume_from/'summary.json'),
        native_solver='norm', native_solver_overrides={'listen_high': 'alt'},
        reason='Normal solver failed at listen_high initialization; preserve failed attempt and retry independently'))
    atomic_json(args.output/'status.json', dict(status='running', pid=os.getpid()))
    try:
        code = suite(args.output/'cases.json', ROOT/'validation/toolchain-pilot-f.json',
                     ROOT/'build/offline-release/ts808_offline', [192000,384000],
                     args.output/'matrix', Path('/mnt/f/ts808-validation/substeps-20261104/pilots.json'),
                     native_solver='norm', resume_from=args.resume_from,
                     native_solver_overrides={'listen_high': 'alt'})
    except BaseException as error:
        atomic_json(args.output/'status.json', dict(status='failed', pid=os.getpid(), error=str(error)))
        raise
    atomic_json(args.output/'status.json', dict(status='completed' if code == 0 else 'failed',
                                               exit_code=code, pid=os.getpid()))
    raise SystemExit(code)
