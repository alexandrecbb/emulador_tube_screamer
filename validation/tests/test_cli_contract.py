import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ts808_validation.artifacts import finalize_run, load_json, validate_case

ROOT = Path(__file__).resolve().parents[2]
BINARY = ROOT / 'build/offline-checks/ts808_offline'


@unittest.skipUnless(BINARY.is_file(), 'Build offline-checks first')
class CliContract(unittest.TestCase):
    def setUp(self):
        self.catalog = load_json(ROOT / 'reference/ts808/cases.json')
        self.case = copy.deepcopy(next(c for c in self.catalog['cases'] if c['case_id'] == 'dc_d050_t050_v050'))

    def execute(self, root, case=None, output='run'):
        path = root / 'case.json'; path.write_text(json.dumps(case or self.case))
        result = subprocess.run([str(BINARY), '--case', str(path), '--output', str(root/output)], capture_output=True)
        return result, path

    def test_all_27_dc_and_ac_cases_publish_valid_traces(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for case in self.catalog['cases']:
                if case['analysis_kind'] == 'transient': continue
                result, path = self.execute(root, case, case['case_id'])
                self.assertEqual(result.returncode, 0, result.stderr)
                final = finalize_run(root/case['case_id'], path, BINARY)
                self.assertEqual(final['trace']['shape'], [1, 32])
                self.assertEqual(final['trace']['integrity'], 'verified')
                if case['analysis_kind'] == 'ac':
                    self.assertEqual(final['response']['shape'], [301, 5])

    def test_invalid_inputs_do_not_create_run(self):
        mutations = [lambda c: c.update(schema_version=2),
                     lambda c: c['circuit']['controls'].update(drive=True),
                     lambda c: c['execution']['solver'].update(unknown=1),
                     lambda c: c['analysis'].update(required_checks=[])]
        for mutate in mutations:
            with self.subTest(mutate=mutate), tempfile.TemporaryDirectory() as temp:
                root = Path(temp); case = copy.deepcopy(self.case); mutate(case)
                result, _ = self.execute(root, case)
                self.assertEqual(result.returncode, 10)
                self.assertFalse((root/'run').exists())
                with self.assertRaises(Exception): validate_case(case)

    def test_existing_output_and_corrupt_payload_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); result, path=self.execute(root)
            self.assertEqual(result.returncode, 0)
            repeated, _=self.execute(root); self.assertEqual(repeated.returncode, 50)
            payload=root/'run/traces.f64le'; payload.write_bytes(payload.read_bytes()[:-1])
            with self.assertRaises(ValueError): finalize_run(root/'run', path, BINARY)

    def test_hold_at_both_rates_keeps_dc(self):
        case=copy.deepcopy(next(c for c in self.catalog['cases'] if c['case_id']=='hold_center'))
        for rate in (192000,384000):
            with self.subTest(rate=rate),tempfile.TemporaryDirectory() as temp:
                root=Path(temp);case['execution']['rate_Hz']=rate
                case['analysis']['time']['sample_count']=int(.2*rate)+1
                result,path=self.execute(root,case);self.assertEqual(result.returncode,0,result.stderr)
                finalize_run(root/'run',path,BINARY)
                data=np.fromfile(root/'run/traces.f64le',dtype='<f8').reshape(-1,32)
                for column,name in enumerate(case['trace_columns'][1:],1):
                    tolerance=1e-9 if name.startswith('i_') else 1e-6
                    self.assertLessEqual(np.max(np.abs(data[:,column]-data[0,column])),tolerance)
