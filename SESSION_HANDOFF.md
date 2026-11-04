## Encerramento desta sessão — 2026-11-04

Todos os produtores, comparações, arquivamento e testes desta sessão concluíram.
O pacote versionável é `validation/results/mvp-2026-11-04/`, com nove relatórios,
plots, metadados, logs de verificação e índice de suíte de 128 entradas.
Centro/alto drive warmup2s passaram nas três taxas. Sobrecarga falhou em
192/384 kHz (recuperação 33/7 amostras), 768 kHz passou como diagnóstico.
Newton 10x não alterou a reprovação. Não há aceitação de MVP nem pares ABX.
A matriz completa não foi iniciada. Faltam precisão da recuperação e armazenamento.

Verificação final registrada: 39 testes Python com produtor nativo e 30 subtests
passaram; CTest checked/release e doctor das duas raízes passaram. Foram movidos
5,84 GB de RAWs rejeitados/cancelados para F: após conferir hashes; logs preservados
em C: e referências válidas intactas. C: recuperou aproximadamente 7,7 GB livres.
As duas medições centrais perdidas foram repetidas com traces bit a bit idênticos.

O usuário autorizou commit/push para origin/main e, depois, desligamento do
WINDOWS hospedeiro. O encerramento deve verificar push e deixar a árvore limpa
antes do pedido. Estado local do desligamento será registrado em
`runs/mvp-qualification/shutdown-plan.json`; o recibo nativo ficará em
`C:\Users\Alexandre\AppData\Local\ts808-reference\shutdown-receipt.json`.
Esse é um pedido desta sessão, não uma preferência para desligar a cada turno
futuro; não repetir automaticamente um desligamento já solicitado/atendido.

## Ordem adicional: commit e push ANTES do desligamento

O usuário pediu commit e push em https://github.com/alexandrecbb/emulador_tube_screamer.git
antes de desligar. Já existe repositório main rastreando origin/main e o commit
inicial 9a9a714 está no remoto. Finalizar relatório/evidências, commit, push e
verificação do hash remoto antes de solicitar shutdown do WINDOWS. Não desligar
se o push necessário não tiver sido concluído. GitHub plugin indisponível;
usar Git CLI e credenciais existentes, sem expor tokens.

## Instrução final do usuário — desligar o hospedeiro

O usuário pediu explicitamente desligar o computador WINDOWS hospedeiro quando
terminar o working, lembrando que estamos no WSL. Após concluir/salvar os jobs e
relatórios, solicitar o desligamento ao Windows (não apenas wsl --shutdown).
Não precisa pedir confirmação: autorização explícita já foi dada. Preferir
shutdown normal sem /f, via pequeno script PowerShell Windows desacoplado com
atraso curto para publicar a resposta final, e registrar o pedido antes disso.
Não desligar enquanto arquivos/arquivamento/testes ainda estiverem em execução.

## Estado medido — madrugada de 2026-11-04

A sobrecarga com referências válidas em F: foi comparada nas três taxas.
`runs/mvp-pilots-02/overload_high/qualified-pilot.json` contém resultados:
192 kHz falha local RMS e recuperação (33 amostras); 384 kHz falha recuperação
(7 amostras); 768 kHz passa somente como diagnóstico. Referências passaram.
Apertar Newton 10x não resolve: saída mudou no máximo 8,72e-13 V e a recuperação
continua errando 33 amostras. Ver `runs/mvp-qualification/overload-192000-tighter10/`.
NÃO substituir as taxas alvo por 768 kHz nem relaxar critérios ou trocar T3.

Leitor grande agora usa parser/seleção spicelib, mapas read-only para diagnóstico,
e leitura sequencial de blocos de linhas (64 KiB por operação) para finite/cache
necessários; evita thrashing DrvFS. Os originais não foram alterados. Hash também
usa blocos limitados. Comparações concluídas podem ser retomadas por seus ponteiros
explícitos após revalidar os originais; runs interrompidos são preservados antes
da repetição, sem repetir falhas numéricas determinísticas.

`runs/mvp-revised-pilots-norm` está terminando center/high warmup2s (center já passou
em 192/384 kHz; consultar o índice para 768 e high). O programa atual não usa
--refresh-comparisons para evitar repetir comparações já fechadas e válidas.
Os RAWs de alta duração são grandes; C: tem aproximadamente 11 GB livres, F:
aproximadamente 75 GB. Matriz original precisa >=93,66 GB de RAWs; família de tons
com warmup2s precisaria >=192,75 GB, fora overhead/WAV. Recurso insuficiente.

Fixtures WAV nativos em ambos os rates passaram com stop exclusivo T-h/2, sem
cortar arquivos; referências numéricas têm guard de um maxstep após T para cobrir
o endpoint. FIR passou. Ainda não há pares ABX aprovados, pois os gates automáticos
não passaram. Testes Python com produtor nativo: 38 passed / 30 subtests na última
execução; há testes novos posteriores, repetir ao finalizar. CTest checked/release
passou. Doctor/path Unicode+espaço+apóstrofo/cancelamento/timeout passaram.

## Continuação autônoma do MVP — 2026-11-03 (em andamento)

O usuário renovou a autorização após a interrupção por créditos. Não solicitar
aprovações intermediárias; ABX humano é o único checkpoint interativo previsto.
Consulte `docs/mvp_validation_report.md` para evidência, correção da escala do
estado nativo, falhas de settling dos pilotos originais e limites de disco.
Biblioteca nativa mudou somente a realização: Cstate e corrente por 1e-6.
Há novos módulos/schemas/scripts/tests em validation e schemas; não há Git.
`runs/mvp-revised-pilots-norm` está executando as revisões explícitas de 2 s
de aquecimento; `runs/mvp-pilots-02/overload_high/*-alt-request.json` aponta os
pedidos corretos de sobrecarga em solver=alt. Grafia alternate foi rejeitada
pelo produtor e não pode qualificar referência. Não retomar pedidos inválidos.
Nunca substituir um resultado original falho pela revisão de duração sem
preservar as identidades distintas. A matriz completa e ABX NÃO passaram.

# Retomada: planejamento do emulador TS808

## Implementação e revisão T22 — 2026-11-01

O usuário pediu resolver as pendências de implementação e aprovou explicitamente
`docs/designs/ts808_scaling_revision.md`, incluindo a atualização de T22.
Foi aplicada equilibração de linhas pelo máximo absoluto após escalas físicas,
sem mudar as equações, os 31 estados, a partição ou o limite rcond=1e-12.
O erro reverso continua verificado também antes da equilibração.

Toolchain instalada em `.tools`: GCC 15.3.0 por conda-forge/micromamba,
CMake/CTest 4.4.5, Ninja 1.13.2, Eigen 5.0.1, JSON 3.12.0, Catch2 3.16.1.
Não foi usado sudo. Ambiente Python 3.14.4 em `.venv`, com versões aprovadas,
locks de bootstrap/análise e hashes reais. LTspice 26.1.1 foi extraído do MSI
oficial para a pasta local Windows, sem alterar execution policy.
`validation/toolchain.json` contém observações, caminhos pareados e hashes;
`doctor` passou somente para qualificação de ambiente.

Núcleo C++ implementado: tipos/mapa fixo, parâmetros, leis/derivadas, montagem,
Schur, Newton, prepare/DC/advance, histórico transacional e AC contínua/discreta.
Executável offline implementado com cases explícitos e traces `<f8`/sidecar.
O manifesto tem 91 casos físicos (27 DC, 27 AC, 37 transientes incluindo escuta).
Decks nativos e gerador para todos os casos, helper PowerShell, testes reais de
semicondutores e fixtures RAW de leitores estão presentes. Os logs/hashes dos
fixtures estão em validation/tests/fixtures/README.md.

Verificações: builds checked e release com CTest aprovado. A bateria cobre
27 DC/AC, endpoints, Schur/full, Jacobianas, condicionamento, históricos e
ausência de alocação; inclui início de senoide das 27 combinações em ambos
os rates. Testes CLI passaram para 27 DC e 27 AC, hold de 0.2 s a 192/384 kHz,
configurações inválidas e payload truncado. Uma senoide central completa
foi processada pelo C++ sem comparação qualificada. Ensaios reais LTspice
para diodos/BJTs passaram contra oráculos Decimal de 80 dígitos. Fixtures
RC de DC/AC/transiente double/stepped passaram; float32/truncado foram rejeitados.

A aceitação integral do MVP AINDA NÃO FOI CONCLUÍDA. Em alguns ensaios do
pedal/op-amp, o produtor nativo recorreu a pseudo-transiente para DC; os logs
foram preservados. Faltam qualificação completa do op-amp, schema/runtime de
comparação persistida, referência nominal/refinada, pilotos com recursos,
matriz completa de precisão, WAV/FIR e ABX humano. Não há alegação de áudio,
performance, tempo real, latência ou ABX aprovado. Consulte README.md e
`docs/validation_protocol.md` para comandos e escopo atual.


## Início da implementação — 2026-11-01

O usuário autorizou a etapa de implementação com “Vamos agora para a etapa
de implementação”. Essa autorização substitui as restrições históricas de
trabalho somente em design registradas abaixo; as decisões T1–T23 continuam
válidas. Os relatórios de revisão foram produzidos posteriormente ao handoff
original, e IMP-001/IMP-002 têm remediação registrada nos contratos.

Primeira entrega: `reference/ts808/README.md`, `component_map.json`,
`device_spec.md`, `schemas/component_map.schema.json`,
`validation/tests/test_artifact_contract.py`, `.gitignore` e `README.md`.
O JPEG foi baixado para inspeção temporária e seu SHA-256 confere com o
registro aprovado. O mapa materializa 43 componentes, 12 capacitores e 31
grandezas, incluindo os cinco segmentos de controle e as cargas retidas.
Cinco testes de contrato passaram com
`python3 -m unittest discover -s validation/tests -v`.

Não há compilador C++, CMake ou Ninja no PATH. PowerShell e wslpath estão
presentes; a instalação/identidade do LTspice não foi verificada.
Python e jsonschema preexistentes foram usados apenas para conferir o mapa;
não há lock de dependências nem qualificação T23. Nenhum pacote foi instalado.
A pasta não é um repositório Git.

Próximos itens do inventário: leis nativas independentes, deck e matriz de
casos; preparação da toolchain aprovada; núcleo C++ e respectivos testes.
Não existem solver, resultados RAW, goldens nativos ou métricas de áudio.
O estágio inicial do mapa não encerra o primeiro marco de congelamento de
entradas: faltam os demais artefatos e sua qualificação.

O restante deste arquivo preserva o histórico da etapa de design.

Data do registro: 2026-10-31.
Projeto: `/home/alexandre/projetos/emulador_tube_screamer`.

Registro atualizado após a confirmação do destino e salvamento do design final. **A egm-draft está concluída. T1–T23, todas as seções e o anexo estão aprovados; a reconciliação não encontrou contradição pendente. O design foi salvo em `docs/designs/ts808_offline_design.md`. Nenhuma implementação está autorizada.**

## Onde paramos

A skill `egm-draft` foi finalizada com o [design canônico](./docs/designs/ts808_offline_design.md). O RFC anterior e os relatórios Goldfish do brainstorm foram preservados. O próximo passo recomendado é solicitar `egm-review` do arquivo final e de seus anexos; essa revisão ainda não foi iniciada.

**T18 e T19 estão aprovadas. T19 é a opção B revisada: região central estritamente linear na função de saturação, acoplada a joelhos suaves C1, com recuperação e preservação do headroom em relação aos trilhos de 0 V/9 V.** O usuário confirmou explicitamente a substituição da tangente hiperbólica global de amplitude; a alternativa de limites rígidos não foi escolhida. O [contrato de modelos](./docs/designs/ts808_model_contract.md) registra as condições de continuidade e o mapa auditado. Não reabrir a escolha rígida/suave da T19 nem pedir nova aprovação dessa estrutura.

**T20-A está aprovada, incluindo o pacote nominal de parâmetros.** O [contrato T20](./docs/designs/ts808_model_data_proposal.md) fixa tanh deslocada somente nos joelhos, junções C2 e o centro exatamente linear da T19. A alternativa racional T20-B não foi escolhida. A origem de cada dado/estimativa/hipótese permanece identificada; a resistência foi fechada separadamente por T21-A. T22/T23 e a seção formal também estão aprovadas. Não pedir nova aprovação dessas escolhas nem tratar aprovação de design como autorização para implementar código.

**T21-A está aprovada no [contrato da resistência de chaveamento](./docs/designs/ts808_switch_resistance_proposal.md).** O usuário escolheu explicitamente adotar 383,30 Ohm como nominal estático condicional às hipóteses documentadas, mantendo a caracterização do gate real fora do MVP. Preservar o valor reproduzível completo `R_on=383.29731360711594 Ohm`, derivado da entrada publicada da biblioteca ADS 2011 para 2SK30A, sob área unitária, 25 graus C, `V_GS=0` e `V_DS=0`. T21-B não foi escolhida. O gate real não foi caracterizado; isso é uma limitação física declarada, não um bloqueio do MVP. O circuito continua com equivalente estático, sem JFET dinâmico ou fonte ideal de gate.

**T22-A está aprovada com os critérios comuns no [contrato numérico agrupado](./docs/designs/ts808_numerical_closure_proposal.md).** Usar um sistema único de 31 incógnitas, cinco correntes auxiliares nos controles, interiores 4/6/11/5 e fronteira `[input_emitter, clip_out, wet_send, vref, i_volume_low]`. A aprovação inclui escalas/condicionamento, palpite DC, obrigações de APIs/metadados e fixtures nomeados. T22-B não foi escolhida e suas uniões de nós/aliases não entram no plano. A aprovação não demonstra posto, convergência, alocação ou desempenho. Não pedir nova escolha nem usar B/solve completo como fallback automático.

**T23-B e o pacote comum estão aprovados no [contrato de execução/ferramentas](./docs/designs/ts808_execution_tooling_proposal.md).** O usuário esclareceu que o Linux é WSL 2 em um host Windows na mesma máquina física. Usar `execution_profile=wsl2-windows-native-v1`: C++/Python nativos no WSL, LTspice nativo no Windows, acionamento batch por interoperabilidade/PowerShell e leitura dos RAW/log originais pelo sistema de arquivos compartilhado. Não exigir Wine, serviço remoto ou transferência manual entre máquinas. Preservar hashes/identidades, fechamento dos arquivos, timeout e controle da árvore de processos nativa. Não pedir nova escolha de rota.

**O [Plano de Implementação formal](./design_draft.md#detailed-implementation-plan) e o [anexo concreto de APIs/schemas/fixtures](./docs/designs/ts808_offline_interface_spec.md) estão aprovados**, incluindo inventário único de arquivos, ordem de implementação/verificação, comandos futuros, requisitos não funcionais, APIs, nove schemas e receitas de casos/fixtures. O usuário autorizou avançar à reconciliação, que foi concluída e registrada no [relatório](./docs/designs/ts808_predecessor_reconciliation.md). Esse detalhamento permanece em Markdown; nenhum código, schema JSON ou netlist foi criado.

Não foram implementados nem compilados o solver, os testes ou o plugin. Nenhuma medição de precisão, CPU, alocação, latência ou ABX foi realizada. Os arquivos de código/configuração citados no inventário são arquivos planejados, não existentes.

Foram feitos apenas cálculos escalares de apoio ao design: junções/valores das curvas candidatas, ajuste efetivo de saída com dois pontos típicos, preparação aceita de parâmetros de 27 para 25 graus C e derivação condicional da resistência da JFET. Não são testes do circuito, validação LTspice ou caracterização física. Downloads/código auxiliar ficaram fora da árvore do projeto.

O design final foi salvo no destino confirmado pelo usuário, com links relativos ajustados. Contratos/anexos, histórico e handoff apontam para a publicação canônica. O predecessor e os dados/equações aprovados permanecem inalterados; a árvore continua contendo somente Markdown. Nenhuma dependência foi instalada, compilação ou simulação executada.

## Objetivo e ordem aprovada

1. MVP: modelo C++ do TS808 clássico, processando sinais offline e comparando com LTspice.
2. Depois da validação: otimizar o mesmo núcleo para tempo real, repetindo os testes de precisão.
3. Depois dos critérios de precisão/desempenho: plugin C++/JUCE VST3/CLAP, TS9 e modificações clássicas, incluindo customização de componentes.

Cenário futuro de tempo real: desktop Ryzen 7 moderno, 48 kHz, oversampling interno 4x/8x, 1–4 instâncias, buffers 64/128 samples, meta abaixo de 5% de CPU por instância sob benchmark definido e latência adicional zero se possível, caso contrário menor que 1 ms. Essas metas não foram demonstradas.

## Decisões aprovadas T1–T23

| Decisão | Escolha |
| --- | --- |
| T1 | MNA implícita com Newton–Raphson, quatro blocos: Buffer de Entrada, Clipping Amp, Tone/Volume, Buffer de Saída. |
| T2 | Newton global acoplado, eliminação dos interiores dos blocos e complemento de Schur nas fronteiras; preservação do carregamento e Vref compartilhado. |
| T3 | Integração trapezoidal em passo fixo. |
| T4 | Fonte ideal de 9 V e rede RC física de alimentação/polarização; Vref calculado pelo circuito. |
| T5 | Falha de convergência encerra o caso offline com diagnóstico; sem subdivisão automática, troca de integrador ou aceitação de estado inválido. |
| T6 | Uma especificação comportamental não ideal do JRC4558, implementada independentemente em C++ e LTspice. Sem topologia interna de transistores do op-amp. |
| T7 | Inicialização pelo ponto de operação DC do circuito carregado; partida a frio fora do MVP. |
| T8 | Limites numéricos iniciais e qualificação da referência, descritos abaixo. |
| T9 | Dados de nós com timestamps e alta precisão como referência principal; WAV em paralelo. |
| T10 | Reconstrução PCHIP sobre a grade do C++; erro precisa ser qualificado, não presumido. |
| T11 | Núcleo C++ reutilizável; análise offline em Python/NumPy/SciPy. |
| T12 | RAW binário via spicelib.RawRead, somente no ambiente de desenvolvimento/testes. |
| T13 | Jacobianas analíticas por componente, reutilizando termos exponenciais; testes automatizados contra diferenças finitas. |
| T14 | Shockley/Ebers–Moll básicos, com os mesmos parâmetros/omissões no LTspice. Sem resistências internas, cargas parasitas ou efeito Early no MVP; capacitores externos e estados dos op-amps permanecem. |
| T15 | Redesenho TS808 de Steve Cerutti, estado de efeito ligado e rede de alimentação/bias. Omitir flip-flop/acionamento, preservando cargas de chaveamento e equivalentes estáticos aplicáveis da JFET em condução. |
| T16 | Eigen, matrizes fixas binary64 e LU com pivoteamento; dimensionamento pelo grafo e testes para ausência de alocação no processamento. |
| T17 | Traces gerados em binário float64 little-endian + sidecar JSON. Escrita binária pela biblioteca padrão C++; leitura NumPy por fromfile ou memmap. |
| T18 | Matriz offline finita, condições elétricas, critérios locais de transientes/recuperação, qualificação WAV e ABX humano conforme contrato de validação. Aprovação do protocolo, sem resultados medidos. |
| T19 | Opção B revisada: transferência de saturação exatamente linear no centro, joelhos suaves com continuidade de valor e primeira derivada (C1), recuperação dentro do solve e headroom preservado. A tangente hiperbólica global de amplitude foi substituída; a curva exata e o nominal foram posteriormente fechados por T20-A. |
| T20 | T20-A: tanh deslocada somente nos joelhos, junções C2 e pacote nominal de op-amp/semicondutores, incluindo a preparação de temperatura documentada. A resistência da JFET foi excluída dessa aprovação e fechada separadamente por T21-A. |
| T21 | T21-A: `R_on=383.29731360711594 Ohm` como nominal estático condicional às hipóteses documentadas. Caracterização do gate real fora do MVP; sem dinâmica JFET ou fonte ideal de gate. |
| T22 | T22-A: sistema único de 31 incógnitas com correntes auxiliares, mapa fixo e critérios comuns documentados, incluindo escalas/condicionamento, palpite DC e obrigações de APIs/metadados/fixtures. T22-B não escolhida. |
| T23 | T23-B e pacote comum: versões/dependências/build/testes/schemas/encoding/configurações de referência aprovados. Linux é WSL 2 no mesmo host Windows; LTspice nativo por interoperabilidade e arquivos compartilhados. Sem Wine ou transferência manual entre máquinas. |

O contrato numérico agrupa configurações iniciais, incluindo 32 iterações Newton transientes, 100 DC, até 9 tentativas de line search e tolerâncias propostas. A escolha do Eigen e do formato de dados está aprovada; os detalhes dos contratos entram na revisão final do Plano de Implementação, sem alegação de resultados medidos.

O JRC4558 deve representar ganho/banda finitos, slew rate nominal de 1 V/us, GBW nominal de 3 MHz, impedâncias e saturação/recuperação. T20-A aprova `q(s)=tanh(s)` somente nos joelhos externos, larguras de 0,25 V, headroom nominal de `37/51 V` por trilho, resistência efetiva de saída `10000/51 Ohm`, recuperação `tau_r=10 us` e o restante do pacote nominal documentado. No centro, `S(z)=z`, `S'(z)=1` e a contribuição de recuperação `z-S(z)` é zero. As junções preservam também segunda derivada zero (C2). Os trilhos continuam 0 V/9 V, sem tornar a saída rail-to-rail. A função de slew do estado é distinta da tangente hiperbólica global de amplitude substituída. Esses dados valem para ambos os canais, com estados independentes; hipóteses aceitas não são medições físicas.

A justificativa do usuário é manter derivadas contínuas para apoiar a execução determinística de Newton e facilitar o Null Test entre C++ e LTspice. Registrar como objetivo de design; continuidade C1 não garante convergência, condicionamento ou aprovação no null. Os limites de trabalho, falhas e validação já aprovados permanecem exigidos.

O clipping original é nominalmente simétrico. Assimetria intencional é modificação posterior. A transição RC próxima de 720 Hz não descreve sozinha todo o mid-hump.

## Nominal aprovado em T20-A

A aprovação explícita do usuário incluiu a opção T20-A **e o pacote nominal de parâmetros**. A escolha anterior de B em T19 determina a estrutura de saturação; a escolha de A em T20 determina a curva dentro dessa estrutura. Não confundir essas letras com reabertura da opção de limites rígidos.

O [contrato T20](./docs/designs/ts808_model_data_proposal.md) é a referência completa, apesar do nome histórico `proposal`. Os dados centrais para retomar são:

| Grupo | Nominal aceito |
| --- | --- |
| Curva dos joelhos | `q(s)=tanh(s)` somente fora do trecho central; `W_plus=W_minus=0.25 V`, `H=4.5-37/51 V`, `L=H-0.25 V`. No centro, identidade exata. |
| Op-amp | `A0=100000`, `GBW=3e6 Hz`, `SR=1e6 V/s`, `R_id=5e6 Ohm`; um estado independente por canal. |
| Saída e recuperação | `R_o=10000/51 Ohm`, headroom `37/51 V` por trilho e `tau_r=10e-6 s`. |
| Entradas | Correntes de bias iguais de 25 nA entrando no dispositivo; offset de tensão e diferença de correntes nominais iguais a zero. |
| Diodos a 25 graus C | Shockley reduzido do modelo oficial Fairchild/onsemi 1N914: `Is=3.0193620074088285e-9 A`, `n=1.94`, iguais nos dois diodos. |
| BJTs a 25 graus C | Ebers–Moll reduzido representativo 2SC1815-GR: `I_S=1.1792496052020765e-14 A`, `BF=271.5505716517182`, `BR=4.2141277418153207`, `NF=0.99569`, `NR=1`, iguais nos dois buffers. |
| Temperatura | Interpretação explícita dos vetores publicados em 27 graus C e preparação para 25 graus C conforme fórmulas/hipóteses documentadas; não aplicar uma segunda correção implícita no LTspice. |

O headroom e `R_o` resultam de um ajuste efetivo de dois pontos típicos de saída a ±15 V, extrapolado como nominal para 9 V. A largura dos joelhos, a recuperação e partes da interpretação dos semicondutores são hipóteses aceitas, com as limitações registradas. Não descrevê-las como calibração física a 9 V. T20-A não inclui a resistência da JFET.

## Decisão T21-A aprovada

Ler [o contrato completo](./docs/designs/ts808_switch_resistance_proposal.md) para preservar as hipóteses e limitações, sem pedir nova escolha. As opções e o resultado são:

* **T21-A — escolhida:** adotar `R_on=383.29731360711594 Ohm` como nominal estático condicional, com as hipóteses e limites registrados.
* **T21-B — não escolhida:** manter o valor aberto até obter caracterização específica do estado ligado.

A instrução explícita foi: "Escolho a opção A: adotar 383,30 Ω como valor nominal estático condicional às hipóteses documentadas, mantendo a caracterização do gate real fora do escopo do MVP". A apresentação arredondada não substitui o nominal completo do contrato.

A fonte nova é a biblioteca Agilent ADS 2011, hospedada pela Keysight, entrada `ap_njf_2SK30A_19930601`, com `Beta=0.0009764` e `Vto=-1.336`. A derivação usa a interpretação de área unitária a 25 graus C, `V_GS=0` e `V_DS=0`: `g0=2*beta*(-Vto)` e `R0=1/g0`. Não houve simulação da instância completa da biblioteca nem caracterização do gate real.

A faixa local documentada e os desvios calculados valem para o núcleo ideal sob essas hipóteses; não são limites demonstrados para todos os casos T18. O resistor estático aprovado será o mesmo elemento em C++ e LTspice. Nenhuma dinâmica JFET, gate ideal ou rede de flip-flop é introduzida. A identidade matemática aprovada passa a ser `ts808-cerutti-reduced-v1`, combinando T20-A/T21-A e o mapa Cerutti; hashes dos artefatos nativos só existirão quando eles forem produzidos. Nenhuma caracterização física é alegada.

## Decisão T22-A aprovada e contratos agrupados

Ler o [contrato T22 completo](./docs/designs/ts808_numerical_closure_proposal.md) para preservar a aprovação. O usuário declarou: "Aprovo a opção A (sistema único de 31 incógnitas com mapa fixo e correntes auxiliares), incluindo os critérios comuns documentados." Não pedir nova aprovação dessa escolha:

* **T22-A — escolhida:** um sistema fixo de 31 incógnitas, interiores 4/6/11/5 e fronteira 5. As cinco correntes dos trechos de controle impõem `v_a-v_b-R*i=0`, inclusive em `R=0`. A corrente do trecho inferior de Volume fica retida na fronteira para evitar uma linha sem coeficientes interiores quando Volume=0. Usar `formulation_id=control-branch-v1`.
* **T22-B — não escolhida:** uniões exatas de nós e variantes de 23–26 incógnitas foram consideradas; não criar seus mapas/aliases/dispatch nem tratá-los como fallback.

Os critérios comuns aprovados incluem escalas físicas de 1 V/1 mA, limiar relativo de pivô `64*N*epsilon`, `rcond` finito e `>=1e-12`, erro reverso linear normalizado `<=1e-10` e comparação de incrementos Schur/completo `<=1e-9`. São requisitos iniciais de qualificação, não resultados medidos. O palpite DC aprovado não fixa Vref nem impõe queda constante no BJT. Preservar T16: 32 iterações transientes, 100 DC, nove comprimentos de line search e tolerâncias não lineares documentadas. T22 não seleciona plataforma, versões ou execução LTspice.

## Decisão T23-B aprovada: WSL 2 e Windows na mesma máquina

Ler o [contrato T23 completo](./docs/designs/ts808_execution_tooling_proposal.md) para preservar a aprovação: "Aprovo a Rota B (Linux + Windows nativo), incluindo o pacote comum documentado." O esclarecimento subsequente estabelece WSL 2 e Windows na mesma máquina; a Rota B não requer acesso a uma máquina separada nem transporte manual de resultados.

* **T23-A — não escolhida:** Wine e sua qualificação não entram no plano.
* **T23-B — escolhida, com esclarecimento WSL:** C++/análise no WSL 2; LTspice 26.1.1 Windows x64 no host nativo. Python prepara uma pasta nova no disco Windows com pequenos inputs/helper e manifesta seus hashes; chama PowerShell via interop com caminhos traduzidos por `wslpath`; o helper usa diretório de trabalho Windows e `-b deck.cir`. Python lê RAW/log originais diretamente pelo caminho compartilhado após fechamento/conclusão e confere identidades. Não copiar grandes RAW manualmente nem presumir o encerramento nativo quando apenas o launcher Linux saiu.

O pacote comum aprovado inclui C++20/GCC 15.3.0, CMake 4.4.5/CTest, Ninja 1.13.2, Eigen 5.0.1, nlohmann/json 3.12.0 e Catch2 3.16.1. Para Python 3.14.4: NumPy 2.5.4, SciPy 1.18.1, spicelib 1.6.4, Matplotlib 3.11.2, pytest 9.2.0, jsonschema 4.26.0 e bootstrap pip 26.2.2/pip-tools 7.6.2. Aprovação não significa instalação/resolução ou testes. Congelamento de transitivas/hashes reais ocorrerá na preparação autorizada, sem inventar hashes de artefatos inexistentes.

T23 também aprova WAV derivado float32/checagem nativa PCM32, ajustes absolutos/integração/qualificação LTspice, timeout de 1800 s, schemas locais Draft 2020-12 e comandos de solicitação/produção. T18/T22 permanecem inalterados. O anexo de interface e o Plano de Implementação agora detalham a sintaxe/receitas para uma revisão única da seção; não abrir outra sequência de perguntas para versões/constantes já aprovadas.

Sondagens de leitura confirmaram kernel `6.18.33.2-microsoft-standard-WSL2`, `wslpath` e executáveis Windows acessíveis, Windows 11 Pro build 26300 e PowerShell `5.1.26100.9818`. Não localizaram LTspice em três caminhos convencionais nem nas entradas de desinstalação filtradas. Isso não é busca completa nem bloqueio da revisão do design: localizar/provisionar o executável aprovado e qualificá-lo é preparação futura. Nenhum LTspice foi lançado e nenhum ajuste de WSL/Windows foi alterado.

## Plano aprovado, reconciliado e salvo

O usuário declarou: "aprovo o plano e seu anexo para avançar à reconciliação com o predecessor". O [plano](./design_draft.md#detailed-implementation-plan) e o [anexo](./docs/designs/ts808_offline_interface_spec.md) estão aprovados; não pedir nova revisão dessa mesma seção nem reabrir T1–T23. Os schemas, APIs, layouts, arquivos e fixtures continuam especificações planejadas, sem arquivos de runtime produzidos.

A [reconciliação Step 6.1](./docs/designs/ts808_predecessor_reconciliation.md) comparou o predecessor completo com o conteúdo aprovado. Não há contradição pendente com requisitos aceitos. Euler, oito iterações e recuperação ao vivo eram propostas antigas, resolvidas por aprovações posteriores; as adições materiais de arquitetura/interfaces/dependências também têm aprovação. Não foi feita revisão Goldfish/Zoom Out nem alegado resultado de testes.

O usuário confirmou o destino com "Sim, salve o design final neste caminho". O [design final](./docs/designs/ts808_offline_design.md) está salvo em `docs/designs/ts808_offline_design.md`, SHA-256 `f43641c6bf96551411bf15a6c23fbb3e43fca0c860f42b3624ce7f3d36b2f629`. Não existia `SITEMAP.md` no destino, portanto nenhum foi criado. O RFC anterior foi preservado; a cópia de trabalho `design_draft.md` foi mantida. Não há gate restante da egm-draft; `egm-review` continua não solicitada para execução.

## Limites e protocolo de referência já aprovados

* DC: erro absoluto ≤10 mV nos nós definidos.
* Bode: erro ≤0,2 dB e ≤2 graus, de 20 Hz a 20 kHz; regras de piso/próximo de zeros e comparação discreta foram aprovadas em T18.
* Null estável: resíduo RMS ≤−60 dB relativo ao RMS da referência e pico ≤−40 dB relativo ao pico da referência.
* Próximo do silêncio, para RMS da referência <1 mV: limites absolutos de 1 uV RMS e 10 uV de pico.
* Harmônicos selecionados acima de −80 dBc: erro de magnitude ≤1 dB; THD: erro relativo ≤5% acima do piso de medição definido.
* Incerteza agregada da referência ≤um décimo do orçamento do erro aceito. Para o null relativo: −80 dB RMS e −60 dB de pico para a diferença de referências refinadas. Separar os erros de integração, armazenamento e reconstrução.

Diretivas LTspice obrigatórias:

```spice
.options plotwinsize=0
.options reltol=1e-6
.options numdgt=15
```

O usuário exige numdgt≥7; 15 é o valor concreto adotado. O Plano Técnico aprovado inclui maxstep inicial ≤h/8, sendo h o período interno de 192/384 kHz, e qualificação por refinamento. Manter inicialização DC sem `uic`/`startup` nos casos de base. Verificar precisão original do RAW, não apenas converter um array para float64.

O contrato de dados descreve `run.json`, `traces.f64le` e `failure.json` nas falhas, layout row-major, coluna de tempo, unidades/identidades, integridade finalizada por Python hashlib e estados explícitos de conclusão. `numpy.fromfile` carrega dados na memória; `memmap` permite acesso mapeado. PCHIP/FFT ainda podem alocar/copiar. I/O/JSON ficam fora do núcleo.

## Pacote T18 aprovado

O [contrato de validação completo](./docs/designs/ts808_validation_contract.md) foi aprovado, incluindo:

* Baseline a 25 graus C, fonte externa de sinal com 1 kOhm e carga externa de 1 MOhm.
* 27 combinações de posições resistivas dos controles para DC/Bode, com 301 frequências e verificação da resposta discreta, não somente do circuito contínuo.
* 36 casos transientes físicos: tons, linearidade em baixo nível, volume zero, hold DC e sobrecarga; cada um nas duas taxas internas. Um caso adicional gera o estímulo ABX.
* Critérios de estabilização, janelas de erro local e recuperação de sobrecarga.
* WAV com escala fixa e um FIR comum somente para escuta offline; não seleciona os filtros/latência do futuro plugin.
* ABX cego, 20 tentativas por ouvinte, regra estatística e participação humana. Distinguir aprovação numérica, qualificação WAV e validação combinada ainda pendente de escuta.

As condições adicionais de T18, incluindo os limites de transientes e o papel do ABX na promoção, **estão aprovadas como requisitos**. Nenhum ensaio ou ABX foi executado. Não reapresentar T18 para aprovação.

## Arquivos para retomar

| Arquivo | Papel |
| --- | --- |
| [Design final](./docs/designs/ts808_offline_design.md) | Publicação canônica aprovada e reconciliada; entrada para a próxima revisão de design. |
| [design_draft.md](./design_draft.md) | Cópia de trabalho preservada, com o mesmo conteúdo técnico e links ajustados à raiz. |
| [concepts_brief.md](./concepts_brief.md) | Contexto predecessor do brainstorm, com propostas históricas. |
| [RFC local](./docs/designs/tube_screamer_rfc.md) | Registro publicado e adendos das decisões posteriores. |
| [Decisões T1–T23](./docs/designs/ts808_decisions.md) | Histórico aprovado, incluindo o esclarecimento WSL da Rota B; não reabrir escolhas. |
| [Referência Cerutti](./docs/designs/ts808_reference_candidate.md) | Fonte escolhida, hash da imagem inspecionada, regras de extração e preservação de cargas. O nome do arquivo conserva “candidate”, mas a fonte foi selecionada. |
| [Contrato numérico](./docs/designs/ts808_numerical_contract.md) | Eigen, precisão, convergência e limites T16, mais representação/critérios comuns T22-A aprovados. |
| [Contrato T22-A numérico agrupado](./docs/designs/ts808_numerical_closure_proposal.md) | Mapa fixo 31, partição 4/6/11/5 + fronteira 5, escalas/condicionamento, palpite DC, APIs/metadados e fixtures aprovados; alternativa B apenas histórica. |
| [Contrato T23-B de execução/ferramentas](./docs/designs/ts808_execution_tooling_proposal.md) | Pacote comum e produtor Windows nativo no host WSL aprovados; Wine apenas alternativa não escolhida. |
| [Especificação concreta de interfaces/artefatos/fixtures](./docs/designs/ts808_offline_interface_spec.md) | Declarações C++20, nove schemas, layouts, protocolo local e receitas dos casos/fixtures; anexo aprovado. |
| [Reconciliação com o predecessor](./docs/designs/ts808_predecessor_reconciliation.md) | Comparação concluída, requisitos preservados, adições já aprovadas e hashes reais dos inputs; sem contradição pendente. |
| [Contrato de dados](./docs/designs/ts808_data_contract.md) | Interface offline, formato binário/JSON, metadados, integridade e falhas. |
| [Contrato de validação](./docs/designs/ts808_validation_contract.md) | T18 aprovada; os testes e a escuta ainda não foram executados. |
| [Contrato de modelos e mapa auditado](./docs/designs/ts808_model_contract.md) | Modelo, mapa numérico, execução e seção aprovados; design final salvo, com evidências de implementação ainda futuras. |
| [Contrato T20-A de equações e dados nominais](./docs/designs/ts808_model_data_proposal.md) | Tanh deslocada, derivadas, parâmetros nominais aprovados e fontes/hipóteses; JFET excluída dessa aprovação. |
| [Contrato T21-A de resistência da chave](./docs/designs/ts808_switch_resistance_proposal.md) | Nominal condicional aprovado, fonte/condições/limites e alternativa B não selecionada; caracterização do gate real fora do MVP. |
| [Inventário de implementação](./docs/designs/ts808_implementation_working.md) | Espelho do inventário completo incorporado ao plano formal; todos os arquivos de código/configuração/fixtures continuam planejados. |
| [Relatório Goldfish](./goldfish_review_report.md) | Revisões concluídas do brainstorm; não é revisão ou aprovação do design final. |

A imagem original foi inspecionada em arquivo temporário; não depender de `/tmp` para retomar. URL e hash estão no registro da referência. Fontes técnicas consultadas estão ligadas nos documentos.

## Passagem para egm-review

O usuário perguntou quando poderemos usar a próxima skill. Foi esclarecido que a `egm-review` já permite uma revisão intermediária da especificação/arquitetura no modo `feature_spec`. A revisão completa, incluindo prontidão de implementação, vem após consolidar o Plano de Implementação, sua aprovação, reconciliação com o predecessor e finalização do design. A revisão do design ocorre antes de implementar o circuito.

A etapa 6 da `egm-draft` foi concluída: reconciliação, escolha do destino e salvamento final. T1–T23 são decisões, não fases extras. A revisão `egm-review` **não foi iniciada nem solicitada para execução**. Os seis relatórios Goldfish existentes pertencem ao brainstorm; quando a revisão final for solicitada, ler a skill e executar seu protocolo de contexto independente.

## Próximo passo

A egm-draft está concluída. Recomendar `egm-review docs/designs/ts808_offline_design.md` e executar somente se o usuário solicitar. A revisão deve consumir o design final e seus anexos, sem tratar os relatórios antigos como revisão desse documento. Não iniciar implementação ou instalar ferramentas durante essa passagem.

## Instruções de colaboração a preservar

* O usuário se incomodou com perguntas excessivamente fragmentadas. Agrupar contratos para revisão e resolver detalhes mecânicos sem transformar cada constante em uma pergunta. Fazer uma pergunta por vez quando necessária.
* Manter as escolhas de arquitetura com o usuário conforme `egm-draft`; não reabrir aprovações já dadas nem transformar propostas em decisões aceitas.
* A skill ativa é de design: produzir documentos, não criar/compilar código de produção. Ler o SKILL.md e as instruções de execução disponíveis na nova sessão antes de continuar.
* Não tratar “precisão máxima”, “zero alocações”, “sem aliasing” ou erro PCHIP desprezível como resultados medidos. Tudo isso exige evidências na implementação.
* Entregar documentos em arquivos com links e evitar despejar propostas longas no chat.

## Mensagem sugerida para a próxima sessão

> Use a skill egm-review. Leia SESSION_HANDOFF.md e revise docs/designs/ts808_offline_design.md com seus anexos, sem implementar código. T1–T23 e todas as seções/anexos foram aprovados; a reconciliação com o predecessor foi concluída e o design final já está salvo. Preserve o fluxo WSL 2/Windows nativo na mesma máquina e use os relatórios antigos apenas como histórico do brainstorm.
