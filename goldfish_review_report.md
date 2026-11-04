# Goldfish Review Report

**Target:** `concepts_brief.md`, original 70-line working hypothesis; preserved in [reviewed snapshot](goldfish_reports/concepts_brief_reviewed.md).

**Mode:** BRAINSTORM. Six independent fresh-context reviewers read the target, exact persona, brainstorm skill standard and Codex integration. They saw no parent history or other findings. Two ran concurrently in each of three waves due to four total slots including root/synthesizer. Reviewers were read-only; the synthesizer persisted their reports with condensed wording. Native completion results retain full returned reports. This is a concept critique, not approval to implement or evidence that performance targets pass.

## Reviewer Status

| Reviewer | Status | Report |
| --- | --- | --- |
| `egm-design` | completed | [design](goldfish_reports/design.md) |
| `egm-codebase-details` | completed | [details](goldfish_reports/codebase_details.md) |
| `egm-zoom-out` | completed | [zoom out](goldfish_reports/zoom_out.md) |
| `egm-comprehension` | completed | [comprehension](goldfish_reports/comprehension.md) |
| `egm-implementation-readiness` | completed | [compatibility](goldfish_reports/implementation_readiness.md) |
| `egm-structural` | completed | [maintainability](goldfish_reports/structural.md) |

Raw reviewer counts: 0 Blocker, 28 Major, 1 Nit. Deduplicated below: 0 Blocker, 8 Major, 1 Nit. No finding is a validated implementation failure: there is no implementation. All reviewers listed their files read; no missing read was reported.

## Prioritized Findings (Blockers -> Major -> Nits)

### Undefined performance and accuracy contract — Severity: Major

* **Reviewer Lens:** `egm-design`, `egm-zoom-out`, `egm-codebase-details`
* **Affected Scope:** Confirmed live-use constraints; validation; solver comparison.
* **Discrepancy Description:** A percentage without a benchmark definition cannot select a solver. Four instances share a host deadline; numerical/filter thresholds are open.
* **Rationale & Recommendation:** Freeze machine/host/channels/meter, finite test matrix and callback margin. Compare error, aliasing, latency and observed worst-case work together. The synthesis adds clearly tentative gates and equations, not accepted or achieved values.

### Unbounded substitutions and unclear staging — Severity: Major

* **Reviewer Lens:** `egm-design`, `egm-zoom-out`, `egm-structural`
* **Affected Scope:** Component customization; goals; next steps.
* **Discrepancy Description:** Arbitrary device values multiply convergence and validation work; three solver implementations and two circuits/formats could expand work before feasibility is known.
* **Rationale & Recommendation:** Propose a fixed stock offline milestone, bounded named substitutions, paper solver comparison, then one prototype; retain the accepted full destination. Boundaries require owner agreement.

### State transitions and solver recovery are unspecified — Severity: Major

* **Reviewer Lens:** All six reviewers
* **Affected Scope:** Automation, components, quality changes, nonconvergence.
* **Discrepancy Description:** Stored circuit energy, expensive rebuilds, oversampling latency and failed solves interact; iteration caps alone do not define valid output.
* **Rationale & Recommendation:** Separate continuous controls from structural settings, prepare outside audio callbacks, define commit/recovery/fallback policy and measure peak transition work. Brief proposes a stopped-playback restriction and bounded fade/restart, both awaiting approval.

### Session sound and future-version behavior are undefined — Severity: Major

* **Reviewer Lens:** `egm-comprehension`, `egm-implementation-readiness`, `egm-structural`
* **Affected Scope:** Reproducible tolerance and saved settings.
* **Discrepancy Description:** Seeds and control values do not preserve sound if model interpretation, parameter meanings or solver behavior changes.
* **Rationale & Recommendation:** Save exact realized components, model/schema versions, calibration and quality; stabilize IDs and define unknown/future-state and downgrade behavior before distribution. No current sessions justify an immediate migration system.

### Reference scope and provenance may drift — Severity: Major

* **Reviewer Lens:** `egm-design`, `egm-structural`, `egm-codebase-details`
* **Affected Scope:** Supply/Vref; SPICE reference; device models.
* **Discrepancy Description:** Ideal versus dynamic supply/bias and multiple copies of model values can create comparisons between different circuits.
* **Rationale & Recommendation:** Freeze versioned reference packages, source/load, operating point, device provenance/rights and corresponding state metadata. Circuit-only and filtered end-to-end null tests must be separate. Supply/bias scope stays provisional.

### Reproduction and failure diagnostics are missing — Severity: Major

* **Reviewer Lens:** `egm-codebase-details`
* **Affected Scope:** Validation, timing, failure recovery.
* **Discrepancy Description:** Aggregate audio errors cannot locate bias/stage/solver/filter defects; timing instrumentation itself can cause dropouts.
* **Rationale & Recommendation:** Use offline named-node traces and reproducible run/event manifests, bounded counters and nonblocking diagnostic transfer. Record distributions/maxima/overruns. User audio capture is opt-in; no remote telemetry is warranted.

### User and host contracts are unresolved — Severity: Major

* **Reviewer Lens:** `egm-comprehension`, `egm-implementation-readiness`
* **Affected Scope:** Loading stock sounds, quality, bypass, calibration.
* **Discrepancy Description:** No defaults, voltage mapping, channel layout, model-switch semantics, restore-stock action or quality ownership is established.
* **Rationale & Recommendation:** Describe the stock-to-custom workflow and predictable unsupported-state/failure indication. Resolve volts-per-full-scale, layouts, bypass and live quality behavior before design approval; synthesis marks them open.

### Framework and numerical coupling would impede maintenance — Severity: Major

* **Reviewer Lens:** `egm-structural`
* **Affected Scope:** JUCE/CLAP/VST3; numerical engine.
* **Discrepancy Description:** Unseparated circuit, format and parameter logic would make solver comparisons and framework changes expensive.
* **Rationale & Recommendation:** Use one host-independent core for offline tools and wrappers; verify CLAP integration/license pins before commitment. Avoid a speculative general circuit editor/framework.

### Reuse candidates need explicit verification — Severity: Nit

* **Reviewer Lens:** `egm-zoom-out`
* **Affected Scope:** Architecture/dependencies.
* **Discrepancy Description:** Repository search found no existing DSP/build code. Framework-provided parameters, smoothing, state and oversampling should be assessed before custom equivalents.
* **Rationale & Recommendation:** Identify this as a new implementation; investigate JUCE and CLAP extension facilities rather than claiming existing integration. Synthesis links verified upstream documentation/license inventory while leaving release choices open.

## Synthesis Disposition

The updated [brief](concepts_brief.md) addresses mechanisms and introduces provisional recommendations; it does not resolve owner decisions. Exact schematic/models, calibration, supply/bias scope, machine/host/platform, substitution catalog, live-change policy, state compatibility, acceptance gates and distribution license remain open. No code, build, numerical measurement or listening test was run. Final owner alignment is still required before a formal design draft.
