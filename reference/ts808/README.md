# Referência TS808

Modelo `ts808-cerutti-reduced-v1`, extraído do desenho de Steve Cerutti
publicado por [General Guitar Gadgets](https://generalguitargadgets.com/effects-projects/distortion/tube-screamer/).
Fonte: <https://generalguitargadgets.com/wp-content/uploads/ts-808.jpg>.
SHA-256 dos bytes JPEG, conferido novamente em 2026-11-01:
`22ea2b084b4248a26a303557e18c8f35968bc1fa73a2a6bcf5edce0d349a12ad`.
O desenho original não é redistribuído neste diretório.

[component_map.json](component_map.json) registra os terminais ordenados,
valores SI, proprietários, parâmetros preparados a 25 °C, controles e extração.
Os identificadores são locais ao projeto: o desenho não tem designadores.
O [schema](../../schemas/component_map.schema.json) usa Draft 2020-12.
Os controles são frações de resistência, sem inferência de taper mecânico.

No estado ligado, `J_wet` é um resistor de 383.29731360711594 Ω entre
`wet_send` e `switch_common`; `J_dry` é aberto. Ambos os resistores de
510 kΩ da seção de chaveamento e o capacitor do ramo seco permanecem.
O cruzamento entre o wiper de Volume e o barramento comum não é uma junção.
As redes de gate e a lógica de acionamento foram omitidas. A proteção de
polaridade, ligada diretamente à alimentação ideal, também foi omitida.
O mapa registra essas diferenças; os modelos não simulam o pedal completo.

O vetor nominal representa as hipóteses aprovadas em T20/T21. Os BJTs são
representativos de uma amostra GR; headroom e resistência de saída do
op-amp são estimativas extrapoladas; a resistência do canal pressupõe
VGS=VDS=0, área unitária e 25 °C. Nenhum desses dados é calibração física
do pedal. As fontes, preparação de temperatura e limitações estão nos
[contratos de design](../../docs/designs/ts808_model_data_proposal.md).

Os nomes `xclip:z`/`xtone:z` e os elementos `R_drive`/`V_drive`,
`R_tone_low`/`V_tone_low`, etc. são o contrato de nomes da realização nativa.
Usa-se `R_…` para segmento positivo e `V_…` de zero volts no endpoint.
As expressões de corrente no mapa seguem a orientação dos terminais,
incluindo Volume de `vref` para `wet_send` e de `wet_send` para `volume_top`.

Estado: mapa, leis, decks e núcleo C++ materializados. Há testes de
componentes/leitores com RAWs reais; a qualificação do pedal completo,
a comparação nominal/refinada e o ABX ainda estão pendentes. Consulte
[protocolo](../../docs/validation_protocol.md).
