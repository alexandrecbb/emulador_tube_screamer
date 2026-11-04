# TS808 offline MVP: approved numerical closure at control endpoints

* **Author:** Project owner and Codex
* **Date:** 2026-10-31
* **Status:** T22-A and the documented common criteria approved by the owner on 2026-10-31. T1–T22 remain approved. Use the single 31-unknown augmented representation; T22-B is unselected. No solver, netlist, fixture or numerical acceptance test has been implemented or run. The filename retains the proposal history.

## Scope and decision boundary

T21-A closes the last missing nominal device value: `R_on=383.29731360711594 Ohm`, with actual gate characterization outside the MVP. The accepted mathematical baseline is `ts808-cerutti-reduced-v1` in the [model contract](./ts808_model_contract.md). Its passives, reduced semiconductor laws, op-amp equations and T18 acceptance requirements remain unchanged.

The selected numerical representation handles exact potentiometer endpoints without dividing by zero or inserting an arbitrary small resistor. It preserves T16's prepared, fixed-size Eigen storage and T2's coupled solve with eliminated block interiors. The owner selected retained current unknowns for the control segments; endpoint-specific node merging remains the unselected alternative.

This approval includes dimensions, scaling, conditioning, DC initialization, API obligations and named verification files. It does not select the development platform, compiler/package versions, build/test framework, JSON dependency or LTspice launching workflow. Those remain one execution-tooling package; T22 approval does not close it or approve the complete Detailed Implementation Plan.

## Owner decision T22

The owner stated: "Aprovo a opção A (sistema único de 31 incógnitas com mapa fixo e correntes auxiliares), incluindo os critérios comuns documentados." Record `formulation_id=control-branch-v1`, interiors of 4/6/11/5 unknowns and a five-unknown retained boundary. Preserve the exact row/unknown ordering and shared numerical settings below.

The approval accepts these as the initial mathematical/numerical contract and verification obligations. It is not evidence of full rank at every iterate, convergence, reference accuracy, allocation behavior or runtime performance. Do not reopen T22 or switch automatically to the unselected merged-node formulation after a failure.

## Common graph inventory

The counts below are derived from the documented terminal map, not a simulated Jacobian rank or a convergence result.

| Quantity | Named inventory | Count |
| --- | --- | --- |
| Prescribed voltages | `gnd`, `v9`, `generator` | 3; not solved unknowns |
| Input-side node voltages | `input`, `input_cap`, `input_base`, `input_emitter`, `dry_send` | 5 |
| Clipping node voltages | `clip_plus`, `clip_minus`, `gain_rc`, `drive_end`, `clip_out` | 5 |
| Tone/Volume node voltages | `tone_in`, `tone_minus`, `tone_wiper`, `tone_rc`, `tone_out`, `volume_cap`, `volume_top`, `wet_send` | 8 |
| Output node voltages | `switch_common`, `output_base`, `output_emitter`, `output_cap`, `output` | 5 |
| Shared bias voltage | `vref` | 1 |
| Op-amp dynamic unknowns | `z_clip`, `z_tone`, one per channel | 2 |

Thus the unmerged physical-node list has 24 unknown voltages and two op-amp state unknowns. Capacitors use trapezoidal companion stamps with committed voltage/current histories; their currents are not additional Newton unknowns in this proposal. Ideal source currents are derived diagnostics outside the node solve. `C_supply` lies across prescribed rails and has constrained voltage history, not a free state unknown. This preserves its documented fixed-supply treatment.

The controls remain fixed throughout each offline case. Any mapping selection occurs during preparation, never as an unrecorded change during a Newton iteration or between samples.

## T22-A: one augmented system for every control position — selected

Introduce one current unknown for each of the five used potentiometer segments. For an oriented segment from `a` to `b`, impose the voltage-unit equation:

```text
v_a - v_b - R_segment * i_segment = 0
```

Add `+i_segment` to KCL at `a` and `-i_segment` at `b`. This is a resistor when `R_segment>0` and an exact voltage equality when it is zero. No reciprocal of a zero resistance is evaluated.

| Current unknown | Orientation | Segment resistance | Unknown location |
| --- | --- | --- | --- |
| `i_drive` | `drive_end` to `clip_out` | `500000*d Ohm` | Clipping interior |
| `i_tone_low` | `tone_in` to `tone_wiper` | `20000*t Ohm` | Tone/Volume interior |
| `i_tone_high` | `tone_wiper` to `tone_minus` | `20000*(1-t) Ohm` | Tone/Volume interior |
| `i_volume_low` | `vref` to `wet_send` | `100000*v Ohm` | Retained boundary |
| `i_volume_high` | `wet_send` to `volume_top` | `100000*(1-v) Ohm` | Tone/Volume interior |

Retain the ordered boundary `[input_emitter, clip_out, wet_send, vref, i_volume_low]`. The lower Volume segment belongs to Tone/Volume assembly even though its current unknown and voltage-constraint row remain in the global boundary. At Volume=0 both terminals are retained voltages: putting its current and constraint in an eliminated interior would leave that constraint row with no interior coefficient. Keeping them at the boundary avoids that structural mistake.

Use the following ordered interiors. Capacitor histories and local branch ownership stay with the components already assigned by the model contract.

| Block | Ordered interior unknowns | Square internal system |
| --- | --- | --- |
| Input Buffer | `input`, `input_cap`, `input_base`, `dry_send` | 4 by 4 |
| Clipping Amp | `clip_plus`, `clip_minus`, `gain_rc`, `drive_end`, `z_clip`, `i_drive` | 6 by 6 |
| Tone/Volume | `tone_in`, `tone_minus`, `tone_wiper`, `tone_rc`, `tone_out`, `volume_cap`, `volume_top`, `z_tone`, `i_tone_low`, `i_tone_high`, `i_volume_high` | 11 by 11 |
| Output Buffer | `switch_common`, `output_base`, `output_emitter`, `output_cap`, `output` | 5 by 5 |
| Retained boundary | As listed above | 5 by 5 Schur system |

The full assembled system has `24+2+5=31` unknowns. Its order is the four interior lists followed by the boundary list. Coupling storage has shapes `n_i by 5` and `5 by n_i`; the full diagnostic solve is 31 by 31. `switch_common` is an Output Buffer interior: the finite T21-A resistor couples it to the retained `wet_send`. Shared bias components contribute directly to retained `vref` KCL.

* **Mechanism:** One unknown/row map, one set of fixed-size factorizations and exact endpoint equations for every case. Native LTspice realizes the same physical positive resistances and exact zero-voltage connections independently; it must not substitute a small positive resistance at an endpoint.
* **Trade-off:** Adds five current unknowns and one retained constraint/current pair compared with a fully resistive interior-position formulation. Simplifies identity and history mapping but increases arithmetic/storage. No speed advantage or allocation result has been measured.
* **Failure conditions:** A wrong row partition, orientation or scale can make the elimination invalid. The remaining Jacobian can still be singular or poorly conditioned at an iterate. Those conditions must fail under the common policy; a fixed count is not proof of full rank.

## T22-B: prepare an exact node map for each endpoint category — not selected

This section preserves the considered alternative and its trade-offs. Its maps, aliases and variant-dispatch implementation are not part of the approved MVP plan.

Represent strictly positive control segments by their conductance. At an exact zero, merge its terminal nodes during preparation, retaining an alias table for all original node/trace names. This is an exact connection, not a small-resistance approximation.

Drive has two structural categories, `d=0` and `d>0`. Tone has three, `t=0`, `0<t<1` and `t=1`. Volume likewise has three. There are 18 preparation categories, with compile-time-sized system variants selected once per case; a general dynamically allocating solve is not introduced. Endpoints are classified by exact declared control values, without rounding a small positive resistance down to zero.

Let `D=1` when `d=0`, `T=1` when Tone is at either endpoint, `V0=1` when `v=0`, and `V1=1` when `v=1`; otherwise each indicator is zero. Then:

```text
Input interior        = 4
Clipping interior     = 5 - D
Tone/Volume interior  = 8 - T - V1
Output interior       = 5
Retained voltages     = 4 - V0
Full system           = 26 - D - T - V0 - V1
```

The full dimension ranges from 23 through 26. Start from A's ordered lists after removing its five introduced current unknowns, then apply the exact merges: `drive_end -> clip_out` at `d=0`; `tone_wiper -> tone_in` at `t=0`, or `tone_wiper -> tone_minus` at `t=1`; `wet_send -> vref` at `v=0`, or `volume_top -> wet_send` at `v=1`. Preserve the order of the remaining unknowns. The retained list starts as `[input_emitter, clip_out, wet_send, vref]`; remove aliased `wet_send` at Volume=0.

* **Mechanism:** Prepare one of the 18 fixed-size maps and matching factorization/storage variants, with original node aliases resolved when reading traces. Restore capacitor histories using terminal voltages in that prepared map.
* **Trade-off:** Smaller systems and a boundary of three or four voltages; more mapping, dispatch and alias/history verification across cases. Exact current observations at merged branches require an explicit KCL reconstruction convention if exposed; do not infer them from `0/0`.
* **Failure conditions:** Lost loads, wrong aliases or incompatible history/trace mapping can silently change the circuit. Unsupported endpoint variants or an unqualified small-positive-resistance solve are visible failures. No allocation, convergence or performance property follows from the smaller counts alone.

## Approved common scaling and linear acceptance

**Revisão aprovada em 2026-11-01:** após as escalas físicas abaixo, dividir
cada linha da matriz completa e seu lado direito pelo máximo absoluto dos
coeficientes dessa linha. Recalcular a equilibração em cada Jacobiana;
linhas nulas continuam sujeitas à rejeição por posto. Avaliar rank/rcond
nas matrizes equilibradas. Verificar o erro reverso do incremento recuperado
também no sistema original com escalas físicas, antes da equilibração.
Aplicar a mesma política ao solve completo de diagnóstico. Identificar a
política em execução como `row_scaling=max_abs_after_physical`.
O limite `rcond>=1e-12`, as escalas das incógnitas e as equações físicas
permanecem. Ver [evidência e decisão](ts808_scaling_revision.md).


These settings were approved with T22-A; they do not replace T16's accepted initial Newton caps, line search or convergence tolerances. They still require qualification during implementation.

| Item | Accepted initial specification |
| --- | --- |
| Unknown reference scales | 1 V for every node/op-amp voltage, 1 mA for A's introduced currents. |
| Factorization row scales | 1 mA for KCL rows, 1 V for voltage constraints and op-amp state rows. Solve the nondimensionalized matrix and transform the increment back to physical units. |
| State rows | Transient: `z-z_previous-(h/2)*(f+f_previous)` in volts. DC: `f/omega_p=0`, also in volts; positive `omega_p` is fixed by T20. Previous history remains immutable during trials. |
| Pivot rank criterion | For each square scaled system of order `N`, set the relative pivot threshold to `64*N*epsilon`, with binary64 `epsilon=2^-52`; require rank `N`. This is an accepted engineering cutoff, not a physical constant. |
| Conditioning criterion | Require a finite reciprocal-condition estimate `rcond >= 1e-12` for every eliminated block and the Schur system. Record its value and system identity on failure. A diagnostic full-system solve uses the same rules on its own scaled matrix. |
| Linear backward error | With scaled `A`, `b` and computed `delta`, require `eta=norm_inf(A*delta-b)/(norm_inf(A)*norm_inf(delta)+norm_inf(b)) <= 1e-10`, as already proposed in T16. The matrix infinity norm is the maximum absolute row sum. A zero denominator passes only with exactly zero numerator. Check the reconstructed full coupled equation after back-substitution. |
| Invalid factorization | Rank deficiency, nonfinite data, a rejected condition estimate or failed backward error stops the case. No added shunt, physical-model change, automatic repartitioning, node-merging fallback or alternate integrator. |

The [Eigen FullPivLU documentation](https://libeigen.gitlab.io/eigen/docs-nightly/classEigen_1_1FullPivLU.html) documents complete pivoting, threshold-controlled rank queries and a reciprocal-condition estimate. Its `info()` result alone does not establish invertibility. These are interface semantics, not a pinned dependency release or evidence that the proposed cutoffs work on this circuit. Check the selected release and its estimator behavior when freezing the tooling package.

Factorization scales above differ from nonlinear convergence weights. Preserve T16's current/voltage absolute tolerances and branch-contribution-based relative scales for convergence. For line search, fix those nonlinear row weights for every trial length at one iterate; evaluate the full circuit merit `0.5*norm_2(W*F)^2`. Use the actual directional slope `(W*F)^T*(W*J*delta)` with the proposed Armijo constant and nine permitted lengths. Do not change weights mid-search to manufacture a decrease. A non-descent direction or exhausted search is a visible numerical failure.

No globally nonsingular matrix or acceptable conditioning is inferred from the node count. T13 derivative tests, monolithic-versus-Schur checks and T18 reference comparisons still qualify the chosen formulation.

## Approved DC initial guess and history

The baseline pre-stimulus generator is 0 V. Hold/overload sources begin at that declared pre-stimulus equilibrium. The following table specifies a deterministic initial guess, never an accepted DC solution or an ideal clamp on `vref`.

| Initial value | Nodes/state |
| --- | --- |
| 0 V | `generator` (prescribed), `input`, `tone_rc`, `output` |
| 3.85 V | `input_emitter`, `output_emitter`, `output_cap` |
| 4.5 V | `vref` and every other unknown physical node listed above |
| 0 V | `z_clip`, `z_tone` |
| 0 A | A's five control-segment current guesses |

`gnd=0 V` and `v9=9 V` remain prescribed. The 0.65 V base/emitter guess is only a starting value, not a fixed BJT drop. A's endpoint constraint guesses are consistent because their terminal voltages match. Controls affect the solve, not hidden DC overrides.

Run the approved full loaded DC Newton solve, capped at 100 iterations. After convergence, initialize every capacitor's committed voltage from the solved terminal difference and its current to zero; initialize each op-amp state from its solved DC value with equilibrium derivative zero within the declared tolerance. Retain measured DC residual diagnostics and enforce the unchanged-input hold test. A failed DC solve must not produce initialized/pass metadata or a transient run. No cold startup, source stepping or homotopy is added.

## Shared API and artifact obligations

These are language-neutral interface specifications, not implemented function bodies. Exact C++ declarations and schema syntax belong in the final implementation section after the numerical representation and tooling choices.

| Operation | Inputs and required behavior | Result/history rule |
| --- | --- | --- |
| Prepare | Validated model parameters, fixed controls, rate and numerical settings. Freeze the chosen map, scales, prepared buffers and model identity. No file/JSON dependency in the core. | A prepared model or a typed configuration failure. Preparation may allocate outside the guarded step path. |
| Initialize DC | Prepared circuit and declared pre-stimulus source. Run the global DC solve and initialize histories only after convergence. | A committed equilibrium or typed failure; no partially initialized valid state. |
| Evaluate residual | Explicit candidate unknowns, source value and immutable previous history. Residual-only evaluation remains separately callable for finite differences. | Fixed-capacity residual and optional analytic Jacobian; no persistent mutation. |
| Advance one step | One source voltage at the next fixed grid time. Use bounded Newton, selected Schur elimination and transactional history. | Committed state/sample index only on success. On failure retain the last valid state and report the failed index. |
| Read diagnostics | Stable node/state identities and fixed-size typed diagnostic fields. | Formatting, file I/O, JSON and hashes remain outside the processing path. Unknown or unavailable values carry an explicit availability state. |

The planned numerical metadata must identify `formulation_id=control-branch-v1`, the fixed 31 ordered unknowns and their units, block counts `[4,6,11,5]`, boundary count 5, endpoint category, scaling, rank/condition settings and actual work limits. These are execution identity, not a change to physical-case identity. Original node names remain stable; no merged-node aliases or variant map enters the selected implementation. `R_on`, model ID and its approximation scope remain physical-model data under T21.

For T21 diagnostics, define `wet_switch_voltage_max_abs_V` as the maximum absolute `v(wet_send)-v(switch_common)` over committed samples, including the initial sample. A partial failed run labels its coverage; an unevaluated value is unavailable, not zero. This observation neither estimates real `V_GS` nor changes T18 pass/fail requirements.

## Named plan additions and verification obligations

These paths are planned files only. Every file must be enumerated in the final implementation section; no code/configuration/fixture is created by this proposal.

| Planned file | Required contents or change |
| --- | --- |
| `tests/control_endpoints.cpp` | Exercise all 27 T18 DC/Bode control triples, exact endpoint equalities, segment/terminal KCL, retained loads and the chosen partition. Check finite residual/Jacobian entries at each endpoint. |
| `tests/conditioning_and_scaling.cpp` | Qualify rank/condition/backward-error rules with identified singular, nearly singular and well-scaled algebraic fixtures. Verify that reporting units/scales do not silently change the physical solve. |
| `tests/fixtures/numerical_layout_cases.json` | Exact fixed node/unknown ordering, counts and endpoint constraints for all 27 control triples under T22-A; no B maps or aliases. |
| `tests/fixtures/numerical_failure_cases.json` | Named algebraic rank/condition failure inputs, exhausted-work paths and expected typed outcomes; separate algebraic manufactured fixtures from measured pedal evidence. |
| `tests/fixtures/dc_guess_cases.json` | The declared deterministic guess, source/rail values, endpoint consistency and explicit distinction from solved DC reference values. |
| `include/ts808/types.hpp`, `include/ts808/parameters.hpp` | Carry the chosen maps, fixed capacities, physical units and typed outcomes with the approved T20/T21 parameter identity. |
| `include/ts808/stages.hpp`, `src/stages.cpp`, `include/ts808/block_solve.hpp`, `src/block_solve.cpp` | Assemble the selected representation and partition, use scaled full-pivot solves and recover the full coupled increment without explicit inverses. |
| `include/ts808/newton.hpp`, `src/newton.cpp`, `include/ts808/model.hpp`, `src/model.cpp` | Apply the shared scales/merit, deterministic DC preparation and transactional solve/commit policy. |
| `tests/coupled_solver.cpp`, `tests/linear_and_history.cpp`, `tests/device_jacobians.cpp`, `tests/allocation_guard.cpp` | Verify normalized Schur/full increment agreement within `1e-9`, full backward error within `1e-10`, KCL/history invariants, endpoint derivatives and no prepared-step allocations, including failure paths. These are approved criteria, not passed tests. |
| `schemas/run.schema.json`, `schemas/report.schema.json`, `app/run_io.hpp`, `app/run_io.cpp`, `validation/ts808_validation/artifacts.py`, `validation/ts808_validation/reports.py` | Add formulation/dimension/condition provenance and the separately labeled T21 branch-voltage observation without altering the accepted numerical gates. |
| `reference/ts808/device_spec.md`, `reference/ts808/component_map.json`, `reference/ts808/ts808.cir`, `docs/artifact_format.md`, `docs/validation_protocol.md`, `tests/fixtures/README.md` | Describe the selected algebraic representation, stable trace identity, exact endpoint realization, evidence scope and fixture recipes. |

Use the full assembled solve only as an independent diagnostic on the same candidate Jacobian/right-hand side, not an automatic fallback after a block fails. Normalize the approved increment comparison by the same unknown scales, with `norm_inf(delta_S-delta_F)/max(1,norm_inf(delta_F)) <= 1e-9`. Both solves must first pass their rank/condition/backward-error checks. The later T18 suite still determines circuit accuracy and reference uncertainty; these algebraic checks cannot replace it.

## Approval boundary and next closure

T22-A and the common settings are approved. T22-B is unselected; do not ask for the same choice again. The accepted numerical values are initial qualification settings, not guarantees of stability or performance.

Carry this selected contract into the numerical/model/data documents and expand the named fixtures in the formal plan. The pending [T23 execution-tooling package](./ts808_execution_tooling_proposal.md) must freeze platform/LTspice workflow and compatible dependency/compiler/build/test versions; complete schema/API syntax follows in the formal section. Approval of that section, predecessor reconciliation, final publication and a separately requested `egm-review` still follow. This drafting work does not authorize production implementation.
