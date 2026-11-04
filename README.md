# Emulador Tube Screamer TS808

MVP offline em C++20, conforme o [design aprovado](docs/designs/ts808_offline_design.md).
O núcleo implementa as 31 incógnitas, DC, transientes trapezoidais com
Newton/Schur e respostas contínua/discreta de pequeno sinal. A revisão de
T22 com equilibração de linhas está aprovada e aplicada.

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
