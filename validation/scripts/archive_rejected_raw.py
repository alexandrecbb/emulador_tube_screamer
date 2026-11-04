"""Reversible relocation of our explicitly rejected/cancelled RAW payloads."""
from pathlib import Path
import shutil
from ts808_validation.artifacts import ROOT,load_json,atomic_json
from ts808_validation.simulator import sha256,windows_path
source_root=Path('/mnt/c/Users/Alexandre/AppData/Local/ts808-reference/runs');destination_root=Path('/mnt/f/ts808-reference/runs/rejected-archive')
ids=['audit-opamp-transient-700a8e7f0909410a8bed931ae417188f','tone_center_f1000_a100mv-warmup2s-nominal-242924cbf386444dbf0c4faf4a5ad73f','tone_center_f1000_a100mv-warmup2s-refined-947b60d1d62c40c598205a5917934e8f'];entries=[]
for identifier in ids:
    source=source_root/identifier;raw=source/'deck.raw'
    if not raw.exists():
        if (source/'raw-archive.json').exists():entries.append(load_json(source/'raw-archive.json'));continue
        raise ValueError('Missing original/archive pointer')
    result=load_json(source/'reference_result.json');log=(source/'deck.log').read_text()
    if result['completion']=='completed' and '.option solver should' not in log:raise ValueError('Refusing to relocate a potentially qualified reference')
    size=raw.stat().st_size;digest=sha256(raw);destination=destination_root/identifier;destination.mkdir(parents=True,exist_ok=True);target=destination/'deck.raw';temporary=destination/'deck.raw.partial'
    if target.exists():raise ValueError('Archive destination exists')
    shutil.copyfile(raw,temporary)
    if temporary.stat().st_size!=size or sha256(temporary)!=digest or raw.stat().st_size!=size or sha256(raw)!=digest:raise ValueError('Archive copy/source identity mismatch')
    temporary.rename(target)
    record=dict(schema_version=1,original_wsl_path=str(raw),original_windows_path=windows_path(raw),archive_wsl_path=str(target),archive_windows_path=windows_path(target),size_bytes=size,sha256=digest,qualification='rejected_or_cancelled',reason='Producer failed/cancelled or ignored invalid solver option; not consumable acceptance evidence',request_sha256=sha256(source/'request.json'),result_sha256=sha256(source/'reference_result.json'),log_sha256=sha256(source/'deck.log'))
    atomic_json(destination/'archive.json',record);atomic_json(source/'raw-archive.json',record)
    raw.unlink();entries.append(record);atomic_json(ROOT/'runs/mvp-qualification/rejected-raw-archive.json',dict(entries=entries,relocated_bytes=sum(e['size_bytes'] for e in entries)))
    print(identifier,size,flush=True)
