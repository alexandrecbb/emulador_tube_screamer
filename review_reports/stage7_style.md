# Stage 7 Style Critic Review

**Mode:** REVIEW. **Reviewer:** `egm-style`, fresh context, completed.  
**Target:** `docs/designs/ts808_offline_design.md`, FeatureRange 1–297.  
**Raw result:** 0 Blockers, 1 Major, 1 Nit. No additional style standard supplied.

## STF-001 — Major — Consolidate superseded drafting placeholders into the current specification

Affected scope:

- `docs/designs/ts808_offline_design.md:70`: “numerical/tooling and final plan readiness remain open.”
- `:117`: concrete signatures, serialization and CLI flags “will be fixed” in the implementation plan.
- `:144`: “remaining pins and conditioning details must be fixed.”
- `:193`: the DC node list “still need[s] the frozen circuit.”
- `:209`: test files, runner and constants “will be enumerated.”
- `:211`: heading “Staging and unresolved implementation contracts.”

These present/future statements appear in the active architecture prose without historical labels. They make the reader reconcile obsolete drafting stages with the approved current contract. The same feature states that T1–T23 close the choices at lines 215 and 263; lines 119, 148 and 181 already point to the selected interfaces, numerical criteria and tooling.

Supporting attachment evidence:

- `docs/designs/ts808_offline_interface_spec.md:5–9` identifies the attachment as approved and normative.
- `:37–69` supplies API declarations and numerical details.
- `:103–109` supplies trace layouts and case conventions.
- `:137` fixes DC comparison to all 24 physical unknown node voltages.
- `docs/designs/ts808_execution_tooling_proposal.md:23–35` supplies accepted build/dependency selections.
- `docs/designs/ts808_decisions.md:464` records complete implementation-section/attachment approval; line 5 explicitly establishes that later accepted decisions supersede earlier pending statements.

**Wording guidance:** Replace pending-decision language with direct references to the completed specification, while retaining future implementation and measurement obligations. For example:

- Line 117: “The approved interface specification defines the concrete C++ declarations, trace serialization and CLI commands.”
- Line 144: “T22 fixes the initial conditioning criteria; T23 fixes tool versions. Implementation must qualify these settings and record actual artifact identities.”
- Line 193 qualification: “Compare all 24 physical unknown node voltages, as enumerated in the interface specification.”
- Rename line 211 to “Delivery stages and qualification evidence.”
- Remove the closed drafting dependencies at lines 70 and 209, or explicitly label them historical.

This is an editorial current-state ambiguity, not evidence that the approved specifications are missing or that implementation has passed.

## STF-002 — Nit — Replace “one coupled Newton iteration” with “a coupled Newton solve”

**Affected scope:** `docs/designs/ts808_offline_design.md:132`.

“The model uses one coupled Newton iteration” can mean exactly one iteration per timestep. The surrounding algorithm and the 32-transient/100-DC iteration limits at line 146 establish an iterative coupled solve.

**Wording guidance:** “Each timestep uses a coupled Newton solve with analytical device stamps.” Keep “iteration” for an individual linearization/update within that solve.

## Read/search ledger

- Read the entire supplied persona: `/home/alexandre/.codex/plugins/cache/egm/egm/0.1.0/agents/style.md`.
- Read the complete target, lines 1–451; findings are restricted to lines 1–297.
- Read the locally linked model/reference documents: `ts808_reference_candidate.md`, `ts808_model_contract.md`, `ts808_model_data_proposal.md`, `ts808_switch_resistance_proposal.md`.
- Read numerical/data/validation/interface documents: `ts808_numerical_contract.md`, `ts808_numerical_closure_proposal.md`, `ts808_data_contract.md`, `ts808_validation_contract.md`, `ts808_execution_tooling_proposal.md`, `ts808_offline_interface_spec.md`.
- Read decision/precedence documents: `ts808_decisions.md`, `ts808_implementation_working.md`, `ts808_predecessor_reconciliation.md`, `tube_screamer_rfc.md`, `concepts_brief.md`, `goldfish_review_report.md`.
- Followed the historical report links and read `goldfish_reports/{design,codebase_details,zoom_out,comprehension,implementation_readiness,structural,concepts_brief_reviewed}.md`. Their brainstorm findings were treated as historical context, not current defects.
- Compared `design_draft.md` with the target and verified that their prose is identical after Markdown-link destinations are normalized.
- Used `rg` to locate headings, links and status language; used a read-only local link traversal to identify documentary references.

## Verification limits

This was a read-only editorial audit. No files were changed; no installation, build, simulation or test ran. No conversation history, memory or `SESSION_HANDOFF.md` was retrieved. External technical claims, source provenance and package availability were not independently verified, and no finding assumes they are false. Necessary electrical/numerical terminology and reproducible nominal precision were not treated as style defects.

Parent saved the complete reviewer result after actual completion. Raw severity is preserved; see `../critic_report.md` for consolidated triage.
