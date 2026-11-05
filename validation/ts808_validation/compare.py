"""Standalone comparisons require explicit, independent nominal/refined imports."""
from pathlib import Path
import hashlib
import json
import numpy as np
from .artifacts import load_json,atomic_json,validate_case,integration_config
from .simulator import sha256,windows_path,confined,native_options
from .persist import consume_reference,validate_schema,check
from .reconstruct import pchip
from .metrics import null_checks,bode_checks,local_checks,harmonic_checks,settling_checks,recovery_index


def validator_hash():
    folder=Path(__file__).parent
    sources={name:sha256(folder/name) for name in ('compare.py','metrics.py','reference.py','persist.py','reconstruct.py','artifacts.py')}
    return hashlib.sha256(json.dumps(sources,sort_keys=True).encode()).hexdigest()


def validate_native_refinement(nominal,refined):
    import math
    allowed={'temp','tnom','plotwinsize','numdgt','method','reltol','abstol','vntol','chgtol','trtol','gmin','gminsteps','srcsteps','solver'}
    for options in (nominal,refined):
        if set(options)-allowed:raise ValueError('Unqualified native option')
        for key,expected in {'temp':25,'tnom':25,'plotwinsize':0,'numdgt':15,'trtol':1,'gmin':1e-12,'gminsteps':0,'srcsteps':0}.items():
            if key not in options or float(options[key])!=expected:raise ValueError('Wrong native option: '+key)
        if options.get('method','').lower()!='trap' or options.get('solver','norm').lower() not in ('norm','alt'):raise ValueError('Unqualified native solver/integrator')
    if nominal.get('solver','norm').lower()!=refined.get('solver','norm').lower():raise ValueError('Refinement changed native solver')
    for key,maximum in {'reltol':1e-6,'abstol':1e-12,'vntol':1e-9,'chgtol':1e-16}.items():
        a=float(nominal[key]);b=float(refined[key])
        if not (math.isfinite(a) and math.isfinite(b) and 0<a<=maximum and 0<b<=a/10*(1+1e-14)):
            raise ValueError('Refinement did not tighten '+key)


def reference_id(path,manifest):
    return dict(reference_id=manifest['reference_id'],manifest_path=dict(wsl_path=str((path/'reference.json').resolve()),windows_path=windows_path(path/'reference.json')),
                manifest_sha256=sha256(path/'reference.json'),**{n+'_sha256':manifest['source'][n]['sha256'] for n in ('request','result','raw','log')})


def compare(run_dir,nominal_dir,refined_dir,output,config,*,diagnostics=False,reference_session=None):
    if output.exists(): raise ValueError('Comparison destination exists')
    run=load_json(run_dir/'run.json');validate_schema('run',run)
    if run['completion']['state']!='completed':raise ValueError('Failed/incomplete C++ run')
    if run['trace']['filename']!='traces.f64le':raise ValueError('Unexpected trace filename')
    if run['trace']['integrity']!='verified' or sha256(confined(run_dir,run['trace']['filename']))!=run['trace']['sha256']: raise ValueError('Pending/changed C++ integrity')
    case=load_json(run_dir.parent/'case.json');validate_case(case)
    if sha256(run_dir.parent/'case.json')!=run['case_input_sha256']:raise ValueError('Changed finalized case bytes')
    consume=reference_session.consume if reference_session is not None else consume_reference
    nm,nq,n=consume(nominal_dir,config);rm,rq,r=consume(refined_dir,config)
    if len({nm['physical_case_sha256'],rm['physical_case_sha256'],run['physical_case_sha256']})!=1 or nm['selection']!=rm['selection'] or nq['request_id']==rq['request_id']:
        raise ValueError('Mismatched reference pair')
    for filename in ('models.lib','component_map.json','device_spec.md'):
        nh=next(e['sha256'] for e in nq['inputs'] if e['path']==filename)
        rh=next(e['sha256'] for e in rq['inputs'] if e['path']==filename)
        if nh!=rh:raise ValueError('Changed model/spec across refinement')
    ns=dict(nq['reference_settings']);rs=dict(rq['reference_settings'])
    for settings,manifest in ((ns,nm),(rs,rm)):
        deck=Path(manifest['source']['request']['locator']['wsl_path']).parent/'deck.cir'
        settings['native_options']=native_options(deck.read_text())
    validate_native_refinement(ns['native_options'],rs['native_options'])
    if ns['level']!='nominal' or rs['level']!='refined' or rs['maxstep_s']!=ns['maxstep_s']/2:
        raise ValueError('Wrong refinement settings')
    count=case['analysis'].get('time',{}).get('sample_count',1)
    if (run['trace']['shape']!=[count,32] or run['trace']['dtype']!='<f8' or run['trace']['order']!='C'
            or run['trace']['byte_length']!=count*256 or (run_dir/'traces.f64le').stat().st_size!=count*256
            or run['completion']['written_samples']!=count or [c['id'] for c in run['trace']['columns']]!=case['trace_columns']):
        raise ValueError('Inconsistent finalized run layout')
    if (run['case_id']!=case['case_id'] or run['model_id']!=case['circuit']['model_id'] or run['physical_case_sha256']!=case['physical_case_sha256']
            or run['execution_config']['ordered_unknowns']!=case['trace_columns'][1:] or run['execution_config']['unknown_count']!=31
            or run['execution_config']['interior_counts']!=[4,6,11,5] or run['execution_config']['boundary_count']!=5):
        raise ValueError('Run identity/layout differs from accepted case')
    for key,value in case['execution'].items():
        if run['execution_config'][key]!=value:raise ValueError('Run execution configuration differs from case')
    if integration_config(run['execution_config'])!=integration_config(case['execution']):
        raise ValueError('Run integration configuration differs from case')
    shape=run['trace']['shape']; data=np.memmap(run_dir/'traces.f64le',dtype='<f8',mode='r',shape=tuple(shape))
    for start in range(0,count,65536):
        if not np.isfinite(data[start:start+65536]).all():raise ValueError('Nonfinite C++ trace')
    expected=np.arange(count)/case['execution']['rate_Hz']
    if np.any(abs(data[:,0]-expected)>4*np.spacing(expected)):raise ValueError('Wrong C++ timestamp grid')
    names=case['trace_columns'][1:]; col=names.index('output')+1; expression=next(t['native_expression'] for t in nm['selection']['traces'] if t['quantity_id']=='output')
    checks=[];uncertainty=[];kind=case['analysis_kind'];rate=case['execution']['rate_Hz'];ref=None
    if kind=='dc':
        indices=[i for i,name in enumerate(names) if not name.startswith('i_')]
        nv=np.array([n['traces'][t['native_expression']][0] for t in nm['selection']['traces']]);rv=np.array([r['traces'][t['native_expression']][0] for t in rm['selection']['traces']])
        uncertainty=[check('dc_reference',float(np.max(abs(nv[indices]-rv[indices]))),.001,'V')]
        checks=[check('dc_voltages',float(np.max(abs(data[0,1:][indices]-nv[indices]))),.01,'V')]
    elif kind=='ac':
        if sha256(run_dir/'response.f64le')!=run['response']['sha256']:raise ValueError('Changed AC payload')
        a=np.fromfile(run_dir/'response.f64le',dtype='<f8').reshape(301,5)
        nv=n['traces'][expression];rv=r['traces'][expression]
        uncertainty=bode_checks('ac_reference',nv,rv,.1)
        checks=bode_checks('bode_discrete',a[:,3]+1j*a[:,4],nv)+bode_checks('bode_continuous',a[:,1]+1j*a[:,2],nv)
    else:
        times=data[:,0];nv=pchip(n['axis'],n['traces'][expression],times);rv=pchip(r['axis'],r['traces'][expression],times);ref=nv
        uncertainty=null_checks('reference_integration',nv,rv,.1)
        # Storage binary64 and reconstruction sensitivity are evaluated separately.
        uncertainty.append(check('storage_roundoff_bound',float(np.max(np.spacing(abs(nv)))),1e-7,'V'))
        # Leave-out native sample reconstruction is an independent sensitivity diagnostic.
        nt=n['axis']; vals=n['traces'][expression];idx=np.arange(1,len(nt)-1,2)
        keep=np.unique(np.r_[np.arange(0,len(nt),2),len(nt)-1]); interp=pchip(nt[keep],vals[keep],nt[idx])
        uncertainty.extend(null_checks('reconstruction_decimation',interp,vals[idx],.1))
        coarse=pchip(nt[keep],vals[keep],times)
        bound=abs(nv-rv)+abs(coarse-nv)+np.spacing(abs(nv))
        uncertainty.extend(null_checks('reference_aggregate',rv+bound,rv,.1))
        uncertainty.extend(local_checks('reference_local',rv+bound,rv,rate,.1))
        required=case['analysis']['required_checks']
        if 'dc_hold' in required:
            for i,name in enumerate(names,1):checks.append(check('dc_hold_'+name,float(np.max(abs(data[:,i]-data[0,i]))),1e-9 if name.startswith('i_') else 1e-6,'A' if name.startswith('i_') else 'V'))
        if 'null' in required or 'harmonics' in required or 'linearity' in required:
            window=next((w for w in case['analysis']['windows'] if w['role']=='steady'),None)
            mask=(times>=window['start_s'])&(times<window['stop_s']) if window else np.ones(len(times),dtype=bool)
            checks+=null_checks('null',data[mask,col],nv[mask])
            if 'harmonics' in required:
                f=case['stimulus']['frequency_Hz'];checks+=harmonic_checks(data[mask,col],nv[mask],nv[mask]-rv[mask],rate,f)
                for prefix,y in [('cpp',data[:,col]),('reference',nv)]:checks+=settling_checks(y[mask],times[mask],f,prefix+'_settling')
            if 'linearity' in required:checks.append(check('linearity',None,.001,'relative',reason='Requires separately bound 10/20 uV paired-case result'))
        if 'local_windows' in required:checks+=local_checks('local',data[:,col],nv,rate)
        if 'recovery' in required:
            # Reconstruct only recovery/bias quantities needed for timing.
            refdata=np.zeros((len(times),32));refdata[:,0]=times
            for name in ('output','vref','input_base','output_base'):
                exp=next(t['native_expression'] for t in nm['selection']['traces'] if t['quantity_id']==name)
                refdata[:,names.index(name)+1]=pchip(n['axis'],n['traces'][exp],times)
            ci=recovery_index(data,names,rate);ri=recovery_index(refdata,names,rate)
            checks.append(check('recovery',None if ci is None or ri is None else abs(ci-ri),1,'samples',reason=f'C++ index={ci}; reference index={ri}; sustained 10 ms'))
    def state(cc):
        if any(c['status']=='failed' for c in cc):return 'failed'
        if any(c['status']=='not_evaluated' for c in cc):return 'pending'
        return 'passed'
    reference_state=state(uncertainty)
    numerical_state='failed' if reference_state=='failed' else state(checks)
    outcomes=dict(reference=reference_state,numerical=numerical_state,wav='pending' if kind=='transient' else 'not_applicable',listening='pending' if case['case_id']=='listen_high' else 'not_applicable',combined='failed' if numerical_state=='failed' else 'pending' if kind=='transient' or numerical_state=='pending' else 'passed')
    reference_pass=reference_state=='passed'
    if kind=='transient':
        checks.extend(check(n,None,limit,unit,reason='Requires separately bound producer WAV evidence') for n,limit,unit in [('wav_header_grid',0,''),('wav_native_rms',1e-6,'V'),('wav_native_peak',1e-5,'V'),('wav_reference_uncertainty',1e-7,'V'),('wav_no_clipping',0,'')])
        if case['case_id']=='listen_high':checks.extend(check(n,None,limit,unit,reason='Listening export awaits automatic numerical gates') for n,limit,unit in [('wav_listening_grid',0,''),('wav_float_rms',1e-6,'V'),('wav_float_peak',1e-5,'V'),('wav_filter_response',.01,'dB'),('wav_pair_level',.1,'dB')])
    report=dict(schema_version=1,comparison_id=run['run_id'],case_id=case['case_id'],physical_case_sha256=case['physical_case_sha256'],inputs=dict(case_sha256=sha256(run_dir.parent/'case.json'),run_sha256=sha256(run_dir/'run.json'),validator_sha256=validator_hash()),execution_config=run['execution_config'],
                reference_qualification=dict(status='passed' if reference_pass else 'failed',nominal=reference_id(nominal_dir,nm),refined=reference_id(refined_dir,rm),settings=dict(nominal=ns,refined=rs,target_rate_Hz=rate if kind=='transient' else None),checks=uncertainty),
                reconstruction=dict(method='PCHIP without extrapolation' if kind=='transient' else 'native grid',alignment='physical timestamps; no fitting'),checks=checks,artifacts=[],outcomes=outcomes)
    if kind=='ac':report['reconstruction']['bode_masked_frequencies_Hz']=[float(f) for f,v in zip(n['axis'],nv) if abs(v)<1e-6]
    if reference_session is not None:reference_session.verify()
    output.mkdir(parents=True)
    if kind=='transient':
        from matplotlib.figure import Figure
        fig=Figure(figsize=(10,5));ax=fig.subplots();stride=max(1,len(data)//10000);ax.plot(data[::stride,0],data[::stride,col]-ref[::stride]);ax.set(xlabel='Time (s)',ylabel='C++ minus native (V)');fig.savefig(output/'residual.png')
        report['artifacts'].append(dict(path='residual.png',sha256=sha256(output/'residual.png'),status='generated',reason='Decimated display only; metrics use full data'))
    validate_schema('report',report);atomic_json(output/'report.json',report)
    failures=[c for c in uncertainty+checks if c['status']!='passed']
    (output/'report.md').write_text(f"# {case['case_id']} at {rate} Hz\n\n"+str(outcomes)+'\n\n'+ '\n'.join(f"- {c['id']}: {c['status']}; {c['value']} {c['unit']}; limit {c['limit']}" for c in failures)+'\n')
    return report
