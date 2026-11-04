# TS808 offline MVP: approved conducting-switch nominal

* **Author:** Project owner and Codex
* **Date:** 2026-10-31
* **Status:** T21-A approved by the owner on 2026-10-31: adopt `R_on=383.29731360711594 Ohm` (383.30 Ohm when displayed) as the conditional static nominal below. Actual gate characterization is outside the MVP. T1–T20 remain approved, including T20-A and its nominal package. No production code, dynamic JFET, gate-control circuit, netlist or model acceptance test has been implemented or run. The filename retains the proposal history.

## What this closes, and what it cannot establish

T15 requires a finite static resistance for the conducting wet switch, with its source, operating assumptions and approximation limits recorded. T20 explicitly excluded this value. A traceable published model-core parameter set is now available for a conditional nominal calculation; it is not a measurement of the original pedal's gate/channel behavior.

The owner selected the conditional nominal for the simplified offline circuit. Specific characterization of the real gate/channel is not an MVP prerequisite. The approved four-block solve, input/output loads and both switching-branch 510 kOhm resistors remain included; no JFET dynamics are introduced.

## Owner decision T21

The owner chose A with the instruction: "Escolho a opção A: adotar 383,30 Ω como valor nominal estático condicional às hipóteses documentadas, mantendo a caracterização do gate real fora do escopo do MVP". Use the full derived decimal in model identity and parameters; the displayed 383.30 Ohm is its rounded presentation. This does not imply physical accuracy to all displayed digits.

The accepted assumptions are unit area, 25 degrees C, `V_GS=0 V`, `V_DS=0 V` and the reduced model-core interpretation below. Characterization of the actual gate, gate tracking and switching dynamics remain outside the MVP; their absence must not be reopened as a blocking model datum. Numerical T18 acceptance still concerns both implementations of this same static approximation. Physical calibration and the local signal-range limitations remain unmeasured and explicitly separate.

## Source and interpretation

The [Agilent ADS 2011 Analog Parts Library, September 2011, page 193, hosted by Keysight](https://edadownload.software.keysight.com/eedl/ads/2011/pdf/vcap.pdf#page=194) lists entry `ap_njf_2SK30A_19930601`, with `Beta=0.0009764` and `Vto=-1.336`. Its entry name is a library identifier; it does not identify the grade, lot, measurement conditions or exact part in the selected pedal. The downloaded PDF has SHA-256 `6e9b3bae7b6add7b05b484155092d955b490562098426873522422966da6fd12`.

The [ADS Nonlinear Devices manual, JFET model and instance sections, pages 408–414](https://edadownload.software.keysight.com/eedl/ads/2011/pdf/ccnld.pdf#page=409) describes a Shichman–Hodges-based model, area scaling, and defaults of unit area and 25-degree nominal/operating temperature. These document the proposed normalization; they do not prove that all hidden parameters of the particular library instance equal the defaults. The complete library instance has not been simulated or characterized here.

Use the accepted effective unit-area interpretation `beta=0.0009764 A/V^2`, `Vto=-1.336 V` at 25 degrees C for the local model-core calculation below. Treat omitted channel-modulation/series-resistance corrections as part of the stated reduction, not measured zero values. No Keysight/ADS dependency is added to the project.

## Conditional local derivation

For the chosen basic ohmic-channel approximation, define:

```text
I_DS = beta * [2*(V_GS-Vto)*V_DS - V_DS^2]
g0 = partial(I_DS)/partial(V_DS) at V_GS=0, V_DS=0
g0 = 2*beta*(-Vto) = 0.0026089408 S
R0 = 1/g0 = 383.29731360711594 Ohm
```

The formula specifies the conventional square-law interpretation used for the calculation; it is not a claim that the complete ADS library entry contains no other behavior. The accepted nominal operating point is `V_GS=0 V`, `V_DS=0 V`, unit area and 25 degrees C. Its absolute channel common mode follows the solved bias node at the unloaded switching DC equilibrium; it does not clamp `vref` to 4.5 V.

This derivation differentiates channel current with respect to **drain-source voltage** at the declared point. It does not simply invert a datasheet saturation transconductance measured under another bias. The same core would give an `I_DSS` of about 1.743 mA, but that calculated value is not evidence of the original switch's grade or specimen parameters.

The gate operating point is an explicit approximation. The omitted flip-flop/gate network has not established it for the actual pedal, and it is not a new ideal gate source in the runtime circuit. Label the selected nominal as a model-derived static switch equivalent under those assumptions, rather than a measured powered TS808 on-resistance.

## Conditional signal range and limits

Within the same ideal core, let `a=-Vto=1.336 V` and let `delta_V_GS` denote departure from the assumed gate point. The chord conductance satisfies:

```text
(I_DS/V_DS)/g0 = 1 + delta_V_GS/a - V_DS/(2*a)
```

At `V_GS` held at zero and `abs(V_DS)<=10 mV`, its departure from `g0` is at most about 0.3743% of `g0`. If both `abs(delta_V_GS)<=10 mV` and `abs(V_DS)<=10 mV`, the bound becomes about 1.1228%. These are algebraic bounds for the stated ideal core, not measured hardware errors, reference-uncertainty budgets or new T18 acceptance thresholds.

That neighborhood is the declared local approximation range. The static resistor remains a defined mathematical element outside it, but this derivation supplies no physical-error bound there. The real gate may vary with audio and switching bias; because T15 omits that network, the extracted resistor model cannot demonstrate the gate-deviation bound. It also omits channel nonlinearity, gate currents, device charge, temperature drift and switching transitions. Do not claim that the local bound covers all T18 tones or overload cases.

Numerical T18 comparisons use the same selected constant resistor in C++ and LTspice at every declared stimulus. They qualify the agreed simplified equations, not the omitted full-switch hardware behavior. Record the maximum wet-to-common voltage in case diagnostics and state the physical qualification limit separately. This observation does not change the approved numerical pass/fail thresholds or authorize discarding stress cases.

## Options considered and decision

### T21-A: adopt the conditional model-derived static nominal — selected

Use `R_on=383.29731360711594 Ohm`, with the source/normalization, gate-point hypothesis and local limits above recorded in model identity. The digits identify a reproducible mathematical nominal, not physical measurement precision.

* **Mechanism:** Stamp one constant resistance from `wet_send` to `switch_common` in both circuit realizations. The blocked dry channel remains open under T15, with its external capacitor and bias resistor retained. No gate node or dynamic JFET is added.
* **Trade-off:** Closes the missing mathematical value with a traceable conditional derivation. It does not establish actual on-state gate tracking or calibrate a historical pedal. Those limitations remain visible even after numerical acceptance.
* **Failure conditions:** A later operating-point/model audit can show the assumed normalization or gate point unsuitable. Then revisit the nominal explicitly and version the change; do not silently replace the value, remove loading or tune it to the C++/LTspice null.

### T21-B: retain the unresolved value pending specific characterization — not selected

Keep `R_on` unset until a source or measurement specifies the relevant device, gate bias, channel point, temperature, resistance definition and signal range.

* **Mechanism:** Use that characterization to derive a reviewed constant equivalent at the selected effect-on state. The runtime circuit still uses T15's static approximation.
* **Trade-off:** Avoids adopting the gate/normalization assumptions above, but requires data not currently available in the project. Independent numerical/tooling documentation can continue; the final complete circuit package remains unfinished.
* **Failure conditions:** A measurement from an unpowered circuit, an unidentified grade or unspecified gate condition does not close this route. A single local point also cannot prove accuracy over arbitrary audio amplitudes.

T21-A is selected as an explicit nominal-approximation decision; it does not retroactively claim the missing physical evidence has been measured. T21-B is retained only as the unselected alternative, not an active MVP dependency.

## Planned integration and checks

Carry the approved value, source and scope into planned `reference/ts808/component_map.json`, `reference/ts808/device_spec.md`, `reference/ts808/ts808.cir` and `include/ts808/parameters.hpp`. Preserve their common physical-case identity with the already approved T20-A package. Use the planned coupled-assembly/KCL and history tests to verify the retained wet/dry/common connections and loads. Report branch-voltage observations through the planned validation reports, separately from required T18 gates.

For T21-A, no JFET law from this derivation enters production processing; it only explains the selected resistor. For T21-B, no placeholder resistor may be substituted while claiming a completed reference circuit. Both routes keep source sag, flip-flop dynamics, cold power-up and production implementation outside the current drafting work.

Only the displayed scalar derivative/arithmetic has been calculated. No loaded circuit point, signal-range coverage, physical switch calibration, nonlinear convergence or C++/LTspice parity has been measured.
