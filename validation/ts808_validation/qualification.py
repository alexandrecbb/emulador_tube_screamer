"""Read-only reconciliation of partitioned automatic qualification evidence."""
from pathlib import Path
from datetime import datetime, timezone

from .artifacts import ROOT, atomic_json, load_json, validate_case
from .compare import validator_hash
from .persist import original_source, validate_schema
from .simulator import confined, sha256

AUDITOR_SHA256 = sha256(Path(__file__))


def wav_source_settings_match(request_settings, source_settings):
    """Legacy WAV manifests omitted derived options; original_source audits the deck.

    All declared settings must still match exactly. Only the omission of this
    derived field is supported; an explicitly supplied wrong value is rejected.
    """
    expected = dict(request_settings)
    if 'native_options' not in source_settings:
        expected.pop('native_options', None)
    return expected == source_settings


def assessment(report, analysis_kind):
    categories = ['reference', 'numerical'] + (['wav'] if analysis_kind == 'transient' else [])
    failed_checks = [c for c in report['checks']+report['reference_qualification']['checks']
                     if c['required'] and c['applicable'] and c['status'] == 'failed']
    blocked_wav = (analysis_kind == 'transient' and report['outcomes']['wav'] == 'pending'
                   and any(report['outcomes'][k] == 'failed' for k in ('reference', 'numerical')))
    evaluated = all(report['outcomes'][k] in ('passed', 'failed') or
                    (k == 'wav' and blocked_wav) for k in categories)
    return dict(evaluated=evaluated, wav_blocked_by_failed_gate=blocked_wav,
                failed_checks=failed_checks)


def reconcile(cases, entries):
    expected = {(c['case_id'], rate): c for c in cases
                for rate in ((192000, 384000) if c['analysis_kind'] == 'transient' else (None,))}
    if len({c['case_id'] for c in cases}) != len(cases):
        raise ValueError('Duplicate physical case in manifest')
    found = {}
    for entry in entries:
        key = (entry['case_id'], entry['rate_Hz'])
        if key in found:
            raise ValueError(f'Duplicate qualification entry: {key}')
        if key not in expected:
            raise ValueError(f'Unexpected qualification entry: {key}')
        if entry['physical_case_sha256'] != expected[key]['physical_case_sha256']:
            raise ValueError(f'Physical identity mismatch: {key}')
        found[key] = entry
    if found.keys() != expected.keys():
        raise ValueError(f'Missing qualification entries: {sorted(expected.keys()-found.keys())}')
    return expected, found


class EvidenceAudit:
    """Hash original payloads once in this command and check stat identity at end."""
    def __init__(self, executable, configs):
        self.executable = Path(executable)
        self.configs = configs
        self.executable_hash = sha256(self.executable)
        self.validator_hash = validator_hash()
        self.files = {}
        self.sources = {}

    @staticmethod
    def fingerprint(path):
        s = path.stat()
        return s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_ino

    def file(self, path, expected=None):
        path = Path(path).resolve()
        before = self.fingerprint(path)
        if path in self.files:
            digest, previous = self.files[path]
            if previous != before:
                raise ValueError(f'Evidence changed during audit: {path}')
        else:
            digest = sha256(path)
            if before != self.fingerprint(path):
                raise ValueError(f'Evidence changed during hashing: {path}')
            self.files[path] = digest, before
        if expected is not None and digest != expected:
            raise ValueError(f'Evidence hash mismatch: {path}')
        return digest

    def source(self, directory):
        directory = directory.resolve()
        if directory not in self.sources:
            cfg = next((c for c in self.configs if directory.is_relative_to(
                Path(c['workspace']['wsl_root']).resolve())), None)
            if cfg is None:
                raise ValueError(f'Unknown original reference provenance: {directory}')
            # Bound original_source's own integrity verification with fingerprints.
            request = load_json(directory/'request.json')
            result = load_json(directory/'reference_result.json')
            paths = [directory/'request.json', directory/'reference_result.json']
            paths += [confined(directory, e['path']) for e in request['inputs']+result['files']]
            before = {p: self.fingerprint(p) for p in paths}
            request, result = original_source(directory, cfg)
            hashes = {directory/'request.json': sha256(directory/'request.json'),
                      directory/'reference_result.json': sha256(directory/'reference_result.json')}
            hashes.update({confined(directory, e['path']): e['sha256']
                           for e in request['inputs']+result['files']})
            for p in paths:
                if self.fingerprint(p) != before[p]:
                    raise ValueError(f'Original changed during audit: {p}')
                self.files[p.resolve()] = hashes[p], before[p]
            self.sources[directory] = request, result
        return self.sources[directory]

    def reference(self, ref, case):
        path = Path(ref['manifest_path']['wsl_path'])
        self.file(path, ref['manifest_sha256'])
        manifest = load_json(path)
        validate_schema('imported_reference', manifest)
        if (manifest['physical_case_sha256'] != case['physical_case_sha256']
                or manifest['case_id'] != case['case_id']
                or manifest['integrity'] != 'verified' or manifest['completion'] != 'completed'
                or manifest['reference_id'] != ref['reference_id']):
            raise ValueError('Reference identity/integrity mismatch')
        self.file(path.parent/'case.json', manifest['case_input_sha256'])
        request_path = Path(manifest['source']['request']['locator']['wsl_path'])
        request, result = self.source(request_path.parent)
        if request['physical_case_sha256'] != case['physical_case_sha256']:
            raise ValueError('Original producer physical identity mismatch')
        for name, source in manifest['source'].items():
            self.file(Path(source['locator']['wsl_path']), source['sha256'])
            if ref[name+'_sha256'] != source['sha256']:
                raise ValueError('Report/reference source binding mismatch')

    def report(self, path, expected_case, rate, *, require_passed=True):
        path = Path(path)
        self.file(path)
        report = load_json(path)
        validate_schema('report', report)
        target = path.parent.parent
        cp = target/'case.json'
        rp = target/'run/run.json'
        self.file(cp, report['inputs']['case_sha256'])
        self.file(rp, report['inputs']['run_sha256'])
        case = load_json(cp)
        validate_case(case)
        run = load_json(rp)
        validate_schema('run', run)
        wanted_rate = rate or 192000
        if (case['physical_descriptor'] != expected_case['physical_descriptor']
                or report['case_id'] != case['case_id']
                or report['physical_case_sha256'] != case['physical_case_sha256']
                or run['physical_case_sha256'] != case['physical_case_sha256']
                or run['case_input_sha256'] != report['inputs']['case_sha256']
                or run['completion']['state'] != 'completed'
                or run['trace']['integrity'] != 'verified'
                or run['build']['executable_sha256'] != self.executable_hash
                or report['inputs']['validator_sha256'] != self.validator_hash
                or report['execution_config'] != run['execution_config']
                or case['execution']['rate_Hz'] != wanted_rate):
            raise ValueError(f'Stale or inconsistent report identity: {path}')
        if any(run['execution_config'].get(k) != v for k, v in case['execution'].items()):
            raise ValueError('Run/case execution mismatch')
        internal = expected_case['execution'].get('integration_rate_Hz')
        if case['execution'].get('integration_rate_Hz') != internal or (
                case['execution'].get('substeps') != (internal//wanted_rate if internal else None)):
            raise ValueError('Unexpected integration configuration')
        if case['analysis_kind'] == 'transient' and (
                case['execution'].get('integration_rate_Hz') != 768000
                or case['execution'].get('substeps') != 768000//wanted_rate):
            raise ValueError('Unapproved transient integration configuration')
        self.file(confined(rp.parent, run['trace']['filename']), run['trace']['sha256'])
        categories = ['reference', 'numerical'] + (['wav'] if case['analysis_kind'] == 'transient' else [])
        if require_passed and (report['reference_qualification']['status'] != 'passed'
                or any(report['outcomes'][k] != 'passed' for k in categories)):
            raise ValueError(f'Automatic qualification gates have not passed: {path}')
        for check in report['checks']+report['reference_qualification']['checks']:
            if require_passed and check['required'] and check['applicable'] and check['status'] != 'passed':
                raise ValueError(f'Unpassed required check: {path}: {check["id"]}')
        for level in ('nominal', 'refined'):
            self.reference(report['reference_qualification'][level], case)
        for artifact in report['artifacts']:
            if artifact['status'] == 'generated':
                self.file(confined(path.parent, artifact['path']), artifact['sha256'])
        if case['analysis_kind'] == 'ac' and wanted_rate == 192000:
            self.report(path.parent/'ac384000/comparison/report.json', expected_case, 384000,
                        require_passed=require_passed)
        if case['analysis_kind'] == 'transient' and report['outcomes']['wav'] in ('passed', 'failed'):
            source = load_json(path.parent/'native-wav-source.json')
            directory = Path(source['files']['audio.wav']['locator']['wsl_path']).parent
            request, result = self.source(directory)
            self.file(directory/'request.json', source['request_sha256'])
            self.file(directory/'reference_result.json', source['result_sha256'])
            if (request['physical_case_sha256'] != case['physical_case_sha256']
                    or not wav_source_settings_match(request['reference_settings'], source['settings'])):
                raise ValueError('WAV producer identity/settings mismatch')
            for file in source['files'].values():
                self.file(Path(file['locator']['wsl_path']), file['sha256'])
        return report

    def finish(self):
        if sha256(self.executable) != self.executable_hash or validator_hash() != self.validator_hash:
            raise ValueError('Executable/validator changed during audit')
        for path, (_, fingerprint) in self.files.items():
            if self.fingerprint(path) != fingerprint:
                raise ValueError(f'Evidence changed during audit: {path}')


def consolidate(root, output, transient_summary=None, *, require_passed=True):
    """Require all 128 canonical entries, retaining each original evidence locator."""
    root, output = Path(root), Path(output)
    output.mkdir(parents=True, exist_ok=False)
    cases = load_json(root/'cases.json')['cases']
    entries = []
    partitions = [root/'matrix-alt/summary.json', Path(transient_summary) if transient_summary else
                  root/'remaining-transients-20261104/matrix/summary.json']
    for path in partitions:
        summary = load_json(path)
        validate_schema('suite_summary', summary)
        for e in summary['entries']:
            if e['report'] is not None:
                entry = dict(e)
                entry['report_path'] = str(path.parent/e['report']['path'])
                entry['partition'] = str(path)
                entries.append(entry)
    hold = next(c for c in cases if c['case_id'] == 'hold_center')
    for rate in (192000, 384000):
        path = root/'hold-diagnosis-20261104/norm'/str(rate)/'comparison/report.json'
        entries.append(dict(case_id=hold['case_id'], physical_case_sha256=hold['physical_case_sha256'],
                            rate_Hz=rate, report_path=str(path), report=dict(sha256=sha256(path)),
                            partition='Independent hold qualification with solver=norm'))
    expected, found = reconcile(cases, entries)
    audit = EvidenceAudit(ROOT/'build/offline-release/ts808_offline',
                          [load_json(ROOT/'validation'/name) for name in ('toolchain-pilot-f.json', 'toolchain.json')])
    audit.file(root/'cases.json')
    audit.file(Path(__file__), AUDITOR_SHA256)
    for path in partitions:
        audit.file(path)
    result = dict(schema_version=1, recorded_at_utc=datetime.now(timezone.utc).isoformat(),
                  scope='Complete automatic numerical and WAV qualification; human ABX separate',
                  automatic_qualification='pending', listening='outside_automatic_audit', mvp_acceptance='pending',
                  validator_sha256=audit.validator_hash, executable_sha256=audit.executable_hash,
                  auditor_sha256=AUDITOR_SHA256, entries=[])
    for key, case in expected.items():
        entry = found[key]
        path = Path(entry['report_path'])
        audit.file(path, entry['report']['sha256'])
        report = audit.report(path, case, key[1], require_passed=require_passed)
        result['entries'].append(dict(case_id=key[0], rate_Hz=key[1],
                                     physical_case_sha256=case['physical_case_sha256'],
                                     report_path=str(path), report_sha256=entry['report']['sha256'],
                                     partition=entry['partition'], outcomes=report['outcomes'],
                                     **assessment(report, case['analysis_kind'])))
        atomic_json(output/'progress.json', dict(audited=len(result['entries']), required=len(expected),
                                               current_case=key[0], status='auditing'))
        print('Audited', key, flush=True)
    audit.finish()
    failed = [e for e in result['entries'] if e['failed_checks'] or
              any(e['outcomes'][k] == 'failed' for k in ('reference', 'numerical', 'wav'))]
    complete = all(e['evaluated'] for e in result['entries'])
    result.update(automatic_qualification='failed' if failed else 'passed' if complete else 'pending',
                  assessment_completion='completed' if complete else 'incomplete',
                  failed_entry_count=len(failed), entry_count=len(result['entries']),
                  physical_case_count=len(cases), verified_file_count=len(audit.files))
    atomic_json(output/'qualification.json', result)
    atomic_json(output/'integrity.json', {str(p): digest for p, (digest, _) in audit.files.items()})
    (output/'qualification.md').write_text(
        f'# Qualificação automática TS808\n\n{len(cases)} casos físicos; {len(expected)} entradas.\n\n'
        f'Qualificação automática: {result["automatic_qualification"]}; '
        f'avaliação: {result["assessment_completion"]}; entradas reprovadas: {len(failed)}.\n'
        'WAVs bloqueados por reprovação anterior permanecem pendentes, sem promoção.\n'
        'Hashes, identidade do executável/validador e cobertura conferidos nos originais.\n'
        'ABX humano fora do escopo desta auditoria; consultar registro humano separado. '
        'Aceitação do MVP pendente.\n')
    return result
