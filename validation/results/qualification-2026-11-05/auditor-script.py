import os,traceback
from pathlib import Path
from ts808_validation.artifacts import atomic_json
from ts808_validation.qualification import consolidate
job=Path(__file__).parent;root=job.parent
atomic_json(job/'status.json',dict(status='running',pid=os.getpid()))
try:
    q=consolidate(root,job/'qualification',root/'qualification-resume-r11-20261104/matrix/summary.json',require_passed=False)
    atomic_json(job/'status.json',dict(status='completed',assessment_completion=q['assessment_completion'],automatic_qualification=q['automatic_qualification'],pid=os.getpid()))
except BaseException as e:
    atomic_json(job/'status.json',dict(status='failed',error=str(e),pid=os.getpid()));traceback.print_exc();raise
