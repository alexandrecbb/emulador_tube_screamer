"""Bound 10/20 uV physical-case pairs and measure resolved fundamental gain."""
import numpy as np
from .artifacts import load_json,atomic_json
from .persist import consume_reference,check,validate_schema,publish_report
from .reconstruct import pchip
from .metrics import spectrum
from .simulator import sha256


def qualify_pair(suite_dir,condition,rate,config):
    documents=[];measurements=[]
    for amplitude in ('010','020'):
        physical=suite_dir/f'linear_{condition}_a{amplitude}uv';target=physical/str(rate);case=load_json(target/'case.json');run=load_json(target/'run/run.json')
        report_dir=target/'comparison';report=load_json(report_dir/'report.json')
        if report['outcomes']['reference']!='passed':raise ValueError('Unqualified linearity reference')
        nm,nq,n=consume_reference(physical/'nominal',config);rm,rq,r=consume_reference(physical/'refined',config)
        data=np.memmap(target/'run/traces.f64le',mode='r',dtype='<f8',shape=tuple(run['trace']['shape']));t=data[:,0];w=next(w for w in case['analysis']['windows'] if w['role']=='steady');mask=(t>=w['start_s'])&(t<w['stop_s']);times=t[mask]
        expression=next(q['native_expression'] for q in nm['selection']['traces'] if q['quantity_id']=='output')
        nv=pchip(n['axis'],n['traces'][expression],times);rv=pchip(r['axis'],r['traces'][expression],times);cpp=np.asarray(data[mask,case['trace_columns'].index('output')])
        f=case['stimulus']['frequency_Hz'];peak=case['stimulus']['peak_V'];fund=lambda a:spectrum(a,rate,f)[0]
        c=fund(cpp);v=fund(nv);unc=abs(fund(nv-rv))
        # Coherent adjacent-bin leakage bounds estimator resolution conservatively.
        for a in (cpp,nv):
            fft=2*np.fft.rfft(a)/len(a);k=round(f*len(a)/rate)
            unc=max(unc,float(max(abs(fft[[k-2,k-1,k+1,k+2]]))))
        measurements.append(dict(cpp=c/peak,reference=v/peak,uncertainty=float(unc),minimum_signal=float(min(abs(c),abs(v)))))
        documents.append((report_dir,report))
    a,b=measurements
    checks=[check('linearity_cpp',float(abs(a['cpp']-b['cpp'])/abs(a['cpp'])),.001,'relative'),check('linearity_reference',float(abs(a['reference']-b['reference'])/abs(a['reference'])),.001,'relative')]
    for i,m in enumerate(measurements):checks.append(check(f'linearity_estimator_{i}',m['uncertainty']/m['minimum_signal'] if m['minimum_signal']>0 else None,.1,'relative',reason='At least 20 dB above combined estimator/reference uncertainty'))
    for directory,report in documents:
        report['checks']=[c for c in report['checks'] if c['id']!='linearity']+checks
        numeric=[c for c in report['checks'] if not c['id'].startswith('wav_')]
        report['outcomes']['numerical']='failed' if any(c['status']=='failed' for c in numeric) else 'pending' if any(c['status']=='not_evaluated' for c in numeric) else 'passed'
        report['outcomes']['combined']='failed' if report['outcomes']['numerical']=='failed' else 'pending'
        publish_report(directory,report)
    return checks
