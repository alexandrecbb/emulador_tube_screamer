# Fixtures matemáticos

`device_nominal_25c.json` contém o vetor T20 e oráculos de diodo/BJT
calculados com `decimal.Decimal`, precisão 80, SI exato para kB/q e os
decimais preparados de Is/BF/BR do contrato.

Diodo: -0.2/0/0.1/0.3/0.6/0.8 V. BJT: produto cartesiano
VBE=-0.2/0/0.6/0.7 V e VBC=-1/-0.2/0/0.5 V. Fórmulas no
[device_spec](../../reference/ts808/device_spec.md). São oráculos
matemáticos, não goldens de hardware ou LTspice.

Os testes nativos comparam RAWs com esses oráculos, sem usar C++ como
verdade. Fixtures de leitor, hashes e proveniência:
[validation/tests/fixtures](../../validation/tests/fixtures/README.md).

Os JSON de op-amp/layout/falhas/palpite DC previstos ainda precisam ser
expandidos; os ensaios atuais estão expressos nos testes C++.
