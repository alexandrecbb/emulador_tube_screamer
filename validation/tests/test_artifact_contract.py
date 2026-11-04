"""Component-map contract checks; no simulator or numerical qualification."""

import copy
import itertools
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]


class ComponentMapContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping = json.loads((ROOT / 'reference/ts808/component_map.json').read_text())
        cls.schema = json.loads((ROOT / 'schemas/component_map.schema.json').read_text())
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)

    def test_schema_and_unique_component_ids(self):
        self.validator.validate(self.mapping)
        ids = [c['id'] for c in self.mapping['components']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 43)

    def test_capacitor_ownership_and_trace_nodes(self):
        components = self.mapping['components']
        expected = {'C_input', 'C_clip_input', 'C_gain_lower', 'C_feedback',
                    'C_tone_lowpass', 'C_tone_shelf', 'C_volume_input', 'C_dry',
                    'C_output_input', 'C_output', 'C_bias', 'C_supply'}
        self.assertEqual({c['id'] for c in components if c['kind'] == 'capacitor'}, expected)
        trace = self.mapping['trace_map']
        self.assertEqual(len(trace), 31)
        physical = {n for n in trace if not n.startswith(('i_', 'z_'))}
        self.assertEqual(len(physical), 24)
        known = set(self.mapping['known_nodes'])
        terminals = {n for c in components for n in c['terminals']}
        self.assertEqual(terminals, physical | known)
        for c in components:
            if 'law' in c:
                self.assertIn(c['law'], self.mapping['device_parameters'])

    def test_switch_connectivity_and_retained_loading(self):
        by_id = {c['id']: c for c in self.mapping['components']}
        for ident, terminals, value in [
            ('J_wet', ['wet_send', 'switch_common'], 383.29731360711594),
            ('R_dry_bias', ['dry_send', 'vref'], 510000),
            ('R_switch_common_bias', ['switch_common', 'vref'], 510000),
            ('C_dry', ['input_emitter', 'dry_send'], 100e-9),
            ('R_source', ['generator', 'input'], 1000),
            ('R_load', ['output', 'gnd'], 1000000),
        ]:
            with self.subTest(ident=ident):
                self.assertEqual(by_id[ident]['terminals'], terminals)
                self.assertAlmostEqual(by_id[ident]['value_SI'], value, places=15)
        self.assertNotIn('J_dry', by_id)
        extraction = {e['id']: e for e in self.mapping['extraction']}
        self.assertEqual(extraction['J_dry']['treatment'], 'omitted')
        self.assertEqual(extraction['J_wet']['treatment'], 'replaced')
        self.assertTrue(set(by_id) <= set(extraction))

    def test_control_orientations_and_all_27_positions(self):
        controls = self.mapping['controls']
        segments = {s['current_id']: (name, s) for name, c in controls.items()
                    for s in c['segments']}
        self.assertEqual({k: s['terminals'] for k, (_, s) in segments.items()}, {
            'i_drive': ['drive_end', 'clip_out'],
            'i_tone_low': ['tone_in', 'tone_wiper'],
            'i_tone_high': ['tone_wiper', 'tone_minus'],
            'i_volume_low': ['vref', 'wet_send'],
            'i_volume_high': ['wet_send', 'volume_top'],
        })
        for fractions in itertools.product((0, .5, 1), repeat=3):
            for name, fraction in zip(('drive', 'tone', 'volume'), fractions):
                c = controls[name]
                resistances = [c['total_Ohm'] * (fraction if s['factor'] == 'fraction'
                               else 1-fraction) for s in c['segments']]
                self.assertTrue(all(r >= 0 for r in resistances))
                if name != 'drive':
                    self.assertEqual(sum(resistances), c['total_Ohm'])
        # A connectivity/contract check, not a numerical rank or endpoint solve.
        self.assertEqual(segments['i_volume_low'][1]['factor'], 'fraction')

    def test_reject_invalid_contracts(self):
        candidates = []
        for key, value in [('schema_version', 2), ('unexpected', 1)]:
            m = copy.deepcopy(self.mapping)
            m[key] = value
            candidates.append(m)
        for value in (True, 0, -1, '1000'):
            m = copy.deepcopy(self.mapping)
            m['components'][0]['value_SI'] = value
            candidates.append(m)
        m = copy.deepcopy(self.mapping)
        del m['device_parameters']['diode_25c']['n']
        candidates.append(m)
        m = copy.deepcopy(self.mapping)
        m['components'][0]['terminals'] = ['input', 'input']
        candidates.append(m)
        m = copy.deepcopy(self.mapping)
        m['components'][0]['law'] = 'unapproved_model'
        candidates.append(m)
        for index, candidate in enumerate(candidates):
            with self.subTest(index=index):
                self.assertFalse(self.validator.is_valid(candidate))


if __name__ == '__main__':
    unittest.main()
