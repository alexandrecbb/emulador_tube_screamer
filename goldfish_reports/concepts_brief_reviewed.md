# Tube Screamer circuit-model audio plugin

* **Author:** Project owner and Codex
* **Date:** 2026-10-30
* **Status:** Working hypothesis; clarification in progress. No Goldfish review has run.

## Overview

Build a C++ audio plugin for VST3 and CLAP using JUCE for the application and audio framework. Reproduce a selected TS808 and TS9 circuit using equations for its components, including BJT buffers, silicon feedback diodes, op-amp behavior, capacitors, resistors, and the Drive, Tone, and Volume controls. Confirm how CLAP will be integrated before choosing build dependencies.

The stock clipping network is nominally symmetric. Deliberate asymmetric clipping belongs to the customization controls. The approximately 720 Hz feedback-network transition does not by itself describe the full pedal's midrange response.

## Analysis

### Confirmed reference and validation

Use a documented SPICE simulation, such as LTspice, as the numerical reference. Freeze the schematic revision, component values, device models, supply voltage, temperature, input source impedance, and output load for each comparison. Agreement with SPICE establishes agreement with those models; it does not independently establish agreement with every physical pedal.

Use a null test to compare time-domain signals, Bode plots to compare small-signal response, THD measurements to compare distortion, and a listening ABX test to assess audible differences. Numerical thresholds and the listening protocol remain open.

For the null test, align clocks, gain calibration, latency, startup conditions, and sample times. Keep startup and steady-state comparisons separate. Report any alignment or gain compensation; do not allow arbitrary fitting to hide model errors. Check convergence of the SPICE reference by tightening timestep and solver tolerances. Quantify residual RMS and peak against a declared reference level.

Bode measurements require an operating point and a small enough signal to avoid significant clipping. Measure multiple Drive and Tone settings. THD comparisons must declare input amplitude, frequency, bandwidth, and harmonic limits; inspect individual harmonics as well as the aggregate value. ABX requires matched levels, aligned playback, randomized trials, and a declared statistical analysis. Listening results do not replace circuit checks.

### Confirmed op-amp scope

Do not simulate the internal transistor topology of the JRC4558. Use a nonideal behavioral macromodel with finite open-loop gain, finite gain-bandwidth product (initial nominal target: 3 MHz), slew limiting (initial nominal target: 1 V/us), finite input and output impedances, and output saturation. Allocate most nonlinear solving effort to the feedback diodes and their interaction with the RC network, while retaining the requested BJT buffer models.

The supply rails are 0 V and 9 V, with nominal Vref = 4.5 V. Output saturation limits must include headroom from those rails and may depend on load; they are not automatically 0 V and 9 V. Parameterize positive and negative limits separately, but validate any claimed asymmetry against the chosen SPICE reference. The NJM4558 manufacturer's listed typical values support the starting slew-rate target. Published datasheet values measured at other supply conditions do not establish the exact output swing at 9 V.

Use a dynamic internal state for the dominant pole, consistent with finite DC gain and gain-bandwidth product. Integrate slew limiting and saturation into the feedback model rather than attaching an output waveshaper after an ideal circuit solution. Check overload recovery and numerical stiffness: a 3 MHz gain-bandwidth product exceeds the internal sample rates proposed here, so a naive explicit time integration is not a justified implementation.

Manufacturer reference: https://www.nisshinbo-microdevices.co.jp/en/products/operational-amplifier/spec/?product=njm4558

Manufacturer datasheet mirror: https://media.digikey.com/pdf/Data%20Sheets/NJR%20PDFs/NJM4558%2C%204559.pdf

### Confirmed live-use constraints

Target a modern desktop in the AMD Ryzen 7 class, monitoring guitar through a DAW at a base sample rate of 48 kHz. Support one to four simultaneous instances and host buffers of 64 or 128 samples. Investigate internal oversampling at 4x and 8x, corresponding to 192 and 384 kHz. The requested CPU target is below 5% per instance; the exact CPU model, host, meter definition, and measurement protocol must be fixed before treating that percentage as an acceptance threshold.

Target zero added latency where feasible, otherwise less than 1 ms of plugin-added latency using minimum-phase oversampling filters. This excludes audio-interface and host-buffer latency. Measure the oversampling chain's delay and frequency-dependent phase response, and define host latency reporting without claiming that minimum-phase filters have zero delay. At 48 kHz, less than 1 ms means fewer than 48 base-rate samples of added latency under the agreed measurement definition.

Benchmark worst-case block processing, not only average CPU. A 64-sample block at 48 kHz lasts approximately 1.33 ms; a 128-sample block lasts approximately 2.67 ms. Four-instance tests must include high Drive, demanding input levels, supported component changes, automation, silence, and recovery from solver nonconvergence. Keep allocation, locks, file operations, and unbounded iteration off the audio thread.

Compare modified nodal analysis with bounded Newton iterations, nonlinear state-space formulations, and wave digital filters. Examine coupled feedback, nonideal op-amp dynamics, BJT behavior, numerical convergence, and the cost of component changes. Do not select a method before defining the real-time budget.

Compare oversampling factors and reconstruction filters using measured alias residual and CPU cost. Include all modeled nonlinear stages in the analysis, including the BJT buffers and any op-amp saturation. Oversampling adds latency and cannot guarantee zero aliasing.

Define component-level customization through explicit device parameters and validated models. Resistor tolerance needs a reproducible random seed and saved component values. Diode and op-amp substitutions need more than a changed clipping threshold or gain value.

## Goals vs. Non-Goals

* **In-Scope Goals:** Circuit-level TS808/TS9 models; VST3/CLAP delivery; C++/JUCE architecture; selectable component variations; SPICE comparison and listening validation.
* **Out-of-Scope Non-Goals:** Not yet agreed. Supply dynamics, electronic bypass, noise, thermal drift, and transistor-level modeling inside the op-amp remain scope questions.

## Alternatives Weighed

No solver has been selected or rejected. A static waveshaper alone cannot represent the requested component-level circuit and its dynamic feedback.

## Key Decisions & Staging for Next Steps

1. Confirmed: SPICE reference, null tests, Bode plots, THD, and ABX.
2. Confirmed: live DAW monitoring; Ryzen 7-class desktop; 48 kHz base rate; 4x/8x oversampling candidates; one to four instances; below 5% CPU per instance as a benchmark-dependent target; zero or less than 1 ms added latency; 64/128-sample host buffers. Operating systems and the precise benchmark machine remain open.
3. Confirmed: nonideal external-behavior op-amp macromodel; no internal transistor simulation. Exact reference schematics, SPICE device models, and saturation headroom at 9 V remain to be established.
4. Open: quantitative error thresholds and supported component substitutions.
5. After clarification, present the anchored hypothesis for explicit readiness confirmation before independent Goldfish reviews.

## Circuit reference

Manfred Zollner, Tube Screamer analysis: https://www.gitec-forum-eng.de/wp-content/uploads/2019/02/poteg-10-08-05-4-tube-screamer.pdf
