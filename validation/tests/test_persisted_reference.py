import copy,shutil
from pathlib import Path
import pytest
from ts808_validation.artifacts import ROOT,load_json,atomic_json
from ts808_validation.persist import import_reference,consume_reference
from ts808_validation.simulator import windows_path


def fixture(tmp_path):
    source=tmp_path/'source';shutil.copytree(ROOT/'validation/tests/fixtures/pedal_dc',source)
    cfg=copy.deepcopy(load_json(ROOT/'validation/toolchain.json'));cfg['workspace']=dict(wsl_root=str(tmp_path),windows_root=windows_path(tmp_path))
    return source,cfg


def test_import_roundtrip_and_changed_original(tmp_path):
    source,cfg=fixture(tmp_path);output=tmp_path/'imported';m=import_reference(source,output,cfg)
    assert {p.name for p in output.iterdir()}=={'case.json','reference.json'}
    assert m['integrity']=='verified' and m['analysis_kind']=='dc'
    consume_reference(output,cfg)
    raw=source/'deck.raw';data=raw.read_bytes();raw.write_bytes(data[:-1]+bytes([data[-1]^1]))
    with pytest.raises(ValueError,match='Changed original'):consume_reference(output,cfg)


def test_import_pending_unknown_keys_and_path_escape(tmp_path):
    source,cfg=fixture(tmp_path);output=tmp_path/'imported';m=import_reference(source,output,cfg)
    for mutation in ('pending','unknown','escape','step','trace'):
        bad=copy.deepcopy(m)
        if mutation=='pending':bad['integrity']='pending'
        elif mutation=='unknown':bad['unknown']=1
        elif mutation=='escape':bad['source']['raw']['locator']['wsl_path']='/etc/passwd'
        elif mutation=='step':bad['selection']['step_index']=1
        else:bad['selection']['traces'][0]['native_expression']='V(missing)'
        atomic_json(output/'reference.json',bad)
        with pytest.raises(Exception):consume_reference(output,cfg)
