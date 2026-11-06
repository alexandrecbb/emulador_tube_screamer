import os
import runpy

import pytest

from ts808_validation.artifacts import ROOT, atomic_json, load_json
from ts808_validation.simulator import sha256


@pytest.fixture
def cleanup():
    return runpy.run_path(str(ROOT/'validation/scripts/cleanup_validation_storage.py'))


def test_dedup_keeps_paths_and_bytes_and_rejects_mismatch(tmp_path,cleanup):
    source,target=tmp_path/'source.f64le',tmp_path/'target.f64le'
    source.write_bytes(b'original trace')
    target.write_bytes(source.read_bytes())
    digest=sha256(source)
    assert cleanup['replace_duplicate'](source,target,digest)
    assert os.path.samefile(source,target)
    assert sha256(target)==digest
    assert not cleanup['replace_duplicate'](source,target,digest)
    other=tmp_path/'different.f64le'
    other.write_bytes(b'another trace')
    with pytest.raises(ValueError,match='hash mismatch'):
        cleanup['replace_duplicate'](source,other,digest)
    assert other.read_bytes()==b'another trace'


def test_failed_cleanup_preserves_metadata_and_records_removed_hash(tmp_path,cleanup):
    raw=tmp_path/'deck.raw';metadata=tmp_path/'reference_result.json'
    raw.write_bytes(b'truncated data');digest=sha256(raw)
    atomic_json(metadata,dict(completion='timed_out',reason='timeout'))
    original=metadata.read_bytes()
    record=cleanup['remove_failed_payload'](raw,metadata,set(),digest)
    assert not raw.exists()
    assert metadata.read_bytes()==original
    assert record['sha256']==digest
    assert load_json(tmp_path/'cleanup-removed-payload.json')==record


def test_cleanup_refuses_completed_protected_changed_and_symlink_payloads(tmp_path,cleanup):
    raw=tmp_path/'deck.raw';metadata=tmp_path/'reference_result.json'
    raw.write_bytes(b'important original')
    atomic_json(metadata,dict(completion='completed'))
    remove=cleanup['remove_failed_payload']
    with pytest.raises(ValueError,match='not explicitly failed'):
        remove(raw,metadata,set())
    atomic_json(metadata,dict(completion='failed'))
    with pytest.raises(ValueError,match='Protected'):
        remove(raw,metadata,{str(raw.resolve())})
    with pytest.raises(ValueError,match='hash mismatch'):
        remove(raw,metadata,set(),'a'*64)
    assert raw.read_bytes()==b'important original'
    raw.rename(tmp_path/'original.raw')
    raw.symlink_to(tmp_path/'original.raw')
    with pytest.raises(ValueError,match='Protected'):
        remove(raw,metadata,set())
    assert (tmp_path/'original.raw').read_bytes()==b'important original'
