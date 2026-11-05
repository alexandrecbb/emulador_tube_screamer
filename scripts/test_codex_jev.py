import unittest
import json
import subprocess
from unittest.mock import patch

import codex_jev as router


class RoutingTests(unittest.TestCase):
    def response(self, confidence=0.9):
        return {'model': 'jev-test', 'answers': {'route': {
            'type': 'choice', 'choice': 'routine', 'confidence': confidence,
            'probabilities': dict(routine=0.7, implementation=0.1, numerical=0.1, research=0.1),
        }}}

    def test_selection_and_low_confidence(self):
        self.assertEqual(router.choose(self.response())['model'], 'gpt-6-luna')
        self.assertEqual(router.choose(self.response(0.2))['profile'], 'numerical')

    def test_invalid_response_cannot_inject_command(self):
        response = self.response()
        response['answers']['route']['choice'] = '$(touch injected)'
        with self.assertRaises(ValueError):
            router.choose(response)
        response = self.response()
        response['answers']['route']['confidence'] = float('nan')
        with self.assertRaises(ValueError):
            router.choose(response)

    def test_launch_uses_fixed_arguments_without_key(self):
        with patch.object(router.sys, 'argv', ['router', '--launch', '-dangerous task']), \
                patch.object(router, 'settings', return_value={'JEV_API_KEY': 'secret', 'JEV_MODEL': 'jev-latest'}), \
                patch.object(router, 'request_jev', return_value=self.response()), \
                patch.object(router, 'validate_codex_profile') as validate, \
                patch.object(router.subprocess, 'call', return_value=0) as call:
            # A task beginning with '-' must be separated from CLI flags.
            router.sys.argv = ['router', '--launch', '--', '-dangerous task']
            self.assertEqual(router.main(), 0)
            validate.assert_called_once()
            command = call.call_args.args[0]
            self.assertEqual(command[-2:], ['--', '-dangerous task'])
            self.assertNotIn('JEV_API_KEY', call.call_args.kwargs['env'])
            self.assertNotIn('secret', command)

    def test_profiles_match_available_catalog(self):
        catalog = {'models': [dict(slug=model, visibility='list',
                    supported_reasoning_levels=[{'effort': e} for e in ('low', 'medium', 'high')])
                    for model in ('gpt-6-luna', 'gpt-6-sol', 'gpt-6-astra')]}
        with patch.object(router.subprocess, 'run', return_value=subprocess.CompletedProcess(
                [], 0, stdout=json.dumps(catalog))):
            for model, effort, _ in router.PROFILES.values():
                router.validate_codex_profile(dict(model=model, reasoning_effort=effort))
            for model, effort in [('gpt-6.1-sol', 'high'), ('gpt-6-sol', 'unsupported')]:
                with self.assertRaises(ValueError):
                    router.validate_codex_profile(dict(model=model, reasoning_effort=effort))

    def test_catalog_failure_prevents_launch(self):
        with patch.object(router.sys, 'argv', ['router', '--launch', 'Tarefa']), \
                patch.object(router, 'settings', return_value={'JEV_API_KEY': 'secret', 'JEV_MODEL': 'jev-latest'}), \
                patch.object(router, 'request_jev', return_value=self.response()), \
                patch.object(router.subprocess, 'run', side_effect=subprocess.TimeoutExpired('codex', 30)), \
                patch.object(router.subprocess, 'call') as call:
            with self.assertRaises(ValueError):
                router.main()
            call.assert_not_called()


if __name__ == '__main__':
    unittest.main()
