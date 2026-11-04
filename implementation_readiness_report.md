# Stage 9 — Implementation Readiness Review

**Target:** [TS808 offline design](docs/designs/ts808_offline_design.md), DetailedRange 298–451. Full target read for context. SHA-256: `f43641c6bf96551411bf15a6c23fbb3e43fca0c860f42b3624ce7f3d36b2f629`.

> **Remediation — 2026-11-01:** A-001/IMP-001 and A-002/IMP-002 are addressed in the design contracts. See [persisted reference/suite handoff](docs/designs/ts808_offline_interface_spec.md#persisted-reference-and-suite-handoff) and [executable WAV rules](docs/designs/ts808_validation_contract.md#executable-wav-qualification-and-listening-grid). The unified plan now includes both schemas, explicit refined input and WAV qualification fixtures. This closes the two specification gaps locally; independent re-review and implementation/native measurements have not run. The findings and target hash below are preserved as the historical audit snapshot; the three editorial Nits remain outside this remediation.

**Result:** Changes required: **0 Blocker, 2 Major, 1 Nit** after deduplication. No design edits were applied. Actual implementation and qualification remain future work.

## Reviewer status

| Reviewer | Context | Status | Raw Blocker / Major / Nit | Complete result |
| --- | --- | --- | --- | --- |
| egm-implementation-readiness | Fresh | completed | 0 / 2 / 0 | [Readiness](review_reports/stage9_implementation_readiness.md) |
| egm-codebase-details | Fresh | completed | 0 / 1 / 0 | [Codebase](review_reports/stage9_codebase_details.md) |
| egm-style | Fresh | completed for editorial scope | 0 / 0 / 1 | [Style](review_reports/stage9_style.md) |

The first two read their installed personas and implementation-readiness standard; style read its persona without an additional standard. All three returned actual results and read ledgers. No reviewer failed or required a retry. Style's supplementary physical/numerical reads were truncated; it limits its conclusion to editorial wording grounded in the fully read target/interface/data contracts. It is not counted as a clean technical-completeness review.

## Prioritized findings

### IMP-001 — Major — Specify imported-reference and suite-index artifacts

**Sources:** IR-001 (Major), CB-001 (Major). **Scope:** target lines 349, 358, 387, 428–432; interface specification lines 81–115 and 129.

The stable `import-reference` command publishes a persisted directory consumed by standalone `compare`. Its exact manifest, fields, payload/locator layout and nominal/refined uncertainty-qualification linkage are unspecified. Native request/result schemas do not close this handoff; native completion explicitly differs from reference qualification. The suite similarly names `summary.json` without fixing its contract.

**Action:** Define exact filenames, versioned fields/types, original-file locators/hashes, analysis/trace/step identity, qualification linkage, integrity/completion/rejection rules and suite summary outcomes; enumerate any chosen schema and test the handoff. Preserve direct original RAW access.

**Strongest counterargument:** A single Python package can coordinate internal files. However, the declared stable independently invocable commands and zero-decision standard make this persisted interface a design obligation. Both reviewers independently found the reference gap; the suite-summary extension comes from IR-001. Both source severities remain Major.

### IMP-002 — Major — Define native WAV acceptance and exact listening windows

**Source:** IR-002 (Major). **Scope:** target lines 355–357, 391, 434, 442–444; validation-contract lines 61–65; tooling-contract line 55; interface lines 123,168–170.

The encoding, scale, FIR and filter-response requirements do not supply waveform-error metrics/limits and a fixed native rate/channel/time grid. Full FIR support does not uniquely select a retained listening interval or decimation phase.

**Action:** Fix native WAV rate/channel/timestamps, numerical reconstruction, comparison window/error limits and exact listening retained interval/phase/DC treatment at both rates. Name the report checks and corresponding fixtures.

**Strongest counterargument:** T8 null limits and FIR length could provide defaults. The text does not explicitly apply these gates to the separate encoding path or uniquely select the window. Severity remains Major because acceptance behavior would otherwise be chosen during implementation.

### IMP-003 — Nit — Describe single-case commands as previously specified interfaces

**Source:** ST9-001 (Nit). **Scope:** target line 422.

“Existing single-case commands” can imply executable commands exist, despite lines 300/399 clearly identifying future implementation.

**Action:** Use “The previously specified single-case interfaces remain the stable process boundary:”. Surrounding text already resolves the intent, limiting this to Nit.

## Traceability

| Raw ID | Raw severity | Normalized ID | Final severity |
| --- | --- | --- | --- |
| IR-001 | Major | IMP-001 | Major |
| CB-001 | Major | IMP-001 | Major; duplicate reference-handoff issue |
| IR-002 | Major | IMP-002 | Major |
| ST9-001 | Nit | IMP-003 | Nit |

## Limits

Planned creates are not missing implementation defects. Binary identities, dependency installation, native precision/compatibility, numerical performance/accuracy, allocation, resource use and human listening evidence remain unmeasured. No finding depends on an external API/version assertion; no external verification was needed for these findings. The raw ledgers distinguish complete operative reads, selected decision-log/duplicated inventory reads and style's truncated supplementary reads. No missing required operative input was called clean. No history/memory/handoff retrieval, production modification, installation, build or simulator run occurred. This stage is a single review audit, not two-round loop convergence.
