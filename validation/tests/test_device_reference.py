"""Real native law parity; opt in with TS808_NATIVE_TESTS=1 after doctor."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import uuid
from spicelib import RawRead

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ts808_validation.simulator import prepare_request, run_request

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(os.environ.get('TS808_NATIVE_TESTS') == '1', 'Requires selected native producer')
class NativeDeviceReference(unittest.TestCase):
    def test_semiconductor_oracles(self):
        config = json.loads((ROOT / 'validation/toolchain.json').read_text())
        manifest = json.loads((ROOT / 'reference/ts808/cases.json').read_text())
        case = next(c for c in manifest['cases'] if c['case_id'] == 'dc_d050_t050_v050')
        oracle = json.loads((ROOT / 'tests/fixtures/device_nominal_25c.json').read_text())
        for fixture in ('diode', 'bjt'):
            with self.subTest(fixture=fixture), tempfile.TemporaryDirectory() as temp:
                case_path = Path(temp) / 'case.json'; case_path.write_text(json.dumps(case))
                destination = Path(config['workspace']['wsl_root']) / ('device-'+fixture+'-'+uuid.uuid4().hex)
                source = ROOT / 'reference/ts808'
                prepare_request(source, case_path, destination, request_id=destination.name,
                                settings=dict(level='nominal', purpose='independent_device_law', fixture=fixture),
                                deck=(source / f'check_{fixture}.cir').read_text())
                run_request(destination, Path(config['tools']['ltspice']['path']))
                log = (destination / 'deck.log').read_text()
                self.assertIn('Direct Newton iteration succeeded', log)
                self.assertNotIn('ERROR:', log)
                raw = RawRead(destination / 'deck.raw', verbose=False)
                for index, row in enumerate(oracle[fixture]):
                    if fixture == 'diode':
                        pairs = [('I(Vd'+str(index)+')', -float(row['current_A']))]
                    else:
                        pairs = [('I(Vc'+str(index)+')', -float(row['collector_A'])),
                                 ('I(Ve'+str(index)+')', -float(row['emitter_A']))]
                    for trace, expected in pairs:
                        actual = float(raw.get_trace(trace).get_wave()[0])
                        self.assertLessEqual(abs(actual-expected), 1e-15+1e-6*abs(expected))
