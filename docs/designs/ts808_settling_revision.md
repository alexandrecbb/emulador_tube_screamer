# Revisão explícita de assentamento DC — 2026-11-05

O usuário solicitou resolver as reprovações de estabilização DC. A cláusula
de assentamento do [T18](ts808_validation_contract.md) exige um caso de maior
duração, explicitamente identificado, quando a janela original não está
estabilizada. Esta revisão aplica essa regra; não altera limites de aceitação.

## Evidência e causa investigada

A avaliação completa de 2026-11-05 registrou 50 entradas reprovadas em 25
casos físicos. Em todos eles, tanto o C++ quanto o LTspice reprovaram somente
a mudança de DC entre as duas metades da janela de 0,5 s.

Os dois pilotos anteriormente revisados para 2 s de aquecimento passaram
nos dois produtores: aproximadamente 0,168 µV no Center e 0,321 µV no High,
contra o limite de 10 µV. A rede de Vref tem R=10 kΩ || 10 kΩ e C=47 µF,
portanto uma constante de tempo RC de 0,235 s. O prolongamento do aquecimento
em 1,5 s prevê uma atenuação exponencial de aproximadamente 0,00169.
A compatibilidade desse decaimento com as medições sustenta o diagnóstico
de transiente físico residual, sem dispensar os novos ensaios nativos.

## Casos revisados

Somente os 25 tons reprovados recebem novos identificadores `-warmup2s`,
novos hashes físicos, duração de 2,5 s e janela final [2,0; 2,5) s.
As revisões constam em [case_revisions.json](../../reference/ts808/case_revisions.json).
Circuito, estímulo e onset, inicialização DC, tolerâncias, passos máximos,
integração interna de 768 kHz e saídas de 192/384 kHz são preservados.

A janela continua tendo 0,5 s, dividida em duas metades de 0,25 s. Mantêm-se
todos os gates, incluindo DC ≤10 µV, fundamental ≤0,1%, THD, null,
incerteza nativa e comparações locais. Os WAVs devem cobrir a nova duração
inteira, inclusive o onset, com N=duration×rate quadros.

Os casos originais continuam reprovados. Um resultado revisado só os substitui
na nova matriz após sua própria qualificação de referência, numérica e WAV.
DC/AC, hold, sobrecarga, linearidade, escuta e os tons já aprovados conservam
suas evidências originais, sujeitas à nova auditoria de integridade.

## Execução e armazenamento

[resolve_dc_settling.py](../../validation/scripts/resolve_dc_settling.py)
prepara os manifestos e um orçamento com crescimento medido dos RAWs; pode
executar diagnósticos C++ antes do custo das referências independentes.
[run_settling_requalification.py](../../validation/scripts/run_settling_requalification.py)
verifica o espaço, executa os 25 casos revisados e reúne as evidências originais
preservadas para auditar as 128 entradas. Uma reprovação permanece reprovação.

Diretório preparado: `/mnt/f/ts808-validation/settling-revision-20261105-r1`.
O orçamento medido, incluindo margem, é 249.704.962.498 bytes
(aproximadamente 232,55 GiB livres). Na preparação havia apenas 29,72 GiB.
O gate impediu iniciar produtores nativos com espaço insuficiente.

Esta revisão e os diagnósticos C++ não aprovam a matriz nem o MVP.
O ABX humano anterior permanece uma evidência separada, sem demonstração
de equivalência perceptual universal.
