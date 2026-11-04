# Stage 9 — Codebase Details Reviewer (raw result)

Review status: **Changes required — 1 Major, 0 Blockers, 0 Nits.** Read-only review complete for the implementation scope and its necessary normative attachments. No files changed, builds run, tools installed or simulators invoked.

Independently confirmed scope: `docs/designs/ts808_offline_design.md:298–451` starts at `## Detailed Implementation Plan` and ends at `*Drafted with EGM*`. Read the entire target for context.

## CB-001 — Major — Imported-reference artifact contract remains unspecified

**Affected scope:** `docs/designs/ts808_offline_design.md:349`, `:387`, `:428–432`; normative attachment `docs/designs/ts808_offline_interface_spec.md:87–97`, `:129`.

The stable standalone CLI publishes an imported reference through:

```text
import-reference ... --output <new-reference-directory>
compare ... --reference <reference-directory>
```

However, the plan and normative attachments do not specify the imported-reference directory’s persisted contract: its manifest filename, versioned fields/layout, original RAW/log locators and hashes, or how nominal/refined references and their uncertainty-qualification evidence are linked for subsequent comparison.

The nine-schema table defines native producer requests/results, C++ runs and comparison reports, but no imported-reference artifact. In particular, attachment line 96 explicitly distinguishes native producer completion from uncertainty qualification. Attachment line 129 specifies import validation behavior and retention of original shared files, but does not supply the output structure consumed by the separate `compare` invocation. The data contract similarly states these CLI boundaries and provenance requirements without closing this handoff.

This leaves an externally observable, persisted interface decision to the implementer despite target line 304’s assurance that no absent file format is delegated. Two implementations could satisfy the validation prose yet produce incompatible reference directories or store qualification linkage differently.

**Recommendation:** Specify the imported-reference/index artifact in the normative attachment: exact filenames, versioned metadata and original-file reference rules, analysis/step/trace identities, nominal/refined qualification linkage, completion/integrity states and rejection behavior. Add its planned schema/file to the inventory if a separate schema is chosen, and cover the handoff with the planned artifact/CLI tests. Preserve direct reads of original shared RAW bytes; no new container or RAW-copy requirement is needed.

**Strongest counterargument:** Both commands belong to one Python package, so their internal on-disk handoff could be treated as an implementation detail. The plan already specifies the information that must be validated and retained. Nevertheless, these are independently invocable, stable process boundaries with persisted artifacts intended for reproducible reruns, and the applicable standard expressly disallows choosing a missing file format during implementation. A short explicit contract would close the issue without changing the approved architecture.

**Finding status:** Open.

**Codebase verification:** Repository inventory contains documentation and review artifacts; the planned C++, Python, schema, build and native-reference files do not currently exist. The implementation inventory explicitly marks entries as planned creates unless marked Modify. Their absence is therefore **not** a finding. No existing production implementation or reusable production/test infrastructure was available to audit. Future tool hashes, native encoding, numerical convergence, allocation behavior and qualification measurements were correctly treated as future evidence rather than missing design decisions.

## Actual read ledger

Read in full, using overlapping chunks where necessary:

- `/home/alexandre/.codex/plugins/cache/egm/egm/0.1.0/agents/codebase_details.md`
- `/home/alexandre/.codex/plugins/cache/egm/egm/0.1.0/resources/document_standards/implementation-readiness-standard.md`
- `docs/designs/ts808_offline_design.md`, lines 1–451; detailed review of 298–451.
- `docs/designs/ts808_offline_interface_spec.md`, lines 1–174.
- `docs/designs/ts808_model_contract.md`, lines 1–244.
- `docs/designs/ts808_model_data_proposal.md`, lines 1–185.
- `docs/designs/ts808_switch_resistance_proposal.md`, lines 1–84.
- `docs/designs/ts808_numerical_contract.md`, lines 1–87.
- `docs/designs/ts808_numerical_closure_proposal.md`, lines 1–176.
- `docs/designs/ts808_data_contract.md`, lines 1–116.
- `docs/designs/ts808_validation_contract.md`, lines 1–77.
- `docs/designs/ts808_execution_tooling_proposal.md`, lines 1–152.
- `docs/designs/ts808_reference_candidate.md`, lines 1–50.
- `docs/designs/ts808_decisions.md`, lines 1–473.
- `docs/designs/ts808_implementation_working.md`, lines 1–112.
- `docs/designs/ts808_predecessor_reconciliation.md`, lines 1–80.

Also inspected the repository file inventory and root directory listing, and searched all `docs/designs/ts808_*.md` attachments for reference-directory/schema/publication definitions.

No necessary normative attachment was missing or left unread. Did not retrieve conversation history, memory, `SESSION_HANDOFF.md`, prior review reports, or predecessor/RFC contents; those were not needed to establish this implementation-interface finding. No external/version/API assertion underlies CB-001, so external verification was unnecessary.

Saved by synthesizer after actual fresh-context reviewer completion; wording and severities preserved.
