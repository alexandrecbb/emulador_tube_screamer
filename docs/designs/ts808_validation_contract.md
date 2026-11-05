# TS808 offline MVP: grouped validation contract

* **Author:** Project owner and Codex
* **Date:** 2026-10-31
* **Status:** Approved by the owner on 2026-10-31 (T18). The electrical fixtures, finite matrix, transient/recovery extensions and WAV/ABX protocol below are accepted design requirements around T8. No test or listening session has run. Historical proposal wording below is superseded by this approval.

## Electrical and control conditions

Propose a deterministic fixed-temperature baseline at 25 degrees C, with explicit device-model nominal temperature consistent with the parameter sources. Retain ideal 9 V supply, physical bias/supply RC and the approved static effect-on switch equivalents. No random component tolerance, stochastic noise or temperature drift is added to the baseline. These are scoped test conditions, not claims that physical noise or variation is absent.

Use a 1 kOhm external resistive source impedance and 1 MOhm external resistive output load for the mandatory baseline. These are fixtures outside the pedal's own components, not replacements for its input resistor or output bias/load network. Source amplitudes below refer to the generator before that source impedance and are peak volts, not RMS or dBFS. Additional source/load sweeps are later exploratory cases, not hidden degrees of freedom in fitting the null.

Express controls as resistance-track wiper fractions in [0,1], with orientation mapped explicitly from the selected schematic. This is not a claim about the original pots' mechanical/audio/EQ tapers. Use fractions 0, 0.5 and 1 for the 27 DC/Bode corner/center combinations. Preserve exact circuit constraints at ideal endpoints; do not replace zero-ohm segments with a guessed finite resistance. The terminal map/stamping strategy must handle those shorts consistently in both implementations and retain fixed core dimensions.

## Rates and reference reuse

The [owner-approved substep revision of 2026-11-04](ts808_substep_revision.md)
permits circuit integration at 768 kHz with output grids 192/384 kHz (4/2 explicit
trapezoidal substeps). Both rates must be recorded. Historical strict-rate
failures remain failed; new executions have distinct identities and require
fresh comparisons. Separately identified single-step768 kHz runs remain
diagnostics. Any required case that fails in the claimed execution configuration
remains failed in that configuration.

A dense LTspice reference for one continuous physical case may serve both target C++ rates if it satisfies the stricter step/uncertainty requirement and preserves the same physical-case identity. For a shared 8x-qualified nominal reference, maxstep is at most (1/384000)/8, with half-maxstep and tighter-tolerance runs for uncertainty qualification. Preserve rate-specific reconstruction/report identities. Do not rerun an identical reference merely because the target grid changes, or reuse one whose physical stimulus/load/model differs.

Save only the declared comparison node/state set for long transient runs. Perform a pilot on center, maximum-drive and overload cases before the full matrix; report actual reference point counts, execution time and storage. Compression remains disabled. A small maxstep can produce large RAW files, and adaptive stepping may use smaller intervals still; do not promise a resource bound from the sample rate alone.

## Required cases

### DC and small-signal response

For all 27 Drive/Tone/Volume fraction combinations, compare the loaded DC operating point and Bode responses over 301 frequencies f_k = 20 * 10^(k/100) Hz for k=0..300. Use the T8 voltage/magnitude/phase limits. At |H_reference|<1e-6 V/V, replace magnitude/phase limits with absolute complex-response error ≤1e-6 V/V, and report the masked phase rather than a meaningless angle. Freeze that rule before runs.

The Bode gate concerns the discrete-time model at its actual processing rate against LTspice's physical small-signal response at the same frequency. A continuous-equation C++ AC comparison may diagnose stamping/model errors, but cannot stand in for the discrete-time gate. Derive the discrete response from the linearized trapezoidal recurrence or its equivalent bilinear frequency mapping, retaining the algebraic port constraints. Do not warp the LTspice comparison frequency to hide digital frequency error.

Verify small-signal linearity with four additional transient pilot cases: Center and High drive (defined below), each at 1000 Hz and generator peaks 10 uV/20 uV. Require the normalized fundamental responses at the two levels to differ by ≤0.1%, with the measured fundamental at least 20 dB above its numerical/estimator uncertainty. Use the same warm-up/window as the tone cases. If the condition fails, mark linearity qualification failed and define a revised case explicitly; do not choose an amplitude afterward simply to minimize C++/reference error. These spot checks supplement the exact infinitesimal linearization and device-Jacobian tests; they are not an exhaustive physical linearity claim for every node/frequency.

### Steady tones and null/harmonics

Use these operating sets:

* **Center:** Drive=0.5, Tone=0.5, Volume=0.5.
* **High drive:** Drive=1, Tone=0.5, Volume=1.
* **Tone edges:** Drive=1, Tone=0 or 1, Volume=0.5.

For Center and High drive, test 82, 440, 1000 and 5000 Hz at 0.01, 0.1 and 0.5 V peak: 24 physical cases. Add Tone-edge cases at 82 and 5000 Hz, 0.1 V peak: 4 more. Generate an analytic sine with a declared 5 ms raised-cosine onset envelope, initialize from DC at t=0, and use 0.5 s warm-up plus a 0.5 s steady analysis window. These frequencies are coherent over that window at both target sample rates.

Apply both T8 relative null gates, with absolute near-silence rules, to the steady window. Compute harmonics only through 20 kHz using coherent FFT amplitudes and identical bandwidth. Use THD = sqrt(sum of selected harmonic powers)/fundamental amplitude, with the DC term excluded. Define the reference floor as the larger of the measured estimator/reference uncertainty floor and 1e-5 relative THD (0.001%). Below that floor, report absolute distortion and uncertainty; do not divide by an unresolved reference THD. Harmonics above −80 dBc still require their individual 1 dB checks when resolved.

Verify periodic settling by fitting a declared sinusoidal/harmonic-plus-DC basis separately to the two 0.25 s halves of the final window, using the known frequencies and ordinary least squares. This avoids pretending that 82 Hz has an integer number of cycles in each half-window. Require complex fundamental response change ≤0.1% relative to the full-window fundamental, DC change ≤10 uV, and THD change ≤1% where above the declared floor. This fitting is only a settling diagnostic; never subtract it or use it to align/repair the null. If the waveform is not settled, report the steady measurement as unqualified and create an explicitly revised longer-duration case rather than silently changing its analysis window. No finite warm-up alone guarantees settling.

Add one muted-volume case at Drive=0.5, Tone=0.5, Volume=0, 1000 Hz and 0.5 V peak, with the same timing and absolute near-silence rules. Add an unchanged-input DC hold at Center, zero signal for 0.2 s; propose drift limits of 1 uV for declared voltage states/nodes and 1 nA for auxiliary current states relative to the committed initial equilibrium.

### Signal onset and overload recovery

Retain full onset traces from the tone cases. Add two overload cases at Center and at Drive=1/Tone=0.5/Volume=0.5. Use a 1 kHz, 2 V peak burst active from 0.1 to 0.2 s, with 5 ms raised-cosine rise/fall edges, total duration 1.5 s and zero input before/after. These are stress conditions rather than a claim that every input level is within the physical macromodel's validated range.

Propose applying the same T8 null limits over each fixed 20 ms window across onset/overload/recovery, using the existing absolute limits when the local reference is near silence. Report the maximum local RMS/peak error and all failing windows, not just a whole-file average that could hide a short error.

Define recovery as output returning within 1 mV of its initial DC value and selected bias nodes within 10 mV, sustained for 10 ms after the burst. Compare recovery times on the common target grid: proposed error ≤one internal sample h. If reference recovery does not occur within the declared duration, classify recovery timing as unqualified and revise the test explicitly; do not invent a passing recovery time.

The mandatory transient set therefore has 28 tone cases, four low-amplitude linearity cases, one mute case, one DC hold and two overload cases: 36 physical cases, each tested at both target C++ rates. The DC/Bode set is separate and comparatively small. Reference refinement and finer-grid pilots add runs; this is not a measured CPU/storage estimate.

## Parallel WAV and ABX protocol

Retain numerical traces as the primary truth path. For parallel output WAV checks, propose a fixed calibration of 8 V per full scale, identical for the paired C++/reference audio output, with explicit encoding, rate and clipping rejection. Record any DC removal and playback gain; never normalize files independently to improve the null. Native LTspice WAV export remains independently qualified against the numerical-node path.

Produce matched, band-limited 48 kHz listening pairs after the numerical path is qualified. Proposed common offline filter: a linear-phase FIR of length 128M+1 at input rate 48000M, cutoff 22 kHz, Kaiser window beta=8.6 and unit DC normalization, followed by decimation by M, using the documented [SciPy firwin interface](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.firwin.html). Record the generated coefficient hash. Qualify magnitude ripple ≤0.01 dB through 20 kHz and stopband rejection ≥80 dB from 24 kHz; a filter failing those measured conditions cannot qualify the listening pair merely because its recipe was followed. Compensate the known delay identically and use only an interior window with complete filter support, without padded edge transients or fitted time alignment. Require paired playback levels within 0.1 dB under the common calibration; do not independently normalize away a measured model-gain difference. This is an offline listening filter, not the future plugin's selected oversampling filter or latency claim.

Propose one predeclared primary listening condition: Drive=1, Tone=0.5, Volume=0.5. The synthetic source is three nonoverlapping 0.8 s decaying notes at 110/220/440 Hz, with attacks at 0.1/1.1/2.1 s. At each note's local time tau, use sin(2 pi f tau)+0.3 sin(4 pi f tau)+0.1 sin(6 pi f tau), multiply by exp(-tau/0.25), and apply 5 ms raised-cosine attack/release envelopes. Use the fixed voltage coefficient 0.5/1.4 V, making 0.5 V an upper bound rather than per-file fitted peak normalization. Duration is 3.5 s; freeze the formula/identities in the case manifest before trials. Numerical/WAV qualification also applies to this additional physical case. Use 20 randomized, concealed ABX trials per listener with no interim score. Record the seed/assignment separately from blinded presentation; analyze an exact one-sided binomial test against p=0.5, alpha=0.05, through [SciPy binomtest](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html). If multiple conditions/listeners form one confirmatory family, apply a predeclared Holm correction across that family rather than presenting uncorrected selective results.

An above-chance result triggers an open discrepancy to investigate before accepting the combined validation result; a nonsignificant result does not prove equivalence. Record numerical acceptance, WAV qualification and listening outcome separately. Completion requires a human participant and cannot be simulated by the agent. An unperformed ABX leaves combined MVP validation pending even if numerical acceptance passed. A statistically unresolved result is reported as such, without an inaudibility claim; the procedural record is distinct from physical/perceptual equivalence.

The listening source adds one physical case beyond the 36 core transient cases. Expected artifact availability and the blind session are tracked separately. This protocol is approved in T18; it does not introduce a requirement to capture or upload real guitar audio.

## Required plan additions

The selected matrix requires `include/ts808/linear_response.hpp`, `src/linear_response.cpp` and `tests/linear_response.cpp` for continuous/discrete small-signal diagnostics; `validation/ts808_validation/abx.py` and `validation/tests/test_abx_protocol.py` for deterministic artifact/trial/statistical handling; and explicit fixture/case names in the final case manifest. These are planned files only, not created code.

## Owner approval boundary

The owner approved the electrical fixtures, finite matrix, time-domain/recovery extensions, small-signal/settling checks and listening protocol together with the instruction "Aprovo T18". The already accepted T8 limits are not relaxed. Reference/device equations, parameters and on-resistance provenance remain a separate model-data contract; this approval does not invent them. The final case file will expand the formulas and identifiers exactly, not select new test conditions during implementation. Approval of the validation design is not evidence that the model, reference, WAV path or ABX has passed.

## Executable WAV qualification and listening grid

Remediation A-002 / IMP-002 (2026-11-01). These rules resolve the previously unspecified grid/error/window choices above. All named checks are mandatory report checks with measured value, unit, limit, status and reason; unavailable evidence is not_evaluated and cannot qualify WAV output.

For every mandatory transient physical case (including `listen_high`), independently export native signed PCM32 mono at 192000 and 384000 Hz. Each native export uses the matching numerical reference request/settings and the isolated `output/8` alias. Export exactly N=duration_s*rate_Hz frames at timestamps t_n=n/rate_Hz, n=0..N-1; the numerical endpoint at duration_s is excluded. Check `wav_header_grid`: actual PCM format tag, 32-bit depth, one channel, declared rate and exact N, with no origin offset or inferred shift. Header/count mismatch fails, rather than truncating/padding to match. Producer files/hashes/settings are bound to the report. DC/AC have no mandatory WAV export.

Decode signed PCM32 q to volts as 8*q/2^31. Reconstruct the qualified original numerical `output` RAW onto precisely these timestamps with the existing PCHIP/no-extrapolation/discontinuity rules. Use all frames [0,duration_s), including onset and recovery, retaining DC. Let e be decoded voltage minus reconstructed voltage. `wav_native_rms` requires sqrt(mean(e²)) <= 1e-6 V; `wav_native_peak` requires max(abs(e)) <= 1e-5 V. Also apply those same limits separately in every complete consecutive 20 ms window starting at zero and the final shorter remainder, recording the worst window. These are export-path gates, separate from C++ circuit T8 gates. Nominal/refined reconstructions must themselves differ by at most 1e-7 V RMS and 1e-6 V peak on this grid (`wav_reference_uncertainty`), in addition to existing reference requirements. This uncertainty is not subtracted from waveform error.

`wav_no_clipping` rejects nonfinite samples, any numerical calibrated magnitude >=1, and any decoded integer at either PCM endpoint (-2^31 or 2^31-1); float32 output requires abs(sample)<1 as well. No limiting, dithering, fitted gain, fitted delay or independent normalization is permitted. Out-of-range output fails qualification. Native exports at both rates are separately identified even when the dense numerical reference is shared.

For `listen_high`, reconstruct the reference on each exact C++ grid including t=3.5 s. For R=192000/384000, M=R/48000 is 4/8. Generate the existing symmetric FIR h with length L=128M+1 and group delay D=64M input samples. Define centered output y[k]=sum(h[j]*x[k*M+D-j], j=0..128M); this fixes delay compensation and decimation phase zero relative to physical t=0. Retain exactly k=64..167935 inclusive, representing [64/48000,3.5-64/48000) s, with 167872 mono frames at 48000 Hz. At 192 kHz D=256 and L=513; at 384 kHz D=512 and L=1025. Every retained output uses complete original support. Both pairs have identical physical timestamps and frame counts. No padding, resampled offset, fitted alignment or endpoint expansion is allowed.

Retain DC throughout reconstruction/filtering/export; `dc_removal` is explicitly `none` and playback gain is 1. Divide filtered volts by 8 once and encode IEEE float32 mono (`wav_listening_grid`). Decode and compare separately against each path's own pre-encoding filtered voltage on the retained interval: `wav_float_rms` <=1e-6 V and `wav_float_peak` <=1e-5 V. Record coefficient hash, R/M/L/D, k range, physical interval, scale, encoding and gain in `report.reconstruction` under `wav` with those exact field names (`input_rate_Hz`, `decimation`, `fir_length`, `delay_samples`, `first_k`, `stop_k`, `start_s`, `stop_s`, `scale_V_per_FS`, `encoding`, `playback_gain`, `dc_removal`, `coefficient_sha256`). Preserve the existing filter-response and paired level checks as `wav_filter_response` and `wav_pair_level`; level means 20*log10(RMS_cpp/RMS_reference) on retained decoded voltages, absolute value <=0.1 dB, without correcting it. Zero RMS makes this listening condition unqualified. Each target-rate pair must pass; ABX uses the predeclared 384 kHz-derived pair, and 192 kHz remains separate qualification evidence.

`test_wave_audio.py` must cover analytic DC, coherent tone and impulse arrays with independently calculated PCM/float quantization bounds; wrong rate/channel/count/format, origin/phase shifts, corrupted/clipped and nonfinite input; independent direct-convolution verification of the exact retained indices at both rates; DC preservation, no padded edges, failing numerical limits and local-window failures hidden by whole-file RMS. Retain native producer-generated PCM32 fixtures at both rates with actual headers/hashes plus original matching numerical RAW/log and generation recipes in the fixture README. Synthetic fixtures test mechanics only; native export qualification requires real selected-producer output. No such outputs or successful measurements are claimed by this specification.
