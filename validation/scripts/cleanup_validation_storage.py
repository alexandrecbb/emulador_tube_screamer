"""Remove only failed unconsumed RAWs and hard-link verified duplicate traces.

All original metadata is retained. A plan and per-operation journal precede
mutations. Completed native originals are never replaced by this script.
"""
import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import shutil
import uuid

from ts808_validation.artifacts import atomic_json, load_json
from ts808_validation.simulator import sha256

ROOTS = (Path('/mnt/f/ts808-reference'), Path('/mnt/f/ts808-validation'))


def identity(path):
    s = path.stat()
    return s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns


def replace_duplicate(source, target, digest):
    """Refuse changed data; replace a duplicate name atomically, retaining bytes."""
    if source.is_symlink() or target.is_symlink():
        raise ValueError('Refusing symlink payload')
    before = identity(source), identity(target)
    if sha256(source) != digest or sha256(target) != digest:
        raise ValueError('Duplicate hash mismatch')
    if before != (identity(source), identity(target)):
        raise ValueError('Payload changed while hashing')
    if before[0][:2] == before[1][:2]:
        return False
    temporary = target.with_name(target.name+'.dedup-'+uuid.uuid4().hex)
    try:
        os.link(source, temporary)
        if before != (identity(source), identity(target)):
            raise ValueError('Payload changed before replacement')
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()
    if identity(source)[:2] != identity(target)[:2]:
        raise ValueError('Hard-link replacement failed')
    return True


def remove_failed_payload(path, metadata, protected, expected_digest=None):
    """Delete only a failed RAW with no imported/audited consumer, keeping metadata."""
    if str(path.resolve()) in protected or path.is_symlink() or path.name != 'deck.raw':
        raise ValueError('Protected or unexpected failed payload')
    state = load_json(metadata)
    failed = state.get('completion') in ('failed','timed_out','cancelled','canceled')
    archived = state.get('qualification') == 'rejected_or_cancelled' and state.get('archive_wsl_path') == str(path)
    if not (failed or archived):
        raise ValueError('Producer is not explicitly failed/rejected')
    before = identity(path)
    digest = sha256(path)
    if expected_digest is not None and digest != expected_digest:
        raise ValueError('Failed payload hash mismatch')
    if before != identity(path):
        raise ValueError('Failed payload changed while hashing')
    record = dict(path=str(path),size_bytes=before[2],sha256=digest,
                  metadata_path=str(metadata),metadata_sha256=sha256(metadata),
                  reason='Explicitly failed/rejected attempt; no imported or audited consumer',
                  disposition='deletion_authorized_by_user')
    marker = path.parent/'cleanup-removed-payload.json'
    if marker.exists():
        raise ValueError('Existing cleanup marker; preserve prior history')
    atomic_json(marker,record)
    path.unlink()
    return record


def plan(inventory):
    rows = load_json(inventory)
    protected = set()
    claims = defaultdict(set)
    failures = []
    metadata = [Path(r['path']) for r in rows if Path(r['path']).name in
                ('reference.json','reference_result.json','run.json','archive.json','integrity.json')]
    for p in metadata:
        a = load_json(p)
        if p.name == 'reference.json':
            raw = a.get('source',{}).get('raw',{}).get('locator',{}).get('wsl_path')
            if raw:
                protected.add(str(Path(raw).resolve()))
        elif p.name == 'integrity.json' and isinstance(a,dict):
            protected.update(str(Path(k).resolve()) for k in a if k.startswith('/'))
        elif p.name == 'run.json':
            trace = a.get('trace',{})
            if trace.get('sha256') and trace.get('integrity') == 'verified':
                path = p.parent/trace['filename']
                claims[str(path)].add(trace['sha256'])
        elif p.name == 'reference_result.json' and a.get('completion') in ('failed','timed_out','cancelled','canceled'):
            raw = p.parent/'deck.raw'
            if raw.exists():
                entry = next((e for e in a.get('files',[]) if e['path']=='deck.raw'),{})
                failures.append(dict(path=str(raw),metadata=str(p),expected_digest=entry.get('sha256')))
        elif p.name == 'archive.json' and a.get('qualification') == 'rejected_or_cancelled':
            raw = Path(a['archive_wsl_path'])
            if raw.exists():
                failures.append(dict(path=str(raw),metadata=str(p),expected_digest=a['sha256']))
    failures = [dict(e,size_bytes=Path(e['path']).stat().st_size) for e in failures
                if str(Path(e['path']).resolve()) not in protected]
    # Experimental diagnostics may have no finalized run.json. They are kept,
    # but a byte-identical trace can still share storage after a real hash.
    for row in rows:
        p=Path(row['path'])
        if p.suffix=='.f64le' and row['size']>=1024**2 and str(p) not in claims and p.is_relative_to(ROOTS[1]):
            claims[str(p)].add(sha256(p))
    groups = defaultdict(list)
    for name, digests in claims.items():
        p = Path(name)
        if len(digests) != 1:
            raise ValueError('Conflicting trace hash claims: '+name)
        if p.exists() and not p.is_symlink() and p.stat().st_size >= 1024**2:
            groups[(p.stat().st_size,next(iter(digests)))].append(p)
    duplicate_groups = []
    all_aliases = defaultdict(list)
    for row in rows:
        all_aliases[(row['device'],row['inode'])].append(Path(row['path']))
    for (size,digest), paths in groups.items():
        inodes = defaultdict(list)
        for p in paths:
            inodes[identity(p)[:2]].append(p)
        if len(inodes)<2:
            continue
        # Retain an audited inode as anchor when possible, otherwise the inode
        # with the most existing names. All aliases must be in these two roots.
        ordered = sorted(inodes, key=lambda k:(not any(str(p.resolve()) in protected for p in inodes[k]),-len(inodes[k])))
        source = inodes[ordered[0]][0]
        targets = []
        reclaim = 0
        for inode in ordered[1:]:
            aliases = all_aliases[inode]
            if len(aliases) != inodes[inode][0].stat().st_nlink:
                continue
            if any(p.suffix != '.f64le' or not p.is_relative_to(ROOTS[1]) for p in aliases):
                continue
            targets.extend(str(p) for p in aliases)
            reclaim += size
        if targets:
            duplicate_groups.append(dict(source=str(source),targets=targets,sha256=digest,
                                         estimated_reclaimed_bytes=reclaim))
    return dict(scope=[str(p) for p in ROOTS],protected_paths=sorted(protected),
                failed_payloads=failures,duplicate_groups=duplicate_groups,
                estimated_failed_payload_bytes=sum(e['size_bytes'] for e in failures),
                estimated_duplicate_bytes=sum(g['estimated_reclaimed_bytes'] for g in duplicate_groups))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    if args.output.exists():
        raise ValueError('Use a new cleanup record directory')
    args.output.mkdir(parents=True,exist_ok=False)
    prepared=plan(args.inventory)
    atomic_json(args.output/'plan.json',prepared)
    print('Plan GiB: failed=',prepared['estimated_failed_payload_bytes']/2**30,
          'duplicate=',prepared['estimated_duplicate_bytes']/2**30,flush=True)
    if not args.apply:
        return
    before=shutil.disk_usage('/mnt/f').free
    journal=dict(status='running',free_bytes_before=before,operations=[])
    atomic_json(args.output/'journal.json',journal)
    try:
        for e in prepared['failed_payloads']:
            p=Path(e['path'])
            if not any(p.is_relative_to(root) for root in ROOTS):
                raise ValueError('Payload outside authorized scope')
            print('Remove failed RAW',p,flush=True)
            record=remove_failed_payload(p,Path(e['metadata']),set(prepared['protected_paths']),e['expected_digest'])
            journal['operations'].append(dict(operation='remove_failed_raw',**record))
            atomic_json(args.output/'journal.json',journal)
        for group in prepared['duplicate_groups']:
            source=Path(group['source'])
            for name in group['targets']:
                target=Path(name)
                print('Deduplicate trace',target,flush=True)
                if replace_duplicate(source,target,group['sha256']):
                    journal['operations'].append(dict(operation='hardlink_duplicate',source=str(source),target=str(target),sha256=group['sha256']))
                    atomic_json(args.output/'journal.json',journal)
        journal['status']='completed'
    except BaseException as error:
        journal.update(status='interrupted' if isinstance(error,KeyboardInterrupt) else 'failed',reason=str(error))
        raise
    finally:
        journal['free_bytes_after']=shutil.disk_usage('/mnt/f').free
        journal['measured_free_increase_bytes']=journal['free_bytes_after']-before
        atomic_json(args.output/'journal.json',journal)


if __name__=='__main__':
    main()
