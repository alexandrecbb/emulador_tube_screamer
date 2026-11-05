# Native negative fixture: invalid DC despite success log

Produced by LTspice26.1.1 on2026-11-04, normal solver, controls0/0/0.5,
the frozen TS808 model and nominal tolerances. The log claims direct Newton
success, but the RAW contains1e200 V at input_base. Matching AC has essentially
zero input-buffer/output response. This must not qualify as a physical reference.

Alternative-solver DC and AC runs from the identical circuit recovered the
expected operating point and response. The fixed independent T22 bias guess
also recovered the point; no C++ solution was used as a native seed.

Original source: `F:\ts808-reference\runs\dc-norm-415ddbbbdae14d2d86e2505cf89d7b94`.
Full diagnostic: `F:\ts808-validation\substeps-20261104\ac-bias-diagnosis`.

SHA-256 RAW: `eb9b972b28a77546d61233b7911e44f730c1e8849b7dd3aa12e1408c2b77daf6`.
SHA-256 log: `43ba09e6778a80b3a601787e8281267495c21683d7be9713b5a47be13f6901af`.
