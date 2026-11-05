# Evidência e próximos gates

Atualização2026-11-04: o usuário aprovou a
[revisão de subpassos](designs/ts808_substep_revision.md). Novas execuções
registram integração 768 kHz e saídas 192/384 kHz; os gates numéricos e de
referência permanecem vigentes. A suíte deve requalificar os três pilotos,
inclusive WAV, antes da matriz completa. Novos payloads e referências vão
para F:; referências anteriores preservadas em C: podem ser lidas mediante
seu próprio contrato de proveniência, sem mover/retargetar seus manifestos.
Uma sessão de comando verifica os hashes originais ao primeiro consumo e
confere identidades de arquivo antes de cada reutilização e publicação.
Comandos independentes sempre revalidam os hashes.

Os itens abaixo preservam o histórico de 2026-11-01; consultar o
[relatório atual](mvp_validation_report.md) para as medições e pendências.

Estado observado em 2026-11-01. T18/T22/T23 continuam normativos, com
a revisão de equilibração de linhas aprovada pelo usuário.

## Executado

- Builds checked/release com versões aprovadas.
- 27 combinações DC/AC, endpoints e início de senoide a 192/384 kHz.
- Jacobianas por perturbações, junções C2 e KCL dos BJTs.
- Schur/solve completo, posto/condicionamento e erro reverso.
- Histórico transacional, falha latched e guards de alocação.
- CLI DC/AC nas 27 combinações e hold de 0.2 s nos dois rates.
- Senoide central de 1 s no C++, ainda sem comparação aprovada.
- Diodos/BJTs nativos comparados com oráculos Decimal de 80 dígitos.
- Fixtures RC nativos DC, AC, double, baixa precisão, stepped e truncado.
- Leitura independente, comparação RC analítica, integridade de traces
  e rejeição de configurações/payloads inválidos.

Esses ensaios não qualificam o pedal completo. `doctor` passou para
versões/hashes, sem declarar aprovação das referências.

## Ainda requerido para aceitação do MVP

1. Qualificar estados/leis do op-amp nativo, integração e inicialização.
   Os decks standalone existem. Auditar o pseudo-transiente observado
   no DC nativo, sem ocultá-lo nem tratá-lo como gate passado.
2. Completar schemas e comandos persistidos de importação, comparação
   nominal/refinada, relatórios e índice de suíte; qualificar cancelamento.
3. Medir tempo, pontos e armazenamento dos pilotos antes da matriz toda.
   Maxstep nominal `1/(384000*8)`; refinado à metade; pilotos a 768 kHz.
4. Aplicar gates de DC/Bode/null/harmônicas/THD/settling/onset/recuperação
   e orçamento agregado de incerteza; emitir gráficos e relatórios.
5. Qualificar WAV PCM32/float32, FIR, janela/escala fixa; preparar ABX e
   coletar respostas humanas reais.

Não há aprovação de áudio, CPU, latência, tempo real ou ABX. RAW/log
existentes e processo com retorno zero não substituem esses gates.
