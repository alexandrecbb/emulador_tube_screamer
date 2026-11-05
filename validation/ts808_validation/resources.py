"""Retained payload bounds for numerical references and parallel WAV exports."""
def estimate(cases, adaptive_factor=1.05):
    durations=[c['analysis']['time']['duration_s'] for c in cases if c['analysis_kind']=='transient']
    duration=sum(durations)
    numerical=duration*384000*8*256*3
    export_raw=duration*384000*8*24*2
    model=sum((round(t*r)+1)*256 for t in durations for r in (192000,384000))
    pcm=duration*(192000+384000)*4
    native=int(((numerical+export_raw)*adaptive_factor+pcm)*1.1)
    output=int(model*1.1)
    return dict(duration_sum_s=duration,minimum_numerical_reference_bytes=int(numerical),
                minimum_export_raw_bytes=int(export_raw),model_trace_bytes=model,
                pcm_payload_bytes=int(pcm),adaptive_factor=adaptive_factor,
                headroom_factor=1.1,native_required_bytes=native,output_required_bytes=output,
                estimated_required_bytes=native+output)
