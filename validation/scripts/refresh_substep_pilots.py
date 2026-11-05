"""Recheck unchanged pilot payloads after tightening native reference validation."""
from pathlib import Path
import shutil

from ts808_validation.artifacts import ROOT,atomic_json,load_json
from ts808_validation.audio_qualification import requalify_existing_audio
from ts808_validation.compare import compare,validator_hash
from ts808_validation.persist import ReferenceSession
from ts808_validation.simulator import sha256


def main():
    root=Path('/mnt/f/ts808-validation/substeps-20261104')
    summary=load_json(root/'pilots.json');atomic_json(root/'pilots-before-reader-guard.json',summary)
    cfg=load_json(ROOT/'validation/toolchain-pilot-f.json')
    for pilot in summary['pilots']:
        session=ReferenceSession();reference_cfg=load_json(Path(pilot['reference_toolchain']))
        for m in pilot['measurements']:
            old=Path(m['comparison_directory']);target=old.parent
            if sha256(old/'report.json')!=m['report_sha256']:raise ValueError('Old pilot report changed')
            new=target/('comparison-'+validator_hash()[:10]+'-reader-guard')
            refs={k:Path(v) for k,v in pilot['references'].items()}
            report=compare(target/'run',refs['nominal'],refs['refined'],new,reference_cfg,reference_session=session)
            report=requalify_existing_audio(target/'case.json',target/'run',refs['nominal'],refs['refined'],new,old/'native-wav-source.json',cfg,reference_config=reference_cfg,reference_session=session)
            m.update(comparison_directory=str(new),report_sha256=sha256(new/'report.json'),outcomes=report['outcomes'])
            print(pilot['case_id'],m['rate_Hz'],report['outcomes'],flush=True)
    summary['validator_sha256']=validator_hash()
    summary['full_matrix_authorized']=all(m['outcomes'][k]=='passed' for p in summary['pilots'] for m in p['measurements'] for k in ('reference','numerical','wav'))
    atomic_json(root/'pilots.json',summary)
    return 0 if summary['full_matrix_authorized'] else 40


if __name__=='__main__':
    raise SystemExit(main())
