# TS808 design: predecessor reconciliation

* **Author:** Project owner and Codex
* **Date:** 2026-10-31
* **Scope:** egm-draft Step 6.1, following owner approval of the complete Detailed Implementation Plan and its interface/schema/fixture attachment. This is a comparison with the predecessor, not a Goldfish review, a readiness score, an executed test or physical validation.
* **Result:** No unresolved contradiction with an accepted predecessor requirement. Material additions are covered by the recorded owner decisions and the approved implementation section; no new architecture choice is inferred here.

## Contradictions

None unresolved. The predecessor explicitly labels its solver/model/tooling suggestions as proposals; resolving those open questions through later owner decisions is not a contradiction with an accepted requirement. The approved later decisions T1–T23 remain authoritative, including the same-host WSL clarification.

The owner's instruction authorizing this step was: "aprovo o plano e seu anexo para avançar à reconciliação com o predecessor". It approves the section/attachment and reconciliation, not production implementation or execution of `egm-review`.

## Compared artifacts and identities

| Input | Identity and role |
| --- | --- |
| [concepts_brief.md](../../concepts_brief.md) | Predecessor read in full. SHA-256 `dbb8c2d93a0fe057e1d6c4fe95d2939242fe7b4995401ba32006a77a6bb80568`. |
| [design_draft.md](../../design_draft.md) | Owner-approved content snapshot before editorial approval/reconciliation metadata updates: SHA-256 `83ff79872fd410829cb8e30843a6d9eb91aa3cf4ced7cb163238733e1aa822e8`. This identifies the reviewed snapshot, not the final publication bytes. |
| [Decision history T1–T23](./ts808_decisions.md) | Explicit later selections resolve predecessor proposals and establish material additions. Original decision records remain preserved. |
| [Interface/schema/fixture attachment](./ts808_offline_interface_spec.md) | Approved with the complete implementation section. Supplies exact APIs/artifacts and fixture recipes; no runtime files or results were produced. |

The comparison includes the draft's incorporated model, numerical, data, validation and execution contracts. No source from a temporary download, old Goldfish answer or external memory is needed to establish owner approval. Final publication has a separate destination gate and will have its own actual byte identity after writing.

## Accepted predecessor requirements retained

Quotes below are short exact excerpts from the predecessor and draft snapshot. An item deferred by the accepted staging remains a product requirement; this table does not claim it is implemented in the offline MVP.

| Accepted predecessor text | Draft text | Reconciliation |
| --- | --- | --- |
| "The MVP is the classic stock TS808 circuit processed offline with test signals and compared against LTspice." | "Build an offline C++ model of a selected classic TS808 circuit and compare its output and internal electrical behavior with LTspice." | Same first deliverable and reference path. |
| "Expand to TS9 and classic modifications only after the base passes agreed accuracy and runtime gates." | "TS9 and classic modifications follow successful accuracy and runtime gates." | Same accuracy, optimization and later-variant order. |
| "Preserve BJT buffers." | "Preserve input and output BJT buffers," | Both buffers remain in the extracted, loaded circuit; they are not replaced with ideal followers. |
| "Do not model the JRC4558's internal transistor topology." | "Simulating the JRC4558's internal transistor topology." | The quoted draft item is under Non-Goals. The selected external behavioral model preserves this boundary. |
| "SPICE numerical reference; null, Bode, THD and ABX validation" | "Compare DC operating points, small-signal Bode response, time-domain null residuals and THD/harmonic spectra against LTspice." and "Include controlled ABX listening in the validation path" | Numerical checks and actual human listening remain required, with separate outcomes and no fabricated completed results. |
| "48 kHz base rate" and "one to four instances; 64/128-sample buffers; compare 4x/8x internal processing" | "Ryzen 7-class desktop, 48 kHz base rate, 4x/8x oversampling candidates, one to four instances and 64/128-sample buffers." | The later runtime scenario is preserved; 192/384 kHz are the corresponding internal offline rates. |
| "below 5% CPU per instance as an incompletely specified target" and "zero added latency if feasible, otherwise below 1 ms" | "The target is below 5% CPU per instance under a defined benchmark and zero added latency if feasible, otherwise below 1 ms." | Targets remain future qualification requirements, not measured properties of the design. |
| "component customization with reproducible resistor tolerances." | "component substitutions, tolerance randomization or classic modifications in the offline MVP. These remain later product goals." | The draft excludes these from the fixed stock MVP, not from the accepted product destination. It does not replace the predecessor's reproducibility requirement with a different policy; exact later preset/randomization interfaces remain future work. |
| "3 MHz gain-bandwidth product and 1 V/us slew rate" | "3 MHz gain-bandwidth product and 1 V/us slew rate" | Same nominal starting behavior, with T20's explicit parameter provenance/limits and no physical 9 V calibration claim. |
| "No implementation is authorized by this brainstorm." | "All listed code/configuration/deck/fixture files are planned, not created." | Design and section approval remain distinct from implementing, compiling or simulating the circuit. |

The brief's accepted destination also names C++/JUCE VST3/CLAP. The draft preserves it verbatim as the eventual plugin direction while excluding host wrappers from the approved offline MVP. Neither architecture nor distribution/licensing decisions for that later wrapper are invented during finalization.

## Historical proposals and raised questions closed by approval

These differences are listed to avoid treating tentative brainstorm wording as a new approval gate. They are not open contradictions.

| Predecessor proposal or open topic | Selected draft behavior | Existing approval and limit |
| --- | --- | --- |
| "backward Euler for initial stability investigation" | Fixed-step trapezoidal integration. | T3 explicitly selected trapezoidal; the predecessor labels its recommendation as proposed. Reference refinement and ringing/convergence checks remain required. |
| "Proposed first benchmark cap: eight Newton iterations" | Initial caps of 32 transient iterations, 100 DC iterations and nine line-search lengths. | T16/T22 and the complete plan approval. These are offline work limits, not a later real-time CPU claim. |
| "Proposed rare-failure policy: preserve last valid state/output briefly, then bounded fade to silence and controlled restart" | Stop a failed offline case, retain committed history and diagnostic partial output. | T5 explicitly chose the offline failure policy; future live-audio recovery remains a later design question. |
| Semiconductor resistance/charge/Early extensions discussed in the analysis. | Reduced Shockley/Ebers–Moll laws in both realizations, with external circuit capacitors and op-amp states retained. | T14 selected the reduced baseline. T20 labels nominal data/temperature hypotheses. Numerical parity does not establish the physical insignificance of omitted effects. |
| Supply/bias/switching/noise/temperature described as open first-stage limits. | Ideal 9 V source, solved physical Vref RC/loading, fixed 25-degree baseline and static effect-on switching. | T4/T15/T18/T21. Real-gate characterization is explicitly outside the MVP; the conditional resistor is not a powered-pedal measurement. |
| Exact macromodel law/nominals were open. | Exactly linear central saturation transfer, shifted-tanh outer C2 knees, coupled recovery and the shared parameter vector. | T6/T19/T20. T21 separately closes `R_on`; no global amplitude-tanh or hard-knee option is reinstated. |
| "low-latency IIR is proposed for live use pending measured aliasing, phase and delay." | Common FIR only for offline listening; future plugin filters/aliasing/latency remain unselected. | T18. An offline listening filter does not decide the eventual plugin latency or satisfy its runtime gate. |
| "Validate mathematical and physical model agreement first" within the offline/LTspice staging. | The two realizations qualify the agreed reduced equations; hardware fidelity is explicitly limited by source/assumption quality. | T14/T20/T21 explicitly accept the scoped nominal model and its physical limitations. No physical pedal calibration or omitted-effect proof is silently asserted as completed, and no already-excluded gate characterization is restored as an MVP prerequisite. |

The predecessor's illustrative numerical limits and ABX suggestions were not marked accepted there. T8/T18 later accept and complete the finite validation contract. Keeping those accepted thresholds, including silence/uncertainty and recovery rules, does not authorize accepting unperformed tests. Later alias/runtime targets remain distinct from offline circuit acceptance.

## Material additions to architecture, interfaces or dependencies

The predecessor did not specify the following mechanisms or interfaces/dependencies at this level. All were selected through the recorded decisions or approved with the complete implementation section. No new confirmation of these same choices is needed.

| Addition | Effect on the design | Approval evidence |
| --- | --- | --- |
| Four coupled audio blocks with Schur elimination, fixed Eigen systems and exact endpoint-current equations. | Defines the internal component/solver boundary, numerical backend and 31-unknown map; retains shared Vref/loading. | T1/T2/T16/T22, including the common criteria and the complete implementation-section approval. |
| C++ executable/Python process boundary and explicit float64/JSON interchange. | Adds the CLI, 32-column trace layout, five-column AC response, schemas, typed failures, identities and integrity/publication semantics. | T11/T17/T22/T23 and the approved interface attachment. |
| Scientific analysis and native RAW reconstruction stack. | Introduces pinned NumPy/SciPy, PCHIP and spicelib, confined to development/analysis rather than the reusable core or audio callback. | T10/T11/T12/T23. RAW encoding/reconstruction compatibility remains future evidence. |
| Offline build/test/JSON/schema dependencies and exact root pins. | Adds C++20/GCC/CMake/Ninja, Catch2, nlohmann/json, Matplotlib/pytest/jsonschema and locked bootstrap tooling in their explicit scopes. | T23 common package, approved together with route B; the section enumerates all planned files and fixtures. No new plugin distribution/license conclusion is inferred. |
| Same-host WSL 2/native Windows reference orchestration. | Adds a PowerShell producer and local hashed request/result protocol, Windows-drive staging and direct shared RAW/log access; no Wine or manual inter-machine transport. | T23-B plus the owner's explicit WSL clarification and the approved implementation section/attachment. |
| Separate qualified listening preparation and concealed session/key artifacts. | Adds the shared offline FIR/encoding path and concrete ABX artifact/response bookkeeping without choosing the eventual plugin oversampler or adding an audio-device runtime. | T18/T23 and the approved interface/fixture attachment. Actual human participation is still required for combined validation. |

Source selection, passive values, exact device nominals and source/load/temperature/control fixtures close questions already raised by the brief. Their provenance/assumption labels remain in the model and validation contracts; they are not new unreviewed claims of measured physical precision.

## Finalization consequence

The owner approved all sections/attachments and confirmed the selected path with "Sim, salve o design final neste caminho". The [finalized design](./ts808_offline_design.md) is saved at `docs/designs/ts808_offline_design.md`, SHA-256 `f43641c6bf96551411bf15a6c23fbb3e43fca0c860f42b3624ce7f3d36b2f629`. Relative Markdown links were relocated for this directory; no constitutive equation, parameter, solver criterion, dependency or accepted scope was changed by finalization.

No `SITEMAP.md` existed in the destination, so none was created. The earlier RFC, working draft and predecessor were retained. The egm-draft workflow is complete. The next recommended step is `egm-review docs/designs/ts808_offline_design.md`, only when requested; the brainstorm reports are not a review of the finalized design. No implementation, installation, native circuit run, runtime/allocation measurement or ABX result is implied.
