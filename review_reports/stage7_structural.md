# Stage 7 Structural Critic Review

**Mode:** REVIEW. **Reviewer:** `egm-structural`, fresh context, completed.  
**Active scope:** `docs/designs/ts808_offline_design.md:1–297`; lines 298–451 read for context.  
**Result:** 0 Blocker, 0 Major, 1 Nit. All required local inputs were accessible.

## STR-001 — Nit — Historical pending statements remain embedded in the finalized architecture

**Evidence:**

- `docs/designs/ts808_offline_design.md:70` says numerical/tooling and final-plan readiness “remain open.”
- `docs/designs/ts808_offline_design.md:144` says remaining pins and conditioning details must still be fixed.
- `docs/designs/ts808_offline_design.md:193` says the node list still needs the frozen circuit.
- Conversely, `docs/designs/ts808_offline_design.md:148` supplies approved conditioning criteria, and lines 215 and 263 explicitly close T1–T23 and drafting decisions. The normative interface attachment fixes the ordered unknowns at `docs/designs/ts808_offline_interface_spec.md:19–25` and required DC node coverage at line 137.

**Consequence:** A fresh reader encounters present-tense pending work after the document declares these contracts closed. The selected contracts remain discoverable, so this is editorial ambiguity rather than a missing architecture decision.

**Guidance:** Replace these pending statements with links to their approved resolutions; describe actual implementation and qualification results separately as future evidence. Rename the subsection at line 211 accordingly. Preserve genuinely historical pending statements in decision history, clearly labeled as historical.

## Heading map

Active scope contains one H1, ten H2s and fourteen H3s:

- H1, line 1: TS808 circuit model: offline validation and real-time path.
- H2, line 7: Overview.
- H2, line 15: The Problem.
- H2, line 21: Goals.
- H2, line 31: Non-Goals.
- H2, line 40: Critical User Journeys; H3 at lines 42, 48, 54: reproduce comparison, locate discrepancy, verify optimization.
- H2, line 60: Technical Plan; H3 at lines 64, 98, 121, 154, 162, 187, 211: model boundary, ownership/data flow, solver, initialization, reference protocol, measurement/tests, staging.
- H2, line 217: Alternatives Considered; H3 at lines 221, 232, 244, 255: circuit/model scope, numerical execution, reference pipeline, later options.
- H2, line 261: Open Questions.
- H2, line 269: Additional Resources.
- H2, line 288: Non-Functional Requirements.

Context beyond the range consists of Detailed Implementation Plan, line 298, with five H3 subsections, and Drafting Sequence, line 447. Heading nesting is sequential and logical throughout.

## Standard compliance and evidence placement

The feature-spec standard requires content, including alternatives and explicit risks/limits; it does not mandate exact section titles or order.

- Problem and motivation: target lines 15–19.
- Goals/non-goals: lines 21–38.
- Architecture, ownership, data flow and integration: lines 60–215.
- Mandatory alternatives evaluation: lines 217–259 contain benefits, limitations and dispositions. Later detailed choices also retain alternatives: Eigen/LAPACK in the numerical contract; binary/HDF5 in the data contract; knee laws, switch characterization, endpoint formulations and producer routes in their respective approved attachments.
- Failure modes and mitigations: target lines 142–158, 177–205 and 290–296; numerical contract lines 18–41; numerical-closure contract lines 100–118.
- Physical limitations: target lines 19, 74, 84, 96 and 267; model-data and switch contracts distinguish assumptions from hardware evidence.
- Security implications: manifest path confinement at interface-spec line 85; argument-array invocation and execution-policy handling at lines 125–127; tooling-contract lines 61, 97–99 and 113 cover shell expansion, process ownership and local schema resolution.
- Scalability/resource limits: target lines 290–296 and validation-contract lines 19–21 address bounded core work, serial reference production, dense-reference storage and measured pilot resources.

No missing risk or alternatives finding is justified merely because some evidence appears in incorporated attachments.

## Formatting and links

Static inspection found no skipped heading levels, five balanced fenced blocks in the active range (including Mermaid), five tables with consistent column counts, and all sixteen distinct direct local documentary targets present. Across the documentary set, 173 local Markdown links were checked; no missing local targets or unresolved heading fragments were found. Target SHA-256: `f43641c6bf96551411bf15a6c23fbb3e43fca0c860f42b3624ce7f3d36b2f629`.

## Document authority and context

Normative supporting material comprises the approved decisions, reference extraction, model/model-data/switch contracts, numerical/numerical-closure contracts, execution contract, data contract, validation contract and interface specification. The interface specification establishes their normative relationship at lines 7–9.

`concepts_brief.md`, the RFC, predecessor reconciliation and brainstorm reports provide history/provenance. `goldfish_review_report.md:3–5` reviews the original concept in BRAINSTORM mode; it is not approval of this finalized design. The implementation working inventory identifies the final design as its authoritative inventory.

Code, schemas, decks, fixtures and documentation listed as planned creations in target lines 310–375 are future deliverables. Their absence is not a broken-link or missing-review-input finding.

## Read/search ledger

Read in full: structural persona and supplied feature-spec standard; target and all fourteen other Markdown files under `docs/designs/`; `concepts_brief.md`, `goldfish_review_report.md`; all seven files under `goldfish_reports/`. `design_draft.md` was checked against the fully read target: identical text after normalization of relocated relative links.

Read-only checks: documentary enumeration; heading/link extraction; local target/anchor resolution; fence/table checks; draft comparison; publication hash verification. A failed `python` invocation was repeated successfully with `python3`.

**Limits:** External URLs were not fetched, Mermaid was not rendered, and no implementation, build, simulation or numerical behavior was tested. Conversation history, memory and `SESSION_HANDOFF.md` were not retrieved. No files were changed. Parent saved the reviewer result after actual completion; heading-map formatting was flattened without changing content.
