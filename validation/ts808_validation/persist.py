"""Immutable reference imports, with original shared producer files rechecked on use."""
from pathlib import Path
import shutil
import math
from .artifacts import ROOT, load_json, validate_case, atomic_json
from .simulator import sha256, windows_path, confined, native_options
from .reference import read_native


def validate_schema(name, value):
    from jsonschema import Draft202012Validator
    Draft202012Validator(load_json(ROOT/'schemas'/f'{name}.schema.json')).validate(value)


def check(identifier, value, limit, unit='', *, required=True, reason=''):
    value=None if value is None else float(value)
    limit=float(limit)
    if (value is not None and not math.isfinite(value)) or not math.isfinite(limit):raise ValueError('Nonfinite check metric')
    return dict(id=identifier, applicable=True, required=required,
                status='not_evaluated' if value is None else 'passed' if value <= limit else 'failed',
                metric=identifier, value=value, unit=unit, limit=limit,
                reason=reason or ('Measured without gain, delay or DC fitting' if value is not None else 'Evidence unavailable'))


def original_source(directory, config):
    root=Path(config['workspace']['wsl_root']).resolve()
    directory=directory.resolve()
    if not directory.is_relative_to(root): raise ValueError('Source outside shared producer root')
    request=load_json(directory/'request.json'); result=load_json(directory/'reference_result.json')
    validate_schema('reference_request',request);validate_schema('reference_result',result)
    if result['completion']!='completed' or result['request_sha256']!=sha256(directory/'request.json'):
        raise ValueError('Incomplete/mutated producer metadata')
    if result['request_id']!=request['request_id'] or result['physical_case_sha256']!=request['physical_case_sha256']:
        raise ValueError('Producer identity mismatch')
    required={'deck.cir','models.lib','case.json','component_map.json','device_spec.md','run_reference.ps1'}
    inputs=[e['path'] for e in request['inputs']];outputs=[e['path'] for e in result['files']]
    if set(inputs)!=required or len(inputs)!=len(set(inputs)) or len(outputs)!=len(set(outputs)) or set(outputs)!=set(request['expected_outputs']):
        raise ValueError('Unexpected or duplicate producer files')
    if result['producer']['executable_sha256']!=config['tools']['ltspice']['sha256']:
        raise ValueError('Wrong producer executable')
    declared=request['reference_settings'].get('native_options')
    if declared is not None and declared!=native_options((directory/'deck.cir').read_text()):raise ValueError('Recorded native options differ from staged deck')
    for entry in request['inputs']+result['files']:
        path=confined(directory,entry['path'])
        if path.stat().st_size!=entry['size_bytes'] or sha256(path)!=entry['sha256']:
            raise ValueError('Changed original producer file')
    return request,result


def selection_for(case,request):
    mapping=request['trace_map']; controls=case['circuit']['controls']
    factors={'i_drive':controls['drive'],'i_tone_low':controls['tone'],'i_tone_high':1-controls['tone'],
             'i_volume_low':controls['volume'],'i_volume_high':1-controls['volume']}
    return [dict(quantity_id=n,native_expression=mapping[n]['zero_resistance_expression'] if factors.get(n,1)==0 else mapping[n]['expression'],
                 unit=mapping[n]['unit'],orientation=mapping[n]['orientation']) for n in case['trace_columns'][1:]]


def import_reference(directory, output, config):
    if output.exists(): raise ValueError('Import destination exists')
    request,result=original_source(directory,config)
    case=load_json(directory/'case.json');validate_case(case)
    if case['physical_case_sha256']!=request['physical_case_sha256']: raise ValueError('Wrong case identity')
    traces=selection_for(case,request)
    native=read_native(directory/'deck.raw',directory/'deck.log',analysis_kind=case['analysis_kind'],trace_names=[t['native_expression'] for t in traces])
    axis=native['axis']; kind=case['analysis_kind']
    if kind=='transient' and (axis[0]!=0 or axis[-1]<case['analysis']['time']['duration_s']): raise ValueError('Insufficient reference coverage')
    if kind=='ac':
        import numpy as np
        if len(axis)!=301 or not np.allclose(axis,case['analysis']['frequencies_Hz'],rtol=1e-12,atol=0): raise ValueError('Wrong native frequency grid')
    source={}
    for name,filename in [('request','request.json'),('result','reference_result.json'),('raw','deck.raw'),('log','deck.log')]:
        path=(directory/filename).resolve()
        source[name]=dict(locator=dict(wsl_path=str(path),windows_path=windows_path(path)),size_bytes=path.stat().st_size,sha256=sha256(path))
    manifest=dict(schema_version=1,reference_id=request['request_id'],case_id=case['case_id'],physical_case_sha256=case['physical_case_sha256'],
                  case_input_sha256=sha256(directory/'case.json'),analysis_kind=kind,source=source,
                  selection=dict(plot_index=0,plot_name=native['plot_name'],analysis_kind=kind,step_index=None,step_parameters={},traces=traces),
                  validation=dict(encoding=native['encoding'],point_count=native['point_count'],domain_start=None if axis is None else float(axis[0]),domain_stop=None if axis is None else float(axis[-1]),
                                  checks=[check(n,0,0,reason='Verified against original producer bytes') for n in ('producer_completion','precision','file_integrity','selection','finite_data','axis_grid','coverage')]),
                  completion='completed',integrity='verified')
    validate_schema('imported_reference',manifest)
    output.mkdir(parents=True);shutil.copyfile(directory/'case.json',output/'case.json');atomic_json(output/'reference.json',manifest)
    return manifest


def consume_reference(directory,config):
    manifest=load_json(directory/'reference.json');validate_schema('imported_reference',manifest)
    if manifest['completion']!='completed' or manifest['integrity']!='verified': raise ValueError('Pending import integrity')
    for entry in manifest['source'].values():
        path=Path(entry['locator']['wsl_path']).resolve()
        if not path.is_relative_to(Path(config['workspace']['wsl_root']).resolve()) or windows_path(path).lower()!=entry['locator']['windows_path'].lower():
            raise ValueError('Invalid paired provenance locator')
        if path.stat().st_size!=entry['size_bytes']: raise ValueError('Changed imported source size')
    source=Path(manifest['source']['request']['locator']['wsl_path']).parent
    request,result=original_source(source,config)
    expected={e['path']:e['sha256'] for e in result['files']}
    expected.update({'request.json':sha256(source/'request.json'),'reference_result.json':sha256(source/'reference_result.json')})
    for name,filename in [('request','request.json'),('result','reference_result.json'),('raw','deck.raw'),('log','deck.log')]:
        if manifest['source'][name]['sha256']!=expected[filename]:raise ValueError('Manifest/source hash mismatch')

    case=load_json(directory/'case.json'); validate_case(case)
    if sha256(directory/'case.json')!=manifest['case_input_sha256'] or selection_for(case,request)!=manifest['selection']['traces']:
        raise ValueError('Changed imported case/selection')
    native=read_native(source/'deck.raw',source/'deck.log',analysis_kind=case['analysis_kind'],trace_names=[t['native_expression'] for t in manifest['selection']['traces']],plot_index=manifest['selection']['plot_index'],step_index=manifest['selection']['step_index'])
    if native['plot_name']!=manifest['selection']['plot_name']:raise ValueError('Changed plot selection')
    if (manifest['case_id']!=case['case_id'] or manifest['physical_case_sha256']!=case['physical_case_sha256']
            or request['physical_case_sha256']!=case['physical_case_sha256'] or manifest['analysis_kind']!=case['analysis_kind']
            or manifest['selection']['analysis_kind']!=case['analysis_kind'] or manifest['selection']['step_parameters']):
        raise ValueError('Imported physical/analysis identity mismatch')
    if (manifest['validation']['point_count']!=native['point_count'] or manifest['validation']['encoding']!=native['encoding']
            or any(c['status']!='passed' for c in manifest['validation']['checks'] if c['required'] and c['applicable'])):
        raise ValueError('Changed or unqualified import validation')
    axis=native['axis']
    if axis is not None and (manifest['validation']['domain_start']!=float(axis[0]) or manifest['validation']['domain_stop']!=float(axis[-1])):
        raise ValueError('Imported domain mismatch')
    return manifest,request,native


def publish_report(directory,report):
    """Publish machine truth and its derived human-readable view together."""
    validate_schema('report',report);atomic_json(directory/'report.json',report)
    checks=report['reference_qualification']['checks']+report['checks']
    pending=[c for c in checks if c['status']!='passed']
    text=f"# {report['case_id']} at {report['execution_config']['rate_Hz']} Hz\n\n{report['outcomes']}\n\n"
    text+='\n'.join(f"- {c['id']}: {c['status']}; {c['value']} {c['unit']}; limit {c['limit']}. {c['reason']}" for c in pending)
    if not pending:text+='All applicable implemented checks passed. Scope remains the identified physical case and rate.'
    (directory/'report.md').write_text(text+'\n')
