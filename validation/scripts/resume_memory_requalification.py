"""Re-evaluate completed R3 references without starting native producers."""
from pathlib import Path
import resource
import shutil
import subprocess
from ts808_validation.artifacts import ROOT, atomic_json, load_json, configure_substeps, finalize_run
from ts808_validation.compare import compare, validator_hash
from ts808_validation.audio_qualification import requalify_existing_audio
from ts808_validation.persist import ReferenceSession
from ts808_validation.simulator import sha256

CASE='tone_high_f5000_a500mv-warmup2s'
SOURCE=Path('/mnt/f/ts808-validation/wav-repair-20261109-r3/matrix')/CASE
OLD=Path('/mnt/f/ts808-validation/wav-completion-20261108-r4')/CASE/'matrix'/CASE
OUT=Path('/mnt/f/ts808-validation/memory-requalification-20261109-r1')

def main():
    OUT.mkdir(exist_ok=False)
    status=dict(status='running',validator_sha256=validator_hash(),shutdown_authorized=False,mvp_accepted=False,results=[])
    atomic_json(OUT/'status.json',status)
    cfg=load_json(ROOT/'validation/toolchain-pilot-f.json')
    executable=ROOT/'build/offline-release/ts808_offline'
    atomic_json(OUT/'provenance.json',dict(source=str(SOURCE),references={k:dict(path=str(SOURCE/k),manifest_sha256=sha256(SOURCE/k/'reference.json')) for k in ('nominal','refined')},executable_sha256=sha256(executable),free_bytes=shutil.disk_usage(OUT).free))
    session=ReferenceSession()
    try:
        for rate in (192000,384000):
            target=OUT/str(rate);target.mkdir()
            if (SOURCE/str(rate)/'run/run.json').exists():
                shutil.copy2(SOURCE/str(rate)/'case.json',target/'case.json')
                (target/'run').symlink_to(SOURCE/str(rate)/'run',target_is_directory=True)
            else:
                case=load_json(SOURCE/'case.json');configure_substeps(case,rate)
                case['analysis']['time']['sample_count']=round(case['analysis']['time']['duration_s']*rate)+1
                atomic_json(target/'case.json',case)
                subprocess.run([str(executable),'--case',str(target/'case.json'),'--output',str(target/'run')],check=True)
                finalize_run(target/'run',target/'case.json',executable)
            print('Comparing completed native pair',rate,flush=True)
            report=compare(target/'run',SOURCE/'nominal',SOURCE/'refined',target/'comparison',cfg,reference_session=session)
            report=requalify_existing_audio(target/'case.json',target/'run',SOURCE/'nominal',SOURCE/'refined',target/'comparison',OLD/str(rate)/'comparison/native-wav-source.json',cfg,reference_session=session)
            status['results'].append(dict(rate_Hz=rate,outcomes=report['outcomes']))
            atomic_json(OUT/'status.json',status)
            print(rate,report['outcomes'],flush=True)
        session.verify()
        status['status']='completed'
    except BaseException as error:
        status.update(status='interrupted',reason=str(error));raise
    finally:
        status['max_rss_MiB']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
        atomic_json(OUT/'status.json',status)

if __name__=='__main__':main()
