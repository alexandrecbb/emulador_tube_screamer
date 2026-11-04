# TS808 offline MVP: circuit extraction and op-amp limiting contract

* **Author:** Project owner and Codex
* **Date:** 2026-10-31
* **Status:** T1–T23, the formal implementation section and interface attachment are approved. T20-A selects shifted-tanh outer knees with C2 joins and the shared nominal parameter package, within T19 revised B's exactly linear central transfer. T21-A closes the static switch nominal at `383.29731360711594 Ohm`; actual gate characterization is outside the MVP. T22-A fixes the augmented 31-unknown map/common criteria and T23-B fixes tooling/native Windows execution on the WSL host. Reconciliation and [final publication](./ts808_offline_design.md) are complete. No circuit implementation, netlist or numerical test has been created or run.

## Approved models and remaining numerical specification

The schematic identifies parts without specifying all current-law parameters. T20-A supplies the accepted nominal op-amp and reduced diode/BJT data, preserving their source/estimate/assumption distinctions. T21-A supplies the conditional static switch nominal and its approximation limits. Numerical/tooling closure and the final implementation plan remain incomplete; simulator defaults must not silently fill the remaining gaps.

T19 fixes the op-amp saturation structure: revised option B with an exactly linear center and C1 knees near the headroom-adjusted output bounds. The owner explicitly confirmed replacing the global amplitude tanh. The passive terminal audit and parameter-evidence register below make the remaining work explicit. This approval does not choose missing curve details or parameter values, or finish the Detailed Implementation Plan. The remaining model-data work will be reviewed together, rather than one constant at a time.

The owner approved [T20-A and its nominal-data contract](./ts808_model_data_proposal.md): shifted-tanh outer knees, analytical derivatives, the op-amp nominal package and reduced 1N914/representative 2SC1815-GR data with explicit temperature interpretation/source identities. Manufacturer values, derived estimates and unverified physical assumptions keep their labels. The JFET resistance was excluded from T20 and subsequently closed by T21-A as an approximation, not as physically characterized data.

The owner approved [T21-A](./ts808_switch_resistance_proposal.md): `R_on=383.29731360711594 Ohm` from the documented model-core derivation at unit area, 25 degrees C, `V_GS=0` and `V_DS=0`. The local signal-range limits and unverified physical gate behavior remain explicit. Actual gate characterization is outside the MVP and does not block its design; no dynamic JFET or ideal gate source is introduced.

### Approved mathematical model identity

Use `ts808-cerutti-reduced-v1` as the planned baseline model identifier: the Cerutti source/hash and extracted graph below, T14's reduced laws, T18's 25-degree baseline, T20-A's complete nominal vector/temperature preparation and T21-A's constant switch resistance. Control positions, source/load and stimuli remain separately identified physical-case inputs under T17; they do not silently select a different device model.

This names the approved mathematical baseline. The future component-map/device-spec/netlist bytes must have their own actual hashes once authored; no hash of a not-yet-created artifact is asserted here. Native circuit generation, parameter-copy checks, numerical qualification and final plan approval remain to be done. Physical gate calibration is not part of that MVP closure.

## Source identity and terminal audit

Use only the [Cerutti TS-808 drawing](https://generalguitargadgets.com/wp-content/uploads/ts-808.jpg) linked by [General Guitar Gadgets](https://generalguitargadgets.com/effects-projects/distortion/tube-screamer/), as selected in T15. The JPEG was retrieved again for this audit and matches SHA-256 `22ea2b084b4248a26a303557e18c8f35968bc1fa73a2a6bcf5edce0d349a12ad`. Enlarged crops were used for inspection only; they are not new circuit evidence. No dependency on the temporary inspection files enters the design.

The drawing lacks component reference numbers. The identifiers below are local design names, not original board designators. Values are transcriptions; the two independent implementations must use the same audited connections. Device parameters remain distinct from printed part labels.

### Node meanings

| Node | Meaning |
| --- | --- |
| `gnd`, `v9`, `vref` | Circuit ground, ideal 9 V rail and loaded physical bias node. `vref` is solved, not fixed at 4.5 V. |
| `generator`, `input`, `input_cap`, `input_base`, `input_emitter` | Generator before the external source resistor; input jack; input capacitor/resistor junction; input BJT base and emitter. |
| `clip_plus`, `clip_minus`, `gain_rc`, `drive_end`, `clip_out` | Clipping amplifier inputs, lower feedback RC junction, fixed-resistor/Drive junction and amplifier output. |
| `tone_in`, `tone_minus`, `tone_wiper`, `tone_rc`, `tone_out` | Tone amplifier noninverting input, inverting input, pot wiper, shelf capacitor/resistor junction and amplifier output. |
| `volume_cap`, `volume_top`, `wet_send` | Post-tone coupling capacitor/resistor junction, upper Volume endpoint and Volume wiper. |
| `dry_send`, `switch_common` | Dry branch after its coupling capacitor and joined drains of the two audio JFETs. |
| `output_base`, `output_emitter`, `output_cap`, `output` | Output BJT base/emitter, series resistor/coupling capacitor junction and output jack. |

### Passives and external fixtures

All two-terminal entries below give terminal pairs; current/voltage orientations will follow the listed order. Capacitors retain one committed voltage/current-history owner. A capacitor between known ideal-source nodes may have constrained history rather than an independent unknown.

| Local identifier | Value | Terminals | Owner / reason |
| --- | --- | --- | --- |
| `R_source` | 1 kOhm | `generator`, `input` | External fixture selected in T18; additional to the pedal's own 1 kOhm input resistor. |
| `C_input` | 20 nF | `input`, `input_cap` | Input Buffer; printed `.02uf`. |
| `R_input` | 1 kOhm | `input_cap`, `input_base` | Input Buffer. |
| `R_input_bias` | 510 kOhm | `input_base`, `vref` | Input Buffer; retain bias loading. |
| `R_input_emitter` | 10 kOhm | `input_emitter`, `gnd` | Input Buffer. |
| `C_clip_input` | 1 uF, bipolar | `input_emitter`, `clip_plus` | Clipping Amp; retained interstage load. |
| `R_clip_bias` | 10 kOhm | `clip_plus`, `vref` | Clipping Amp. |
| `R_gain_lower` | 4.7 kOhm | `vref`, `gain_rc` | Clipping Amp. |
| `C_gain_lower` | 47 nF | `gain_rc`, `clip_minus` | Clipping Amp. |
| `R_feedback` | 51 kOhm | `clip_minus`, `drive_end` | Clipping Amp. |
| `P_drive` | 500 kOhm total, printed `A` | `drive_end`, `clip_out`; wiper tied to `clip_out` | Clipping Amp; effective used-track resistance specified below. |
| `C_feedback` | 51 pF | `clip_minus`, `clip_out` | Clipping Amp; keep despite semiconductor-charge omissions. |
| `R_tone_input` | 1 kOhm | `clip_out`, `tone_in` | Tone/Volume. |
| `R_tone_bias` | 10 kOhm | `tone_in`, `vref` | Tone/Volume. |
| `C_tone_lowpass` | 220 nF, tantalum | `tone_in`, `gnd` | Tone/Volume; drawn positive terminal at `tone_in`. |
| `P_tone` | 20 kOhm total, printed `G` | Ends `tone_in`, `tone_minus`; wiper `tone_wiper` | Tone/Volume; do not replace the pot by two unrelated resistances. |
| `R_tone_feedback` | 1 kOhm | `tone_minus`, `tone_out` | Tone/Volume. |
| `C_tone_shelf` | 220 nF, tantalum | `tone_wiper`, `tone_rc` | Tone/Volume; drawn positive terminal at the wiper. |
| `R_tone_shelf` | 220 Ohm | `tone_rc`, `gnd` | Tone/Volume. |
| `C_volume_input` | 1 uF, bipolar | `tone_out`, `volume_cap` | Tone/Volume. |
| `R_volume_input` | 1 kOhm | `volume_cap`, `volume_top` | Tone/Volume. |
| `P_volume` | 100 kOhm total, printed `B` | Ends `vref`, `volume_top`; wiper `wet_send` | Tone/Volume. |
| `C_dry` | 100 nF | `input_emitter`, `dry_send` | Input Buffer; retain the inactive dry branch's load. |
| `R_dry_bias` | 510 kOhm | `dry_send`, `vref` | Input Buffer; not deleted with the flip-flop. |
| `R_switch_common_bias` | 510 kOhm | `switch_common`, `vref` | Output Buffer; the other switching-branch bias resistor. |
| `C_output_input` | 100 nF | `switch_common`, `output_base` | Output Buffer. |
| `R_output_bias` | 510 kOhm | `output_base`, `vref` | Output Buffer. |
| `R_output_emitter` | 10 kOhm | `output_emitter`, `gnd` | Output Buffer. |
| `R_output_series` | 100 Ohm | `output_emitter`, `output_cap` | Output Buffer; preserve the TS808 value. |
| `C_output` | 10 uF, electrolytic | `output_cap`, `output` | Output Buffer; drawn positive terminal at `output_cap`. |
| `R_output_shunt` | 10 kOhm | `output`, `gnd` | Output Buffer; separate from the external load. |
| `R_load` | 1 MOhm | `output`, `gnd` | External fixture selected in T18. |
| `R_bias_upper` | 10 kOhm | `v9`, `vref` | Shared bias network. |
| `R_bias_lower` | 10 kOhm | `vref`, `gnd` | Shared bias network. |
| `C_bias` | 47 uF, electrolytic | `vref`, `gnd` | Shared bias network; positive terminal at `vref`. |
| `C_supply` | 100 uF, electrolytic | `v9`, `gnd` | Shared supply network; positive terminal at `v9`. Ideal fixed rails constrain its voltage. |

This table does not add ESR, leakage, capacitor voltage dependence or component tolerances. It transcribes the ideal external R/C baseline, with fixed values under T18. Physical polarity is recorded for provenance, not used to invent a nonlinear electrolytic law.

### Active terminals and switching

| Identifier | Printed part / terminal map | Effect-on treatment |
| --- | --- | --- |
| `Q_input` | 2SC1815: C=`v9`, B=`input_base`, E=`input_emitter` | Basic Ebers–Moll under T14. |
| `Q_output` | 2SC1815: C=`v9`, B=`output_base`, E=`output_emitter` | Same declared nominal parameter set unless a later reviewed package explicitly distinguishes them. |
| `D_feedback_positive` | 1N914: A=`clip_minus`, K=`clip_out` | Basic Shockley. |
| `D_feedback_negative` | 1N914: A=`clip_out`, K=`clip_minus` | Matched antiparallel device; original clipping remains nominally symmetric. |
| `U_clip` | JRC4558 channel A: +=`clip_plus`, -=`clip_minus`, out=`clip_out` | Proposed behavioral law below; rails `v9`/`gnd`. |
| `U_tone` | JRC4558 channel B: +=`tone_in`, -=`tone_minus`, out=`tone_out` | Same behavioral law and nominal parameters; independent state. |
| `J_dry` | Left 2SK30A: S=`dry_send`, D=`switch_common` | Effect-on: channel open under the approved static/no-parasitic approximation. Keep its external capacitor and bias resistor. |
| `J_wet` | Right 2SK30A: S=`wet_send`, D=`switch_common` | Effect-on: T21-A constant `R_on=383.29731360711594 Ohm` between those terminals, under its documented conditional assumptions. |

The two drain terminals join the common bus. The wire from the Volume wiper passes over that bus with a drawn crossover before reaching the wet JFET source. Do not short the wiper to the common bus by mistaking the crossover for a junction. The three `SW` marks identify switching-path access points; they are not three additional ideal-ground connections.

Channel A package pins are 1=out, 2=−, 3=+; channel B pins are 7=out, 6=−, 5=+; pin 8 is positive supply and pin 4 negative supply, as shown in the [manufacturer-authored NJM4558/4559 datasheet, revision 2013-11-05](https://www.mouser.com/datasheet/2/294/njr_njm4558_njm4559_e-551674.pdf). The netlist must state logical terminals explicitly rather than assume a package pin order matches a C++ device constructor.

Under T15, omit both JFET gate-control networks and the flip-flop/LED/footswitch logic, recording the corresponding removed connections. Those logic branches reach the ideal rail/ground rather than adding another direct `vref` load in this drawing. Their omission does not authorize deletion of the two 510 kOhm audio-switch bias resistors above. The unlabeled reverse-polarity protection diode lies directly across the ideal supply; document its omission in the fixed-polarity baseline rather than invent a device model for it. No supply sag, reverse-polarity or cold-power-up behavior is claimed.

### Control fractions and ideal endpoints

T18 uses resistance-track fractions, not mechanical knob angles or taper approximations. Define Drive `d` as the fraction of the track from `drive_end` to the tied wiper/output: used resistance is `500 kOhm * d`, in series with the unchanged 51 kOhm resistor. The unused track segment terminates on the same tied node and adds no separate load.

Define Tone `t` from the `tone_in` end toward `tone_minus`: the two segments are `20 kOhm * t` from `tone_in` to the wiper and `20 kOhm * (1-t)` from the wiper to `tone_minus`. Define Volume `v` from its `vref` end toward `volume_top`: the two segments are `100 kOhm * v` from `vref` to `wet_send` and `100 kOhm * (1-v)` from `wet_send` to `volume_top`. Thus Volume=0 puts the wet wiper at `vref`, as required by the mute case.

At an endpoint, a zero-length segment is an exact voltage constraint. It is not a conductance computed by dividing by zero, and not an arbitrary small resistance. T22-A fixes `v_a-v_b-R*i=0` for all five used control segments, with one fixed 31-unknown map. Retain the lower Volume segment's current/constraint at the five-unknown boundary as documented in the numerical contract; do not eliminate it into a structurally empty row at Volume=0.

## Semiconductor-law interface and missing parameter evidence

At the approved 25 degrees C, use `T = 298.15 K` and `VT = k_B T / q`, with the SI values of Boltzmann's constant and elementary charge. Set nominal temperature explicitly in both models; do not leave a simulator's different nominal temperature implicit and then compensate by fitting the null.

The Shockley law remains `i = Is * expm1(v / (n VT))`. The two feedback diodes share `Is` and `n` in the nominal symmetric baseline. The [Vishay 1N914 datasheet](https://www.vishay.com/docs/85622/1n914.pdf) provides electrical limits and typical curves; a part number or one forward-voltage limit is insufficient to identify both parameters uniquely. No copied third-party model has been accepted as a manufacturer model.

For an Ebers–Moll transport-current parameter `I_S`, use `alpha_F = BF/(BF+1)` and `alpha_R = BR/(BR+1)`, with `I_ES = I_S/alpha_F` and `I_CS = I_S/alpha_R` in the already approved terminal-current convention. T20 accepts the representative GR parameter vector and explicit temperature interpretation in the linked nominal-data contract. The [Toshiba-authored 2SC1815 datasheet, 1997-04-10, hosted by Farnell](https://www.farnell.com/datasheets/25636.pdf) shows multiple gain ranks; the drawing does not identify one. The accepted nominal must not be described as the measured devices of this pedal.

T14 still omits internal semiconductor resistance, Early effect and stored junction/diffusion charge. Native SPICE defaults and numerical shunts need an audit against the same law; absence of a keyword is not evidence that an effect is disabled. Standalone device checks must distinguish model-law mismatch from small numerical regularization within the accepted reference budget.

The [Toshiba-authored 2SK30ATM datasheet, 2003-03-25, hosted by Radiotovar](https://radiotovar.kz/pdf/27780.pdf) gives drain-current classes, cutoff-voltage ranges and forward-transfer-admittance conditions. Transfer admittance in saturation is not an on-resistance specification and does not establish a unique resistance for this drawing. T21-A instead adopts the separately sourced model-core approximation, with its source, gate condition, channel bias and local envelope documented in the linked contract. This does not characterize the actual gate, which is outside the MVP.

## T19 approved: revised option B with an exactly linear center and C1 knees

### Common physical interface

The selected formulation implements the external-behavior scope from T6, for both channels, inside the global MNA/Newton solve. It does not clip the already solved pedal output. Each channel has one independent dynamic voltage state `z`, differential input resistance `R_id`, declared input bias currents/offset, a finite output resistance `R_o`, rail headroom and a recovery-feedback time constant `tau_r`. Values without adequate evidence remain explicit missing inputs below.

Let `V_m = (V_plus + V_minus)/2` be the ideal supply midpoint. This is an internal output-coordinate origin, not a voltage source attached to the physical `vref` network. Let `e = v_plus - v_minus + V_os`, `omega_p = 2 pi GBW / A0`, `H_plus = V_plus - headroom_plus - V_m`, and `H_minus = V_m - (V_minus + headroom_minus)`. Require positive `H_plus`, `H_minus`, `R_id`, `R_o` and `tau_r`.

Use `S(z) = S_B(z)` from the approved structural contract below in these behavioral equations, not production code:

```text
drive = omega_p * (A0 * e - z) - (z - S(z)) / tau_r
dz/dt = SR * tanh(drive / SR)
v_drive = V_m + S(z)
i_out_into_device = (v_out - v_drive) / R_o
i_plus_into_device = (v_plus - v_minus) / R_id + I_bias_plus
i_minus_into_device = (v_minus - v_plus) / R_id + I_bias_minus
```

`SR` has units V/s; `drive` is also V/s, and `tau_r` is in seconds. The recovery term feeds the difference between internal state and limited drive back into the state equation; it reduces accumulated overdrive instead of discarding hidden state after processing. It is often called anti-windup. Its parameter is not determined by GBW or SR alone. The smooth slew law approaches, but does not exceed, the declared SR for the state. Loaded terminal slew also depends on the coupled output current and circuit.

Input bias-current returns and the controlled output branch must have declared return terminals in the independent LTspice realization, conserving terminal current. A differential resistance is not an independently specified common-mode input resistance. Output loading comes from the finite branch resistance and the actual circuit; no extra supply-current, current-limit or common-mode-breakdown law is silently added. Parameter applicability and omitted behavior must be explicit in the final device specification.

The revised saturation transfer has `S(z)=z` and `S'(z)=1` throughout its declared central interval, not merely at zero. Its recovery term `z-S(z)` is exactly zero there. This preserves the centered small-signal single-pole gain `A0/(1+s/omega_p)` before external loading. Finite bandwidth and the state slew law remain as documented; the identity requirement concerns the amplitude-saturation transfer, not a claim that the complete op-amp is linear under slew/overload conditions. The tanh in `dz/dt` limits slew and is distinct from the superseded global amplitude tanh.

T18 must linearize the actual equations at each loaded DC state, including the knees when active. Imposing a bounded target *before* a slow dominant pole is not an interchangeable formulation: it can unintentionally prevent the nominal large-signal slew rate.

### Historical option A: hard output bounds, not selected

```text
S_A(z) = min(H_plus, max(-H_minus, z))
```

* **Mechanism:** The internal output-drive voltage has exact plateaus at the selected headroom bounds. Inside them, the saturation function is the identity; the recovery term is zero. Outside them, it feeds the excess state back into the same differential law.
* **Trade-off:** The central region has a simple linear interpretation and the headroom boundary is explicit. The two corners are nondifferentiable and need shared branch conventions. A rigid knee is a modeling assumption, not measured NJM4558 behavior.
* **Failure conditions:** Boundary transitions can stress Newton/trapezoidal convergence, or produce overload spectra/recovery inconsistent with characterization. A convergence or accuracy failure remains visible under T5; no replacement smoothing is allowed without a reviewed model change.
* **Derivative convention proposed with A:** `S'_A=1` strictly inside the interval and `0` at/outside either bound. The residual itself is continuous. Test both one-sided derivatives at each corner and the specified generalized derivative at equality; do not call it a unique classical derivative.

### Approved revised option B: linear center and smooth compression knees

The owner selected B and then confirmed this revision: "Confirmo T19 como a opção B revisada, substituindo a tangente hiperbólica global." Normal central operation must remain strictly linear in the saturation transfer. Compression curvature is confined to the approach to the output limits, with continuous value and first derivative across each join.

Let `L_plus` and `L_minus` be positive knee-onset magnitudes in the internal `z` coordinate, with `0 < L_plus < H_plus` and `0 < L_minus < H_minus`. These are not new supply rails. Define `K_plus` and `K_minus` as the positive and negative compression branches, respectively. The approved structure is:

```text
S_B(z) = K_minus(z)   for z < -L_minus
S_B(z) = z            for -L_minus <= z <= L_plus
S_B(z) = K_plus(z)    for z > L_plus

K_minus(-L_minus) = -L_minus       K_minus'(-L_minus) = 1
K_plus(L_plus) = L_plus           K_plus'(L_plus) = 1

lim K_minus(z), z -> -infinity = -H_minus
lim K_plus(z),  z -> +infinity = H_plus
```

Both compression branches must be C1 on their domains, remain within the headroom bounds and meet the central identity with the values/slopes above. Thus `S'_B=1` throughout the central interval, including both join points; outside it, use the analytical derivative of the frozen knee expression. A discontinuity in the second derivative is not excluded by the C1 requirement. No particular knee function, onset fraction or width has been selected by this approval; those details remain in the grouped model-data closure. Do not introduce a global tanh, polynomial, spline or tail function as an undocumented implementation default.

T20-A now closes the exact knee expression and nominal values. With `W_plus=H_plus-L_plus` and `W_minus=H_minus-L_minus`, use:

```text
K_plus(z) = L_plus + W_plus * tanh((z-L_plus)/W_plus)
K_minus(z) = -L_minus - W_minus * tanh((-z-L_minus)/W_minus)
S'(z) = 1 in the central interval; sech(s)^2 in either outer knee
```

Here `s` is the nonnegative overdrive in that branch. Both join second derivatives are zero, so the selected law is C2 there. T20 fixes `W_plus=W_minus=0.25 V`, headroom `37/51 V` on each rail, `H=4.5-37/51 V` and `L=H-0.25 V` at 9 V. It does not restore a global amplitude tanh; rational knees are unselected.

The output-drive limits are `V_minus + headroom_minus` and `V_plus - headroom_plus`, corresponding to `V_m-H_minus` and `V_m+H_plus`. The supply remains 0 V/9 V. The knees approach the headroom-adjusted limits; the approval does not make the output rail-to-rail or assign headroom/onset values. The final knee onsets must identify the intended normal central range and confine amplitude-compression curvature to the approach to those limits.

* **Mechanism:** Exact identity in the center, smooth compression only in the two outer knees, and recovery feedback through the same coupled state equation. The recovery contribution is zero throughout the center.
* **Trade-off:** C1 joins remove the hard saturation corners while preserving a finite linear central interval. The onset, width and curve need explicit specification; their selection can alter headroom approach, overload spectra and recovery.
* **Failure conditions:** Inconsistent joins/derivatives, an incorrect central gain, or a knee/recovery model unsupported by characterization can invalidate the model. Smoothness does not establish Newton convergence, nonsingular Jacobians or a passing C++/LTspice null. Under T5/T18, those remain measured checks with visible failures.

The owner's motivation is to maintain continuous derivatives, support deterministic bounded Newton execution and make C++/LTspice null comparison easier. Record those as design objectives. Matching constitutive laws, parameters, initialization, integration/reference qualification and the approved numerical gates remain necessary; neither guaranteed convergence nor bit-identical simulator output follows from C1 continuity.

Option A is unselected. The original global amplitude-tanh version of B is superseded because it has curvature outside zero and does not preserve a finite exactly linear central region. Revised B above is the approved saturation structure; the complete numerical device specification remains unfinished.

### Discrete state and analytical derivative obligations

For revised B, integrate `z` with the already approved trapezoidal law, using committed `z_previous` and `f_previous`. Evaluate saturation and recovery in every Newton trial; never clamp `z` or replace the output after convergence. Commit both channels with the whole circuit only after full convergence.

Let `c = 1 - tanh(drive/SR)^2`. At smooth points, the common state-law derivatives are:

```text
df/de = c * omega_p * A0
df/dz = c * (-omega_p - (1 - S'(z))/tau_r)
```

The trapezoidal residual must include the corresponding `h/2` factors; previous-step history stays fixed during finite differences. The output-branch derivative also includes `S'(z)/R_o`, with the signs dictated by the listed current orientation. Tests cover both channels, positive/negative slew, each compression knee, recovery, off-center bias and analytical versus finite-difference derivatives. Verify the exact central identity and zero recovery contribution throughout that interval; check value and first-derivative continuity approaching both knee joins from both sides, including the common derivative 1 at equality. Unlike historical A, the selected C1 joins require no arbitrary generalized-derivative convention. These formulas are design specifications, not executed or verified production results.

## Model data after T20 and T21 approval

The [T20 contract](./ts808_model_data_proposal.md) is the source of the accepted nominal vector, exact knee equations and temperature preparation; [T21-A](./ts808_switch_resistance_proposal.md) closes the switch resistance and [T22-A](./ts808_numerical_closure_proposal.md) fixes the numerical endpoint map/partition. [T23-B](./ts808_execution_tooling_proposal.md) closes execution tooling. The complete implementation section/attachment are also approved; all implementation/qualification results remain future work.

| Parameter group | Current decision | Remaining work before implementation |
| --- | --- | --- |
| `A0`, `GBW`, `SR`, `R_id` | T20 accepts `100000`, `3e6 Hz`, `1e6 V/s`, `5e6 Ohm`. | Carry the accepted values and physical applicability limits into the final device specification; qualify the independent realizations. |
| Revised-B knee expressions and onsets | T20-A selects shifted-tanh outer knees with C2 joins, 0.25 V spans and the derived onset magnitudes. | Carry exact equations, stable analytical derivatives and central/first-/second-derivative join checks into the plan. |
| Headroom, `R_o`, `tau_r`, input offset/bias | T20 accepts headroom `37/51 V`, `R_o=10000/51 Ohm`, `tau_r=10 us`, zero nominal offset/mismatch and equal 25 nA bias currents. | Preserve estimate/assumption labels and current-return conventions; test the selected nominal, without claiming physical calibration. |
| Diode `Is`, `n` | T20 accepts the reduced official 1N914 vector and 25-degree preparation. | Encode the same reduced law/omissions in the independent implementations and verify actual device currents. |
| BJT transport/gain parameters | T20 accepts a representative 2SC1815-GR vector and the documented temperature interpretation. | Preserve the representative-sample limitation; verify reciprocity, terminal KCL and all required device regimes. |
| `R_on` | T21-A accepts `383.29731360711594 Ohm` as the conditional static nominal. | Carry its provenance, operating assumptions and local limitations into both realizations; record branch-voltage diagnostics. Real gate characterization is outside the MVP. |
| Exact endpoint stamp and matrix partition | T22-A: 31 fixed unknowns, interiors 4/6/11/5, boundary 5, with five control currents and exact zero-resistance constraints. | Implement the accepted map/scales/criteria and qualify endpoint, rank/condition, KCL/history and Schur/full-solve fixtures. Counts and approval do not establish measured rank or convergence. |

The owner selected the [T22-A augmented 31-unknown map and common numerical criteria](./ts808_numerical_closure_proposal.md). T22-B is unselected and its merged maps/aliases are outside the selected plan. Counts remain graph derivations, not measured ranks or proof of convergence.

The datasheet's main electrical-characteristic table is at ±15 V, not a complete measured 9 V device characterization. Typical values are nominal modeling inputs and not guarantees for historical JRC4558 samples. Keep this distinction in the final device specification. General macromodel limitations are also discussed in the manufacturer-authored [Analog Devices AN48](https://www.analog.com/media/en/technical-documentation/application-notes/an48.pdf); that document is not parameter evidence for an NJM4558 at 9 V.

## Required plan and evidence updates

Carry the terminal audit into the planned `reference/ts808/component_map.json` and the selected equations/parameters into `reference/ts808/device_spec.md`. Only after the model-data package is frozen should the independently authored `reference/ts808/models.lib` and `reference/ts808/ts808.cir` be implemented. These files remain planned, not created here.

The existing device/Jacobian, linear-response, KCL/history and coupled-solver tests must exercise revised B and exact control endpoints. Include exact central identity, zero central recovery contribution and C1 matching at both knee joins. Add named standalone op-amp cases for centered/biased small-signal gain, positive/negative slew, headroom with specified resistive loads, sustained overload and recovery. Freeze their exact fixture files and values in the final file-by-file plan; this document does not claim that unnamed fixtures already exist or pass.

The full T18 matrix remains unchanged, including overload timing and local residual gates. Passing two independent realizations of the same equation establishes numerical agreement within that scope; external characterization is still needed for a hardware-fidelity claim.

## Owner approval boundary

T19 is approved as **revised B: exactly linear center, smooth C1 knees near the headroom-adjusted limits, with recovery feedback**. T20-A further approves **shifted-tanh outer knees with C2 joins and the nominal op-amp/semiconductor parameter package**. T21-A approves **the conditional static switch nominal**, with actual gate characterization outside the MVP. T22-A approves **the fixed 31-unknown map and common numerical criteria**; T23-B approves **tooling and native Windows production on the WSL host**. The owner also approved the complete implementation section/attachment on 2026-10-31. Do not reopen these choices or restore the superseded global amplitude tanh. Actual validation results remain outstanding.
