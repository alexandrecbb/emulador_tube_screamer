# Selected TS808 reference and effect-on extraction

* **Author:** Project owner and Codex
* **Date:** 2026-10-31
* **Status:** T15 source/extraction, T20-A/T21-A nominal baseline, T22-A numerical endpoints, T23-B same-host WSL/native Windows execution and the complete implementation section/attachment are approved. Predecessor reconciliation and [final publication](./ts808_offline_design.md) are complete; actual native circuit implementation/qualification remains outstanding.

## Source inspected

[General Guitar Gadgets](https://generalguitargadgets.com/effects-projects/distortion/tube-screamer/) links a [TS-808 schematic drawn by Steve Cerutti](https://generalguitargadgets.com/wp-content/uploads/ts-808.jpg), credited by the publisher as an original TS-808 schematic. It is a redraw, not evidence of an authenticated factory revision. This candidate is the linked historical drawing, not the site's separately modified ITS8 kit schematic.

Visual inspection of the drawing shows two 2SC1815 audio buffers, a dual JRC4558D, two 1N914 feedback diodes and a 51 pF feedback capacitor. It also shows the supply/bias network, FET bypass branches and control circuitry. A physical device label does not specify the numerical semiconductor model needed by this project.

## Approved use for the MVP

Freeze the stock audio path in effect-on operation and its physical supply/bias RC network from this drawing. Produce a component/node mapping that can be checked against the four accepted audio blocks. The implementation reference must be named as an extraction from this drawing, not a simulation of the complete original switching circuit or every TS808 revision.

Document each omitted or replaced switching connection, including passive branches attached to audio nodes and the shared bias node. Where a static switch equivalent is used, state the assumed connection/impedance and retain the associated electrical load. Do not delete attached resistors/capacitors merely because they appear near the bypass section. Exact extraction and loading must be reviewed before freezing the netlist.

The accepted current-law catalog contains basic diode/BJT laws and the behavioral op-amp, with no JFET model selected. A full dynamic simulation of the original flip-flop/FET bypass would add scope. No assertion that removal is inaudible or electrically exact is made here.

After source selection, record the original URL, attribution, retrieval identity/hash, readable reference version, complete passive values and terminal map, control orientations/tapers, selected model parameters and every extraction difference. The reference package is not complete until those data are checked.

## Owner decision T15

The owner selected the Cerutti redraw and the effect-on audio/supply extraction. Omit the footswitch flip-flop/control logic while retaining the bias/load resistors and connected branches that load the audio path. Include the conducting JFET's equivalent resistance where it participates in the active connection. Another schematic is not the selected source.

Selection fixes the documentary source and intended extraction boundary. It does not approve an unseen final netlist, invented diode/BJT parameters or unreviewed JRC4558 equations. The remaining model details stay in the reference/model contract of [the formal draft](./ts808_offline_design.md).

## Source identity

The inspected JPEG downloaded on 2026-10-31 has SHA-256 `22ea2b084b4248a26a303557e18c8f35968bc1fa73a2a6bcf5edce0d349a12ad`. Preserve this identity with the source URL and attribution; do not silently substitute the separate ITS8 kit drawing. The project currently contains this provenance record, not a copied original image or a completed reference netlist.

The post-T18 [terminal audit](./ts808_model_contract.md) rechecked the same source hash and records passive values, control fractions, active pins and the dry/wet/common switching connections. T20-A and T21-A subsequently close the nominal model data; this audit alone did not approve them or qualify the native circuit implementation.

After approval of T20-A's op-amp/semiconductor nominal package, the owner selected [T21-A](./ts808_switch_resistance_proposal.md): `R_on=383.29731360711594 Ohm`, with explicit normalization, gate-point and signal-range limitations. This closes the mathematical switch nominal without waiving the extraction rules or qualifying actual powered gate behavior. The owner keeps actual gate characterization outside the MVP.

## Extraction rules

1. Name the dry send, wet send and common output/buffer input nodes from an audited terminal map. Determine the effect-on switch truth table from actual connectivity, rather than inferring it from the two FET symbols' left/right order.
2. Retain the bias/load resistors and coupling capacitors connected to those nodes, including both drawn 510 kOhm switching-branch bias resistors. An inactive branch may still load the input buffer through its coupling capacitor and bias resistor. Turning the channel off does not remove its external components.
3. Represent a conducting switch channel by its explicitly parameterized static terminal equivalent; preserve the terminal connection and finite on resistance. Represent the blocked channel according to the declared no-parasitic static-switch approximation. The exact terminal mapping and state truth table must be checked before either native circuit is generated.
4. Do not invent an on-resistance value, use zero by default, or infer it from the 2SK30A part name alone. Record its source/operating conditions and admissible signal range. A fixed resistance is a declared model approximation, not the full nonlinear JFET characteristic.
5. Keep all direct loads on the physical Vref network. For each removed logic connection, document whether it affects only the ideal supply, or also a finite-impedance audio/bias node. If a retained port load depends on removed logic, supply a justified frozen-state equivalent rather than dropping it silently. No fifth dynamic logic subsystem is introduced.
6. Use the same extracted graph and static-switch parameters in C++ and LTspice. Native LTspice JFET dynamics are not silently included on one side while C++ uses a resistor/open channel.

## Extraction verification

The component map must classify every connection of the drawing as retained, statically replaced or omitted with a reason. Preserve actual branch connectivity at node crossings and pot wipers. Verify terminal KCL, bias voltages, and the effective source/load seen at clipping-to-tone and tone/volume-to-output interfaces. Compare small-signal loaded port responses against the paired LTspice extraction without disconnecting the neighboring stage or clamping Vref.

Matching these tests establishes agreement of the two extracted models. It does not prove exact hardware impedance over every signal level: the accepted basic semiconductor laws, op-amp macromodel and static switch equivalent limit that claim. This is a scoped baseline with explicit loads, not permission to replace every interstage impedance by an ideal buffer.
