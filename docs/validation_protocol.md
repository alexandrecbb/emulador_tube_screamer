# Evidência e próximos gates

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
