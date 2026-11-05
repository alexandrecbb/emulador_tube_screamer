# Qualificação automática do MVP — resultados e gates de bloqueio

## Estado consolidado após a matriz — 2026-11-05

Avaliação completa: 128 entradas em 91 casos físicos; 50 entradas reprovadas por assentamento DC nos dois produtores.
Qualificação automática reprovada; MVP não aceito. Nenhum critério foi relaxado.
ABX humano realizado: 10/20, p=0,588099; listening permanece pendente pelo protocolo.
Detalhes, contagens, hashes e proveniência: [registro consolidado](../validation/results/qualification-2026-11-05/README.md).

As seções seguintes preservam o histórico e não representam o estado atual.

## Continuação de 2026-11-04

O usuário aprovou incorporar os subpassos. O produtor offline agora registra
`integration_rate_Hz=768000` e `substeps=4/2` nas saídas de192/384 kHz;
as respostas AC usam a taxa interna e falhas identificam o subpasso sem
publicar uma amostra externa incompleta. A execução histórica permanece
disponível na ausência dos campos novos. Schemas e contratos foram atualizados.
49 testes Python e30 subtests com produtor real passaram; CTest checked/release
passou. Os novos traces de alto drive e sobrecarga coincidem bit a bit com
as linhas correspondentes dos diagnósticos antigos de768 kHz.

O piloto central revisado passou em referência, precisão e WAV nos dois rates.
Alto drive e sobrecarga passaram numericamente, mas as referências originais
não cumpriram os limites mais estritos da qualificação WAV. No alto drive192,
a incerteza nominal/refinada foi0,924 uV RMS /2,358 uV pico, contra0,1 /1 uV.
Na sobrecarga192, o pico da diferença nominal/refinada foi1,084 uV.
Estão sendo produzidos pares novos com tolerâncias nativas100x mais apertadas,
mantendo a matriz física, maxsteps e critérios. Resultados anteriores ficam
preservados. A matriz completa continua condicionada aos seis pilotos com WAV.

Processos e evidências correntes: `F:\ts808-validation\substeps-20261104`.
As medições seguintes preservam o diagnóstico anterior à aprovação.

O usuário determinou usar F: para a validação completa. O planejamento atualizado
mediu aproximadamente 143 GiB livres nessa partição e estimou 120,71 GiB para
a matriz com as duas revisões de duração existentes, incluindo exportações RAW,
traces C++, PCM, fator adaptativo observado e margem de 10%. Esse cenário passa
no gate de espaço; estender todos os tons a 2 s de aquecimento ainda não cabe.
O planejamento deve ser repetido antes de uma execução e após novas revisões.

O diagnóstico revalidou as referências originais em F: e confirmou que nominal
e refinada dão exatamente o mesmo índice de recuperação nas três grades. A
quantidade limitante é `output`. A diferença RMS entre as soluções de 192/384 kHz
é 20,751 uV, e entre 384/768 kHz é 4,912 uV, compatível com convergência temporal.

Um executável experimental separado integra em 768 kHz e grava somente os
estados em 192/384 kHz, avaliando a fonte em todos os tempos internos. Nos dois
casos a recuperação diferiu zero amostras da referência nominal e todos os
critérios locais RMS/pico passaram. Os traces são bit a bit iguais às linhas
correspondentes do diagnóstico original de 768 kHz. Não houve ajuste de tempo,
ganho, interpolação de estados ou filtragem.

Isso não aprova o solver integrando em 192/384 kHz. A
[revisão de subpassos](designs/ts808_substep_revision.md) foi posteriormente
aprovada pelo usuário, alterando explicitamente o contrato das taxas de integração.
Produção, critérios, matriz completa e ABX permanecem no estado anterior.
Doctor F:, CTest checked/release e testes Python com produtor real passaram
(39 testes e 30 subtests). As novas evidências estão em
[continuation-2026-11-04](../validation/results/continuation-2026-11-04/README.md).

O restante deste relatório preserva os resultados da execução anterior.

Atualizado em 2026-11-04. A execução encerrou no gate dos pilotos; a aceitação combinada ainda não foi obtida.
Os limites T18/T22/T23 permanecem vigentes. Nenhuma resposta humana foi gerada.

## DC nativo e inicialização

Os logs de `runs/mvp-qualification/dc-audit.json` confirmam que
`gminsteps=0 srcsteps=0` não desabilita o pseudo-transiente do LTspice.
O ponto central obtido por esse caminho difere do C++ em no máximo
2,48 nV nos nós/estados de tensão e 1,13 fA nas correntes auxiliares.
O follower carregado foi conferido independentemente por
`Vout=(4.5+A0*4.5-Ro*Ibminus)/(1+A0+Ro/Rload)`; o ensaio original
sem nodeset diferiu dessa solução em 1,78e-15 V.

A realização original usava Cstate=1 F e correntes computacionais de até
1 MA. A biblioteca nativa agora usa Cstate=1 uF e corrente comportamental
multiplicada por 1e-6. A condutância estrutural de 1 nS continua exatamente
compensada. Dividir a KCL por 1e-6 recupera a mesma lei dz/dt; isso não
altera ganho, slew, saturação ou recuperação. O estado z continua em volts.
A realização anterior foi preservada em
`runs/mvp-qualification/models-before-state-scaling.lib`.

O DC nominal/refinado central passou com o solver normal após essa mudança;
o DC continua podendo usar pseudo-transiente. Não se deve confundir o tempo
artificial desse algoritmo com tempo físico da gravação. Ambos os produtores
iniciam o caso físico em t=0 a partir do equilíbrio, sem uic/startup. O C++
compromete as tensões dos capacitores, correntes iniciais zero e os dois z.
`nodeset` com o palpite do C++ não resolveu consistentemente o produtor e
não foi adotado como correção.

A redução de escala também eliminou a explosão de pontos observada no
standalone: a execução antiga foi cancelada após ultrapassar 22 milhões de
pontos ainda perto de 0,113 s. A nova completou 0,5 s em 9,36 s, com
1.536.157 pontos e RAW de 135.183.052 bytes. O ensaio de ambos os sinais,
cargas 2k/10k e recuperação foi comparado a uma integração DOP853 independente,
refinada em tolerância: pico do erro de z de 8,46 uV e da saída até 3,93 uV.
Ver `runs/mvp-qualification/opamp-qualification.json` e a receita
`validation/scripts/qualify_opamp.py`. Esse ensaio não aprova o pedal inteiro.

Uma tentativa de solver alternativo usou a grafia inválida `alternate`.
Esses logs mostram que o LTspice manteve o solver normal e são diagnósticos
inválidos para qualificar a configuração solicitada. O leitor agora rejeita
essa advertência. As grafias efetivas são `norm` e `alt`, verificáveis no log.

## Pilotos e critérios de avanço

`runs/mvp-pilots-02` preserva os pilotos originais de 1 s. No central,
a referência nominal gerou 3.076.011 pontos / 787.462.424 bytes em 43,20 s;
a refinada gerou 6.165.809 pontos / 1.578.450.783 bytes em 91,67 s.
No alto drive, foram 3.187.450 / 815.990.798 bytes / 38,59 s e
6.406.367 / 1.640.033.621 bytes / 90,90 s, respectivamente.
Os tempos nativos incluem o helper quando registrados como native_elapsed_s;
o log também preserva o tempo interno do simulador.

Os nulls/harmônicas/THD desses dois pilotos passaram nos checks implementados
nas três taxas, mas a estabilização DC falhou nas duas implementações:
99,26 uV no central e 204,27 uV no alto drive, contra 10 uV. A permanência
em 768 kHz mostra que aumentar a taxa não resolve esse assentamento físico.
Os resultados originais continuam reprovados e não serão promovidos.

Conforme a regra de revisão explícita de duração em T18,
`reference/ts808/case_revisions.json` registra novos IDs com 2 s de aquecimento
e janela [2,2.5) s, preservando os casos originais. O C++ central revisado
mediu mudança DC de 0,168 uV. A qualificação nominal/refinada e os gates numéricos desses novos casos passaram nas três taxas em `runs/mvp-revised-pilots-norm`. Os arquivos originais de 1 s continuam reprovados.

O C++ de sobrecarga completou as três taxas. A referência normal falhou no
início do transiente com matriz singular; as execuções efetivamente em `solver=alt` completaram e foram comparadas, com a falha numérica de recuperação detalhada abaixo. As tentativas e logs permanecem preservados.

A matriz completa exige no mínimo 93,66 GB somente para RAWs nominal/refinados
nos tempos originais, sem overhead adaptativo, WAV ou margens. O diretório
Windows configurado está no C:, com aproximadamente 18–23 GB disponíveis
nas medições desta execução. F: tem aproximadamente 78 GB, mas não é a raiz
qualificada dos pedidos atuais. Estender as durações aumenta o requisito.
A existência de espaço virtual livre no ext4 do WSL não comprova espaço
físico no volume que armazena seu VHD. A suíte não deve iniciar uma grade
que exceda o armazenamento retido disponível.

## Persistência, WAV e FIR

Foram implementados os schemas ausentes, importação com hashes dos originais,
comparação com referência refinada explícita, checks/gráficos e índice de suíte.
O índice inclui todos os casos/taxas previstos, inclusive os não invocados;
ausência de evidência impede aprovação. A integração de todos os estágios da
suíte continua sob verificação; um comando existente não demonstra aceitação.

A leitura grande mantém o parser e as APIs de spicelib 1.6.4 e mapeia seus
buffers binários, evitando cópias integrais por trace. Testes com os fixtures
reais conferem igualdade entre os caminhos normal e mapeado.
Cancelamento e timeout foram exercitados com processos nativos reais e
identidade PID/start-time, em `runs/mvp-qualification/lifecycle.json`.

O primeiro fixture WAV inclusivo produziu 769 frames em 192 kHz para 4 ms,
e é mantido como negativo. Nos pedidos exclusivos de exportação, o produtor
agora simula até T-h/2: cobre o último frame T-h e exclui o endpoint T.
A referência numérica independente continua cobrindo T. Não há corte,
padding, ajuste de ganho ou deslocamento posterior do WAV. Fixtures nativos
com 768/1536 frames passaram em ambos os rates, incluindo incerteza contra
uma referência RC refinada e erros RMS/pico locais/globais. As receitas e
resultados estão em `validation/scripts/qualify_native_wav.py` e
`runs/mvp-qualification/native-wav-qualified.json`.

Os FIRs prescritos (513/1025 taps) passaram: ripple máximo de aproximadamente
0,000184 dB até 20 kHz e rejeição superior a 93 dB a partir de 24 kHz.
Os coeficientes/hashes estão em `runs/mvp-qualification/fir-checks.json`.
Os testes conferem convolução direta, suporte completo, fase de decimação,
DC, quantização, clipping e grades. Isso qualifica a mecânica de exportação,
não os WAVs do pedal nem a escuta. Os pares ABX só podem ser publicados após
a aprovação de todos os gates automáticos requeridos.

## Atualização de cobertura e armazenamento

O RAW nominal da sobrecarga concluída em solver `alt` terminou em
1,4999999916908893 s: faltaram 8,31 ns para o endpoint 1,5 s. Essa referência
foi rejeitada, sem extrapolar nem ajustar timestamps. A geração numérica agora
simula um maxstep além do domínio declarado; só a janela original participa
dos checks. Os pontos adicionais são integração real do mesmo estímulo, não
padding de arrays. Esse guard não se aplica ao pedido exclusivo de export WAV,
cuja última amostra exigida é T-h.

Os novos pedidos de sobrecarga com guard estão em
`/mnt/f/ts808-reference/runs`, com o par Windows `F:\ts808-reference\runs`
conferido por doctor em `validation/toolchain-pilot-f.json`. Os originais no
C: continuam no lugar. `runs/mvp-qualification/resource-gate.json` registra
um preflight reprovado para a raiz C:; a estimativa de 93,66 GB também excede
o espaço livre da raiz F:. Aplicar 2 s de aquecimento à família dos 28 tons
levaria a um mínimo de aproximadamente 192,75 GB de RAWs nominal/refinados,
ainda sem overhead, WAV e margem. Não há autorização para remover arquivos
alheios ao trabalho para tentar acomodar essa matriz.

`runs/mvp-suite-attempt-20261103/summary.json` mantém o índice completo de
128 entradas esperadas. A execução foi barrada pelo gate dos pilotos; nenhum
caso omitido é marcado como aprovado.

## Resultado confirmado da sobrecarga — 2026-11-04

As duas referências com guard em F: passaram nos checks de incerteza. O nominal
produziu 4.621.084 pontos / 1.183.000.920 bytes em 89,56 s (helper); o refinado,
9.245.799 pontos / 2.366.927.978 bytes em 230,28 s. Os tempos C++ foram 6,48 /
12,02 / 23,58 s para 192 / 384 / 768 kHz, respectivamente.

| Taxa | Referência | Gates locais | Erro de recuperação | Resultado numérico |
| --- | --- | --- | --- | --- |
| 192 kHz | passou | RMS reprovou em 11 janelas | 33 amostras (171,875 us) | falhou |
| 384 kHz | passou | passaram | 7 amostras (18,229 us) | falhou |
| 768 kHz | passou | passaram | 1 amostra (1,302 us) | passou, diagnóstico |

O limite de recuperação é uma amostra na própria grade. Em 192 kHz, a maior
reprovação RMS local foi 4,243 uV contra orçamento de 1,118 uV naquela janela.
Os relatórios e gráficos estão em
`runs/mvp-pilots-02/overload_high/{192000,384000,768000}/comparison-ef36bde59e/`.
O índice `qualified-pilot.json` vincula explicitamente essas comparações.

Foi executado o diagnóstico aprovado com as seis tolerâncias de Newton 10x mais
apertadas, mantendo taxa, integrador, equações e limites de trabalho. O caso
completou, mas a diferença máxima de saída contra o baseline foi somente
8,72e-13 V, e a recuperação continuou reprovada por 33 amostras. Isso é compatível
com erro temporal de discretização, não resolvido por apertar Newton. Não foi
usado 768 kHz como substituto de uma taxa alvo. Nenhum resultado ABX pode promover
a aceitação combinada enquanto essas reprovações automáticas persistirem.

## Fechamento e evidências versionadas

Os nove relatórios finais dos três pilotos nas três taxas, gráficos, metadados,
logs nativos, auditoria das diretivas reais e hashes estão no
[pacote de evidências](../validation/results/mvp-2026-11-04/README.md).
Os RAWs e traces grandes ficam retidos localmente; os snapshots não os substituem.

Os casos central e alto drive com aquecimento explícito de 2 s passaram em
192/384 kHz e no diagnóstico 768 kHz. No alto drive, o nominal mediu 7.968.874
pontos / 2.040.035.400 bytes / 158,86 s e o refinado 16.016.868 pontos /
4.100.321.935 bytes / 293,86 s. C++: 20,69 / 37,90 / 71,24 s.
As medições centrais perdidas em retomadas foram repetidas em diretório temporário:
19,85 / 36,06 s em 192/384 kHz, com SHA-256 dos traces idêntico aos originais;
a duplicata temporária foi removida após a conferência. O centro em 768 kHz mediu
69,62 s. São tempos offline com I/O, não resultados de CPU/latência em tempo real.

O AC standalone adicional do op-amp, de 10 Hz a 10 MHz, passou contra a solução
complexa independente do follower carregado, incluindo Rid/Ro e o estado z:
erros de magnitude/ângulo abaixo de 6e-15 dB / 2e-14 graus e erro relativo do
estado abaixo de 2,9e-11. Não substitui o Bode do pedal nas 27 posições.

Doctor em C:/F:, CTest checked/release, caminhos Windows com espaço/acento/apóstrofo,
cancelamento e timeout passaram. A verificação Python final com produtor real
registrou **39 passed / 30 subtests passed**, com logs versionados. As passagens
da infraestrutura não promovem os gates numéricos reprovados.

Foram movidos de forma reversível 5,84 GB de RAWs de pedidos rejeitados/cancelados
para F:, depois de conferir os hashes das duas cópias. Os logs ficaram em C:;
referências válidas não foram movidas. O manifesto do arquivo permite restauração.
A mudança aliviou C:, mas não cria a capacidade necessária à matriz completa.

**Pendências:** recuperação da sobrecarga nas duas taxas alvo, espaço para a
matriz completa, comparação dos demais casos DC/Bode/transientes, qualificação
WAV de todos os casos e pares de escuta. O ABX humano continua não realizado.
Nenhum limite foi relaxado, nenhum resultado humano foi simulado e o diagnóstico
768 kHz não foi promovido a substituto de 192/384 kHz. A grade completa não foi
iniciada porque o pré-requisito dos pilotos não passou.
