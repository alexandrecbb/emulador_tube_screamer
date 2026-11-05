# TS808 offline MVP: grouped numerical execution contract

**Approved amendment, 2026-11-04:** the owner approved
[explicit trapezoidal substeps](ts808_substep_revision.md): fixed internal
integration768 kHz with output grids192/384 kHz (4/2 steps). The source is
evaluated at every internal physical time, and each step retains the existing
31-unknown Newton/Schur solve, work caps and transactional history. No output
sample is published until its final substep succeeds. `Model::advance` remains
an internal-step API; this revises artifact rate semantics without introducing
adaptive steps, integrator fallback or threshold changes.

* **Author:** Project owner and Codex
* **Date:** 2026-10-31
* **Status:** T16/T22-A/T23-B and the complete implementation section/interface attachment are approved on 2026-10-31. Use the fixed 31-unknown map and accepted initial settings. Predecessor reconciliation and [final publication](./ts808_offline_design.md) are complete. No performance or numerical acceptance results exist.

## Purpose

Complete the numerical execution contract as one reviewable package: precision, residual scaling, bounded Newton work, derivative checks and the linear algebra implementation. The circuit reference/device parameters and data/validation contracts remain separately tracked. The values below are proposed engineering settings for offline validation, not demonstrated stability/accuracy or the final live-plugin iteration budget.

## Common settings in both options

| Item | Proposed initial setting | Reason and limit |
| --- | --- | --- |
| C++ arithmetic | IEEE-754 binary64 (`double`) throughout device evaluation, histories, Jacobians, Schur systems and diagnostic numerical output. No float32 or mixed-precision solve. | Match the reference storage precision and avoid an additional initial accuracy variable; this does not make floating-point results exact. |
| Floating-point mode | Disable unsafe fast-math transformations for the validated baseline; record compiler/build options and floating-point environment. | Nonfinite checks and reproducibility must retain their declared semantics. Later optimization requalifies accuracy. |
| Execution | One thread for every circuit solve; all matrix/work storage prepared before stepping. | Avoid implicit backend worker pools in the later processing path. Does not prohibit independent offline cases running as separate jobs. |
| Transient Newton cap | 32 iterations per attempted fixed timestep. | Bounded offline work with convergence evidence before later runtime optimization; not a promise that this cost meets the live budget. |
| DC Newton cap | 100 iterations for the initial coupled equilibrium. | Explicit finite initialization budget. No unrecorded homotopy, added shunts or acceptance of a non-equilibrium state. |
| Line search | Full step first, then factors 1/2 through 1/256: at most 9 trial step lengths per Newton iteration. Armijo sufficient decrease with c1=1e-4 on a consistently scaled residual-squared merit. | Bound trial evaluations; reject invalid/nonfinite trials. No sample subdivision or alternate integrator. |
| Warm start | Last committed state for transient Newton; documented topology-based DC initial guess without randomization. | Trial evaluation/history remains transactional. Exact node initialization follows the frozen map. |
| Convergence | Require both scaled full residual and scaled actual accepted state increment infinity norms ≤1. Check the initial guess explicitly; it may finish with zero increment if its full residual already passes. | A small increment with a large residual is failure, not convergence. |
| Numerical sensitivity | Repeat representative runs with algebraic tolerances ten times tighter and compare output/state errors within the aggregate numerical budget. | Detect whether algebraic stopping error is significant compared with temporal/model/reference errors. |

The line-search merit uses row weights fixed for all trial lengths at one Newton iterate; otherwise changing the weights could create an artificial decrease. Evaluate the merit at the entire trial circuit, not only the block with the largest device change. Specify the Newton directional slope consistently with that merit and the actual scaled system. If no permitted trial passes, stop the case under T5.

## Proposed scaling and tolerances

Express current-balance residual rows in amperes. Convert charge-based trapezoidal rows to their current-equivalent form consistently, including Jacobian factors, rather than comparing coulombs with amperes. Voltage constraints use volts. Behavioral state rows must declare their units and a consistent voltage- or current-equivalent normalization in the frozen device specification.

For current rows propose absolute tolerance 1e-12 A and relative tolerance 1e-9; for voltage rows propose absolute tolerance 1e-9 V and relative tolerance 1e-9. The row scale uses the magnitudes of the actual constituent branch contributions/constraint terms in the current trial state, with an explicit absolute floor. Do not normalize a cancellation residual solely by its own magnitude. Freeze row scales during a line-search sequence; recompute them for the next Newton iterate.

For unknown increments propose `atol_x + 1e-9 * max(abs(x_old), abs(x_new))`, with atol_x=1e-9 V for voltage/state variables in volts and 1e-12 A for auxiliary currents. Any other state units need an explicit scale in the device specification. Use the actual damped increment. These tolerances are solver stopping rules, not substitutes for the approved DC/Bode/null/harmonic acceptance gates.

Nondimensionalize rows and columns before factorization using declared electrical scales. Check the reconstructed full linear residual with a normalized backward error ≤1e-10. Do not accept a singular or nonfinite solve because the audio output appears plausible. Conditioning thresholds depend on the chosen rank/condition estimator and must be recorded and exercised with fixtures; they cannot be inferred from determinant magnitude alone.

## Required derivative checks

Use scaled coordinates and a fixed central-difference perturbation sweep from 1e-3 to 1e-7 for smooth test points, refining the sweep if no stable region appears. Proposed normalized entry acceptance: absolute error ≤1e-7 plus relative error ≤1e-5, with agreement at at least two neighboring perturbation sizes. Define these scales by the same declared physical units, not by unscaled mixtures of amperes and volts. Near expected zero entries use the absolute term.

At branch boundaries, use the accepted one-sided convention and points inside/outside the branch; do not demand a central derivative at a nondifferentiable point. Include directional-product tests, KCL/history invariants and the approved component-regime matrix. Failed or inconclusive finite-difference estimates must be diagnosed rather than silently dropped. No finite differences enter the live Jacobian path.

T19 selects [revised-B saturation](./ts808_model_contract.md); T20-A fixes shifted-tanh outer knees and the nominal parameters in the [accepted model-data contract](./ts808_model_data_proposal.md). The center is exactly linear. At each join the first derivative is 1 and the second derivative is zero, giving C2 continuity. Check these limits from both sides rather than borrowing historical hard-clamp option A's generalized-derivative convention. Also verify the exact central identity and zero central recovery contribution. Smoothness does not waive residual, conditioning, convergence or T18 null gates. T21-A closes the static switch nominal; actual gate characterization is outside the MVP. Final numerical/tooling closure remains open.

## Linear algebra selection

The core needs general nonsymmetric linear solves; no positive-definiteness assumption is justified merely because some components are passive. The owner selected Eigen with the block elimination and full assembled-solve diagnostic specified below. LAPACK is retained as the unselected alternative, not an automatic fallback.

### A. Eigen dense fixed-size or bounded-size matrices

Use an explicitly pinned Eigen dependency with preallocated matrices and pivoted LU. For the offline qualification path, use full-pivot LU/rank diagnostics for internal blocks and the boundary system. Freeze dimensions or maximum storage sizes after the node map is known; verify allocations in the step path rather than assuming a template type eliminates every allocation. The [FullPivLU documentation](https://eigen.tuxfamily.org/dox/classEigen_1_1FullPivLU.html) describes the decomposition and rank-related facilities.

* **Mechanism:** C++ matrix types and factorization objects own the small coupled systems; the core links no external BLAS/LAPACK runtime for this baseline.
* **Trade-off:** C++ integration and size-specific storage are direct; full pivoting has a cost and expression/storage behavior still requires tests. The dependency version/license inventory must be pinned before builds.
* **Failure condition:** Singular/poorly conditioned blocks or insufficient runtime performance remain failures to address explicitly, not reasons to silently fall back to another physical model or factorization.

### B. LAPACK backend with fixed single-thread configuration

Use a pinned LAPACK implementation through an explicit C interface, preallocated double arrays and general LU solve/condition-estimation routines. [Netlib's LU documentation](https://netlib.org/lapack/lapack_routine/dgetrf.f) specifies partial-pivot factorization. The backend/package, integer ABI, storage layout and worker-thread configuration must be fixed before implementation.

* **Mechanism:** C++ marshals the block and boundary systems to compiled LAPACK routines and verifies their outcomes and full residuals.
* **Trade-off:** Reuses a mature numerical backend; adds binary/build/runtime integration and more configuration for small per-step systems. Conditional/rank diagnostics must be specified consistently with the selected routines.
* **Failure condition:** Hidden backend allocation/threading, unsupported ABI or uncontrolled timing invalidates the intended processing path. Numerical correctness alone does not qualify it for live use.

## Fixed storage and processing-path qualification

T22-A fixes compile-time dimensions: internal systems 4/6/11/5, retained boundary 5 and full diagnostic system 31. Use the exact [T22 unknown and row map](./ts808_numerical_closure_proposal.md), including retained `i_volume_low`; coupling matrices have shapes `n_i by 5` and `5 by n_i`. A scalar voltage at a signal port does not make the boundary problem scalar: shared Vref and the retained auxiliary current still contribute.

Fixed-size matrix coefficients use inline storage; the [Eigen matrix documentation](https://eigen.tuxfamily.org/dox/group__TutorialMatrixClass.html) describes this and size-specific optimization. Where that storage physically resides follows the owning object's lifetime/location. The acceptance requirement is no allocation/deallocation during the prepared processing path, rather than an unsupported claim that every core object lives on a thread's stack. Stack/inline footprint, expression temporaries and factorization workspaces must be checked for the final dimensions.

Add tests that enable Eigen's runtime allocation checks during every prepared step, using the pinned release's documented [allocation-check facility](https://libeigen.gitlab.io/eigen/docs-master/TopicPreprocessorDirectives.html). Keep assertions active in that diagnostic configuration. Supplement this with detection of allocations outside Eigen; Eigen's guard alone cannot observe every standard-library or application allocation.

Exercise the first step after preparation, steady processing, line-search trials, singular/failing solves and returned error diagnostics. Use fixed-capacity numerical diagnostics in the core and format them outside the guarded region. Preparation and offline file/report operations may allocate; they are outside the prospective audio callback. The later host wrapper and oversampling chain require their own full-path qualification.

The owner's expectation of small-matrix speed and build simplicity motivates the choice. No Eigen-versus-LAPACK timing comparison or proof of a live CPU target has been produced; measure the selected implementation before attributing a speedup to inlining/unrolling.

## Owner decision T16 and subsequent use

The owner selected A, Eigen, in response to T16. Carry its binary64 arithmetic, bounded iteration/line-search settings and initial tolerances into the implementation-section draft, with the explicit verification requirements above. T20/T21 later closed nominal device data and T22-A closed the endpoint map, initial conditioning/scales, DC guess and fixture obligations. Package versions and exact API/schema syntax still need execution-tooling/final-section closure; no library was installed and no production code was written during drafting.

## Approved T22-A: endpoint representation and common numerical closure

The owner selected [T22-A](./ts808_numerical_closure_proposal.md): five control-segment currents in one 31-unknown system, with exact endpoint equations and the fixed five-unknown boundary. T22-B is unselected and its variant maps/aliases are not part of the plan. This preserves the physical circuit and T16's prepared fixed-size Eigen approach.

The same approval accepts the documented 1 V/1 mA scales, `64*N*epsilon` pivot threshold, finite `rcond>=1e-12`, normalized backward error `<=1e-10`, Schur/full increment comparison `<=1e-9`, deterministic DC guess, API/metadata obligations and named numerical fixtures. T16's nonlinear tolerances, work limits and line search remain in force. Qualification still requires tests; the approval is not evidence that any Jacobian has full rank or a case converges. Dependency/compiler/build/test versions, platform/LTspice execution and final schemas remain in the execution-tooling package.

The owner approved [T23-B and its common package](./ts808_execution_tooling_proposal.md), the [interface specification](./ts808_offline_interface_spec.md) and complete implementation section. Exact tooling/native Windows production remain on the same WSL 2 host. No environment installation, build, native simulation or numerical compatibility test has been performed; the finalized design has been saved at the owner-selected path.
