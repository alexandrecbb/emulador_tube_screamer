# TS808 offline MVP: approved T20-A knee equations and nominal model data

* **Author:** Project owner and Codex
* **Date:** 2026-10-31
* **Status:** T20-A and the shared nominal-data package approved by the owner on 2026-10-31. T1–T20 are approved. Use shifted-tanh outer knees with C2 joins; rational knees are unselected. The conducting JFET resistance remains excluded from this approval. Only documentation and scratch arithmetic have been produced; no circuit solver, production code, netlist or acceptance test has been implemented or run. The filename retains the proposal history; earlier proposal wording below is superseded by this approval.

## Approved decision and remaining evidence gap

T19 selects an exactly linear central amplitude-saturation transfer, smooth C1 compression knees and recovery feedback inside the coupled solve. T20-A selects the shifted-tanh knee equations below, whose joins are C2, and accepts the common nominal parameter package. The rational candidate is retained as unselected history. The hard-versus-smooth decision is unchanged.

The accepted package contains manufacturer values, estimates derived from those values and explicit modeling assumptions. It defines the selected mathematical nominal; approval does not turn it into a measured calibration of a historical pedal at 9 V. The conducting JFET's resistance was excluded from T20 and remains physically unqualified. The owner subsequently closed its mathematical nominal through [T21-A](./ts808_switch_resistance_proposal.md), `383.29731360711594 Ohm`, under the documented conditional approximation, with actual gate characterization outside the MVP. T20's own approval scope and nominal values remain unchanged.

## Selected knee equations and retained alternative within revised B

Keep the notation and common state/current equations in the [approved model contract](./ts808_model_contract.md). On each side, `H` is the positive available swing from the internal supply midpoint after headroom, `L` is the positive onset magnitude and `W = H-L > 0` is the remaining output span. For a state beyond that side's onset, define nonnegative normalized overdrive `s = (abs(z)-L)/W` using that side's parameters.

Use the following construction with `q=q_A=tanh` under approved T20-A. The historical rational candidate used the same construction:

```text
S(z) = -[L_minus + W_minus * q((-z-L_minus)/W_minus)]  if z < -L_minus
S(z) = z                                               if -L_minus <= z <= L_plus
S(z) = L_plus + W_plus * q((z-L_plus)/W_plus)            if z > L_plus
```

At each join, require `q(0)=0` and `q'(0)=1`. Both candidates are monotone, have `0 < q'(s) <= 1` for finite nonnegative `s`, and approach `q=1` in overdrive. The center is exactly the identity; neither candidate applies a global amplitude tanh. The saturation derivative is 1 in the center and `q'(s)` in either outer branch. Negative-side signs cancel in that first derivative.

### Approved T20-A: shifted tanh only in the knees

```text
q_A(s) = tanh(s)
q_A'(s) = sech(s)^2
```

* **Mechanism:** Begin each tanh tail at the linear region's endpoint, then scale the tail by the remaining headroom span. The center uses the explicit identity branch.
* **Trade-off:** The second derivative also matches zero at each join, so this construction is C2 there and satisfies the required C1 contract. The tail approaches the limit exponentially. It still requires a transcendental evaluation, and C2 smoothness alone establishes neither physical fidelity nor a processing-time advantage.
* **Failure conditions:** An exponential approach may compress too late or too sharply for the intended device. Very deep saturation can lose derivative precision if evaluated as `1-tanh(s)^2`; the independent implementations must qualify a stable equivalent, for example `4 exp(-2s)/(1+exp(-2s))^2` for `s>=0`. Underflow at extremely large overdrive must be diagnosed against the declared numerical range, not interpreted as a physical discontinuity.

### Historical T20-B: rational knees, not selected

```text
q_B(s) = s / (1+s)
q_B'(s) = 1 / (1+s)^2
```

* **Mechanism:** A rational branch starts at the identity endpoint with slope 1, then approaches the headroom bound algebraically.
* **Trade-off:** The knee uses arithmetic and division. Its first derivative is continuous at the join, while the second derivative changes from zero to a nonzero one-sided value. The tail remains farther from the limit than A for large overdrive. No measured runtime or spectral comparison exists.
* **Failure conditions:** A long algebraic tail may disagree with compression/recovery characterization. The denominator is safe only on its declared `s>=0` domain; inactive-branch evaluation must not introduce an artificial singularity at `s=-1`. Large-argument evaluation must avoid overflow and cancellation without changing the mathematical transfer.

The owner selected T20-A, including the common nominal package, with the instruction "Aprovo a opção T20-A (tanh deslocada nos joelhos com junções C2), incluindo o pacote nominal de parâmetros." T20-B is unselected. T20-A preserves T19 and retains the same recovery term and T18 accuracy gates. Both independent implementations must use the selected shifted-tanh law; no curve replacement or fitting between implementations is implied.

### Arithmetic comparison, not circuit validation

These are calculated normalized transfer values, independent of a pedal run:

| Normalized overdrive `s` | `q_A` | `q_B` | `q_A'` | `q_B'` |
| --- | --- | --- | --- | --- |
| 0 | 0 | 0 | 1 | 1 |
| 0.25 | 0.244919 | 0.2 | 0.940015 | 0.64 |
| 1 | 0.761594 | 0.5 | 0.419974 | 0.25 |
| 2 | 0.964028 | 0.666667 | 0.070651 | 0.111111 |
| 4 | 0.999329 | 0.8 | 0.00134095 | 0.04 |

The output distance from the asymptote is `W*(1-q)`. This table explains the shape difference; it is not a null, THD, aliasing or CPU result.

## Approved op-amp nominal data

Use the same nominal parameters in both channels, with independent dynamic states. Source labels distinguish **S** (stated source value), **D** (derived estimate) and **A** (explicit modeling assumption). T20 approval adopts these values as declared mathematical nominals; their evidence labels remain unchanged and assumptions do not become measurements.

| Parameter | Approved nominal baseline | Basis |
| --- | --- | --- |
| Supply | `V_minus=0 V`, `V_plus=9 V` | Approved T4/T18. |
| Physical bias | Solved RC network | Approved; never connect the op-amp's internal midpoint coordinate as an ideal source on `vref`. |
| `A0` | `100000 V/V` | S/D: 100 dB nominal, converted to linear gain. |
| `GBW` | `3e6 Hz` | S: nominal NJM4558 value. |
| `SR` | `1e6 V/s` | S: nominal NJM4558 value; same positive/negative state bound in this nominal. |
| `omega_p` | `2 pi GBW/A0`, about `188.4955592 rad/s` | D: centered single-pole convention already used in T19. |
| `R_id` | `5e6 Ohm` between inputs | S/A: use the stated input-resistance magnitude as the differential resistor in this reduced model; no separate finite common-mode resistance is inferred. |
| `I_bias_plus`, `I_bias_minus` | `25e-9 A` each, into the device | S/A: typical bias-current magnitude, identical currents/sign convention for the nominal. Returns go to the negative supply terminal. |
| `V_os`, input offset-current difference | `0 V`, `0 A` | A: matched nominal offsets, not the datasheet's typical offset magnitudes or a claim about an actual unit. |
| Effective `R_o` | `(10000/51) Ohm`, about `196.0784314 Ohm` | D/A: two-point effective large-signal load fit below, reused as the constant output resistor. It is not a measured small-signal output impedance. |
| Positive/negative headroom | `(37/51) V` each, about `0.7254901961 V` | D/A: fit at the source conditions, assumed constant relative to each rail when using 9 V. |
| `W_plus`, `W_minus` | `0.25 V` each | A: accepted nominal knee output spans, not extracted device data. |
| `H_plus`, `H_minus` at 9 V | `4.5 - 37/51 V`, about `3.774509804 V` | D: internal swing magnitude after the accepted nominal headroom. |
| `L_plus`, `L_minus` at 9 V | `H - 0.25 V`, about `3.524509804 V` | D: exact center extends from `-L_minus` to `L_plus` in state coordinates. |
| `tau_r` | `10e-6 s` | A: accepted nominal recovery-feedback time constant; no NJM4558 recovery measurement supports this number yet. |

Manufacturer values above come from the [NJM4558/4559 datasheet, revision 2013-11-05, pages 1–2](https://www.mouser.com/datasheet/2/294/njr_njm4558_njm4559_e-551674.pdf). Its main electrical table uses ±15 V and 25 degrees C. It does not establish all those typicals at 9 V, specify this knee, or determine `tau_r`.

### Effective output fit and its limits

Interpret the datasheet's typical output swings of ±14 V with the 10 kOhm load condition and ±13 V with the 2 kOhm condition as two endpoints for a simple Thevenin fit. This interpretation is an approximation to the stated load conditions, not an extracted transistor-level output model. If the asymptotic internal drive magnitude at ±15 V is `E`, then:

```text
14 = E * 10000/(10000+R_o)
13 = E *  2000/(2000+R_o)
R_o = 10000/51 Ohm
E = 728/51 V
headroom = 15-E = 37/51 V
```

The fractions make the mathematical nominal reproducible; they do not imply that the two rounded source typicals have this physical precision. Assuming the same resistor and headroom at 9 V is an extrapolation accepted as the T20 nominal. It must not be presented as measured NJM4558 behavior at that supply.

Under that nominal, the internal drive approaches approximately 0.72549 V and 8.27451 V, with the central saturation-identity interval mapping to approximately 0.97549–8.02451 V. These are internal drive levels before `R_o`. The actual terminal voltage follows the coupled load, including feedback current. No final-output clamp is added.

The counter-argument is material: two high-supply swing points do not uniquely identify low-supply headroom, output resistance or recovery. This proposal prioritizes an explicit nominal for comparing two implementations of the same equations. A later physical characterization can require a versioned model revision, even after a numerical pass.

### Applicability and omitted behavior

Keep the existing T19 state slew function. Input offset and offset-current mismatch, a separate common-mode resistance, finite CMRR/PSRR, input protection/breakdown, output current limiting and dynamic supply current are not added in this nominal package. Input bias currents and finite differential/output resistances remain included. Ideal fixed rails do not validate behavior under supply sag, common-mode violation or externally forced output voltage.

The 0.25 V knee span and 10 us recovery constant are hypotheses for the finite baseline, not fit results. Diagnostic sensitivity runs may compare knee spans 0.1/0.25/0.5 V and recovery constants 1/10/100 us as separately identified model configurations. Those diagnostics do not silently replace the accepted nominal or relax a failed T18 target-rate case. They require no new dynamic state or integrator.

## Approved nominal semiconductor data and temperature interpretation

The baseline temperature remains 25 degrees C. Preserve both the source parameter temperature and the prepared baseline values. [Analog Devices' LTspice quick reference](https://www.analog.com/media/en/news-marketing-collateral/solutions-bulletins-brochures/ltspice-keyboard-shortcuts.pdf) lists 27 degrees C as the default nominal parameter temperature when a model does not specify it. Interpreting an unqualified published card at that nominal temperature is a simulator convention, not proof of the specimen's measurement temperature.

Propose reading the source vectors below at `T0=300.15 K`, then preparing constants at `T=298.15 K`. Use `VT = k_B T/q`, with `k_B=1.380649e-23 J/K` and `q=1.602176634e-19 C`. The proposed preparation rules are:

```text
r = T/T0
Is_diode(T) = Is_diode(T0) * exp(((r-1)*EG_diode/VT + XTI_diode*ln(r))/n)
Is_BJT(T)   = Is_BJT(T0)   * exp((r-1)*EG_BJT/VT + XTI_BJT*ln(r))
BF(T) = BF(T0) * r^XTB
BR(T) = BR(T0) * r^XTB
```

With bandgap numbers in eV and `VT` in volts, the numerical exponent uses their corresponding per-charge ratio. These are fixed-data preparation formulas, not a new temperature-variation simulation feature. The diode/BJT factors follow the public SPICE-style formulas in [ngspice diode temperature preparation](https://raw.githubusercontent.com/ngspice/ngspice/master/src/spicelib/devices/dio/diotemp.c) and [BJT temperature preparation](https://raw.githubusercontent.com/ngspice/ngspice/master/src/spicelib/devices/bjt/bjttemp.c). These sources document the proposal; ngspice is not selected as the simulator, dependency or expected-waveform generator.

Both implementations must receive the same prepared 25-degree parameter vector. In the planned reduced LTspice cards, state the prepared nominal temperature explicitly as 25 degrees C and keep the operating temperature at 25 degrees C, avoiding a second implicit rescaling. Standalone current/derivative fixtures must still qualify the pinned LTspice realization. This document does not claim that every native simulator default or physical constant is already identical.

### Feedback diodes: reduced official 1N914 vector

The [onsemi-hosted Fairchild 1N914 model](https://www.onsemi.com/download/models/lib/1n914.lib), dated 2007-07-24, revision 1.0, explicitly supplies `IS=3.45e-9 A`, `N=1.94` and `EG=0.92 eV`. The downloaded ASCII file has SHA-256 `558f99082a6a9197abf646fd9e54ac12836dcb2f580747c07f16434fc70670c5`. Its absent nominal temperature/XTI are made explicit here as the proposed 27-degree/3 conventions.

For the approved basic Shockley scope, propose retaining only its main current-law parameters, with `XTI=3` for the preparation above. The prepared values are approximately `Is=3.0193620074088285e-9 A` and `n=1.94` at 25 degrees C. Use the same values for both opposing feedback diodes.

Do not import the full vendor card unchanged. Internal resistance, charge/transit time, its extra recombination-current branch, high-injection rolloff and reverse-breakdown extension are outside this basic current law. Removing them changes the vendor model; retaining its core parameters does not establish that the reduced curve still fits all vendor data. The independent LTspice reference must use the same reduced law, not the richer download.

### Buffers: approved representative 2SC1815-GR nominal vector

The [Kaz-electro first-person 2SC1815 characterization, version 260823_V5R14EN](https://kaz-electro.jp/lab/2sc1815-spice/) publishes a GR specimen vector with `IS=16.045e-15 A`, `BF=275.022`, `NF=0.99569`, `BR=4.268` and `XTB=1.9`. This is independent specimen characterization, not a Toshiba nominal or the identified devices of the selected pedal. The article reports a 26.6-degree measurement temperature for that specimen, while its published SPICE card does not state TNOM. Its retrieved HTML has SHA-256 `d8b7b47b020886dd026c8dc537bf88fd66e8e341685d49ba950119997ca0e630`.

Propose GR as a representative nominal for both buffers, with the explicit card interpretation `T0=27 degrees C`, `NR=1`, `EG=1.11 eV` and `XTI=3`. The latter conventions are assumptions for the reduced baseline, not additional measured values. Under the preparation above:

| Parameter at 25 degrees C | Calculated nominal |
| --- | --- |
| Transport `I_S` | `1.1792496052020765e-14 A` |
| `BF` | `271.5505716517182` |
| `BR` | `4.2141277418153207` |
| `NF`, `NR` | `0.99569`, `1` |
| `alpha_F`, `alpha_R` | Approximately `0.9963309561453503`, `0.8082133676970780` |
| `I_ES = I_S/alpha_F` | Approximately `1.1835922570993981e-14 A` |
| `I_CS = I_S/alpha_R` | Approximately `1.4590820349361811e-14 A` |

The source card's temperature ambiguity limits the physical interpretation. Do not relabel the prepared constants as measured at 25 degrees C. Selecting this nominal does not establish the actual pedal's gain rank. The downloaded onsemi KSC1815 card was inspected but is not used as an undeclared replacement for the selected 2SC1815.

Retain only the basic Ebers–Moll transport/current-gain terms. Explicitly omit Early effect, high-injection rolloff, recombination/leakage extensions, internal resistances and all semiconductor charge/transit-time terms in the reduced baseline. The original measured model's fit claims do not transfer to this reduction. Confirm terminal KCL, reciprocity convention and forward/reverse/saturation behavior independently under T13/T14.

The calculated decimals above identify a reproducible mathematical nominal. They are not statements of physical measurement precision.

## Conducting JFET: historical T20 gap, closed as an approximation by T21

The evidence gap below describes the state at T20 approval. T21-A subsequently selected the separate documented model-derived constant; T21-B is unselected. No further gate characterization is required to complete the MVP design, and no physical characterization is claimed.

The selected circuit still requires a finite wet-channel `R_on`; T15 is unchanged. The [Toshiba 2SK30ATM datasheet](https://radiotovar.kz/pdf/27780.pdf) does not, by its part name or saturation transconductance alone, establish that resistance at the extracted gate/channel conditions.

A [first-person 2021 report by Manfred](https://www.freestompboxes.org/viewtopic.php?p=285892) describes about 400 Ohm measured on a 2SK30A in a similar switching circuit without power. The indexed report supplies a lead, not a qualified powered TS808 resistance: test voltage/current, grade, gate bias and temperature are not established. The full thread could not be retrieved during this pass. Do not adopt 400 Ohm as a sourced effect-on value or silently set zero.

To close this item, identify a traceable static characterization/model and derive the local channel resistance at the extracted on-state, or review a documented approximation with explicit conditions and limitations. Record the channel DC point, incremental or secant resistance definition, gate condition, temperature and declared validity range. A resistance chosen to minimize the C++/LTspice null is not independent evidence. A full dynamic JFET is not introduced by this research.

T20 approval therefore cannot mark the complete model-data package implementation-ready. The remaining switch datum is a visible dependency, rather than another mandatory question for the owner in this gate.

## Required validation and planned artifacts

Use the selected T20-A law/parameter vector and nominal-temperature preparation together with the now approved T21-A switch nominal in the final model identity. The common data and selected equations must enter the already planned `reference/ts808/device_spec.md`, reduced `reference/ts808/models.lib`, `include/ts808/parameters.hpp` and the case/model identities. Their production contents are not created by this documentation update.

Extend the planned `tests/device_jacobians.cpp` and `tests/linear_and_history.cpp` obligations with exact center identity, zero center recovery contribution, join values/slopes, monotonicity, headroom bounds and independent finite differences. Add planned fixtures `tests/fixtures/opamp_revised_b_cases.json` and `tests/fixtures/device_nominal_25c.json` for explicit scalar/model vectors and temperature interpretation; enumerate them in the final implementation plan. These fixtures are planned, not existing or passing files.

Standalone op-amp checks must include both channels, positive/negative overload and recovery, the center and each knee, finite loading and the actual biased small-signal linearization. Standalone semiconductor fixtures must verify actual LTspice currents against the declared reduced equations before full-pedal use; quantify numerical shunts and reject hidden richer-model terms. Then run the unchanged T18 matrix at its target rates, with separately identified refinements and source uncertainty.

Scratch arithmetic checked the displayed temperature conversions, the two-point fit and the normalized comparison table. No C++/LTspice parity, nonlinear convergence, physical headroom, CPU, allocation, aliasing, latency or listening result has been measured.

## Owner approval boundary

The owner approved **T20-A: shifted-tanh outer knees with C2 joins and the shared nominal parameter package** on 2026-10-31. This includes the explicit op-amp assumptions, reduced diode/representative BJT data and temperature interpretation above. T20-B remains unselected; do not reopen this choice. Approval does not establish physical calibration or validation success. `R_on` remains unqualified and unselected, and complete model/implementation approval remains pending.
