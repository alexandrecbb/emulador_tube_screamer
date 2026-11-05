# Artefatos implementados

Contrato normativo: [especificação de interfaces](designs/ts808_offline_interface_spec.md).

Revisão aprovada em 2026-11-04: [subpassos explícitos](designs/ts808_substep_revision.md).
`execution.rate_Hz` identifica a grade de saída. Quando presentes,
`integration_rate_Hz` e `substeps` identificam a integração interna 768 kHz e
os 4/2 passos por saída 192/384 kHz. Os dois campos são obrigatórios em conjunto.
Sua ausência conserva um passo por amostra. Configurações inconsistentes ou
divergentes entre caso e execução são rejeitadas. A resposta AC discreta usa
a taxa interna. Somente amostras externas completas entram no trace; uma
falha registra o índice/tempo internos e o subpasso nos diagnósticos.

Os schemas run/failure/report/reference_request/reference_result/imported_reference/
suite_summary/abx_session já estão implementados; os parágrafos históricos
abaixo descrevem o estágio inicial. O estado atual de aceitação está no
[relatório](mvp_validation_report.md).

Cada execução cria uma pasta nova com `run.json` e `traces.f64le`.
O binário contém linhas de 32 doubles little-endian: tempo e as
31 incógnitas na ordem canônica. Não há dump de structs/Eigen nem padding.
Timestamps são calculados por índice/rate; transientes incluem o endpoint.
DC/AC contêm uma linha de equilíbrio. Falhas preservam o prefixo
comprometido e acrescentam `failure.json`.

AC também produz `response.f64le`, 301 linhas de cinco doubles:
frequência, real/imaginária da resposta contínua e da discreta.
Metadados identificam dtype `<f8`, ordem C, shape, bytes e colunas.

O C++ não calcula hashes. `artifacts.finalize_run` verifica o caso,
hashes do mapa/spec, identidade física, tamanho, grid, colunas e finitude,
antes de publicar hashes do payload, caso, executável e fontes.
Ainda faltam os schemas completos de run/failure/report e os testes
de todos os caminhos de publicação especificados no design.

`reference_result.json` pertence ao produtor Windows. Python verifica
hashes do pedido, inputs, executável e outputs fechados. O índice Linux
aponta para os originais compartilhados. Conclusão nativa não declara
precisão ou incerteza. Ainda faltam os schemas de request/result e os
ensaios completos de cancelamento/timeout em árvore e caminhos Unicode.

Schemas já materializados: component_map, case e toolchain, Draft 2020-12.
Os contratos persistidos de importação/comparação/suíte e ABX continuam
definidos no design, ainda sem implementação completa.
