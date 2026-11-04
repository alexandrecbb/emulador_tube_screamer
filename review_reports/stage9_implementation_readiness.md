# Stage 9 — Implementation Readiness Reviewer (raw result)

Implementation Readiness review — **FAIL: 2 Major findings; no Blockers or Nits.**

Scope independently confirmed: `docs/designs/ts808_offline_design.md:298–451`, beginning at “Detailed Implementation Plan” and ending at the EGM attribution. The full target was read for context. Planned implementation artifacts were treated as future creates, and future qualification measurements were not treated as missing design decisions.

## IR-001 — Major — Imported-reference and suite-index interfaces remain unspecified

Affected scope: target lines 349, 358, 387, 428–432; `ts808_offline_interface_spec.md:81–115,129`.

The stable process boundary makes `import-reference --output <new-reference-directory>` produce an artifact subsequently consumed by `compare --reference`. However, the normative artifact specification defines C++ traces and nine schemas without defining the imported-reference directory’s filenames, numerical container/layout, metadata structure, or how nominal/refined qualification results attach to it. Interface line 129 describes validation and index publication but does not close that contract. Target line 432 similarly introduces `summary.json`/`summary.md` without defining their machine-readable contract.

An engineer must therefore design a persistent interface between independently invocable commands. Choosing whether import stores reconstructed arrays, preserved adaptive samples, or locators into original RAW files also determines how a single reference supports both target grids.

Recommendation: specify the exact imported-reference and result-index directory layouts, metadata fields/types, array or locator representation, qualification/provenance linkage, and compatibility/failure rules. Specify the suite summary’s required structure and outcomes, and enumerate any additional schema files in the inventory.

Strongest counterargument: these formats are internal Python implementation details, and the original RAW remains authoritative. Nevertheless, the design explicitly exposes separate commands and promises exact artifact/schema contracts; a persisted producer/consumer boundary requires a documented representation under this review’s zero-decision rule.

Status: **Open**.

## IR-002 — Major — Mandatory WAV qualification lacks an executable acceptance rule

Affected scope: target lines 355–357, 391, 434, 442–444; `ts808_validation_contract.md:61–65`; `ts808_execution_tooling_proposal.md:55`; `ts808_offline_interface_spec.md:123,168–170`.

The design fixes calibration, encodings, FIR recipe, filter-response limits and clipping rejection. It also requires native WAV qualification against numerical traces before acceptance. It does not specify the numerical waveform-error limits for that native-WAV comparison, its exact sample rate/channel/time grid, or the exact retained listening window after FIR delay compensation. T18 instructs using an interior window with complete support, which admits multiple choices. These decisions affect which artifacts qualify and what listeners hear.

Recommendation: fix the native WAV sample rate/channel and timestamp convention, reference reconstruction and comparison window, and explicit error metrics/limits. Fix the listening pair’s exact retained interval and decimation phase at both input rates, plus the DC treatment. Link those rules to named report checks and fixtures.

Strongest counterargument: the existing T8 null gates and FIR support length could supply reasonable defaults. No text explicitly applies those gates to this separate encoding path, and complete support constrains a window without uniquely selecting it. The implementer would still choose acceptance behavior.

Status: **Open**.

## Actual read ledger

- Reviewer instructions and implementation-readiness standard: both entire files.
- `ts808_offline_design.md`: entire file, lines 1–451, using overlapping reads.
- `ts808_offline_interface_spec.md`: entire file, lines 1–174.
- `ts808_model_contract.md`: entire file, lines 1–244.
- `ts808_model_data_proposal.md`: entire file, lines 1–185.
- `ts808_switch_resistance_proposal.md`: entire file, lines 1–84.
- `ts808_numerical_closure_proposal.md`: entire file, lines 1–176.
- `ts808_execution_tooling_proposal.md`: entire file, lines 1–152.
- `ts808_data_contract.md`: entire file, lines 1–116.
- `ts808_numerical_contract.md`: entire file, lines 1–87.
- `ts808_validation_contract.md`: entire file, lines 1–77.
- `ts808_reference_candidate.md`: entire file, lines 1–50.
- `ts808_decisions.md`: section headings; T8/reference settings, lines 217–262; T13–T23 and approval/publication sections, lines 351–473. Earlier decisions were not reread because their operative contracts are expanded in the attachments above.
- `ts808_implementation_working.md`: partial read; consolidated inventory and milestone/readiness material. Its duplicated inventory was truncated; the normative unified inventory in the target was read completely.
- Historical predecessor resources/reconciliation were not read: outside this implementation-readiness assessment’s operative contracts. No handoff or conversation-memory retrieval occurred.

No required operative attachment was missing. No external/API/version assertion underlies these findings, so external verification was unnecessary. No files were written, and no build, simulation, installation or production modification was performed.

Saved by synthesizer after actual fresh-context reviewer completion; wording and severities preserved.
