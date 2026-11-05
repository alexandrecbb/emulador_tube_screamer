"""Audit complete automatic qualification without overwriting original partitions."""
import argparse
import time
from pathlib import Path
from ts808_validation.artifacts import atomic_json, load_json
from ts808_validation.qualification import consolidate


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('/mnt/f/ts808-validation/substeps-20261104'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--transient-summary', type=Path)
    parser.add_argument('--record-rejections', action='store_true',
                        help='Audit full coverage while recording failed gates; never promotes them.')
    parser.add_argument('--wait-for-partition', type=Path,
                        help='Wait for this producer status.json to leave running state.')
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Qualification destination must be new')
    try:
        if args.wait_for_partition:
            while True:
                status = load_json(args.wait_for_partition)
                if status['status'] != 'running':
                    break
                process = Path('/proc')/str(status['pid'])
                if not process.exists() or (process/'stat').read_text().split()[2] == 'Z':
                    raise RuntimeError('Partition process disappeared without finalized status')
                time.sleep(15)
            if status['status'] != 'completed' or status.get('exit_code') != 0:
                raise RuntimeError('Partition has not passed; automatic qualification remains pending')
        result = consolidate(args.root, args.output, args.transient_summary,
                             require_passed=not args.record_rejections)
        if result['automatic_qualification'] != 'passed':
            raise SystemExit(40 if result['automatic_qualification'] == 'failed' else 50)
    except Exception as error:
        args.output.mkdir(parents=True, exist_ok=True)
        atomic_json(args.output/'failure.json', dict(automatic_qualification='not_qualified',
                    listening='pending_human_abx', mvp_acceptance='pending', reason=str(error)))
        raise
