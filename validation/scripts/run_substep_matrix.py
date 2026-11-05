"""Run the complete matrix only after all approved substep pilots qualify."""
from pathlib import Path
import argparse
import time

from ts808_validation.artifacts import ROOT,load_json
from ts808_validation.suite import suite


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wait-for-pilot-pid',type=int)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--native-solver',choices=('norm','alt'),default='alt')
    args=parser.parse_args()
    if args.wait_for_pilot_pid:
        cmdline=Path(f'/proc/{args.wait_for_pilot_pid}/cmdline')
        while cmdline.exists():
            try:
                command=cmdline.read_bytes()
                if not any(name in command for name in (b'qualify_substep_pilots.py',b'refresh_substep_pilots.py')):break
            except FileNotFoundError:break
            time.sleep(1)
    root=Path('/mnt/f/ts808-validation/substeps-20261104')
    if not load_json(root/'pilots.json').get('full_matrix_authorized'):
        raise ValueError('Substep pilot reference/numerical/WAV gates have not passed')
    return suite(root/'cases.json',ROOT/'validation/toolchain-pilot-f.json',
                 ROOT/'build/offline-release/ts808_offline',[192000,384000],
                 args.output or root/'matrix-alt',root/'pilots.json',native_solver=args.native_solver)


if __name__=='__main__':
    raise SystemExit(main())
