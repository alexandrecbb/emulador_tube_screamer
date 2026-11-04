# MVP validation evidence — 2026-11-04

**Acceptance is blocked.** The full native comparison matrix was not run and no
ABX listening pair was released. No human responses were generated or collected.

The center and high-drive tone pilots with explicitly revised 2 s warm-up passed
at 192/384 kHz and in the separate 768 kHz diagnostic. The original 0.5 s warm-up
cases remain failed historical evidence; their windows were not silently changed.

| Overload rate | Reference uncertainty | Local windows | Recovery error | Numerical outcome |
| --- | --- | --- | --- | --- |
| 192 kHz | passed | RMS failed in 11 windows | 33 samples; limit 1 | failed |
| 384 kHz | passed | passed | 7 samples; limit 1 | failed |
| 768 kHz, diagnostic | passed | passed | 1 sample; limit 1 | passed |

Tightening all six Newton tolerances 10x at 192 kHz changed output by at most
8.72e-13 V and left the recovery error at 33 samples. The diagnostic does not
replace the failed target-rate case. See `overload-tolerance-diagnosis.json`.

`pilots.json` indexes the nine closed rate-specific reports copied here. Each
case/rate directory contains its numerical report, residual plot, case/run
metadata, native request/result/reference metadata and native logs. The additional
`native-option-audit.json` checks the actual hashed deck directives and the
nominal/refined tolerance relationship without rewriting the original reports.
`evidence.json` records source hashes, scope, outcomes and snapshot file hashes.

**Large original RAW and C++ trace payloads are retained locally, outside Git.**
The copied metadata are evidence snapshots, not self-contained runnable reference
imports. They cannot replace missing original payloads or their integrity checks.
Machine-specific producer paths and hashes preserve provenance. Reproduce with a
qualified WSL/Windows toolchain and fresh output directories; do not fabricate or
retarget a reference manifest to unrelated data.

`verification.json` and the five associated logs record the final doctor,
checked/release CTest and real-native Python tests. Passing tests/doctor do not
supersede the failed numerical gates. Native RC PCM32 export fixtures at both
rates and the prescribed common FIR passed their separate mechanical checks;
this does not qualify all mandatory pedal WAVs or human listening.

`resource-gate.json` records storage preflight failure: the baseline reference
matrix alone requires at least 93.66 GB, or 100.74 GB with the two explicit tone
revisions, before adaptive overhead, additional WAV production, C++ traces and
margin. The qualified Windows roots have insufficient space.

`rejected-raw-archive.json` records reversible relocation of 5.84 GB of explicitly
rejected/cancelled RAWs from C: to F:, with verified copy hashes. Their original
logs remain in place; no accepted reference was relocated. These archived files
are not acceptance evidence.

See [the detailed report](../../../docs/mvp_validation_report.md) for rationale,
initialization alignment, exact limits, commands and remaining work.
