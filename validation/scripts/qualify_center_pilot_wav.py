from ts808_validation.artifacts import ROOT,load_json
from ts808_validation.audio_qualification import qualify_audio
p=ROOT/'runs/mvp-revised-pilots-norm/tone_center_f1000_a100mv-warmup2s';target=p/'192000';comparison=target/'comparison-ab87f8bbcc'
r=qualify_audio(target/'case.json',target/'run',p/'nominal',p/'refined',comparison,load_json(ROOT/'validation/toolchain.json'))
print(r['outcomes'],flush=True)
