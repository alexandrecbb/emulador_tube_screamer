# TS808 offline MVP: grouped data and tooling contract

**Approved amendment, 2026-11-04:** the
[substep revision](ts808_substep_revision.md) separates output-grid
`execution.rate_Hz` from optional paired `integration_rate_Hz`/`substeps`.
The new execution identity records both rates (768 kHz internal,192/384 kHz
output) and4/2 steps; physical-case identity excludes these execution settings.
Absent fields retain the historical single-step meaning. Case/run/report
schemas reject inconsistent pairs; finalization and comparison reject
configuration mismatches. Historical failures remain preserved.

* **Author:** Project owner and Codex
* **Date:** 2026-10-31
* **Status:** Owner selected T17's little-endian float64/JSON route and approved the complete implementation section/interface attachment on 2026-10-31. Predecessor reconciliation and [final publication](./ts808_offline_design.md) are complete. No schema/configuration/implementation files have been created.

## Boundary

This contract covers configuration, the C++/Python process boundary, numerical artifacts, provenance and reporting. The accepted binary LTspice RAW/spicelib import is unchanged. The format choice below concerns C++-generated traces and derived analysis artifacts, not replacing the simulator's RAW file format.

Parsing, file operations and serialization belong to the offline executable/Python tools. They do not enter the reusable C++ circuit core or the later audio callback. All proposed added dependencies are listed here for owner selection; versions/lock hashes must be frozen after the selected path is checked for compatibility.

## Shared proposed interface

Use a standalone C++ executable `ts808_offline` and a Python package `ts808_validation`; keep a process boundary rather than embedding Python or requiring a C++ Python-extension ABI. Proposed commands are interface specifications, not commands currently available in the repository:

```text
ts808_offline --case <case.json> --output <new-run-directory>
python -m ts808_validation import-reference --case <case.json> --raw <reference.raw> --log <reference.log> --output <new-reference-directory>
python -m ts808_validation compare --case <case.json> --run <run-directory> --reference <reference-directory> --output <new-report-directory>
```

Each invocation identifies a single case. A Python suite runner may enumerate cases using the same commands/contracts. Simulator execution is not implied by importing an existing RAW/log pair; automated LTspice launching and its development platform must be specified separately. No automatic simulator installation or dependency download occurs during a numerical run.

Propose JSON metadata/configuration in both options, using a pinned nlohmann/json dependency only in the C++ offline I/O target and Python's standard JSON facilities. The [upstream CMake documentation](https://json.nlohmann.me/integration/cmake/) describes the interface target and integration options. Do not leak JSON types or parsing exceptions into the circuit API. No additional binary runtime dependency is implied by that header-based I/O parser.

## Required case and run metadata

| Group | Required meaning |
| --- | --- |
| Identity | Schema version, case/model identifiers, exact component/device-spec versions and input file hashes. |
| Circuit | Frozen component-map/model identities, source/load, controls, supply/bias/static-switch parameters and temperature. No missing electrical parameter receives a silent guessed value. |
| Numerical configuration | Internal rate/timestep, solver tolerances/work caps, precision and build identity. Include the actual settings used, not just a preset label. |
| Stimulus | Type, units, amplitudes/frequencies/phases/timing and pre-stimulus DC value. Analytic test signals have the same continuous definition in both implementations. Input audio requires its own declared reconstruction semantics. |
| Grid and analysis | Time origin, sample count, sample-rate identity, node/channel selection and analysis windows. Compute times from origin/index/rate, not by accumulating floating-point h indefinitely. |
| Reference | Simulator version, effective directives/netlist/model hashes, RAW/log identity, analysis plot/step, original storage precision and reference-convergence settings. |
| Reconstruction | Reader/NumPy/SciPy versions, selected PCHIP implementation, source/target coverage and refinement qualification results. |
| Result | Model-run completion, failure stage/time/reason, solver work counts, trace format/shapes/units/hashes and per-check outcomes. Completion of C++ processing is not a numerical acceptance pass. |

Reject unknown major schema versions, absent required fields, invalid ranges/units, incompatible source/model hashes and ambiguous case/step identity. Serialize finite numeric metadata with enough digits to round-trip binary64; encode unavailable metrics as null plus a reason, never JSON NaN/Infinity or an invented zero.

T21-A closes the nominal model identity as `ts808-cerutti-reduced-v1`, including `R_on=383.29731360711594 Ohm` and the linked [conditional-switch assumptions](./ts808_switch_resistance_proposal.md). Actual gate characterization is outside the MVP, not a missing configuration field. Preserve the physical approximation labels and planned maximum wet-to-common voltage observation separately from T18 acceptance outcomes. Hash actual model/configuration bytes when they exist; do not invent hashes for planned artifacts.

The owner approved [T22-A and the common criteria](./ts808_numerical_closure_proposal.md). Record `formulation_id=control-branch-v1`, the 31 ordered unknowns, interior counts `[4,6,11,5]`, boundary count 5 and actual scaling/rank/condition/work settings. Carry the separately labeled `wet_switch_voltage_max_abs_V` observation with coverage/availability. These meanings are approved; no schema file has been implemented. The [concrete interface specification](./ts808_offline_interface_spec.md) expands syntax/layouts and API obligations for final section review, without reopening the selected representation.

The first committed sample must match the initialized DC state and the declared input at the time origin. Delayed signal onset tests avoid undefined history at a jump; any case with a discontinuity exactly at the origin needs explicit history/source semantics. The case matrix will fix those semantics before such a case is mandatory.

## Trace storage selection

### A. Explicit float64 binary traces with JSON sidecars

**Selected by the owner.** Binary writes use standard C++ stream I/O outside the core. Metadata parsing is separate and uses the header-based JSON tool already proposed in this contract.

* **Mechanism:** Write dense numerical trace arrays as little-endian IEEE-754 float64 in a fixed row-major layout. The JSON sidecar supplies schema version, shape, ordered node/channel names, units, time origin/grid, byte order and file hash. Include a timestamp column when stored samples are not represented completely by the declared regular grid. Preserve adaptive reference timestamps from the original RAW.
* **Trade-off:** Simple C++ writes, no numerical container runtime, and Python can use [NumPy fromfile](https://numpy.org/doc/stable/reference/generated/numpy.fromfile.html) or [memmap](https://numpy.org/doc/stable/reference/generated/numpy.memmap.html). A headerless binary file is not self-describing: metadata and payload must remain paired and checked.
* **Failure condition:** Wrong byte order/dtype/shape, missing metadata, size mismatch or mismatched hashes invalidates the artifact. Never guess layout from filename or host architecture. Explicit endian/schema rules address the portability limitation of unqualified raw-array dumps.

Use separate typed layouts for complex AC values, if C++ exports them, rather than silently casting complex values to real float64. Specify real/imaginary ordering and units in the final format document. No lossy compression of the numerical reference or C++ traces is permitted in this baseline.

### B. HDF5 numerical containers with JSON run configuration

**Not selected.** No HDF5/h5py dependency is introduced into this MVP plan.

* **Mechanism:** Use HDF5 datasets with explicit float64/complex storage types and named datasets/attributes. C++ offline I/O links the selected HDF5 implementation; Python reads it through h5py. Retain JSON case/run identity and check consistency with dataset metadata.
* **Trade-off:** Supports structured multi-node arrays, chunking and metadata facilities; adds compiled libraries plus h5py and their version/build coordination. The [h5py dataset documentation](https://docs.h5py.org/en/stable/high/dataset.html) describes shapes, dtypes and chunked access. These dependencies remain outside the circuit/plugin core.
* **Failure condition:** Unsupported filters/types, ambiguous dataset names, metadata inconsistency or accidental lossy storage invalidate the artifact. Container support does not make a trace correct or eliminate provenance/refinement tests.

## Outcomes and artifact publication

Propose one outcome vocabulary across the toolchain: completed model run, failed DC solve, failed transient solve, invalid configuration, invalid/unqualified reference, failed numerical gate and I/O failure. A report separately labels each required check passed, failed or not evaluated with a reason. A completed waveform cannot override an unqualified reference.

CLI exit zero means the requested operation succeeded: for model execution, a complete run; for comparison, every mandatory evaluated gate passed with all required data qualified. Nonzero codes distinguish invalid inputs, numerical solve failure, reference qualification failure, measured gate failure and I/O failure. Exact numeric code assignments belong to the final schema/interface document and must be covered by tests, not inferred by callers.

Write each run/report into a new directory, using incomplete-state metadata until its files/hashes are finalized. Preserve partial outputs with explicit failure state. Avoid overwriting prior evidence or treating the newest timestamp as proof that a result matches the current inputs. Hash source/config/model bytes independently; do not create a hash dependency cycle by hashing a manifest containing its own final hash.

Reports contain machine-readable metrics/provenance plus a human-readable Markdown report and standard plots for Bode, spectra, waveform/residual and convergence where relevant. Proposed plotting/test tools are Matplotlib and pytest in the Python development environment. WAV files remain separate calibrated artifacts with recorded full-scale conversion, encoding, rate and alignment; numeric trace acceptance does not bypass WAV qualification.

## Planned file additions to the inventory

Add `validation/ts808_validation/__main__.py` for module invocation, `schemas/case.schema.json`, `schemas/run.schema.json` and `schemas/report.schema.json` for the shared contracts, and `validation/tests/test_artifact_contract.py` for round-trip/types/units/shape/hash/incomplete-artifact checks. Extend the already planned C++ I/O, Python reference/reconstruction/metrics/report modules and `docs/artifact_format.md`. No schema or executable code is created during this proposal.

The selected route is specified below. Freeze dependency pins and schema files in the implementation section; this contract does not declare that missing device parameters, stimulus envelopes or validation thresholds have been resolved.

## Concrete layout for the selected route

For schema version 1, each C++ run directory contains `run.json` and `traces.f64le`. On a numerical failure, also write `failure.json`. The binary file has no embedded header. It is a row-major array of shape `[written_samples, columns]`, with 8-byte IEEE-754 float64 values explicitly serialized little-endian. Column zero is time in seconds; subsequent ordered columns are the selected node/branch/state quantities with units and sign conventions in `run.json`. Do not dump an Eigen object, padded struct or native-memory layout as the file format.

Metadata contains `schema_version`, `run_id`, `case_id`, `model_id`, `physical_case_sha256`, `execution_config`, `build`, `reference_identity`, `trace`, `completion`, and `diagnostics`. `trace` contains filename, dtype `<f8`, order `C`, shape, columns, payload byte length and integrity status/hash. Record requested and actually written sample counts separately. Each column has a stable identifier, quantity, SI unit and orientation where applicable.

Define the physical-case identity from the circuit/model, source/load, controls, temperature, stimulus and time windows. Keep execution settings such as the C++ internal rate/tolerances separate. This allows one qualified, sufficiently dense LTspice reference for the same continuous physical case to serve multiple C++ sample grids without pretending that the execution configurations are identical. Preserve both physical and execution identities in every comparison.

The expected payload size is `8 * written_samples * columns` bytes, checked with overflow-safe arithmetic. Zero-row failure artifacts are valid diagnostic artifacts but are not mappable as a nonempty array and cannot pass numerical gates. Time values must agree with the declared grid within a stated rounding budget; monotonicity, coverage, column identity and finite values remain mandatory.

Python may read the payload with numpy.fromfile using explicit dtype/shape, which allocates an in-memory array, or use a read-only numpy.memmap for file-backed access. Memory mapping avoids an initial full-file read, but later slicing/conversion and PCHIP/FFT operations may allocate. Do not claim zero-copy for fromfile or for the complete analysis pipeline.

Integrity finalization uses Python's standard hashlib after the C++ writer closes its files. The writer emits trace length/completion and an explicit pending-hash state; the Python finalizer checks lengths/configuration and adds the payload/source hashes before analysis accepts the artifact. Direct C++ runs can therefore produce useful outputs without a custom C++ SHA implementation. A pending/unverified hash is not a qualified reference or a complete evidence package. No manifest hashes itself.

For AC artifacts, use `response.f64le` with one frequency-in-Hz column and consecutive real/imaginary column pairs for each declared response, never a real cast of complex data. Its JSON metadata declares this layout and the response convention. Imported native complex RAW data remain preserved with source identity; the derived container does not replace the original.

Comparison output is `report.json` and `report.md`, with standard plots `bode.svg`, `spectrum.svg`, and `residual.svg` only for applicable analysis types. Every plot used is enumerated in the report; absent/inapplicable plots are distinguished from failed generation. Large numerical arrays stay out of JSON/Markdown. Separate calibrated listening/WAV artifacts have their own file identities.

### Exit and failure semantics

Reserve exit code 0 for a successful requested operation; 10 for invalid configuration/schema; 20 for failed DC solve; 21 for failed transient solve; 30 for missing/invalid reference; 31 for unqualified reference uncertainty; 40 for a measured acceptance-gate failure; 50 for I/O failure. An unhandled internal error uses 70 and cannot produce a passing result. A completed model command with exit 0 is not a passing comparison; the comparison command applies the required gates.

Inside the core, return fixed-size typed failure information. The offline executable creates `failure.json` after leaving the allocation-guarded step region, with stage, case/step/time, reason, residual/increment norms, iteration counts and the last valid state identity. Report unavailable quantities as unavailable; never store nonfinite values as valid JSON numbers. Interrupted or truncated artifacts retain incomplete completion state and require requalification or a new run.

### Owner decision T17

The owner selected the simple binary/JSON route to avoid compiled numerical-container dependencies and permit direct NumPy reads/mapping. Carry this format and the grouped interface semantics into the final implementation review. This acceptance does not assert zero-copy processing, eliminate the JSON I/O dependency, or fill in unknown reference model values.

## Approved T23-B execution/tooling package

The owner approved [T23-B and the common package](./ts808_execution_tooling_proposal.md): exact root versions, native Linux build/test/analysis, nlohmann/json offline I/O, Python Draft 2020-12 validation, WAV encoding and native reference settings. The owner clarified WSL 2 on the same Windows host. Python invokes the native PowerShell helper and reads closed RAW/log files through a shared drive; requests/results preserve identity/completion without manual transport or Wine. Native process lifetime/path/file visibility are qualification obligations, not an added remote service.

The approved [interface attachment](./ts808_offline_interface_spec.md) specifies nine schema contracts, exact trace/response ordering, local publication and canonical/hash rules in Markdown. The formal implementation section enumerates every planned schema/API/fixture file and is approved. No schema, producer, code or acceptance result has been implemented by this documentation update.
