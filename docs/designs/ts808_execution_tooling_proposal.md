# TS808 offline MVP: approved WSL 2 and native Windows execution contract

* **Author:** Project owner and Codex
* **Date:** 2026-10-31
* **Status:** T23-B and the documented common package approved by the owner on 2026-10-31. T1–T23 remain approved. Linux runs under WSL 2 on the same physical Windows host; native LTspice is orchestrated through WSL interoperability and a shared filesystem. T23-A/Wine is unselected. No tools were installed, production code/configuration created, build performed or circuit simulated. The filename retains the proposal history.

## Boundary and observed environment

The mathematical model is `ts808-cerutti-reduced-v1`; the numerical formulation is the approved `control-branch-v1`, with 31 unknowns, interiors 4/6/11/5 and boundary 5. Preserve T1–T23. Actual JFET gate characterization remains outside the MVP. This contract selects how to build/test the offline tools and produce/import identified LTspice references; it does not select a plugin platform or claim runtime readiness.

Read-only inspection found Ubuntu 26.04.1 LTS, x86-64, and standard CPython 3.14.4 (`Py_GIL_DISABLED=0`). The owner clarified that this is WSL 2 on the same physical Windows machine. Subsequent read-only probes confirmed kernel `6.18.33.2-microsoft-standard-WSL2`, `wslpath`/Windows executable interoperability, Windows 11 Pro build 26300 and Windows PowerShell `5.1.26100.9818`. No C++ compiler/CMake/Ninja was found on the Linux PATH; LTspice was not located in the three checked conventional paths or matching uninstall-registry entries. This is not a complete installation search. Setup must locate/provision the approved executable and verify its actual version/hash before running references.

The selected profile keeps C++ model processing and Python analysis native in Ubuntu/WSL 2, and executes LTspice natively on its Windows host. The common dependencies and simulator settings below are approved with T23-B. No Wine qualification, remote Windows service, separate-machine transfer or manual copying of RAW files is required for this baseline.

## Owner decision T23 and WSL clarification

The owner stated: "Aprovo a Rota B (Linux + Windows nativo), incluindo o pacote comum documentado." They explicitly clarified WSL 2 on the same Windows machine, with native batch invocation through WSL interoperability and direct access to shared RAW files. This refines B's producer connection; it does not reopen the route or introduce another architecture gate.

Use `execution_profile=wsl2-windows-native-v1`. The logical request/result boundary still records inputs, producer identity and completion, but it is a local shared-directory protocol. No remote transfer is part of its completion criteria. Tooling installation, simulator availability and reference qualification remain future implementation evidence, not results of this approval.

## Approved common C++ and build package

| Item | Exact initial selection | Scope and reason |
| --- | --- | --- |
| Language/compiler | C++20, GCC 15.3.0 | One qualification compiler for the offline baseline. C++20 permits fixed array/span-style APIs without a Python ABI in the core. The [GCC 15 release record](https://gcc.gnu.org/gcc-15/) identifies 15.3; it is not claimed to be installed or available in a particular apt repository. |
| Build and test driver | [CMake 4.4.5](https://github.com/Kitware/CMake/releases/tag/v4.4.5), its matching CTest, [Ninja 1.13.2](https://github.com/ninja-build/ninja/releases/tag/v1.13.2) | Named configure/build/test presets; no dependency downloads during model or comparison runs. |
| Numerical library | [Eigen 5.0.1](https://gitlab.com/libeigen/eigen/-/releases/5.0.1) | The only third-party library in the circuit core; fixed-size binary64 matrices and `FullPivLU` under T16/T22. No BLAS/LAPACK backend is introduced. |
| C++ JSON reader | [nlohmann/json 3.12.0](https://github.com/nlohmann/json/releases/tag/v3.12.0) | Offline I/O target only. Schema meaning and JSON exceptions do not cross into the core. T23-B closes the previously proposed reader/version. |
| C++ test framework | [Catch2 3.16.1](https://github.com/catchorg/Catch2/releases/tag/v3.16.1) | Tests only, registered with CTest. Keep the planned `tests/test_main.cpp` as the test runner; do not link framework code into the circuit library or executable. |
| Baseline optimization | `-O2 -fno-fast-math -ffp-contract=off`, no `-march=native` or link-time optimization | Freeze the initial qualification path and record actual compiler/link flags. Later optimization requires the same accuracy checks. No speed claim follows from these flags. |
| Diagnostic configuration | Assertions active, Eigen runtime allocation guard plus the planned application allocation checks | Compile a checked core/test target from the same sources. Guard prepared stepping, including failure paths; prepare, JSON and reporting remain outside that region. |

The Eigen 5.0.1 [FullPivLU source](https://gitlab.com/libeigen/eigen/-/blob/5.0.1/Eigen/src/LU/FullPivLU.h) was inspected for `setThreshold`, `rcond` and its constant-success `info()` behavior. That establishes the selected API exists, not that T22's accepted cutoffs or allocation requirements have passed on the circuit.

Freeze dependency source archives/commits and actual SHA-256 identities in the future build specification. Require exact selected versions at configure/preflight, rather than silently accepting whichever package is installed. Actual tool binaries, OS package revisions and their identities are collected during authorized setup; no fabricated binary hashes appear in this design. A root-version change requires an explicit tooling revision, not an automatic update after a failed build.

## Approved common Python analysis package

Use a dedicated standard CPython 3.14.4 environment, with the normal GIL-enabled ABI. Do not use a free-threaded interpreter or depend on the system environment's unrelated packages. The initial direct package pins are:

| Package | Pin and primary metadata | Use |
| --- | --- | --- |
| NumPy | [2.5.4](https://pypi.org/project/numpy/2.5.4/) | Float64 arrays, file mapping and the already selected FFT path. |
| SciPy | [1.18.1](https://pypi.org/project/scipy/1.18.1/) | Accepted PCHIP/filter/statistical operations and WAV I/O. |
| spicelib | [1.6.4](https://pypi.org/project/spicelib/1.6.4/) | The selected `RawRead` import, confined to development/analysis. |
| Matplotlib | [3.11.2](https://pypi.org/project/matplotlib/3.11.2/) | SVG reports with a noninteractive backend. |
| pytest | [9.2.0](https://pypi.org/project/pytest/9.2.0/) | Python analysis/interface tests. |
| jsonschema | [4.26.0](https://pypi.org/project/jsonschema/4.26.0/) | Analysis-only dependency for explicit Draft 2020-12 validation. |
| Bootstrap/lock tools | [pip 26.2.2](https://pypi.org/project/pip/26.2.2/), [pip-tools 7.6.2](https://pypi.org/project/pip-tools/7.6.2/) | Reproduce the analysis dependency lock during setup, outside circuit processing. |

Maintainer metadata was checked on 2026-10-31. It supplies CPython 3.14-compatible Linux wheels for the listed numerical packages; SciPy 1.18.1 declares NumPy `>=2.0.0,<2.8`, which contains the accepted 2.5.4 pin. These are metadata checks, not a solved/installed environment or an import/RAW-compatibility test. No yanked direct release was selected.

The final `validation/requirements.lock` must pin all resolved transitives and artifact hashes for this Linux/Python environment, including spicelib's declared `clipin`/`psutil` and the plotting/schema dependencies. Pin bootstrap tools separately in `validation/bootstrap-requirements.lock`. Resolve/freeze once during authorized setup; normal runs install nothing and never update a lock. If the root pins cannot be resolved or their tests fail, record that incompatibility and revise the package explicitly.

Use Python's standard JSON/hash libraries and [SciPy WAV read](https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.read.html)/[write](https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.write.html). No SoundFile/libsndfile, HDF5 or Python interpreter in the C++ core is added. Use the approved 32-bit float encoding for derived listening WAVs, with T18's unchanged 8 V/full-scale calibration and matched filtering; request 32-bit PCM for the separate native LTspice WAV check and verify its actual header/encoding. Reject clipping and qualify each WAV path against the numerical traces; 32 bits alone is not qualification.

## Approved common LTspice reference protocol

Pin the Windows x64 release **LTspice 26.1.1**, listed on the [manufacturer download page](https://www.analog.com/en/resources/design-tools-and-calculators/ltspice-simulator.html) when checked on 2026-10-31. Its [command-line reference](https://github.com/analogdevicesinc/ltspice-reference/blob/main/ai_ref/LTSPICE-QUICKSTART.md) documents batch `-b`. Reader compatibility with its generated original RAW still requires qualification; Wine compatibility is not a selected requirement.

Use the declared executable path and an isolated, new working directory per case/refinement. Archive the actual executable version/hash, OS/runtime identity, effective netlist, local model bytes, command arguments, settings, stdout/stderr, simulator log and original RAW. Pass arguments as an array; paths with spaces remain single arguments. No shell expansion, source download, library update or network transfer occurs in a numerical run.

The accepted mandatory settings remain `.options plotwinsize=0`, `.options reltol=1e-6` and `.options numdgt=15`, plus T18's maxstep bound/refinement. T23-B also approves the remaining initial reference settings:

| Setting | Nominal / refinement rule |
| --- | --- |
| Integration | Request `.options method=trap`; verify the effective classic trapezoidal setting in the simulator log/configuration. Modified-trap output processing or Gear is not an unrecorded substitute. |
| Absolute tolerances | Nominal `abstol=1e-12 A`, `vntol=1e-9 V`, `chgtol=1e-16 C`; refinement uses one tenth of each. |
| Transient error control | `trtol=1` in nominal and refined runs. |
| Junction numerical conductance | Explicit `gmin=1e-12 S`; audit any effect on a native junction realization within the reference-uncertainty budget. Do not silently stamp a new C++ physical resistor. |
| DC aids | Explicit `gminsteps=0`, `srcsteps=0` for the baseline; no `uic` or `startup`. A failure is recorded rather than silently enabling a different DC protocol. |
| Reference refinement | Shared nominal maxstep `<=1/(384000*8) s`, then half maxstep and `reltol=1e-7` with the tighter absolute tolerances. Preserve independent storage/reconstruction qualification and the aggregate uncertainty budget. |
| Run management | One reference process at a time; initial wall timeout 1800 s per invocation, recorded as execution policy. A timed-out run remains incomplete/unqualified; changing timeout cannot turn it into a numerical pass. |

The manufacturer [simulation-command reference](https://github.com/analogdevicesinc/ltspice-reference/blob/main/ai_ref/SIMULATION-COMMANDS-REFERENCE.md) is the source for option meanings; values above are accepted initial project settings. Preflight must confirm the selected release accepts them and the effective configuration matches the request. No relaxation, alternate integration, automatic retry or reference reuse after a hash/case mismatch is allowed.

Keep RAW float64 storage checks under T12; `numdgt=15` or a float64 NumPy result does not replace inspection of original encoding. A process exit alone is insufficient: require log completion, the expected DC/AC/transient plot and step identity, required nodes, coverage, finite values and finalized file identities. Then run uncertainty qualification before a reference can support a pass.

## T23-A: local LTspice through a controlled Wine profile — not selected

Retained as the historical alternative only. Its Wine runtime, prefix, launch path and compatibility qualification are outside the selected implementation plan.

Run the native Linux C++/Python package above. Add stable [Wine 11.0](https://www.winehq.org/news/2026011301) for the Windows x64 LTspice executable, with a dedicated project prefix separate from any personal Wine configuration. Set runtime/prefix/executable paths explicitly in the toolchain configuration. The simulator adapter converts the case directory to a Wine path and invokes `wine <LTspice.exe> -b <deck.cir>` with the declared environment.

* **Mechanism:** Preparation, batch simulation, original RAW/log collection and analysis are controlled by the Linux harness. Before the circuit matrix, qualify simulator launch/timeout/completion, DC/AC/float64 RAW fixtures and repeated identical reference inputs in that exact Wine/OS profile.
* **Trade-off:** Keeps reference production on one machine and permits local orchestration. Adds Wine/prefix/environment state that must be frozen and qualified. Neither the Wine release nor a successful application launch proves the circuit/reference contract.
* **Failure conditions:** If LTspice 26.1.1 does not operate correctly under this Wine profile, its RAW/log output is incompatible or required settings cannot be established, report the failure. Do not switch to native Windows, another Wine release, another simulator or lower-precision data without a reviewed profile change.

## T23-B: native Windows producer on the WSL host — selected

Run C++/Python inside WSL 2 and LTspice 26.1.1 natively on the same Windows 11 x64 host. Invoke the reviewed PowerShell helper through WSL executable interoperability. Keep the Linux source/build/analysis tree in the Linux filesystem and stage each reference request under a configurable Windows drive directory, initially `%LOCALAPPDATA%\ts808-reference\runs`. Obtain the corresponding WSL path using `wslpath`; do not assume a particular drive letter, mount root, username or distribution name.

* **Mechanism:** Python writes the small deck/models/request manifest and a byte-identical helper copy into a new shared request directory. Windows verifies input hashes, runs the native executable in that drive directory with fixed arguments `-b deck.cir`, enforces completion/timeout and publishes result metadata after the producer closes its files. Linux reads the original RAW/log directly through the shared path and independently verifies their lengths/hashes and case identity before import/qualification. No RAW transfer between machines occurs.
* **Trade-off:** Uses native Windows execution with local orchestration. Windows/WSL path translation, quoting, case sensitivity, process lifetime and cross-filesystem I/O must be qualified. Shared access removes manual transport, not provenance or reference-uncertainty checks; no storage-throughput claim is made.
* **Failure conditions:** Disabled interoperability, inaccessible/mismatched path pairs, an unavailable/wrong-version executable, changed request bytes, an untracked native process or incomplete/stale outputs produce a visible configuration/reference failure. No automatic Wine/remote/manual-transfer fallback is introduced. Interrupted files are never read as completed evidence merely because they are visible from WSL.

Microsoft documents [Windows executable interoperability and shared paths](https://learn.microsoft.com/en-us/windows/wsl/filesystems), and [the interop/automount controls](https://learn.microsoft.com/en-us/windows/wsl/wsl-config). The shared-drive staging above is the project's use of those mechanisms. Qualify spaces/non-ASCII paths, Windows working-directory behavior and read-after-close/hash consistency on the selected host. Do not edit WSL configuration or execution policies automatically.

The native helper records its owned process PID and start identity, waits for completion and uses PID-scoped [taskkill tree termination](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/taskkill) on timeout/cancellation when required. It must never terminate LTspice by a global image-name match. A killed WSL launcher is not proof that the Windows child stopped; the native helper retains its own timeout, and missing final metadata leaves the run incomplete. Tests must establish the selected executable's process/completion behavior before its results are trusted.

## Selected command, schema and publication contract

Keep the accepted T17 process boundary and exit codes. The selected additional commands are future interfaces, not implemented or executed commands:

| Operation | Interface and outcome |
| --- | --- |
| Environment check | `python -m ts808_validation doctor --toolchain <toolchain.json>` verifies selected versions/paths/profile and emits its provenance. Missing/incompatible configuration returns 10; it installs nothing. |
| Prepare reference | `python -m ts808_validation prepare-reference --case <case.json> --toolchain <toolchain.json> --output <new-request-directory>` writes the explicit request. Success means request construction, not reference completion. |
| Local orchestration, selected B | `python -m ts808_validation run-reference --request <request-directory> --toolchain <toolchain.json> --output <new-result-directory>` invokes native Windows PowerShell through WSL. The result directory is the new Linux metadata/index publication; original RAW/log remain in their shared request directory. Incomplete/failed/unreadable output returns 30; uncertainty qualification remains separate. |
| Native producer helper | `reference/ts808/run_reference.ps1 -RequestDirectory <windows-path> -ExecutablePath <windows-path>` consumes the staged request and declared native executable. Linux invokes it with `-NoProfile -NonInteractive -File`; it writes native result metadata into the same shared directory. No manual transfer is part of the interface. |
| Import and compare | Preserve T17's existing commands; verify the shared request/result identity and original closed files before accepting the reference. Unqualified uncertainty returns 31; measured acceptance failure 40. |

Use explicit [Draft 2020-12 validation](https://python-jsonschema.readthedocs.io/en/stable/validate/) in Python with local schema references. C++ offline I/O independently checks required types/ranges/version/model consistency and applicable cross-field rules; it does not acquire a schema-validation runtime in the core. Share valid/invalid case fixtures across both checks. Do not fetch schemas over the network while processing data.

The approved [concrete interface/schema/fixture specification](./ts808_offline_interface_spec.md) spells out field meanings, units, C++ declarations, exact layouts and local producer lifecycle. Schema files remain planned creates; this is a Markdown specification, not implemented runtime code. No new dependency or changed accepted behavior is silently inserted.

Publish only to new directories, with incomplete/pending-integrity states until files/hashes are finalized. Preserve physical-case and execution identities separately under T17/T22. Reports label numerical acceptance, WAV qualification and human listening independently; a completed reference/export/import command is not an overall MVP pass.

## Planned file additions and qualification fixtures

All entries below are plans, not created files. Carry them into the unified file-by-file implementation section; do not use a directory name as a substitute for the explicit list.

| Planned file | Change and reason |
| --- | --- |
| `CMakeLists.txt`, `CMakePresets.json`, `tests/test_main.cpp` | Use the selected root pins, native core/offline/Catch2 targets, qualification flags and checked allocation configuration. Existing inventory entries are extended, not separate untracked build paths. |
| `validation/pyproject.toml`, `validation/requirements.lock`, `validation/bootstrap-requirements.lock` | Define the selected Python package and locked bootstrap/analysis environments, including resolved transitives and hashes. |
| `validation/toolchain.json`, `schemas/toolchain.schema.json` | Declare the selected profile, exact tool versions/paths, simulator policy and observed binary/environment identities. Paths are machine configuration, not hard-coded developer home paths. |
| `validation/ts808_validation/simulator.py`, `validation/tests/test_simulator_contract.py` | Prepare shared requests, launch the native helper through WSL and qualify results; test path translation/quoting, completion, native timeout, version/hash mismatch and stale/incomplete output. No Wine adapter is required. |
| `reference/ts808/run_reference.ps1` | Implement the selected same-host native producer/request/result protocol, with Windows working directory and owned-process lifetime control. |
| `validation/tests/test_cli_contract.py` | Compare C++/Python valid/invalid case handling and declared exit/publication semantics; failed processing cannot create a passing result. |
| `validation/tests/fixtures/README.md` | Record each tiny native fixture's producer/profile/version, generation recipe, identity/hash and intentional negative variants. No fabricated simulator goldens. |
| `docs/dependencies.md` | Record exact root/transitive/tool identities, scope and upstream notices. Existing spicelib licensing remains confined to development analysis; no new distribution/legal conclusion is assumed. |
| `schemas/case.schema.json`, `schemas/run.schema.json`, `schemas/report.schema.json`, `docs/artifact_format.md`, `docs/validation_protocol.md`, `README.md` | Complete the selected contract syntax and reproducible setup/build/reference/import/compare documentation without claiming commands already worked. |

Freeze these explicit tiny fixture paths in the final plan:

| Fixture purpose | Planned files |
| --- | --- |
| Native DC | `validation/tests/fixtures/ltspice26_dc.cir`, `validation/tests/fixtures/ltspice26_dc.raw`, `validation/tests/fixtures/ltspice26_dc.log` |
| Native complex AC | `validation/tests/fixtures/ltspice26_ac.cir`, `validation/tests/fixtures/ltspice26_ac.raw`, `validation/tests/fixtures/ltspice26_ac.log` |
| Valid float64 transient | `validation/tests/fixtures/ltspice26_tran64.cir`, `validation/tests/fixtures/ltspice26_tran64.raw`, `validation/tests/fixtures/ltspice26_tran64.log` |
| Rejected low-precision transient | `validation/tests/fixtures/ltspice26_tran32.cir`, `validation/tests/fixtures/ltspice26_tran32.raw`, `validation/tests/fixtures/ltspice26_tran32.log` |
| Native stepped identity | `validation/tests/fixtures/ltspice26_stepped.cir`, `validation/tests/fixtures/ltspice26_stepped.raw`, `validation/tests/fixtures/ltspice26_stepped.log` |
| Deliberately truncated copy | `validation/tests/fixtures/ltspice26_truncated.raw` |

The RAW/log files must originate from the selected producer during implementation. A single-precision negative fixture uses the documented low-precision simulator configuration and records its actual encoding; it is never a permitted numerical reference. The truncated fixture is a labeled corruption of a valid source, with the derivation recorded. Actual payload hashes and compatibility results cannot be asserted before these files exist.

## Approval boundary and remaining drafting work

T23-B, the common package and the owner's same-host WSL clarification are accepted. Do not request the route again or reinstate Wine/manual transport requirements. Approval does not install any tools, authorize production implementation or mark qualification complete. If a selected version cannot be provisioned, resolved or qualified, retain that explicit failure and review the necessary version/profile change.

The concrete interface/fixture attachment and [unified Detailed Implementation Plan](./ts808_offline_design.md#detailed-implementation-plan) are approved. [Predecessor reconciliation](./ts808_predecessor_reconciliation.md) is complete with no unresolved contradiction. The [final design](./ts808_offline_design.md) is saved at the selected destination; the egm-draft workflow is complete. `egm-review` has not started and remains a separately requested design review before implementation.

## Review remediation contracts (2026-11-01)

The [persisted handoff](./ts808_offline_interface_spec.md#persisted-reference-and-suite-handoff) fixes the imported-reference and suite-summary version-1 contracts, including explicit `compare --refined-reference`. [T18 executable WAV qualification](./ts808_validation_contract.md#executable-wav-qualification-and-listening-grid) fixes mandatory mono PCM32 at both target rates, grids, error thresholds and the exact 48 kHz listening phase/window/DC rules. These requirements extend the planned schema/fixture inventory; they add no runtime dependency and claim no native qualification result.
