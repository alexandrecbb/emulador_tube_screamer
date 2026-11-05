# Emulador Tube Screamer TS808

Estado da matriz: avaliação completa (128 entradas), qualificação automática
reprovada por assentamento DC; MVP não aceito. ABX humano realizado, sem
distinção acima do acaso nessa sessão. Veja o [registro consolidado](validation/results/qualification-2026-11-05/README.md).

MVP offline em C++20, conforme o [design aprovado](docs/designs/ts808_offline_design.md).
O núcleo implementa as 31 incógnitas, DC, transientes trapezoidais com
Newton/Schur e respostas contínua/discreta de pequeno sinal. A revisão de
T22 com equilibração de linhas está aprovada e aplicada.

Na [continuação de 2026-11-04](validation/results/continuation-2026-11-04/README.md),
F: passou no planejamento de espaço para a matriz com as duas revisões existentes.
Um experimento de integração interna em 768 kHz, com saídas em 192/384 kHz,
eliminou as falhas locais e de recuperação da sobrecarga. A
[revisão de subpassos](docs/designs/ts808_substep_revision.md) foi aprovada e
incorporada: novos casos podem declarar `integration_rate_Hz=768000` e
`substeps=4`/`2` junto à grade de saída de192/384 kHz. Ausência desses campos
preserva a execução histórica. Novos pilotos, incluindo WAV, estão sendo
qualificados em `F:\ts808-validation\substeps-20261104`; a matriz só é liberada
após a aprovação automática dos seis resultados. Isso não promove os
resultados históricos de integração nas taxas originais. Exemplo de execução
revisada: `"execution": {"rate_Hz": 192000, "integration_rate_Hz": 768000,
"substeps": 4, ...}`; os demais campos obrigatórios continuam presentes.

O executável grava traces float64 little-endian e metadados JSON, com
falhas explícitas. A validação completa de áudio com LTspice, WAV e ABX
permanece pendente; não há qualificação de plugin ou tempo real.

## Compilar e testar

Toolchain local em `.tools`, sem sudo: GCC 15.3.0, CMake/CTest 4.4.5,
Ninja 1.13.2, Eigen 5.0.1, JSON 3.12.0 e Catch2 3.16.1.

```sh
.tools/cmake-4.4.5-linux-x86_64/bin/cmake --preset offline-checks
.tools/cmake-4.4.5-linux-x86_64/bin/cmake --build --preset offline-checks
.tools/cmake-4.4.5-linux-x86_64/bin/ctest --preset offline-checks
```

Substitua `offline-checks` por `offline-release` para a variante normal.
A variante checked mantém assertions e o guard de alocação do Eigen.
Os testes cobrem as 27 combinações em DC/AC, endpoints, início de senoide
nos dois rates, Jacobianas, Schur/solve completo, condicionamento,
histórico transacional e avanço sem alocação.

Python 3.14.4 e pacotes aprovados estão em `.venv`:

```sh
PYTHONPATH=validation .venv/bin/python -m ts808_validation doctor --toolchain validation/toolchain.json
PYTHONPATH=validation .venv/bin/python -m pytest validation/tests -q
TS808_NATIVE_TESTS=1 PYTHONPATH=validation .venv/bin/python -m pytest validation/tests -q
```

A última forma também executa os ensaios reais de diodo/BJT no LTspice
26.1.1 nativo. `doctor` verifica ambiente e hashes, sem qualificar a
referência numérica inteira. Veja [dependências](docs/dependencies.md).

## Executar um caso

O [manifesto](reference/ts808/cases.json) contém 91 casos físicos:
27 DC, 27 AC e 37 transientes, incluindo a condição de escuta.

```sh
mkdir -p runs
.venv/bin/python - <<'PY'
import json
from pathlib import Path
manifest = json.loads(Path('reference/ts808/cases.json').read_text())
case = next(c for c in manifest['cases'] if c['case_id'] == 'dc_d050_t050_v050')
Path('runs/center.json').write_text(json.dumps(case))
PY
build/offline-release/ts808_offline --case runs/center.json --output runs/center-dc
```

O destino deve ser novo. Saída 0 significa processamento completo,
com integridade pendente até a finalização Python; não é aprovação numérica.
Veja [formato e limites atuais](docs/artifact_format.md).

## Referência nativa

O [mapa](reference/ts808/component_map.json) registra 43 componentes,
12 capacitores e a extração Cerutti com hash da fonte conferido.
As leis independentes estão em `reference/ts808/models.lib`.
O LTspice foi extraído em `%LOCALAPPDATA%\ts808-reference\ltspice-26.1.1`.
Caminhos pareados e hashes desta máquina constam no
[toolchain.json](validation/toolchain.json).

`prepare-reference` gera um pedido novo na raiz Windows declarada;
`run-reference` aciona o helper e verifica as identidades dos arquivos
originais fechados. Endpoints usam fontes de zero volts.
Os estados nativos se chamam `xclip:z` e `xtone:z`.

Há [fixtures RAW reais](validation/tests/fixtures/README.md) de DC,
AC complexo, transiente double, baixa precisão e `.step`, além do
negativo truncado identificado. Os leitores rejeitam os negativos.
Ensaios do pedal completo revelaram uso de pseudo-transiente para DC
pelo produtor nativo; os logs são preservados e ainda devem entrar na
qualificação nominal/refinada.

O [protocolo](docs/validation_protocol.md) registra medições e gates pendentes.
Plugin, JUCE, TS9 e tempo real vêm depois da validação offline.

## Resultado medido em 2026-11-04

A aceitação do MVP está bloqueada. Os pilotos de senoide com revisão explícita
para 2 s de aquecimento passaram; a sobrecarga falhou na recuperação por 33
amostras em 192 kHz e 7 em 384 kHz (limite: uma amostra). Newton 10x mais apertado
não resolveu. A matriz completa também excede o armazenamento disponível.

Veja o [relatório](docs/mvp_validation_report.md) e as
[evidências versionadas](validation/results/mvp-2026-11-04/README.md).
Os testes Python com LTspice real registraram 39 testes e 30 subtests aprovados;
CTest checked/release passou. WAV/FIR têm fixtures mecânicos aprovados; pares
ABX só serão liberados após todos os gates automáticos obrigatórios passarem.

Importação e comparação exigem referências explícitas, preservadas e refinadas:

```sh
PYTHONPATH=validation .venv/bin/python -m ts808_validation import-reference --case <case.json> --raw <original/deck.raw> --log <original/deck.log> --output <new-reference-directory>
PYTHONPATH=validation .venv/bin/python -m ts808_validation compare --case <case.json> --run <run-directory> --reference <nominal-directory> --refined-reference <refined-directory> --output <new-report-directory>
PYTHONPATH=validation .venv/bin/python -m ts808_validation suite --cases reference/ts808/cases.json --toolchain validation/toolchain.json --model-executable build/offline-release/ts808_offline --rates 192000 384000 --pilot-summary validation/results/mvp-2026-11-04/pilots.json --output <new-suite-directory>
```

O último comando conserva o índice completo mesmo quando o gate dos pilotos
impede a execução. Os RAWs grandes e a toolchain local não são distribuídos pelo
Git; os metadados versionados não substituem os payloads originais.
