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

## Resultado do piloto e orçamento medido — 2026-11-07

O piloto r3 passou referência, numérica e WAV nas duas taxas. A execução
precisou de WSL com 10 GB de RAM e 8 GB de swap após uma interrupção por OOM.
Originais nativos do piloto somam 19.855.180.677 bytes (~18,49 GiB).
O fator observado é 3,16735, superior ao fator inicial de 1,38917.
Assim, os dez casos restantes exigem aproximadamente 207,18 GiB livres,
incluindo a margem contratual do planejador. O orçamento inicial acima foi
superado pela medição; não deve orientar a execução completa.

`validation/scripts/complete_wav_requalification.py` reaproveita o piloto,
mede seus originais e bloqueia produtores quando falta espaço para os dez
casos restantes. Executa cada caso em um processo separado para liberar
memória entre casos. Reúne os relatórios por identidade física exata, sem
duplicar o piloto nem alterar as evidências antigas, e chama o auditor
existente para conferir as 128 entradas, hashes e identidades atuais.
Mesmo uma auditoria automática aprovada não substitui a aceitação humana.

Retomada de 2026-11-08: cinco casos aprovados; o refinado de
`tone_edge_t000_f5000_a100mv-warmup2s` excedeu o prazo operacional de 1800 s.
A nova execução r3 permite 7200 s por produtor via `TS808_NATIVE_TIMEOUT_S`,
com prazo WSL de 7230 s e registro `launch-policy.json` ligado ao hash do
pedido. O padrão permanece 1800 s. Esta alteração não muda os parâmetros do
circuito, os gates ou a identidade do validador; não constitui aprovação dos
seis casos restantes. A auditoria completa continua obrigatória.

Diagnóstico r3: o RAW interrompido declarou 156.971.101 pontos e chegou a
0,2849431318758579 s dos 2,5 s requeridos em 7200 s. A execução r4, autorizada
pelo usuário, move esse caso para o fim e testa um novo par nominal/refinado
com solver `alt` em ambos. Os outros cinco casos pendentes são tentados antes;
falhas individuais são registradas sem bloquear as tentativas seguintes.
Nenhum RAW parcial é promovido. A auditoria integral só começa com toda a
fila concluída; aprovação continua sujeita aos mesmos gates.
