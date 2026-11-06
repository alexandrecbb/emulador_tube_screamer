# Requalificação das referências WAV

A avaliação r4 concluiu os 91 casos/128 entradas: referência e comparação
numérica passaram em todas as entradas; 22 entradas, correspondentes a
11 casos físicos, falharam na qualificação WAV.

Todas as 22 falharam no limite de incerteza RMS nominal/refinada de 0,1 µV;
13 também falharam no pico de 1 µV. No caso
`tone_edge_t100_f5000_a100mv-warmup2s`, as duas taxas falharam ainda no RMS
do WAV nativo contra a referência nominal: aproximadamente 1,350/1,262 µV,
contra 1 µV. Este gate avalia a exportação nativa do LTspice, não o erro do
modelo C++. A comparação numérica C++ permanece uma evidência separada.

A correção em investigação aperta `reltol`, `abstol`, `vntol` e `chgtol`
nativas em 100 vezes nos dois membros do par, mantendo a relação nominal/
refinada. O produtor WAV herda as opções efetivas da referência nominal.
Preserva circuito, estímulo, duração inteira com onset, janela, inicialização,
solver por caso, maxsteps T18, integrações e todos os limites. Não altera o
validador, os casos físicos nem promove relatórios anteriores.

O primeiro piloto é o caso com os maiores erros, identificado acima.
[requalify_wav_references.py](../../validation/scripts/requalify_wav_references.py)
seleciona apenas reprovações WAV pareadas que já passaram nas fases de
referência e numérica. O modo padrão executa somente esse piloto; `--all`
seleciona os 11 casos, exigindo orçamento completo antes de iniciar produtores.
Tentativas usam novos diretórios em F: e retêm RAWs, logs e proveniência.

O orçamento inicial é aproximadamente 9,30 GiB para o piloto e 102,33 GiB
para os 11 casos, usando crescimento observado da execução anterior.
Tolerâncias mais apertadas podem elevar o custo: medir o piloto antes de
ampliar a execução. Aprovação do piloto não substitui as 22 entradas nem a
auditoria completa de 128 entradas. Reprovação exige novo diagnóstico;
não autoriza relaxar limites ou reduzir cobertura. MVP permanece não aceito.
