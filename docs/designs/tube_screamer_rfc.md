# Tube Screamer circuit-model audio plugin

* **Author:** Project owner and Codex
* **Date:** 2026-10-31
* **Status:** Local RFC, published 2026-10-31. MVP scope and staging approved; architectural proposals and numerical gates remain open.

## Overview

Build a C++ audio plugin for VST3 and CLAP using JUCE, for a guitarist monitoring through a DAW. Model selected TS808 and TS9 circuits through component equations, including BJT buffers, silicon feedback diodes, capacitors, resistors, Drive/Tone/Volume and a nonideal op-amp behavioral model. This is a new implementation: the reviewed repository contained only the concept brief.

**Accepted constraints:** SPICE numerical reference; null, Bode, THD and ABX validation; 48 kHz base rate; modern Ryzen 7-class desktop; one to four instances; 64/128-sample buffers; compare 4x/8x internal processing; below 5% CPU per instance as an incompletely specified target; zero added latency if feasible, otherwise below 1 ms; component customization with reproducible resistor tolerances. Preserve BJT buffers. Do not model the JRC4558's internal transistor topology.

**Proposals are not accepted decisions.** Solver choice, exact circuits/devices, platforms, voltage calibration, numerical thresholds, supported substitutions, release licensing and user workflow remain open. The initial nominal op-amp targets are 3 MHz gain-bandwidth product and 1 V/us slew rate, not verified characteristics of every historical device at 9 V.

**Owner-approved staging (2026-10-31):** The MVP is the classic stock TS808 circuit processed offline with test signals and compared against LTspice. Validate mathematical and physical model agreement first, then optimize the validated base model and solver for real-time use. Expand to TS9 and classic modifications only after the base passes agreed accuracy and runtime gates. This approval establishes scope and order; it does not select a solver or accept the tentative numerical thresholds below. “100%” means passing an explicit finite validation contract, not zero numerical error or proof of equivalence to every physical pedal.

## Analysis

### Circuit definition and coupling

Freeze one schematic revision per pedal, pot tapers/end stops, device-model files, component values, temperature, 0/9 V rails, input source impedance, output load and startup conditions. Stock antiparallel clipping is nominally symmetric; deliberate asymmetry belongs to customization. The roughly 720 Hz feedback-network transition alone does not describe the full pedal response. Use the [circuit analysis](https://www.gitec-forum-eng.de/wp-content/uploads/2019/02/poteg-10-08-05-4-tube-screamer.pdf) as a starting reference, then identify exact schematics before implementation.

Approved first milestone: a fixed classic stock TS808 reference, offline, compared against LTspice before expanding to TS9 or modified components. Optimize the validated base for real-time use before expansion. This stages the accepted destination without dropping it. Proposed supply assumption: ideal 9 V rails, with the documented bias/reference RC network included; confirm whether the user instead wants ideal Vref or supply sag. A nominal 4.5 V reference does not justify removing its impedance/dynamics silently. Noise, electronic switching/bypass circuitry and changing temperature are unresolved scope, with proposed deferral. Fixed-temperature device physics still belongs to the baseline model.

For a resistor, i=(v1-v2)/R; for a capacitor, i=C d(v1-v2)/dt. Retain coupling/bypass/feedback capacitors and their charge states. Do not split the circuit into independently filtered stages unless the intervening loading is preserved or its approximation is measured. Input/output BJT buffers affect bias, input impedance, loading and potentially distortion. Proposed baseline: documented Ebers–Moll or Gummel–Poon device equations from the reference model, including finite current gain and reverse behavior; add junction charge/Early-effect terms where required by the selected model and error tests. A fixed gain or ideal emitter follower is not the accepted BJT scope. The [ngspice manual](https://ngspice.sourceforge.io/docs/ngspice-manual.pdf) documents these device families; freeze a release/model version rather than a changing development manual.

For a junction, start from i=Is[exp(vj/(n VT))-1], VT=kT/q. Include series resistance through vterminal=vj+i Rs. For equal opposing diodes the static pair reduces to 2 Is sinh(v/(n VT)) only when series resistance and other terms are neglected. Use the actual two-device equations for substitutions. Junction capacitance, diffusion charge and reverse breakdown are model terms to retain or explicitly justify omitting against the reference, not promises that a threshold change represents another diode. Apply safe exponential evaluation and physical voltage limiting inside the numerical iteration without silently changing the converged physical solution.

### Nonideal op-amp and stiffness

Use a dominant-pole behavioral state z with finite DC gain A0: dz/dt=wp[A0(v+−v−)−z], wp=2 pi GBW/A0. Add finite input impedance, output resistance, separate positive/negative headroom and load dependence matching the chosen reference. Integrate slew limiting into the state equation, for example bound dz/dt to ±SR, and include saturation/recovery in the same coupled feedback solve. Exact limiting/anti-windup behavior is a proposed model to compare with SPICE; merely clipping the final ideal-amplifier output loses feedback dynamics.

At nominal SR=1 V/us, an internal sample spans about 5.21 V of allowed slew at 192 kHz or 2.60 V at 384 kHz. A 3 MHz unity-gain crossover lies above both internal rates; the dominant pole itself is GBW/A0, not 3 MHz. Closed-loop dynamics and algebraic feedback can still be stiff. Oversampling does not justify explicit Euler integration or resolve all continuous-time dynamics. The [manufacturer page](https://www.nisshinbo-microdevices.co.jp/en/products/operational-amplifier/spec/?product=njm4558) and linked datasheet ground initial parameters, but typical measurements at other rails do not establish exact headroom or recovery at 9 V. Fit or select a documented macromodel and declare its limits.

### Solver comparison and proposed starting point

Let x contain node voltages, capacitor/op-amp states and auxiliary currents; u is the source, p the fixed component set. A general circuit has qdot(x,p)+f(x,u,p)=0. With step h, backward Euler solves F=q(xn)−q(xprevious)+h f(xn,un)=0. Newton solves J delta=−F and updates x with bounded damping. Trapezoidal integration instead uses q(xn)−q(xprevious)+(h/2)[f(xn,un)+f(xprevious,uprevious)]=0; it can reduce error but requires checking stiff ringing. Compare convergence under smaller h; neither method guarantees agreement by name alone.

| Candidate | Mechanism | Fit and strongest objection |
| --- | --- | --- |
| Modified nodal analysis (MNA) + bounded implicit Newton | Stamp KCL/device equations and solve the coupled residual above | Direct reference correspondence; handles loading, BJTs and op-amp states. Cost, conditioning and failed convergence need measurement. |
| Reduced nonlinear state space | Eliminate linear algebraic variables; solve xdot=A x+B u+E iNL, vNL=C x+D u+F iNL | Smaller solve for a fixed topology. Elimination/model updates can be complex; nonlinear devices and stiffness remain. |
| Wave digital filters (WDF) | Use waves a=v+Rp i and b=v−Rp i, scatter connected ports and solve nonlinear junction relations | Component structure and reusable passive adaptors; active multiport feedback, BJTs and changing devices need special coupled solvers. No universal iteration-free guarantee. |

**Proposed recommendation:** start with a topology-specific implicit MNA reference prototype, backward Euler for initial stability investigation, double precision and bounded damped Newton. Then consider trapezoidal or a reduced state-space implementation if error/cost results require it. Compare all three on paper; prototype another only against a failed declared gate. Do not build three full plugins. WDF remains credible: [Werner et al.](https://www.dafx.de/paper-archive/2015/DAFx-15_submission_53.pdf) demonstrate the Tube Screamer tone/volume stage, not this entire requested nonideal model. [Esqueda et al.](https://www.dafx.de/paper-archive/2021/proceedings/papers/DAFx20in21_paper_39.pdf) provide related white-box work, not proof of the proposed performance budget.

Specify scaled voltage/current residual and step criteria, bounded iterations, bounded line search and warm starts from the last valid state. Proposed first benchmark cap: eight Newton iterations, subject to validation rather than an accuracy promise. Commit new persistent states only after a valid solution. Proposed rare-failure policy: preserve last valid state/output briefly, then bounded fade to silence and controlled restart; report repeated failure outside the audio thread. This policy itself needs audible/transient tests and owner agreement. No unbounded retries or switching secretly to an ideal model.

### Oversampling, latency and alias measurement

At 48 kHz, 4x/8x mean 192/384 kHz. All nonlinear stages, including BJTs and op-amp limiting, belong inside the oversampled circuit path. Compare JUCE polyphase IIR half-band chains for low latency and FIR as an offline comparison. Specify transition bands, passband ripple and stopband rejection separately for interpolation and decimation; choose them using measurements, not a quality label. Proposed exploration starts with 80 dB stopband rejection, then measures whether residual aliasing meets the tentative gate.

[JUCE oversampling documentation](https://docs.juce.com/master/classjuce_1_1dsp_1_1Oversampling.html) describes its filters and latency API. Constructor factor is an exponent: 2 selects 4x, 3 selects 8x. Initialize storage before playback. Measure returned latency, integer/fractional compensation, impulse response and frequency-dependent phase/group delay. Minimum-phase filters have delay; a single host-reported delay cannot remove all phase distortion or nonlinear circuit memory. Below 1 ms means fewer than 48 base-rate samples under the agreed latency definition, excluding interface/host buffers. Define whether that gate uses explicit pipeline delay or a specified impulse/phase measure; report both.

Proposed alias protocol: coherent tones across 80 Hz–18 kHz, two-tone stimuli and guitar transients, several voltages and Drive/Tone settings. Compare 4x and 8x with a much higher-rate reference whose rate/filter results converge. Apply matched output filtering/alignment, identify folded components separately from valid in-band harmonics, and report integrated residual plus worst spur relative to declared signal level. A broadband null alone cannot isolate aliasing from solver or filter error. Neither 8x nor 80 dB filters guarantee an alias-free result.

### Runtime, architecture and reproducible state

Keep a host-independent C++ circuit core and offline measurement harness; JUCE handles host parameters, audio buffers, state and oversampling where suitable. Proposed CLAP route: [clap-juce-extensions](https://github.com/free-audio/clap-juce-extensions), verified in a minimal CMake build for the chosen JUCE revision and target hosts before commitment. VST3 and CLAP need matched parameter meanings and preset sound, plus independent discovery/automation/state tests. Platform and host matrix remain open.

License inventory checked against primary files on 2026-10-30: [JUCE](https://github.com/juce-framework/JUCE/blob/master/LICENSE.md) offers AGPLv3 or a commercial license; current [VST3 SDK](https://github.com/steinbergmedia/vst3sdk/blob/master/LICENSE.txt), [CLAP](https://github.com/free-audio/clap/blob/main/LICENSE) and [CLAP JUCE extension](https://github.com/free-audio/clap-juce-extensions/blob/main/LICENSE.md) show MIT terms. This does not select a distribution license. Pin versions, inspect bundled SDKs/submodules, preserve required notices, verify device-model redistribution and settle the JUCE licensing path before distributing binaries. Do not assume older bundled SDKs have current upstream terms.

The 64/128-sample callback intervals are about 1.33/2.67 ms for the entire host. At 8x four serial 64-sample instances need 2,048 internal circuit advances before iterations/filtering. Freeze exact Ryzen model, OS, DAW/version, power configuration, compiler/build flags and channels. Report average and high-percentile block time, observed maximum, deadline overruns and iteration/failure counts, alongside the host CPU meter. Proposed engineering screen: the four-instance chain consumes at most 50% of the callback interval in observed stress runs, leaving host margin; this is tentative and does not prove a hard real-time bound or define the requested 5% meter target.

Preallocate, avoid locks, file/network operations and memory allocation in callbacks; bound all solver work, handle nonfinite values and denormals. Prepare coefficient/device replacements off-thread, transfer ownership safely and reclaim away from audio. Continuous Drive/Tone/Volume automation needs defined smoothing and sample timing. Proposed initial restriction: structural substitutions and oversampling changes require stopped playback; do not quietly treat that as owner-approved. If live switching is required, benchmark state mapping or crossfade peak cost, including both simultaneous models.

Persist state schema/model versions, stable parameter IDs, controls, oversampling, exact realized resistor/component values, seed and generator identity, device models and calibration. Rerandomize only by explicit action, never per block or on session load. Define legal distributions, bounds and correlations; exact same-version/platform replay should be deterministic, with cross-platform numerical tolerance declared. Future state must fail visibly and preserve the original rather than silently change sound. Model corrections need an explicit compatibility/version policy before public release. No existing sessions require migration today.

Proposed UX: load one named stock model, adjust three stock controls, optionally enter a bounded customization panel, and restore stock values explicitly. Open decisions include model-switch knob preservation, mono/stereo layouts, bypass/tail behavior, initial controls, input/output gain calibration in volts per full scale, quality ownership and status display. CPU-only diagnostics use bounded local counters. Offline tools expose named circuit/DC/state traces and save manifests, stimuli, event timelines, reference/output/residual files. User audio capture is opt-in; remote telemetry is unnecessary.

### Validation and tentative acceptance gates

Freeze SPICE tool/version, netlist, device models, voltage calibration, source/load, temperature and operating point. Tighten transient timestep/tolerances until reference changes are comfortably below the proposed model-error gate. Save node-level bias and stage measurements before full-pedal tests. Test stock and supported substitutions, controls at 0/50/100% and selected combinations, tones/transients/silence/DC offsets, startup, overload/recovery, automation and state recall. Keep the mandatory matrix finite and exploratory sweeps separate.

Circuit-only null tests use identical input and sample times at internal rate, without unmatched resampling filters. End-to-end null tests include matching interpolation/decimation or explicitly report their difference. Align known delay/clocks and fixed voltage gain calibration; report any compensation. Do not use arbitrary EQ, gain fitting or time warping to hide circuit errors. Report residual RMS/peak against input/output reference levels and separate startup/steady state.

The following numbers are **proposed discussion targets, not accepted requirements or measured achievements**:

| Check | Proposed initial gate and method |
| --- | --- |
| DC bias | Key node errors ≤10 mV against the same reference; tighter checks where sensitivity requires. |
| Small-signal Bode | 20 Hz–20 kHz; ≤0.2 dB magnitude and ≤2 degrees phase error after declared pipeline-delay handling; identify frequency bins near nulls separately. Use perturbations small enough to verify linear scaling at each operating point. |
| Circuit-only steady null | Residual RMS ≤−60 dB relative to reference RMS, peak ≤−40 dB relative to reference peak, for declared nonsilent cases; use absolute volts near silence. Assess startup/overload separately. |
| THD/harmonics | Coherent tones at 82/440/1000/5000 Hz and several input voltages; same bandwidth/window/harmonic set. Individual harmonics above −80 dB relative to fundamental within 1 dB; THD relative error ≤5% where above a declared numerical floor. Report THD+N separately. |
| Aliasing | Folded energy ≤−80 dB relative to output RMS over declared audible analysis band, plus worst-spur report; specify window/reference leakage floor. Revisit against CPU/latency and listening evidence. |
| Runtime/reliability | Requested below-5% meter target only after its definition; proposed 50% four-instance timing screen; zero observed failures/dropouts in a declared stress duration is evidence, not proof of universal convergence. |
| Latency | Accepted zero if feasible, otherwise <1 ms; measurement definition and filter implementation still open. |

Proposed ABX protocol: matched files within 0.1 dB, identical playback alignment, randomized concealed identities, fixed stimuli/conditions and 20 trials per listener/condition. Predeclare exact binomial analysis and multiple-comparison handling; 15/20 has one-sided chance probability about 0.0207 before correction. A failure to reject chance is not proof of inaudibility or equivalence; use confidence intervals/power planning and trained listeners if making a perceptual claim. Compare the numerical reference first; hardware testing is separate and needs calibrated capture. No listening claim replaces numerical checks.

## Goals vs. Non-Goals

* **In-Scope Goals (accepted):** TS808/TS9 component circuit models; BJT buffers; nonideal external-behavior op-amp; Drive/Tone/Volume; reproducible customization; C++/JUCE VST3 and CLAP; SPICE and listening validation; live performance targets stated above.
* **Out-of-Scope Non-Goals (accepted):** Transistor-level simulation inside the op-amp. No implementation is authorized by this brainstorm.
* **Approved MVP:** Classic stock TS808, offline test-signal processing and LTspice comparison; validate accuracy, then optimize for real-time use before TS9 and classic modifications.
* **Other proposed first-stage limits, awaiting agreement:** Finite named substitutions later; fixed temperature, ideal supply rails with explicit bias network; defer noise, supply sag and electronic switching. Stereo, platforms, live structural switching and hardware matching remain open rather than silently excluded.

## Alternatives Weighed

* A static waveshaper alone is rejected as the complete solution because it loses requested component dynamics and coupled feedback. It can serve only as a diagnostic baseline.
* An ideal op-amp followed by an output clipper is rejected as the final model because requested nonideal behavior must act inside feedback.
* Naive explicit integration is rejected as the default without a stiffness/stability analysis.
* MNA/Newton is the proposed initial route; reduced state space and WDF remain conditional alternatives, not rejected designs. Do not maintain three complete implementations before one fails an agreed gate.
* A generic arbitrary-topology editor, automatic adaptive oversampling and remote telemetry are proposed deferrals; the user has not agreed these scope boundaries.
* FIR remains a comparison option; low-latency IIR is proposed for live use pending measured aliasing, phase and delay.

## Key Decisions & Staging for Next Steps

1. **Accepted:** Preserve all confirmed constraints in Overview; readiness for independent review was approved. Six independent fresh-context reviews completed; see [review report](../../goldfish_review_report.md) and [individual reports](../../goldfish_reports/).
2. **Approved stage 1 scope:** Classic stock TS808 offline, processing test signals and comparing with LTspice. Next design work must freeze exact reference, voltage calibration, supply/bias scope, legal model inputs and acceptance matrix. Implicit MNA remains a proposed implementation route; no code has been requested or written in this brainstorm.
3. **Approved stage 2 objective:** Optimize the validated base model and solver for real-time operation before expanding variants. Proposed method: measure 4x/8x, filters and solver cost against the same reference and fixed hardware budget. Revise/reduce solver only from evidence; no accuracy, CPU or latency results exist yet. Re-run accuracy checks after optimization.
4. **Later scope:** TS9 and classic modifications follow successful base accuracy and runtime gates. Wrapper/host integration order remains proposed. Set state compatibility, license path and release matrix before distribution.
5. **Owner decisions needed:** exact TS808/TS9 revisions; OS/hosts/channels and Ryzen machine; volts-per-full-scale and input/load values; supply/bypass/noise/thermal scope; substitution catalog; live-change/oversampling policy; saved-model compatibility; numerical/listening gates and license/distribution route.
6. Review this synthesis before a formal design draft. The reviewers' reports identify unresolved product contracts, not an implementation-ready or validated plugin.

## Publication and design handoff

Published locally at the owner's request on 2026-10-31. This RFC records the brainstorm and approved MVP staging; publication does not approve every proposal. The evolving predecessor remains [concepts_brief.md](../../concepts_brief.md). Formal design drafting starts in [design_draft.md](../../design_draft.md).

## Owner decision addendum: initial numerical gates

During formal drafting, the owner approved the initial offline acceptance contract in decision T8 of [design_draft.md](../../design_draft.md): key-node DC error ≤10 mV; Bode magnitude/phase error ≤0.2 dB/2 degrees; steady-state relative null RMS/peak ≤−60/−40 dB; selected harmonic magnitude error ≤1 dB above −80 dBc; THD relative error ≤5% above a declared measurement floor. The draft also records absolute null limits near silence and reference uncertainty at most one tenth of the corresponding acceptance budget. Exact case matrix, measurement floors and transient/recovery limits remain open; no measurements have been performed.

The owner additionally requires LTspice reference transients with `.options plotwinsize=0`, `.options reltol=1e-6` and maximum timestep below a fraction of the internal oversampled sample period. The draft proposes h/8 as the initial bound, subject to approval and convergence qualification. Export interpolation, WAV calibration/encoding and clipping must be checked explicitly. This addendum records subsequent approval; the earlier brainstorm sections retain their original proposal status unless superseded by a specific decision.

The owner subsequently selected high-precision timestamped node data (uncompressed floating-point RAW/text) as the primary numerical reference, with WAV tests retained in parallel (T9). Reconstruction onto the C++ time grid is controlled and independently qualified by the analysis tool. A higher-order interpolator does not remove reference uncertainty automatically; the interpolation method, data precision and timestep refinement remain explicit parts of the protocol.

The selected reconstruction method is PCHIP (T10), to preserve monotonicity of the supplied data and avoid cubic-spline overshoot between monotone samples. Its error near smooth extrema and saturation/slew transitions must be measured; no error below −80 dB has yet been demonstrated. The approved aggregate reference-uncertainty budget remains in force.

The owner selected a reusable C++ circuit core with Python/NumPy/SciPy offline analysis (T11), including SciPy PCHIP reconstruction and NumPy FFT measurements. Analysis dependencies remain outside the plugin core. The selected binary RAW reader is spicelib.RawRead (T12); exact dependency versions and the interchange contract remain to be specified in the formal draft.

For binary RAW storage, the owner requires `.options numdgt=7` or higher together with `.options plotwinsize=0`. The protocol uses `.options numdgt=15`, retains `.options reltol=1e-6` and the sub-h maximum timestep, and verifies float64 dependent-variable storage during import. Casting lower-precision data to float64 is not an acceptable substitute.

The owner selected analytical device Jacobians with reuse of evaluated junction terms and explicitly required automated unit tests against numerical finite differences (T13). Selected current-law families are Shockley diodes, Ebers–Moll BJTs and the behavioral JRC4558. The full design specifies smooth-branch, boundary, charge and assembled-stamp checks; additional semiconductor effects/parameters remain a separate scope decision. No maximum-performance claim has been established by this choice.

The owner subsequently selected basic quasi-static Shockley/Ebers–Moll devices without semiconductor parasitics for the MVP, matched by explicit LTspice model parameters (T14). Internal series resistance, junction/diffusion charge and Early-effect extensions are deferred refinements. External circuit capacitors and the behavioral op-amp dynamics remain included. The simplifications define the MVP reference; their claimed physical insignificance and any stiffness reduction have not been measured. The detailed decision history is preserved in [the decision log](ts808_decisions.md).

The consolidated Technical Plan was approved on 2026-10-31, including h/8 as the initial reference maxstep bound, subject to convergence qualification. Exact circuit/model values, numerical execution constants, data/tool contracts and the remaining validation matrix must still be fixed before implementation readiness. This supersedes earlier proposal labels for h/8 only; it does not imply completed numerical validation.

The owner selected the Cerutti TS-808 redraw as the documentary reference (T15), extracting the effect-on audio and supply/bias circuit while omitting footswitch flip-flop logic. Switching-related bias/load resistors and applicable finite conducting-switch equivalents must remain explicit. The [extraction record](ts808_reference_candidate.md) identifies the source and required connectivity/loading checks; final model parameters and netlist remain to be frozen.

The owner selected Eigen within the grouped numerical execution contract (T16): fixed-size binary64 matrices after topology freezing, pivoted LU and preallocated work storage, with automated checks for processing-path allocations. Initial numerical work/tolerance settings are recorded in [the contract](ts808_numerical_contract.md) for implementation review. Header-based integration does not constitute measured proof of zero allocations or a performance advantage; both require qualification of the actual path.

Generated numerical traces use little-endian float64 binary payloads with JSON sidecars (T17), standard C++ binary stream writes and direct NumPy reading or memory mapping. The [data contract](ts808_data_contract.md) defines layout, units, integrity and failure/result semantics for the implementation section; HDF5 is not selected. Mapping is distinct from fromfile loading and does not imply an allocation-free analysis pipeline.

The owner approved the [grouped validation matrix](ts808_validation_contract.md) in T18 on 2026-10-31: fixed electrical fixtures, 27 DC/Bode combinations, 36 physical transient cases at 192/384 kHz plus the listening case, measurement floors, transient/recovery limits, calibrated WAV and a human ABX protocol. This supersedes earlier statements that these offline conditions are undecided. Numerical acceptance, WAV qualification and listening remain separate outcomes; an unperformed ABX leaves combined MVP validation pending. No measurements or listening results exist, and the future plugin's filters/runtime contract remains open.

The owner approved T19 as [revised option B](ts808_model_contract.md): the op-amp amplitude-saturation transfer has an exactly linear central region joined to smooth C1 compression knees near the headroom-adjusted output limits, with recovery feedback in the coupled solve. This replaces the original global amplitude tanh; 0 V/9 V remain supply rails and do not become the output bounds. Exact knee expressions/onsets, headroom and other missing model data remain unfrozen. The intent is continuous derivatives and easier numerical comparison; convergence and null acceptance still require tests. T1–T18 and the design-only scope remain unchanged.

The owner approved [T20-A with the shared nominal package](ts808_model_data_proposal.md) on 2026-10-31: shifted tanh only in the outer knees, C2 joins and the exact central identity, with the specified op-amp and reduced 1N914/representative 2SC1815-GR parameters and temperature preparation. This closes the earlier pending knee/nominal-data statements while preserving their source/estimate/assumption distinctions. Rational knees are unselected. Conducting-JFET resistance was excluded from T20 and remains open. No implementation or measured validation is implied.

The owner subsequently approved [T21-A](ts808_switch_resistance_proposal.md) on 2026-10-31: `R_on=383.29731360711594 Ohm` (383.30 Ohm displayed) as a constant wet-channel equivalent under the documented unit-area, 25 degrees C, `V_GS=0` and `V_DS=0` model-core assumptions. This supersedes the open-resistance statements above. Actual gate characterization is explicitly outside the MVP; no gate source or dynamic JFET is introduced. The accepted mathematical baseline is named `ts808-cerutti-reduced-v1`. Physical calibration and all numerical acceptance results remain unmeasured; numerical/tooling and final implementation-plan closure still follow before implementation.

The owner approved [T22-A and all documented common criteria](ts808_numerical_closure_proposal.md) on 2026-10-31: the fixed 31-unknown `control-branch-v1` system, exact endpoint constraints, interiors 4/6/11/5, boundary 5, physical scaling/rank/condition/backward-error criteria and the DC/API/fixture obligations. This supersedes earlier pending endpoint/dimension statements. T22-B is unselected; qualification remains unperformed.

The next grouped choice is the unapproved [T23 execution/tooling proposal](ts808_execution_tooling_proposal.md), with exact dependency/build/test candidates and either local Wine reference generation or an identified native Windows reference producer. T1–T22 remain in force; no tools were installed or production code implemented.

The owner subsequently approved **T23-B and the complete common package**, clarifying that Ubuntu is WSL 2 on the same physical Windows host. This supersedes the pending-route and manual/separate-machine-transfer descriptions above. The selected `wsl2-windows-native-v1` profile invokes native Windows LTspice through WSL/PowerShell and reads original closed RAW/log through the shared drive, preserving hashes, identities, native timeout and qualification. Wine is unselected.

The [formal implementation section](../../design_draft.md#detailed-implementation-plan) and [concrete API/schema/fixture attachment](ts808_offline_interface_spec.md) are now drafted for section review. T1–T23 remain approved; the entire implementation section is not yet approved. No tools were installed, production implementation built, native circuit simulated or acceptance result measured. Final predecessor reconciliation/publication and a separately requested design review still follow.

The owner subsequently approved the complete implementation section and attachment and authorized predecessor reconciliation on 2026-10-31. The [reconciliation record](ts808_predecessor_reconciliation.md) finds no unresolved contradiction with accepted predecessor requirements; material additions already have recorded approvals. This supersedes the pending-section/reconciliation statements above. Final publication awaits destination selection. No implementation, simulator run or final-design Goldfish review is implied.

## Final design publication

The owner confirmed the final destination on 2026-10-31. The approved and reconciled [TS808 offline design](./ts808_offline_design.md) is now saved at `docs/designs/ts808_offline_design.md`; this supersedes the pending-publication statements above while preserving the RFC as brainstorm history. T1–T23 and all sections/attachments are approved. The egm-draft workflow is complete; `egm-review` is recommended but has not started. No implementation or measured circuit/runtime/listening result is implied.
