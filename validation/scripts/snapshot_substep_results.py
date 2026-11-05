"""Archive lightweight evidence; original F:/C: payloads remain authoritative."""
import shutil
from pathlib import Path

from ts808_validation.artifacts import ROOT,atomic_json,load_json
from ts808_validation.simulator import sha256


def main():
    source=Path('/mnt/f/ts808-validation/substeps-20261104')
    destination=ROOT/'validation/results/substeps-2026-11-04'
    destination.mkdir(exist_ok=False)
    summary=load_json(source/'pilots.json')
    shutil.copyfile(source/'pilots.json',destination/'pilots.json')
    shutil.copyfile(source/'cases.json',destination/'cases.json')
    for pilot in summary['pilots']:
        physical=destination/pilot['case_id'];physical.mkdir()
        for level,path in pilot['references'].items():
            shutil.copytree(path,physical/level)
        for measurement in pilot['measurements']:
            target=physical/str(measurement['rate_Hz']);target.mkdir()
            original=source/pilot['case_id']/str(measurement['rate_Hz'])
            shutil.copyfile(original/'case.json',target/'case.json')
            shutil.copyfile(original/'run/run.json',target/'run.json')
            comparison=Path(measurement['comparison_directory'])
            for name in ('report.json','report.md','residual.png','native-wav-source.json'):
                if (comparison/name).exists():shutil.copyfile(comparison/name,target/name)
    for name in ('production-overload-equality.json','production-high-equality.json','verification.json'):
        if (source/name).exists():shutil.copyfile(source/name,destination/name)
    matrix=source/'matrix'
    for name in ('summary.json','summary.md','resource-gate.json'):
        if (matrix/name).exists():shutil.copyfile(matrix/name,destination/('matrix-'+name))
    for name in ('substep-tests-20261104.log','substep-pilots-20261104.log','substep-matrix-20261104.log',
                 'substep-high-refinement-20261104.log','substep-high-alt-refinement-20261104.log',
                 'substep-overload-refinement-20261104.log','substep-final-matrix-20261104.log'):
        path=source.parent/name
        if path.exists():shutil.copyfile(path,destination/name)
    atomic_json(destination/'evidence.json',dict(scope='Evidence snapshot only; not a self-contained reference import. Original payloads remain at their recorded locators.',
                                              files={str(p.relative_to(destination)):sha256(p) for p in sorted(destination.rglob('*')) if p.is_file()}))


if __name__=='__main__':
    main()
