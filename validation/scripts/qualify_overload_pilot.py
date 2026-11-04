from pathlib import Path
from ts808_validation.artifacts import ROOT,load_json,atomic_json
from ts808_validation.persist import import_reference
from ts808_validation.compare import compare,validator_hash
cfg=load_json(ROOT/'validation/toolchain-pilot-f.json');physical=ROOT/'runs/mvp-pilots-02/overload_high';refs={};rows=[]
for level in ('nominal','refined'):
    source=Path(load_json(physical/(level+'-alt-guard-request.json'))['directory']);out=physical/(level+'-alt-guard')
    m=load_json(out/'reference.json') if (out/'reference.json').exists() else import_reference(source,out,cfg);refs[level]=out
    result=load_json(source/'reference_result.json');rows.append(dict(level=level,native_elapsed_s=result['invocation']['elapsed_s'],point_count=m['validation']['point_count'],bytes=sum(e['size_bytes'] for e in result['files']),directory=str(source)))
    print(rows[-1],flush=True)
for measured in load_json(physical/'cpp-resources.json')['measurements']:
    rate=measured['rate_Hz'];target=physical/str(rate);out=target/('comparison-'+validator_hash()[:10]);report=load_json(out/'report.json') if (out/'report.json').exists() else compare(target/'run',refs['nominal'],refs['refined'],out,cfg)
    rows.append(dict(measured,outcomes=report['outcomes'],comparison_directory=str(out)));print(rows[-1],flush=True)
atomic_json(physical/'qualified-pilot.json',dict(case_id='overload_high',measurements=rows))
