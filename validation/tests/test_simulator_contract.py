from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ts808_validation.simulator import confined, sha256


class SimulatorContract(unittest.TestCase):
    def test_confined_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(confined(root, 'a/b.raw'), root / 'a/b.raw')
            for path in ('../escape', '/absolute', 'C:/absolute', 'a\\b', '.'):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    confined(root, path)
            (root / 'link').symlink_to(root.parent, target_is_directory=True)
            with self.assertRaises(ValueError):
                confined(root, 'link/outside')

    def test_hash_uses_actual_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'data'
            path.write_bytes(b'abc')
            self.assertEqual(sha256(path), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')


def test_reference_has_native_endpoint_guard_without_startup():
    from ts808_validation.cli import make_deck
    from ts808_validation.artifacts import ROOT,load_json
    case=next(c for c in load_json(ROOT/'reference/ts808/cases.json')['cases'] if c['case_id']=='overload_high')
    for refined in (False,True):
        deck=make_deck(case,refined);line=next(l for l in deck.splitlines() if l.startswith('.tran '));words=line.split()
        stop=float(words[2]);step=float(words[4])
        assert stop==case['analysis']['time']['duration_s']+step
        assert step==1/(384000*8*(2 if refined else 1))
        assert 'uic' not in line and 'startup' not in line
