# Consolidated design review

**Target:** [TS808 offline design](docs/designs/ts808_offline_design.md), 451 lines. FeatureRange: 1–297. DetailedRange: 298–451. SHA-256: `f43641c6bf96551411bf15a6c23fbb3e43fca0c860f42b3624ce7f3d36b2f629`.

> **Remediation — 2026-11-01:** A-001/IMP-001 and A-002/IMP-002 are addressed in the design contracts. See [persisted reference/suite handoff](docs/designs/ts808_offline_interface_spec.md#persisted-reference-and-suite-handoff) and [executable WAV rules](docs/designs/ts808_validation_contract.md#executable-wav-qualification-and-listening-grid). The unified plan now includes both schemas, explicit refined input and WAV qualification fixtures. This closes the two specification gaps locally; independent re-review and implementation/native measurements have not run. The findings and target hash below are preserved as the historical audit snapshot; the three editorial Nits remain outside this remediation.

**Outcome:** Changes required before implementation readiness. Two Major contract gaps and three editorial Nits remain open; no Blocker was established. The architecture and feature specification passed their lenses with editorial follow-up. This is a document review, not evidence that the model, simulator workflow or acceptance suite works. No design changes were applied.

## Prioritized actions

### A-001 — Major — Specify the persisted reference and suite-index contracts

**Evidence:** target lines 349, 358, 387, 428–432; [normative interface specification](docs/designs/ts808_offline_interface_spec.md), lines 81–115 and 129. Sources: IR-001 and CB-001.

`import-reference` publishes a directory consumed by a separate `compare` invocation. The normative schema list defines native request/result, C++ run and comparison report formats but leaves the imported-reference directory's manifest, fields and payload/locator representation unspecified. The suite also promises `summary.json` without defining its structure. Native producer completion explicitly does not establish uncertainty qualification (interface line 96).

**Action:** Define filenames, versioned fields/types, preserved RAW/log locators and hashes, analysis/step/trace identity, nominal/refined qualification linkage, integrity/completion/rejection rules and suite summary outcomes. Add any selected schema to the planned inventory and cover the handoff with the existing CLI/artifact test plan. This does not require copying RAW arrays or introducing a new container.

**Strongest counterargument:** One Python package owns these commands and could coordinate its internal representation. That reduces architecture risk, but independently invocable persisted process boundaries and the selected zero-decision standard still require the missing contract. Severity remains Major because implementation would otherwise select observable interface behavior.

### A-002 — Major — Fix executable WAV qualification and listening-window rules

**Evidence:** target lines 355–357, 391, 434 and 442–444; [validation contract](docs/designs/ts808_validation_contract.md), lines 61–65; [tooling contract](docs/designs/ts808_execution_tooling_proposal.md), line 55; interface specification lines 123 and 168–170. Source: IR-002.

Calibration, encoding, FIR recipe, filter-response limits and clipping rejection are specified. Mandatory native WAV qualification still lacks explicit waveform-error metrics/limits and a fixed rate/channel/time grid. Requiring an interior listening window with complete FIR support does not select its exact endpoints or decimation phase. These choices affect qualification and the listening stimulus.

**Action:** Define the native WAV rate/channel/timestamps, numerical reconstruction, comparison interval and error limits. Fix the listening pair's retained interval, delay/phase convention at both target rates and DC treatment. Give these rules named report checks and corresponding fixtures.

**Strongest counterargument:** Existing T8 null limits and the FIR support length could supply defaults. The text does not explicitly apply those limits to the separate WAV path, and full support permits several windows. Retain Major because the missing choices alter acceptance behavior; future measured filter performance itself is not the defect.

### A-003 — Nit — Replace superseded pending-contract prose

**Evidence:** target lines 70, 117, 144, 193, 209 and heading 211 versus closure statements at 215/263 and normative links at 304–306. Interface lines 37–69 and 137 already define APIs and all 24 physical DC nodes. Related remnants: model-contract lines 9/21, numerical-contract lines 43/79, implementation-working line 9.

**Action:** State approved contracts directly and link their resolutions. Rename the staging heading around delivery and qualification. Preserve future tense for implementation, actual artifact identities and measurements.

**Strongest counterargument:** Later accepted decisions and normative precedence resolve the chronology. This is why the consolidated action remains Nit despite STF-001's raw Major. No approved architectural choice needs reopening.

### A-004 — Nit — Use “Newton solve” for the coupled timestep operation

**Evidence:** target line 132 says “one coupled Newton iteration”; line 146 supplies repeated-iteration caps. Sources: STF-002 and CRIT-002.

**Action:** Use “Each timestep uses a coupled Newton solve with analytical device stamps.” Reserve “iteration” for one update. The surrounding caps already resolve the intended algorithm.

### A-005 — Nit — Describe single-case commands as previously specified interfaces

**Evidence:** target line 422 versus explicit planned/future status at lines 300/399. Source: ST9-001 and IMP-003.

**Action:** Replace “The existing single-case commands” with “The previously specified single-case interfaces remain the stable process boundary:”. “Existing” can mean already documented, and the surrounding context resolves the intent; severity remains Nit.

## Complete finding traceability

Rows for stage-level IDs preserve their relationship to the underlying reviewer IDs; they are not counted as additional defects.

| Stage / source | Original finding | Source severity | Action | Consolidated severity / decision |
| --- | --- | --- | --- | --- |
| 5 zoom-out | ZO-001 | Nit | A-003 | Nit |
| 6 comprehension | COMP-001 | Nit | A-003 | Nit |
| 7 structural raw | STR-001 | Nit | A-003 | Nit |
| 7 style raw | STF-001 | Major | A-003 | Nit; explicit normative precedence resolves the apparent open decisions |
| 7 critic synthesis | CRIT-001 | Nit after triage | A-003 | Nit; includes STR-001/STF-001 |
| 7 style raw | STF-002 | Nit | A-004 | Nit |
| 7 critic synthesis | CRIT-002 | Nit | A-004 | Nit; includes STF-002 |
| 8 zoom-out | IZO-001 | Nit | A-003 | Nit; carried forward, not independent |
| 9 readiness raw | IR-001 | Major | A-001 | Major; includes suite-index extension |
| 9 codebase raw | CB-001 | Major | A-001 | Major; independent confirmation of reference handoff |
| 9 readiness raw | IR-002 | Major | A-002 | Major |
| 9 style raw | ST9-001 | Nit | A-005 | Nit |
| 9 synthesis | IMP-001 | Major | A-001 | Major; includes IR-001/CB-001 |
| 9 synthesis | IMP-002 | Major | A-002 | Major; includes IR-002 |
| 9 synthesis | IMP-003 | Nit | A-005 | Nit; includes ST9-001 |

## Stage and reviewer status

| Stage | Reviewer | Status | Source result: Blocker / Major / Nit | Report |
| --- | --- | --- | --- | --- |
| 5 initial zoom-out | egm-zoom-out | completed | 0 / 0 / 1 | [Stage 5](zoom_out_report.md) |
| 6 comprehension | egm-comprehension | completed | 0 / 0 / 1 | [Stage 6](comprehension_report.md) |
| 7 critic | egm-design | completed | 0 / 0 / 0 | [Raw design](review_reports/stage7_design.md) |
| 7 critic | egm-structural | completed | 0 / 0 / 1 | [Raw structure](review_reports/stage7_structural.md) |
| 7 critic | egm-style | completed | 0 / 1 / 1 | [Raw style](review_reports/stage7_style.md) |
| 7 synthesis | three lenses above | completed | 0 / 0 / 2 after triage | [Stage 7](critic_report.md) |
| 8 intermediate zoom-out | egm-zoom-out | completed after one usage-limit retry | 0 / 0 / 1 carried forward | [Stage 8](intermediate_zoom_out_report.md) |
| 9 readiness | egm-implementation-readiness | completed | 0 / 2 / 0 | [Raw readiness](review_reports/stage9_implementation_readiness.md) |
| 9 readiness | egm-codebase-details | completed | 0 / 1 / 0 | [Raw codebase](review_reports/stage9_codebase_details.md) |
| 9 readiness | egm-style | completed for editorial scope | 0 / 0 / 1 | [Raw style](review_reports/stage9_style.md) |
| 9 synthesis | three lenses above | completed | 0 / 2 / 1 after deduplication | [Stage 9](implementation_readiness_report.md) |

Stage 9's normalized report is [implementation_readiness_report.md](implementation_readiness_report.md). Each completed reviewer returned an actual report with its read ledger. Stage 9 readiness/codebase read the installed implementation-readiness standard; style has no additional standard. This is one audit per stage, not a claim of two-round review-loop convergence. No remediation loop was requested or run.

## Coverage and limits

The repository contains design documents and review artifacts, with no production implementation to exercise. Planned source, schema, deck and fixture paths are explicitly future creates; their absence is not a finding. Actual binary identities, dependency resolution, native RAW behavior, numerical convergence/conditioning, allocation, resource use, accuracy, WAV results and human ABX remain future evidence. Hardware fidelity is outside what numerical agreement with the selected reduced model can prove.

Reviewers used fresh conversation contexts. Their documentary coverage differs and is recorded in the linked ledgers: Stage 5 explicitly read `SESSION_HANDOFF.md` as a referenced documentary input; later stages excluded it, and Stage 9 did not retrieve handoff/history/memory context. This limits a claim of uniform context isolation across all stages. Stage 9 readiness read operative contracts in full but only selected decision-log sections and part of the duplicated working inventory; its raw report lists those limits. The target's unified implementation inventory was read fully. Stage 9 style explicitly reports truncated supplementary model-data/switch/numerical-closure reads; its wording finding uses fully read target/interface/data contracts. It makes no technical-completeness conclusion about those truncated passages. No unavailable required operative contract was counted as a clean read.

No current finding depends on an unverified external release, API or parameter claim. Stage 7 design recorded targeted primary-source checks: [ADI support on modified trap](https://ez.analog.com/design-tools-and-calculators/ltspice/f/q-a/571510/how-to-use-modified-trap-by-setting-a-option-for-it), [manufacturer command reference](https://github.com/analogdevicesinc/ltspice-reference/blob/main/ai_ref/SIMULATION-COMMANDS-REFERENCE.md) and [ADI background article](https://www.analog.com/en/resources/technical-articles/spice-differentiation.html). These do not prove selected-version behavior; actual qualification remains required. Other upstream versions, APIs, schematic transcriptions and physical parameters were not comprehensively reverified.

No production code, design text or historical brainstorm report was changed. No installation, build, simulator run or human listening result was produced. Local report links and the unchanged target hash were checked at delivery.
