"""Original binary precision and explicit plot/step selection via spicelib."""
from pathlib import Path
import re
import mmap
import numpy as np
from spicelib import RawRead

MAPPED_RAW_THRESHOLD = 64*1024*1024


def validate_native_values(values):
    if not np.isfinite(values).all():
        raise ValueError('Nonfinite native data')
    # Observed failed native DC solves can report success with finite 1e200 V.
    # Such magnitudes are impossible for this frozen 9 V circuit and its stimuli.
    if np.any(np.abs(values)>=1e100):
        raise ValueError('Unphysical native magnitude: invalid operating point')


def read_native(raw_path: Path, log_path: Path, *, analysis_kind: str,
                trace_names: list[str], plot_index: int = 0, step_index: int | None = None):
    if not log_path.is_file():
        raise ValueError('Missing native log')
    log = log_path.read_text(encoding='utf-8', errors='strict')
    if ('Total elapsed time:' not in log or 'Simulation Failed:' in log or 'ERROR:' in log
            or '.option solver should' in log or 'Singular matrix:' in log or 'skipping operating point for Transient' in log):
        raise ValueError('Incomplete or failed native log')
    with raw_path.open('rb') as stream:
        prefix = stream.read(1024*1024)
    # The qualified producer emits UTF-16LE headers and uncompressed binary payloads.
    marker = 'Binary:\n'.encode('utf-16-le')
    split = prefix.find(marker)
    if split < 0:
        raise ValueError('Unqualified or absent RAW binary header')
    header = prefix[:split].decode('utf-16-le')
    fields = dict(re.findall(r'^([^:\r\n]+):\s*([^\r\n]*)', header, re.MULTILINE))
    flags = fields.get('Flags', '').split()
    if 'double' not in flags or 'nocompression' not in flags:
        raise ValueError('Original RAW encoding is not qualified float64')
    variables = int(fields['No. Variables']); points = int(fields['No. Points'])
    width = 16 if 'complex' in flags else 8
    if points <= 0 or variables <= 0 or raw_path.stat().st_size != split+len(marker)+points*variables*width:
        raise ValueError('RAW binary length mismatch')
    reader = RawRead(raw_path, verbose=False)
    # Pinned spicelib 1.6.4 extension: preserve its parser, trace and step APIs,
    # but map binary reads instead of retaining multi-GB Python bytes objects.
    # Each NumPy buffer view retains the mapping; no global monkey patch is used.
    mapped = raw_path.stat().st_size >= MAPPED_RAW_THRESHOLD
    if mapped:
        with raw_path.open('rb') as stream:
            mapping = mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ)
        def mapped_read(stream, length):
            start = stream.tell()
            if length < 0 or start+length > len(mapping):
                raise ValueError('Truncated mapped RAW read')
            stream.seek(start+length)
            return memoryview(mapping)[start:start+length]
        for plot in reader._plots:
            plot._read_bytes_from_file = mapped_read
    for plot in reader._plots:
        plot.read_trace_data(trace_names)
    plots = reader.get_plot_names()
    if len(plots) != 1 or plot_index != 0:
        raise ValueError('Unsupported or ambiguous plot selection')
    expected = {'dc': 'Operating Point', 'ac': 'AC Analysis', 'transient': 'Transient Analysis'}[analysis_kind]
    if plots[plot_index] != expected:
        raise ValueError('Wrong analysis plot')
    if analysis_kind == 'ac' and 'complex' not in flags:
        raise ValueError('AC reference must preserve complex values')
    steps = list(reader.get_steps())
    stepped = 'stepped' in flags
    if (stepped and step_index is None) or (not stepped and step_index is not None):
        raise ValueError('Explicit step required only for stepped data')
    step = step_index if stepped else 0
    if step not in steps:
        raise ValueError('Unknown step')
    actual_names = reader.get_trace_names()
    if len(trace_names) != len(set(trace_names)) or any(n not in actual_names for n in trace_names):
        raise ValueError('Missing or duplicate trace selection')
    arrays = {n: np.asarray(reader.get_wave(n, step)) for n in trace_names}
    cached_axis=None
    if mapped and 'fastaccess' not in flags and not stepped:
        payload=np.ndarray((points,variables),dtype='<c16' if width==16 else '<f8',buffer=mapping,offset=split+len(marker))
        cached={name:np.empty(points,dtype=arrays[name].dtype) for name in arrays
                if raw_path.stat().st_size<=256*1024*1024 or name.lower() in ('v(output)','v(vref)','v(input_base)','v(output_base)')}
        cached_axis=np.empty(points,dtype=np.float64) if analysis_kind!='dc' else None
        indices={name:actual_names.index(name) for name in cached}
        # Read bounded row buffers sequentially. DrvFS page faults for a huge
        # strided mmap are much slower than these 64 KiB reads, and can pin
        # several GB in the guest. Spicelib still owns parsing/trace selection.
        with raw_path.open('rb',buffering=0) as stream:
            stream.seek(split+len(marker))
            for start in range(0,points,65536):
                stop=min(start+65536,points)
                block=np.empty((stop-start,variables),dtype='<c16' if width==16 else '<f8')
                target=memoryview(block).cast('B');position=0
                while position<len(target):
                    read=stream.readinto(target[position:position+65536])
                    if not read:raise ValueError('Truncated native row buffer')
                    position+=read
                validate_native_values(block)
                for name,column in indices.items():cached[name][start:stop]=block[:,column]
                if cached_axis is not None:cached_axis[start:stop]=np.abs(block[:,0].real) if analysis_kind=='transient' else block[:,0].real
        arrays.update(cached)
    else:
        for a in arrays.values():validate_native_values(a)
    axis = None
    if analysis_kind != 'dc':
        axis = cached_axis if cached_axis is not None else np.asarray(reader.get_axis(step)).real
        if len(axis) < 2:
            raise ValueError('Nonmonotone native axis')
        for start in range(0,len(axis),65536):
            block=axis[max(0,start-1):start+65536]
            if not np.isfinite(block).all() or not np.all(np.diff(block)>0):
                raise ValueError('Nonmonotone native axis')
    if mapped:
        # Keep only arrays used for comparison resident; all other views can
        # fault their original read-only bytes back in on explicit diagnostic use.
        if axis is not None and cached_axis is None:axis=axis.copy()
        mapping.madvise(mmap.MADV_DONTNEED)
    return dict(axis=axis, traces=arrays, encoding='complex128le' if width == 16 else 'float64le',
                plot_name=expected, step_index=step_index, point_count=points,
                dc_solver='direct' if 'Direct Newton iteration succeeded' in log else 'pseudo_transient_level_2' if 'Pseudo Transient level 2 succeeded' in log else 'pseudo_transient' if 'Pseudo Transient succeeded' in log else 'unqualified')
