## COMMIT/PUSH SOLICITADOS — 2026-11-06

Usuário autorizou commit e push das alterações pendentes. Inclui correção de
assentamento, limpeza auditada, requalificação r4 reprovada e piloto WAV100x.
Piloto ts808-wav-tight-pilot-20261106-r1.service ainda em execução nesta gravação;
monitor registra resultado posteriormente. Não declarar a correção WAV aprovada.
Artefatos volumosos/referências nativas permanecem em F:, fora do Git.
Este commit registra o estado parcial; confirmar SHA remoto após push.
Nenhum desligamento solicitado nesta operação. Histórico abaixo.

## CORREÇÃO WAV EM INVESTIGAÇÃO — PILOTO 100x — 2026-11-06

Usuário pediu corrigir os pontos reprovados. r4 continua preservada/reprovada.
22entradas/11casos falham incerteza WAV RMS;13também pico. Duas entradas
edge_t100/5kHz/100mV falham RMS do WAV LTspice contra sua referência nominal
(não se trata de erro C++). Critérios, circuito e validador inalterados.
Iniciado piloto desse caso com tolerâncias nativas100x mais apertadas nos
pares nominal/refinado e no produtor WAV; maxsteps/solver/onset preservados.
Serviço: ts808-wav-tight-pilot-20261106-r1.service.
Output: /mnt/f/ts808-validation/wav-tight-pilot-20261106-r1/
Log: /mnt/f/ts808-validation/wav-tight-pilot-20261106-r1.log
Script: validation/scripts/requalify_wav_references.py; modo padrão só piloto.
Plano em output/plan.json:~9,30GiB piloto,~102,33GiB todos11casos; F:~74GiB
antes do piloto. Usuário consultado sobre liberar mais40GiB. Não ampliar antes
de medir custo real e conferir espaço/processos. Não iniciar duplicados.
Gate completo exercitado: /mnt/f/ts808-validation/wav-tight-all-20261106-plan-r1/
status blocked_storage; nenhum produtor adicional iniciado.
Monitor: ts808-wav-tight-monitor-20261106-r1.service; registra resultado do piloto
em snapshot pequeno e no topo deste handoff ao término. Não inicia outros jobs.
Suíte Python:71passed,1skipped,28subtests (inclui5testes novos de proteção).
Documentação:
docs/designs/ts808_wav_reference_revision.md. Piloto ainda não aprovado;
correção completa e auditoria128entradas pendentes; MVPnãoaceito.
Sem commit/push/desligamento nesta operação. Histórico abaixo.

## REQUALIFICAÇÃO R4 CONCLUÍDA — 2026-11-06

Avaliação concluída: 91 casos físicos, 128 entradas. Qualificação automática: failed; entradas reprovadas: 22.
Resultados por categoria: {'reference': {'passed': 128}, 'numerical': {'passed': 128}, 'wav': {'not_applicable': 54, 'passed': 52, 'failed': 22}}.
Critérios e circuito preservados. MVP não aceito.
ABX humano anterior: 10/20, p=0,588099; listening permanece pendente pelo protocolo.
Evidências: /mnt/f/ts808-validation/settling-requalification-20261106-r4/qualification/.
Python/build/CTest checked e release aprovados; logs: /mnt/f/ts808-validation/settling-requalification-20261106-r4/finalization-checks.log.
Snapshot com hashes/proveniência: validation/results/settling-requalification-2026-11-06-r4/.
Estado externo da finalização: /mnt/f/ts808-validation/settling-requalification-20261106-r4-finalization-state.json.
Nenhum commit/push/desligamento executado nesta retomada.
As seções inferiores preservam histórico.

## RETOMADA DA VALIDAÇÃO — R4 — 2026-11-06

Usuário pediu continuar de onde parou. r3 estava interrompida: serviço ausente,
nenhum produtor Linux/Windows ativo, estados running obsoletos. Foram encontrados
48/50 relatórios revisados; resta tone_high_f82_a500mv-warmup2s nas duas taxas.
F: ~80GiB livres, orçamento restante ~9,30GiB; interop Windows conferido.
Retomada em novo diretório, preservando r3 e verificando identidade/hashes.
Serviço: ts808-settling-resume-20261106-r4.service.
Output: /mnt/f/ts808-validation/settling-requalification-20261106-r4/
Log: /mnt/f/ts808-validation/settling-requalification-20261106-r4.log
Consulta de estado antes de qualquer retomada; não iniciar produtores duplicados.
Script run_settling_requalification.py reúne os resultados e audita91casos/128entradas.
Finalizador independente: ts808-settling-finalize-20261106-r4.service.
Aguarda o produtor terminar; exige avaliação completa, roda checks e salva snapshot,
proveniência e relatório/handoff. Falha bloqueia promoção e fica no estado externo.
Script: /mnt/f/ts808-validation/settling-requalification-20261106-r4-finalize.py
Estado: /mnt/f/ts808-validation/settling-requalification-20261106-r4-finalization-state.json
Log: /mnt/f/ts808-validation/settling-requalification-20261106-r4-finalize.log
Verificações nesta sessão:71passed,1skipped,28subtests; build/CTest
checks e release passaram. Critérios e circuito preservados; MVP não aceito.
A retomada atual executa validação e consolidação. Não executa a entrega histórica
com commit/push/desligamento por constar nas seções antigas.
As seções inferiores preservam histórico.

## RETOMADA E ENTREGA AUTORIZADAS — SERVIÇO R3 — 2026-11-06

Usuário pediu continuar e, ao terminar, commit, push e desligamento do Windows.
A tentativa r1 perdeu o processo sem traceback e deixou status running obsoleto:
2entradas aprovadas;1reprovada somente WAV (incerteza de referência RMS
0,355502µV contra0,1µV);47pendentes. Causa da morte não comprovada.
Não promover essa reprovação; referências e todos os artefatos r1 preservados.

Retomada parcial acrescentada: valida metadados/traces/identidade das entradas
com relatório, reaproveita referências nativas verificadas e preserva diretórios
de taxas incompletas antes de refazer apenas o necessário. Validador de métricas
inalterado.71testes passaram,1opcional ignorado,28subtests passaram.

Serviço systemd usuário: ts808-settling-delivery-20261106-r3.service.
Output: /mnt/f/ts808-validation/settling-requalification-20261106-r3/
Log: /mnt/f/ts808-validation/settling-requalification-20261106-r3.log
Entrega: /mnt/f/ts808-validation/settling-requalification-20261106-r3-delivery-state.json
Script: validation/scripts/complete_settling_delivery.py, flag explícita de
commit/push/shutdown usada sob autorização atual. Após avaliação completa
91casos/128entradas, inclusive eventual reprovação, roda Python/build/CTest
checked e release, preserva snapshot e atualiza relatório/handoff. Então commit
de tudo pendente, push origin/main, confere SHA remoto e árvore limpa, solicita
shutdown.exe /s /t 60 do Windows. Não usa /f. Falha técnica/check/push bloqueia
desligamento e fica registrada no estado externo. MVP não aceito automaticamente.
Não iniciar produtores duplicados. Consulte serviço/status/log antes de agir.

Tentativa r2 falhou antes de produtores: serviço não herdava PATH para
powershell.exe. Corrigido em r3 com PATH/WSL_INTEROP/WSL_DISTRO_NAME explícitos;
interop Windows testado com sucesso em serviço. r2 preservado, não retomar dele.
Espaço na retomada:~224GiB livres; orçamento agora exclui caso concluído.
As seções abaixo são históricas e não revogam a autorização desta seção.

## REQUALIFICAÇÃO RETOMADA — EM EXECUÇÃO — 2026-11-05

Usuário informou que liberou espaço e autorizou a continuidade. Conferidos
253380673536 bytes livres em F: (~235,98GiB), acima do orçamento
249704962498 bytes (~232,56GiB). Nenhum produtor Linux/Windows concorrente.
Iniciado run_settling_requalification.py para25casos revisados/50entradas.
PID38342; sessão de execução9529. Não iniciar produtor duplicado.
Output: /mnt/f/ts808-validation/settling-requalification-20261105-r1/
Log: /mnt/f/ts808-validation/settling-requalification-20261105-r1.log
status.json registra execução; primeiro caso tone_center_f1000_a010mv-warmup2s.
Scripts preservam referências anteriores e critérios. Resultado ainda pendente;
MVP não aceito. Testes proporcionais:5passed (settling_revision/storage_cleanup).
Sem autorização nova de commit/push/desligamento. Se desconectado, conferir
status.json e processos antes de agir; não assumir que execução foi interrompida.
As indicações de espaço bloqueado abaixo são históricas.

## LIMPEZA CONCLUÍDA — REQUALIFICAÇÃO AINDA BLOQUEADA POR ESPAÇO — 2026-11-05

Usuário autorizou eliminar tentativas incompletas e arquivos redundantes nas
pastas F:\ts808-reference e F:\ts808-validation. Limpeza concluída, exit0:
12RAWs de tentativas failed/timed_out/rejected_or_cancelled removidos,
7,7701GiB;4traces duplicados substituídos por links físicos após SHA256,
0,2335GiB. Ganho real medido:8,0036GiB; F:~37,03GiB livres.
Logs, decks, requests/results, hashes e referências válidas preservados.
Cada RAW removido tem cleanup-removed-payload.json ao lado dos metadados
originais, com hash/motivo. Não consumir essas tentativas como referências.
Caminhos dos traces e seus bytes/hashes continuam válidos após deduplicação.

Auditoria pós-limpeza:3174caminhos canônicos presentes; hashes dos arquivos
até1MiB conferidos. Payloads grandes preservados não foram todos rehashados;
os traces deduplicados foram individualmente conferidos antes da operação.
Metadados de todas as12remoções e links das4deduplicações verificados ao fim.
3testes de proteção passaram. Nenhum produtor ativo ou nova simulação iniciada.
Não houve commit/push/desligamento nesta operação.

Registros completos: /mnt/f/ts808-validation/cleanup-20261105-r1/
inventory.json,applied/plan.json,applied/journal.json,applied.log,
audit-check.json,summary.json,executed-script.py. Snapshot pequeno:
validation/results/cleanup-2026-11-05/. Script reutilizável:
validation/scripts/cleanup_validation_storage.py. Não repetir a remoção manual.
Os links anteriores já evitavam30,11GiB de duplicação antes desta limpeza.

A requalificação dos25casos revisados ainda precisa de232,55GiB LIVRES:
faltam~195,53GiB adicionais. Não iniciar produtores até o gate de espaço passar.
O estado da correção DC e comando de retomada estão na seção seguinte.
Contagens da matriz anterior e ABX humano permanecem iguais; MVPnãoaceito.

## RETOMADA AUTORIZADA — CORREÇÃO DC PREPARADA; ESPAÇO BLOQUEIA NATIVO — 2026-11-05

Usuário pediu resolver as falhas de estabilização DC. T18 exige revisão
explícita de duração, sem relaxar critérios. Foram acrescentadas 25 revisões
`-warmup2s` a reference/ts808/case_revisions.json, mantendo a janela de0,5s,
estímulo, circuito e todos os gates. Os dois pilotos já revisados continuam
intactos. A matriz anterior permanece REPROVADA até a nova qualificação.

Preparação: /mnt/f/ts808-validation/settling-revision-20261105-r1/
cases.json contém25casos novos; complete-cases.json contém91casos ativos.
plan.json conserva origem/hash da avaliação anterior e orçamento medido.
Diagnósticos C++ de edgeT0/5kHz/100mV e High/82Hz/500mV nas duas saídas
CONCLUÍDOS:4entradas aprovadas, DC~0,308/~0,348µV; gate10µV preservado.
Produtor PID5884/sessão14729 terminou exit0. Nenhum produtor nativo iniciado.
cpp-diagnostics.json não substitui qualificação nativa/WAV.
Snapshot pequeno: validation/results/settling-revision-2026-11-05/.

Orçamento necessário:249704962498bytes (~232,55GiB) LIVRES em F:.
Há ~29GiB: faltam cerca de205GiB adicionais após os diagnósticos.
Gate nativo foi exercitado e bloqueou ANTES de iniciar produtores.
Usuário foi consultado sobre liberar espaço; aguardar alteração real do estado.
Não apagar/mover RAWs, traces, logs ou relatórios originais.
Compressão NTFS testada em1RAW, hash SHA256 confirmado antes/depois;
razão1,0:1, sem ganho relevante; nenhuma compressão em lote iniciada.
compression-probe.json/log preserva a operação no caminho original.

Scripts novos: validation/scripts/resolve_dc_settling.py prepara revisões e
probes; validation/scripts/run_settling_requalification.py executa os25casos,
reúne as aprovações antigas por links e audita128entradas sem promover falhas.
Correção em suite.py evita preparar ABX numa partição sem listen_high.
qualify_substep_pilots.py agora filtra somente os pilotos declarados em vez
de tratar todas as revisões como pilotos. Não executar scripts históricos
que escrevem na raiz antiga. Validador de métricas e executável inalterados.
Testes:66passed,1nativoopcionalskipped,28subtests, log na preparação.
Documento: docs/designs/ts808_settling_revision.md.

Quando houver espaço suficiente, conferir processos nativos/volumes e usar:
PYTHONPATH=validation .venv/bin/python validation/scripts/run_settling_requalification.py --prepared /mnt/f/ts808-validation/settling-revision-20261105-r1 --output /mnt/f/ts808-validation/settling-requalification-20261105-r1
Usar novo output se uma tentativa já existir. Script revalida espaço e casos;
solveralt+nodesetT22, norm no edgeT0/5kHz/100mV conforme antecedente conhecido,
tolerâncias originais/maxsteps preservados. Referências100x antigas dos pilotos
não serão regeneradas. Novos WAVs só após gates numéricos aprovados.

Não há novo commit/push nem desligamento autorizado nesta retomada.
A autorização anterior já foi cumprida. ABX humano existente10/20,p0,5881;
aceitação do MVP ainda pendente. Histórico abaixo.

## MATRIZ CONCLUÍDA — AVALIAÇÃO REPROVADA — 2026-11-05

Cobertura completa: 91 casos físicos,128 entradas; auditoria de
3174 arquivos concluída. automatic_qualification=failed;
assessment_completion=completed; 50 entradas reprovadas por
cpp_settling_dc/reference_settling_dc (limite10µV), WAV bloqueado nesses casos.
Não alterar critérios nem promover reprovações. Os demais resultados e
contagens estão em validation/results/qualification-2026-11-05/README.md.
Pares lineares/WAV finalizados, originais/hashes preservados. ABX humano já
realizado10/20,p0.588099,listeningpending; MVP NÃO ACEITO.

Evidência original: /mnt/f/ts808-validation/substeps-20261104/qualification-audit-r12-20261105/qualification/qualification.json
Partição: /mnt/f/ts808-validation/substeps-20261104/qualification-resume-r11-20261104/matrix/summary.json
Não reexecutar automaticamente. Uma próxima tentativa demanda revisão
explícita da duração de assentamento e novo orçamento de armazenamento.
Nenhuma simulação foi repetida para recuperar a importação pausada.
Testes64passed,28subtests,1nativo opcional skipped; CTest checked/release passou.

Usuário autorizou commit/push de tudo pendente e desligamento do Windows
hospedeiro via WSL APÓS concluir processos e conferir push. Estado de entrega
(commit, verificação remota, solicitação de desligamento) será registrado em
/mnt/f/ts808-validation/substeps-20261104/qualification-resume-r11-20261104/delivery-state.json
Credenciais .env e artefatos volumosos não entram no Git. Histórico abaixo.

## MATRIZ EXECUTADA; AUDITORIA r12 ATIVA — 2026-11-05

Usuário autorizou continuar e, ao concluir todos processos, fazer commit/push
completo e desligar o Windows hospedeiro via WSL. Não desligar antes de verificar push.
Matriz r11 terminou:128relatórios presentes; oito lineares passaram numérico/WAV.
50tons reprovados exclusivamente cpp_settling_dc/reference_settling_dc nos dois
produtores; WAV bloqueado nesses. Nenhum critério/equação relaxado.
Partição final: /mnt/f/ts808-validation/substeps-20261104/qualification-resume-r11-20261104/matrix/summary.json

Auditoria r11 parou em74/128: manifesto WAV histórico de piloto omitiu o campo
derivado native_options; pedido original o contém e deck/hash são auditados.
Correção r12 aceita somente essa omissão histórica, rejeita qualquer parâmetro
declarado divergente. Novos WAVs persistem request.reference_settings completo.
Teste de regressão cobre solver/calibração/maxstep/extra/missing conflitantes.
64testes+28subtests passaram,1nativo opcional skipped; CTest checks/release passou.
Métrica validator_sha256 permanece inalterada. Nenhum nativo/WAV regenerado.

Auditor r12: /mnt/f/ts808-validation/substeps-20261104/qualification-audit-r12-20261105/,
execute.py/log/status.json, qualification/progress.json. Sessão9793.
NÃO editar qualification.py enquanto ativo. Não iniciar duplicados.
ABX humano é fora do escopo do auditor; r12 corrige lembrete histórico incorreto.
ABX já realizado10/20,p0.5881,listeningpending; MVPnãoaceito.
Após auditoria, adaptar/executar r11/publish.py para registrar snapshot pequeno,
atualizar docs/handoff, conferir credenciais, gitdiffcheck, commit/pushverificado,
encerrarprodutores e solicitar shutdown.exe /s do Windows. F:~30GiB livres.
Histórico abaixo.

## RETOMADA AUTORIZADA APÓS /compact — 2026-11-05

Usuário pediu continuar. Produtor r11 em
/mnt/f/ts808-validation/substeps-20261104/qualification-resume-r11-20261104/,
execute.py/log/status.json; sessão31032. Conferência inicial: nenhum produtor
Linux/LTspice Windows; F:44GiB livres. Não iniciar duplicados.
Primeiro importa RAW refinado já concluído de tone_high_f5000_a010mv,
verificando integridade e preservando parciais; depois mede as duas taxas e
retoma os cinco casos restantes, pares lineares/WAV e auditoria128entradas.
Reusa r10 com hashes; sem repetir referências concluídas. Critérios intactos.
Reprovações de assentamento DC serão registradas; conclusão da avaliação
não implica aprovação. ABX humano já realizado, conforme histórico abaixo.
Usuário autorizou commit e push de todas as alterações pendentes, seguidos de
desligamento do Windows hospedeiro via WSL, SOMENTE após concluir os processos.
Conferir exclusão de credenciais e artefatos volumosos; verificar push antes
de desligar. Testes r11:63passed,1skipped,28subtests; CTest checks passou.
Estado histórico de pausa abaixo
foi revogado pelo pedido explícito de retomada.

## PAUSADO POR PEDIDO DO USUÁRIO PARA /compact — 2026-11-05T00:42:30.452711+00:00

NÃO RETOMAR sem novo pedido explícito. Produtor r10 PID194712 recebeuSIGINT;
sessão17146 terminou comexit130. O produtor nativo já havia concluído; SIGINT interrompeu a importação do RAW.
Resultado nativo e parciais preservados. Nenhum LTspiceativo no Windows.
Estado da pausa: /mnt/f/ts808-validation/substeps-20261104/pause-state-20261105T004230Z.json
Última partição: /mnt/f/ts808-validation/substeps-20261104/qualification-resume-r10-20261104/matrix/summary.json
Log: /mnt/f/ts808-validation/substeps-20261104/qualification-resume-r10-20261104/execute.log; status.jsonfailed por cancelamento usuário,
não confundir com nova reprovação numérica. Nenhum auditor em execução.

60/72relatórios transientes presentes; somados54DC/AC+2hold =
116/128relatórios. Ponto: tone_high_f5000_a010mv, nominal concluído,
refined NATIVO CONCLUÍDO, importação interrompida. Reaproveitar RAW válido
após conferir originais; não repetir simulação semnecessidade.
Pedido refinado: /mnt/f/ts808-reference/runs/tone_high_f5000_a010mv-refined-2035339bb21c4452b789564d64e22054
Preservar diretório de importação parcial em nova tentativa.
Faltam fechar estecaso,5kHz100/500mV,82Hz10/100/500mV, depois pareslineares/WAV
no fim da suíte e auditoria completa. Não regenerar casos concluídos.
Referências de100x mantidas nos pilotos/sobrecarga central; próximos casos
usam tolerânciasoriginais, solveralt+nodesetT22independente (norm no
caso tone_edge_t000_f5000_a100mv, já medido). Critérios/equações inalterados.
Falhas medidas nos relatórios: {'cpp_settling_dc': 38, 'reference_settling_dc': 38}.
Até aqui reprovações por assentamentoDC de ambosprodutores; não promover
varredura/rejeição a aprovação. WAV fica bloqueado quando numericalfailed.
Sobrecarga central reparada passoureference/numerical/WAV nasduastaxas.
Todos pilotos reutilizados. ABXhumano realizado10/20, p0.5881; listeningpending
pelo protocolo, semprova de equivalência universal. MVPnãoaceito.

Retomada: novo diretório F:, reutilizar esta partição via suite(resume_from=...),
solveralt, native_topology_nodeset=True, continue_native_failures=True,
override tone_edge_t000_f5000_a100mv=norm; não sobrescreveroriginais.
Auditor consolidate(require_passed=False) / CLI --record-rejections registra
cobertura e reprovações semrelaxar critérios; require_passed padrão continua
estrito. Só concluir avaliação com128entradas; identity/import continuamgates.
Últimos testes completos58passed/28subtests,1nativoopcionalpulou; r9/tests.log.
9testes específicos passaram após continue_native_failures; gitdiffcheckpassou.
Nãohouvecommit/push/desligamentoWindows. Detalhes anteriores abaixo.

## RETOMADA r10 APÓS TIMEOUT NATIVO — 2026-11-04

Usuário perguntou por que interrompeu. Conferência mostrou r9 failed, PID173461
ausente; atualização anterior de andamento estava desatualizada e foi corrigida.
r9 avançou até tone_edge_t000_f5000_a100mv; refined alt+nodeset excedeu timeout.
Request preservado /mnt/f/ts808-reference/runs/tone_edge_t000_f5000_a100mv-refined-66f9607e9b35430992a4c091671ee7b1/.
reference_result reason Native producer timeout, elapsed2864.489s; limite
configurado1800s. Não inferir causa externa ou atribuir a cancelamento usuário.
RAW parcial847579726bytes preservado.40/72relatórios transientes produzidos;
com54DC/AC+2hold já há96/128relatórios, ainda semfechamentolineares.
F:68GiBlivres; nenhum LTspiceativo antesda nova execução.

Novo produtor /mnt/f/ts808-validation/substeps-20261104/qualification-resume-r10-20261104/,
execute.py/log/status.json. Reutiliza r9 verificando originais, tenta norm no
caso que teve timeout (parinteiro, semmisturarsolvers); restantealt+nodeset,
tolerânciasoriginais/maxsteps/critériosiguais. continue_native_failures=True
registra falha do produtor como NOT_EVALUATED e continua outroscasos; nunca
promove essa entrada. Identidade/importação continua bloqueante.
Consolidação só conclui com128entradas presentes; faltantes continuam bloqueio.
9testes específicos passaram após ajuste, gitdiffcheckpassou. Não duplicar.
Meta permanece concluir varredura e auditoria, possivelmente REPROVADA:
assentamento DC falhou em vários tons, WAV bloqueado nesses. ABXhumanorealizado.

## VARREDURA COMPLETA r9 ATIVA — 2026-11-04

Sessão80488; /mnt/f/ts808-validation/substeps-20261104/qualification-resume-r9-20261104/,
execute.py/log/status.json. Reutiliza todos relatórios r8, inclusive reprovados.
Próximos casos usam tolerâncias nativas ORIGINAIS da matriz (scale1), alt+nodeset
T22 independente nos dois níveis; critérios/maxsteps/modelo inalterados.
Referências100x mantidas nos casos que precisaram; custo medido extrasignificativo
emtempo/espaço, não repetir em casos novos semnecessidade. F:91GiBlivres.
r8 interrompido explicitamente no pedido parcial440Hz10mV, cancelamento do helper
finalizado e retido. Nenhum LTspiceativo na transição; não duplicar produtor.

Meta: CONCLUIR avaliação de128entradas, sem prometer aprovação. Tonscentrais
1kHz10mV e500mV reprovados nasduastaxas por assentamento; WAV bloqueado.
Sobrecarga central100x aprovada reference/numerical/WAV nasduastaxas.
Todos pilotos reaproveitados atécentral1kHz100mVwarmup2s; overload_highambos.
r9 chama consolidate(require_passed=False) mesmo se suite exit40; gera
qualification.json com automatic_qualification failed quando houverreprovações,
assessment_completion completed apenas com cobertura/gatesavaliadosouWAVbloqueados.
Audita originais/hashes/critérios semrelaxamento. NÃO editar qualification.py
enquanto r9ativo (auditorhashcapturadonoinício). ABXhumano realizado10/20.
9testesauditorpassaram; suítePythoncompleta atéantesúltimoteste57/28subtests,
1nativoopcionalpulando. Nenhum commit/push. Continuar atéfechamentoefetivo.

## r8 CONTINUA — SOBRECARGA CENTRAL APROVADA; REPROVAÇÃO REAL DE ASSENTAMENTO

Produtor r8 ativo, sessão46493, execute.log/status.json em
/mnt/f/ts808-validation/substeps-20261104/qualification-resume-r8-20261104/.
Sobrecarga central reparada: reference/numerical/WAV passed em192/384, no seed.
Par nativo alt+nodesetT22 independente100x apertado; C++r5 reaproveitado intacto.
Reutilização dos lineares/listen/mute concluída, overload_highpilotoambostambém.
Primeiro novo tom tone_center_f1000_a010mv passou referência mas FALHOU
cpp_settling_dc/reference_settling_dc em ambas taxas:~58.738uV contra10uV.
Ambosprodutoresconcordam; não relaxar limite nem trocar duração da matriz atual.
WAV pending por bloqueio numérico. Executar toda cobertura e registrar
qualificação reprovada se necessário: varredura concluída não significa aprovada.
Em andamento tom central1kHz100mVwarmup2s(pilotoreuso). Não duplicar produtor.

Auditor foi estendido com require_passed=False (CLI --record-rejections) para
auditar cobertura/integridade completa e emitir automatic_qualification=failed,
assessment_completion=completed com failed_checks e WAV bloqueados explícitos.
Modo padrão continua exigindo tudo passed.9testes específicos passaram.
Após r8 terminar com exit40, executar CLI de consolidação em NOVO diretório
com --record-rejections --transient-summary r8/matrix/summary.json.
O execute.py r8 aborta antes de consolidar se código nãozero (esperado pelas
reprovações); usar novo processo auditor pois hash do auditor mudou.
Auditor não integra hash das métricas. ABX humano já realizado10/20.

## QUALIFICAÇÃO r8 EM EXECUÇÃO — 2026-11-04

Pasta /mnt/f/ts808-validation/substeps-20261104/qualification-resume-r8-20261104/,
execute.py/log/status.json; sessão registrada no histórico de ferramentas.
Primeiro recompõe overload_center com nominal/refined solveralt+nodesetT22
independente100x mais precisos. Nominal concluído em overload-center-nominal-alt-diagnosis-20261104/;
refined em overload-center-refined-diagnosis-20261104/. Traces C++r5 intactos.
r7 foi bloqueado corretamente: parnorm/alt não permite comparar refinamento.
Novo parmesmosolver. suite.py passa a opção native_topology_nodeset para
ambosníveis; r8 novoscasos usamalt+nodeset, tol100x e maxstepsoriginais.
WAV agora preserva .nodeset do produtor nominal, além das .options; nenhuma
equação/métrica/limite alterado. Hash do validador permanece mesmo: lista de
fontes em compare.validator_hash não inclui suite.py nem audio_qualification.py;
pedidos e decks nativos têm identidade própria verificada no relatório.
57testes/28subtests passaram,1teste nativo opcional pulado; tests.log r8.
Aguardar r8, não duplicar. Qualificação completa e MVP ainda pendentes.
ABX humano realizado, resultado10/20, sem prova universal de equivalência.

## QUALIFICAÇÃO r7 EM EXECUÇÃO — 2026-11-04

Pasta /mnt/f/ts808-validation/substeps-20261104/qualification-resume-r7-20261104/,
execute.py/log/status.json; sessão99651. Primeiro recompara overload_center
com nominal100x de r6 e refined100x alt+nodeset independente concluído em
/overload-center-refined-diagnosis-20261104/; reaproveita traces C++ r5 intactos.
Depois retoma matriz e consolida128entradas. Critérios/circuito inalterados.
Refined r6 norm ficou no DC sem RAW; tentativa própria WindowsPID16256 foi
encerrada explicitamente para tentaralt (registro refined-normal-early-stop.json).
Alt semnodeset falhou. Ambos preservados nos *-attempts.json.
Diagnóstico alt+nodeset independente T22 passou inicialização e completou.
Não usar solução C++ para nodeset. suite.py permite explicitamente tolerâncias
mais apertadas, retry de solver por falha do produtor e nodeset T22 nos refined;
WAV conserva opções nominais existentes. Importação/identidade continuam gates.
Alteração apenas orquestração, sem mudança de hash do validador.
Testes completos em tests.log r7. Nenhum outro produtor ativo. Não duplicar.
Qualificação matriz e MVP ainda pendentes; ABX humano já realizado (abaixo).

## QUALIFICAÇÃO r6 EM EXECUÇÃO — 2026-11-04

Nova pasta /mnt/f/ts808-validation/substeps-20261104/qualification-resume-r6-20261104/,
execute.py/log/status.json; sessão29609. Reutiliza r5; overload_center é
repetido com tolerâncias LTspice100x mais apertadas, maxsteps/critérios iguais.
r5 passou numerical nas duas taxas, mas WAV uncertainty peak foi1.0104668uV
contra1uV em192kHz (384tambémfalhou). r5 interrompido por SIGINT durante
conferência do piloto overload_high, antes de nova produção; originais retidos.
Nova suíte pode repetir falha do produtor no outro solver, em novo request,
preservando cada tentativa em *-attempts.json; erros de importação/identidade
continuam bloqueantes. Apenas orquestração alterada: suite.py não integra
hash do validador. Sete testes específicos passaram; suíte Python em andamento
sessão49736, tests.log na nova pasta. Sem mudança física ou relaxamento.
Consolidação final programada ao fim em qualification/. Ainda pendente.
Não duplicar produtores. ABX humano já realizado; ver seção própria abaixo.

## RETOMADA r5 APÓS FALHA NATIVA ISOLADA — 2026-11-04

r4 concluiu mute_1000hz_500mv nas duas taxas (reference/numerical/WAV passed),
mas overload_center solver alt falhou imediatamente com singular clip_minus.
Original preservado: /mnt/f/ts808-reference/runs/overload_center-nominal-a493fd77a1ba4c8db39629bb201918ed/.
Nova execução em /mnt/f/ts808-validation/substeps-20261104/qualification-resume-r5-20261104/,
execute.py/log/status.json; sessão44859. Reutiliza r4 com verificações integrais;
overload_center agora norm, listen_high alt, demais conforme histórico.
Não alterou implementação, circuito, passos ou critérios. Consolidação automática
programada ao fim; pendente até status completed e qualification.json passed.

## QUALIFICAÇÃO COMPLETA RETOMADA POR PEDIDO EXPLÍCITO — 2026-11-04, r4

Usuário: “Conclua a qualificação da matriz”. Preflight: F:109GiB livres,
nenhum produtor Python/C++ ou LTspice ativo. Nova execução PID138410,
sessão exec56552, pasta /mnt/f/ts808-validation/substeps-20261104/qualification-resume-r4-20261104/.
execute.py/log/status.json registram andamento. Não duplicar produtores.
Seed preserva r3 e importa byte a byte listen_high384000 já aprovado da
listening-preparation-20261104; parcial384 preservado em novo seed.
A suíte verifica identidade atual, hashes de traces e originais nativos antes
reutilizar. Restante: solver norm, listen_high alt e overload alt, conforme
partições anteriores. Circuito e critérios inalterados. Após suíte aprovada,
execute.py chama auditor consolidate para 128 entradas na subpasta qualification/.
Seis testes específicos do auditor/retomada passaram nesta retomada.
ABX humano realizado (10/20); interpretação e evidências na seção abaixo.
Qualificação completa e MVP seguem pendentes até fechamento efetivo.

## ABX HUMANO REALIZADO E ANALISADO — 2026-11-04T19:22:53Z

Usuário entregou C:\Users\Alexandre\Desktop\Resultados dos teste e relatou
não perceber distinção.20JSONs são salvamentos sucessivos da MESMA sessão;
os dois completos são idênticos. Identidades/schemas, respostas anteriores
sem alteração, sessão original e22hashes WAV conferidos. Arquivos recebidos
copiados e preservados; nenhum original sobrescrito. Uma sessão humana real,
Alexandre, listen_high384000 convertido48kHz,20tentativas.
Resultado:10/20acertos, binomial unilateral exato p=0.5880985260009766,
alfa0.05, Holm família primary-alexandre com uma sessão. Não detectada
discriminação acima do acaso. Não prova equivalência perceptual universal.
Registro subjetivo: participante relata não perceber distinção nesta sessão.

Evidência: /mnt/f/ts808-validation/substeps-20261104/abx-human-results-20261104T192253Z/
result.json, resultado.md, received-index.json, received/ e analysis/.
Chave original permanece separada em listening-preparation-20261104/abx/private.
ABX humano agora REALIZADO; evaluate_family mantém listening=pending
por resultado não significativo, conforme protocolo (não transformar em passed).
Qualificação automática COMPLETA da matriz e aceitação MVP continuam pendentes.
Nenhum job longo iniciado para esta análise. Não generalizar a todos humanos,
condições, equipamentos, ou caracterizar os20downloads como20sessões.

## ÁUDIOS E SESSÃO DE ESCUTA PRONTOS — 2026-11-04

Pedido: preparar tudo para ouvir os áudios. Entrega pública Windows:
F:\ts808-validation\escuta-ts808-20261104\OUVIR.html
WSL: /mnt/f/ts808-validation/escuta-ts808-20261104/OUVIR.html
Página local com A/B/X,20 tentativas, confirmação, persistência no navegador
quando disponível e exportação de respostas JSON. Nenhuma resposta humana
foi registrada. Não apresentar a chave antes de concluir a escuta.

Nova execução isolada listen_high384000 concluiu reference/numerical/WAV
passed, validator atual, executável/circuito/critérios inalterados. Job:
/mnt/f/ts808-validation/substeps-20261104/listening-preparation-20261104/
report comparison/report.json; prepare.log/status.json completed; delivery.json.
Referências nominal/refined reutilizadas da r3 após verificação de originais;
novo WAV nativo: listen_high-wav-384000-7da8d7f086cb487eb598d58a74d85d48.
Sessão original em abx/blinded; chave em abx/private/key.json, fora da entrega.
A cópia pública contém22WAVs de48kHz mono float32, hashes conferidos,
session.json sem respostas, OUVIR.html e LEIA-ME.txt. JS node --check passou;
fluxo da interface verificado em memória com fixture sintética, sem escuta.

Ao receber JSON humano: validar schema e identidades contra sessão original;
conferir respostas20/completion e arquivos antes de evaluate_family, usando
chave privada original e family_id primary-alexandre. Não alterar original
para fingir conclusão. Guardar retorno humano em novo diretório com os WAVs
correspondentes (hardlinks/cópias verificadas), pois evaluate_family resolve
artefatos relativamente ao JSON. A sessão se chama abx.
Qualificação automática COMPLETA da matriz ainda pendente; r3 perdeu produtor
sem status final (ver abaixo); esta entrega qualifica só listen_high384000.
ABX humano e aceitação MVP pendentes. Não há jobs desta preparação ativos.

## PREPARAÇÃO DE ESCUTA SOLICITADA — 2026-11-04

Usuário pediu preparar áudios e ABX. Na inspeção, produtor r3 PID112810
já não existia, embora status.json ainda dissesse running; consolidador também
não estava ativo. Causa não determinada. Preservar status/log/saídas originais.
r3 completou listen_high192000 com reference/numerical/WAV passed; run384000
ficou incompleto. Não declarar qualificação completa.
Nova preparação isolada em F: listening-preparation-20261104/, no mesmo root
substeps-20261104. prepare.py reutiliza referências nominais/refinadas de r3,
executa C++384000, comparação e WAV completos, depois prepara ABX às cegas.
Sessão exec74134; log prepare.log e status.json na pasta. Não duplicar.
create_player.py gera página local OUVIR.html em abx/blinded após preparação.
Nenhuma resposta humana criada. Chave privada deve ficar fora da apresentação.

## RETOMADA AUTORIZADA — 2026-11-04, r3

Usuário autorizou continuar após /compact. Preflight: F:118GiB livres,
nenhum produtor da matriz ou LTspice ativo. Novo produtor PID112810,
sessão39692, preserva e reutiliza a última matrix pausada em
remaining-transients-resume-20261104/matrix.
Nova saída: /mnt/f/ts808-validation/substeps-20261104/remaining-transients-resume-r3-20261104/
Log externo com mesmo prefixo e extensão .log. Consolidador sessão30827
aguarda o status desta nova partição; saída futura full-qualification-r3-20261104/
e log full-qualification-r3-20261104.log no mesmo volume. Não duplicar jobs.
Circuito/critérios inalterados; originais cancelados preservados.
Testes nesta retomada:56passed+30subtests com TS808_NATIVE_TESTS=1;
git diff --check passou. Qualificação completa, ABX humano e MVP pendentes.
A pausa abaixo foi revogada pelo novo pedido explícito do usuário.

## PAUSADO POR SOLICITAÇÃO DO USUÁRIO — 20261104T180532Z

Usuário pediu pausa para usar /compact. Produtor PID108289 recebeu SIGINT;
helper nativo confirmou cancelamento e preservou resultado. Consolidador em
espera PID109972 recebeu SIGTERM. Ambos encerraram; consulta Windows confirmou
nenhum LTspice ativo. Não retomar implementação/validação sem novo pedido.
Estado desta pausa: /mnt/f/ts808-validation/substeps-20261104/pause-state-20261104T180532Z.json

Última partição: /mnt/f/ts808-validation/substeps-20261104/remaining-transients-resume-20261104/matrix/summary.json.
Quatro casos lineares (oito relatórios) foram reutilizados após conferir hashes
e originais; ainda falta fechar pares e WAVs no final da suíte. A pausa ocorreu
na nova referência nominal listen_high com solver alt. Tentativa nativa:
/mnt/f/ts808-reference/runs/listen_high-nominal-8f256f56f9884d29819462697b1c9240/
completion do helper: failed. Não importar referência cancelada.
status.json do wrapper foi preservado com status failed e mensagem
Cancelled reference; finalized helper result retained — é cancelamento pelo
usuário, não reprovação numérica medida. O índice registra interrupção.

Na retomada, usar resume_substep_transients.py com --resume-from apontando para
a matrix acima e --output NOVO em F:. Não sobrescrever os dois jobs anteriores
nem rerodar DC/AC/hold ou os quatro casos lineares já processados. O script
confere manifest/toolchain, hashes de traces/relatórios, executável/validator e
originais antes do reuso; preserva cópia de diretórios incompletos. listen_high
permanece override alt após falha norm. Circuito e critérios inalterados.

O consolidador deve ser iniciado novamente com --transient-summary e
--wait-for-partition apontando para a NOVA retomada. Sua última versão registra
auditor_sha256 além de validator/executável. Sessão93512 foi interrompida;
não há auditoria final em execução ou aprovação completa.

Pré-auditoria54DC/AC+2hold passou (1678 arquivos). Seis pilotos atuais passaram
reference/numerical/WAV. Últimos testes:15 focados; suíte55pass/1skip+28subtests;
nativa54pass+30subtests antes dos dois testes extras de retomada. MVP e ABX
humano pendentes. Sem commit/push/desligamento. Há alterações locais sem commit.

## Qualificação completa: retomada após falha nativa — 2026-11-04

A primeira partição remaining-transients-20261104 terminou com falha nativa
em listen_high: solver norm, pseudo-transiente encontrou OP e matriz singular
em clip_out. Original preservado em /mnt/f/ts808-reference/runs/
listen_high-nominal-0dfc29e53eef433fb50d778127662417/. Os quatro casos físicos
lineares têm oito relatórios numéricos ainda pendentes do fechamento dos pares;
não repetir simulações já concluídas. PID99696 terminou. Consolidador inicial
terminou sem aprovação (full-qualification-20261104.log).

RETOMADA ATIVA: PID108289, sessão exec21253; novo job
/mnt/f/ts808-validation/substeps-20261104/remaining-transients-resume-20261104/.
Status em status.json, índice matrix/summary.json; log externo
/mnt/f/ts808-validation/substeps-20261104/remaining-transients-resume-20261104.log.
Script validation/scripts/resume_substep_transients.py chama suite com
resume_from da partição anterior, copiando metadados e hardlinkando traces
(só leitura); confere identidades/hashes e originais antes de reutilizar cada
caso. Diretórios de tentativas incompletas são preservados na nova cópia.
Override explícito listen_high=alt; demais norm, overload mantém alt histórico.
Não se alteraram circuito, tolerâncias ou critérios.

suite.py agora aceita resume_from e native_solver_overrides opcionais; planejamento
de espaço desconta apenas os casos já completos reutilizados. Validador de métricas
permanece com hash df57852f796c97448ac180f6fd4050c448b434c5324818ad455ddbed8eb20266.
Testes:15 focados passaram; suíte sem nativos opcionais55pass/1skip+28subtests.
Antes dos dois testes extras de retomada, suíte nativa54pass+30subtests passou.

Auditoria preliminar das54DC/AC+2hold PASSOU:1678 arquivos, resultado em
consolidation-preflight.json. Não equivale à qualificação completa.
Novo consolidador ativo: sessão exec23023, aguardando status do job acima;
log full-qualification-r2-20261104.log, saída futura full-qualification-r2-20261104/.
Comando usa --transient-summary apontando para nova matrix/summary.json.
Após aprovação da partição, auditará cobertura128, hashes/proveniência e AC384.
ABX humano e aceitação MVP continuam pendentes. Não duplicar produtores.

## Qualificação completa solicitada — 2026-11-04

Usuário pediu realizar a qualificação completa automática. PID99696 continua
produzindo a partição de72 transientes restantes (não duplicar). A cobertura
final prevista é54DC/AC +2hold +72transientes =128 entradas.

Novo módulo validation/ts808_validation/qualification.py e script
validation/scripts/consolidate_substep_qualification.py reconciliam cobertura
exata, identidades físicas/executável/validator, relatórios AC secundários384,
hashes dos traces, referências nativas originais, exportações WAV e artefatos.
Auditam originais sem mover/retargetar/sobrescrever evidências; arquivos são
rechecados por stat antes de publicar. ABX humano/MVP permanecem pendentes
mesmo se a qualificação automática passar.

Consolidador já iniciado (sessão exec13962), aguardando status.json da partição:
log /mnt/f/ts808-validation/substeps-20261104/full-qualification-20261104.log
saída futura /mnt/f/ts808-validation/substeps-20261104/full-qualification-20261104/.
Só audita/publica após status completed/exit0; falha não vira aprovação.
Preflight independente das56 entradas concluídas ainda rodando (sessão83859):
consolidation-preflight.log; resultado será consolidation-preflight.json.
Testes novos:4 passaram. Suíte Python sem TS808_NATIVE_TESTS:53pass/1skip,
28subtests; testes nativos completos50/30 já passaram antes desta alteração
somente no consolidator (núcleo e validador histórico inalterados).

## Continuação nesta sessão — 2026-11-04

Usuário pediu continuar nesta própria sessão. Confirmado refresh exit0: seis
pilotos reference/numerical/WAV passaram sob validator atual. matrix-alt parou
em hold_center após54 entradas aprovadas (27DC+27AC),74 não avaliadas.

Novo script validation/scripts/diagnose_hold_reference.py executou duas
inicializações em diretório separado, sem modificar o circuito/tolerâncias:
solver norm sem nodeset e alt com nodeset independente da solução C++ (guess
físico T22). Ambos passaram reference/numerical em192/384. Qualificação WAV
adicional do norm passou nas duas taxas. Resultado hold aprovado separado em
/mnt/f/ts808-validation/substeps-20261104/hold-diagnosis-20261104/norm/
(comparison/report.json em cada taxa; audio-diagnosis.json resume). Tentativas
alt são diagnóstico numérico, sem WAV qualificado. Log principal
hold-diagnosis-20261104.log; áudio em hold-diagnosis-audio-20261104.log.
Não promover esses diretórios como se fossem parte da matrix-alt original.

CONTINUAÇÃO ATIVA: PID99696, sessão exec41961, pasta
/mnt/f/ts808-validation/substeps-20261104/remaining-transients-20261104/.
status.json e run.log consolidam progresso; matrix/summary.json contém índice.
Manifesto cases.json seleciona36 casos físicos transientes (72 entradas),
excluindo hold_center já qualificado, DC e AC já concluídos. suite roda com
native_solver=norm, overload mantém alt explícito; seis pilotos são reutilizados
com seus settings/proveniências originais e verificações de integridade.
Não reiniciar produtores nem repetir as54 entradas anteriores.

resource-gate passou:130051489075 bytes estimados contra136843689984 livres.
Primeiro caso em andamento:linear_center_a010uv. scope.json vincula hashes dos
índices anteriores e qualificação hold. Esta partição NÃO é matriz completa:
ainda será preciso reconciliar54+2+72 entradas e conferir evidências/identidades
antes de qualquer qualificação combinada. MVP não aceito; ABX humano pendente.
Sem commit/push ou desligamento autorizado nesta continuação.

## Retomada da matriz-alt — 2026-11-04

A matriz retomada completou os casos DC e AC registrados antes de `hold_center`;
os resultados concluídos no índice em
`/mnt/f/ts808-validation/substeps-20261104/matrix-alt/summary.json`
passaram referência e análise numérica. O job wrapper encerrou com exit1 após
a falha nativa de `hold_center` (PID original 85456 e observador 90050 não estão
mais ativos). `status.json` registra refresh exit0 e matrix-alt exit1.

Falha preservada em `/mnt/f/ts808-reference/runs/hold_center-nominal-b8af5c46c9fe460ebeeda60e685306ed/`: LTspice 26.1.1 `solver=alt` informa OP direto encontrado e em seguida
matriz singular em `clip_minus`; produtor exit1, log/RAW mantidos. O índice da
matriz marca hold_center e itens não invocados seguintes como não avaliados.
A matriz anterior `matrix` não contém referência aprovada reutilizável para
hold_center. A suíte não suporta retomada incremental; relançá-la repetiria
casos e exige novo diretório. Não alterar solver/circuito/critério nem declarar
a matriz completa. Diagnóstico ou protocolo alternativo requer decisão técnica
explícita e identidade de evidência própria.

Próximo passo: ler log e índices; qualquer investigação de convergência fica
separada da matriz aprovada. Espaço F: permaneceu em cerca de129 GiB após a
falha. MVP/ABX continuam pendentes.

## Correção dos perfis Jev — 2026-11-04

scripts/codex_jev.py: implementation/numerical agora usam gpt-6-sol medium/high,
conforme catálogo REAL de codex debug models do CLI0.157.1. Luna/low e Astra/high
mantidos e conferidos no mesmo catálogo. Antes de --launch, confere presença
visível do modelo e suporte ao esforço; falha clara sem substituição silenciosa.
Cinco testes unitários passaram, incluindo bloqueio de lançamento se catálogo
falhar e rejeição do antigo gpt-6.1-sol. Consulta Jev real retornou numerical/
gpt-6-sol/high (0,95). Smoke real codex exec efêmero, read-only, em /tmp com
gpt-6-sol/medium respondeu OK e exit0. Não abriu novo produtor de validação.
Docs atualizadas; conferência do catálogo não garante acesso futuro no backend.
Pipeline original permanece no refresh; centro192/384 e alto drive192 já passaram
reference/numerical/WAV com o leitor atual no log. MVP/ABX continuam pendentes.

## Tentativa de --launch — 2026-11-04

Usuário solicitou executar scripts/codex_jev.py com --launch. Jev selecionou
implementation/gpt-6.1-sol/medium (confiança0,57). CLI0.157.1 abriu, mas o
backend rejeitou: model_not_found, modelo não suportado com autenticação ChatGPT.
Logo: classificação Jev funciona; execução com esse perfil NÃO foi validada.
Sessão filha interrompida; pipeline de validação existente permanece independente.
Não substituir modelos silenciosamente; PROFILES precisa refletir acesso real da conta.

## RETOMADA AUTORIZADA — 2026-11-04 17:18 UTC

Usuário pediu retomar implementação/validação e conferir scripts/codex_jev.py.
Pausa revogada explicitamente. Nenhum LTspice nativo/produtor estava ativo;
F: com129 GiB livres, toolchain-pilot-f doctor passou. CTest checked/release
passou (build sem alterações); Python com TS808_NATIVE_TESTS=1:50 testes e30
subtests passaram novamente nesta retomada.

As duas comparações reader-guard existentes (centro192/384) foram preservadas
com sufixo -preserved-20261104T171803Z, incluindo a parcial. Não se alteraram
originais nem se regeneraram referências/WAVs.

Pipeline em execução: PID85456; diretório
/mnt/f/ts808-validation/substeps-20261104/resume-20261104T171822Z/.
run.py usa lock exclusivo resume.lock e executa refresh_substep_pilots.py;
somente exit0 libera run_substep_matrix.py --native-solver alt para matrix-alt.
Estado consolidado em status.json; logs refresh.log, matrix-alt.log e runner.log.
Consultar esse estado e processos antes de qualquer nova tentativa; não duplicar.
Matriz ainda não iniciada no registro desta retomada; qualificação dos seis
pilotos com identidade atual ainda em execução. MVP/ABX continuam pendentes.

Seletor Jev:3 testes unitários passaram; consulta REAL autenticada selecionou
numerical, gpt-6.1-sol/high, confiança0,95, Jev1.14.0 (516 tokens entrada/49 saída).
Script funciona sob demanda, sem daemon/hook de troca automática nesta sessão;
--launch abre NOVA sessão Codex. Não foi iniciada sessão concorrente.

O restante preserva histórico anterior à retomada.

## PAUSADO POR SOLICITAÇÃO DO USUÁRIO — 2026-11-04

Usuário pediu “Dê uma pausa”. Todos os jobs desta tarefa foram interrompidos;
nenhum produtor LTspice estava ativo no momento da pausa. Não retomar sem
pedido do usuário. Estado salvo em
`/mnt/f/ts808-validation/substeps-20261104/pause-state.json`.

Subpassos incorporados e seis pilotos passaram reference/numerical/WAV após
refinamentos100x de alto drive e sobrecarga. Matriz inicial `matrix` executou
14 entradas AC (7 passaram,7 falharam) e foi interrompida para diagnóstico:
LTspice solver normal declarou sucesso DC com input_base=1e200 V. Diagnóstico
em ac-bias-diagnosis confirmou alt e/ou nodeset fixo independente recuperam
DC e AC; alt sem nodeset diferiu do C++ em1,03e-10 V. Não se mudou o circuito.

Leitor agora rejeita magnitudes impossíveis>=1e100; fixture RAW/log real negativo
foi adicionado. Testes finais:50 Python e30 subtests nativos passaram. Essa
mudança alterou validator_hash, exigindo revalidar os seis pilotos. Novo helper
requalify_existing_audio verifica originais WAV/RAW/log e compara WAV já existente
com referências revalidadas, evitando regenerar simulações aprovadas.

PAUSA interrompeu refresh_substep_pilots.py (PID65514) e o observador
run_substep_matrix.py (PID67147). A nova `matrix-alt` NÃO começou. O refresh
foi interrompido durante geração de gráfico de comparação, deixando diretório
reader-guard parcial; consultar pause-state.json e preservar/renomear esse
diretório antes de repetir. O índice pilots.json ainda aponta os seis relatórios
aprovados do leitor anterior; não promover silenciosamente para o leitor novo.

Na retomada: finalizar refresh dos pilotos, então rodar run_substep_matrix.py
--native-solver alt. Nova suíte processa DC antes de AC, exige DC correspondente
aprovado e conserva ordem canônica no índice. Reusa runs/relatórios dos pilotos
após conferir originais, hashes e identidades, sem regeneração. Estimativa de
espaço da matriz passou; havia cerca de129 GiB livres emF na última medição.
Não há ABX realizado nem aceitação combinada do MVP.

O restante preserva histórico anterior à pausa.

## Continuação solicitada — 2026-11-04

ATUALIZAÇÃO: o usuário aprovou explicitamente incorporar os subpassos.
Implementação C++ offline, schemas, finalizador/comparador, AC e diagnósticos
de falha atualizados. Campos opcionais pareados integration_rate_Hz/substeps;
saídas192/384 com interna768 e4/2 passos. Sem campos, execução histórica.
Model::advance continua um passo interno. Contratos aprovados atualizados.

ÚLTIMO ESTADO: os seis pilotos passaram numericamente. Centro192/384 também
passou WAV. Alto drive WAV falhou por incerteza das referências antigas
0,924 uV RMS /2,358 uV pico; sobrecarga por pico1,084 uV. Limites0,1 /1 uV.
O primeiro produtor terminou com exit40; o primeiro observador de matriz
terminou sem executar a matriz. Não chamar esses resultados de aprovação.

Refinamentos em andamento: refine_substep_pilot_reference.py para
overload_high --factor100 (PID31799 nesta execução) e para
tone_high_f1000_a500mv-warmup2s --factor100 --solver alt (PID33304).
Novo nominal alto drive em norm falhou singular na inicialização e foi
preservado em reference-tol100; a tentativa alt é distinta em
reference-tol100-alt. Nominais de sobrecarga e alto drive alt já produzidos;
refinadas ainda em execução. Tolerâncias100x, maxsteps originais mantidos.
Logs em /mnt/f/ts808-validation/substep-{high-alt,overload}-refinement-20261104.log.

finish_substep_qualification.py --wait-for-pids31799 33304 está aguardando
ambos os refinamentos; depois consolida os dois pares/relatórios explicitamente
e só libera a matriz se todos os seis reference/numerical/WAV passarem.
Log substep-final-matrix-20261104.log. Esse consolidator também evita perder
uma linha de índice pela versão antiga do refinador de sobrecarga, iniciada
antes da adição de lock de atualização. A versão atual do refinador usa flock
e preserva qualified-pilot.json por refinamento. Não iniciar duplicatas.

Production-overload-equality.json e production-high-equality.json confirmam
igualdade bit a bit entre produção nova e as linhas dos diagnósticos768.
verification.json registra49/30 Python nativo, CTest checked/release e doctor F:.
snapshot_substep_results.py arquivará metadados leves quando concluir.

Teste final atual:49 testes Python e30 subtests nativos passaram; CTest
checked/release passou. Novo ReferenceSession verifica hashes ao primeiro
consumo no comando e confere stat de todos os originais/inputs antes de
reutilizar e publicar. Evita reler12GB para cada uma das fases do mesmo caso;
comandos independentes não compartilham cache. Teste de mutação passou.

Pilotos rodando via validation/scripts/qualify_substep_pilots.py; output
/mnt/f/ts808-validation/substeps-20261104, log substep-pilots-20261104.log.
Reutiliza explicitamente referências antigas com configuração de proveniência
própria (tons emC, sobrecarga emF), sem mover/retargetar originais. Exportações
WAV novas vão paraF. Cada taxa terá comparação nova e WAV. Manifesto cases.json
no output usa as duas revisões de duração existentes e subpassos em todos
os casos. A suíte foi atualizada para as duas taxas AC, planejamento completo
de espaço e reuso explícito de referências dos pilotos.

Um segundo processo run_substep_matrix.py aguarda o produtor dos pilotos
terminar e só executa a matriz se pilotos.json/full_matrix_authorized=true;
valida hashes do executável, validador e seis relatórios aprovados. Log
/mnt/f/ts808-validation/substep-matrix-20261104.log. Não iniciar duplicatas.
Consultar os processos/logs e índices; nenhum resultado humano foi coletado.

O texto abaixo preserva o diagnóstico anterior à aprovação.

Usuário pediu continuar a implementação e definiu F: como único volume com
disponibilidade para a matriz. Novos payloads em
`/mnt/f/ts808-validation/continuation-20261104`; usar toolchain-pilot-f.json
para produtores em `/mnt/f/ts808-reference/runs`. Doctor passou.

Planejamento atual: cerca de 143 GiB livres; estimativa 120,71 GiB para matriz
com as duas revisões existentes, incluindo overhead observado, export RAW,
traces/PCM e margem. Hipótese de estender todos os tons ainda excede F:.

Novos scripts `diagnose_overload_convergence.py` e `plan_f_storage.py`;
alvo CMake opt-in `ts808_substep_diagnostic`, separado da produção. Integração
768 kHz com saídas192/384 kHz deu recuperação zero amostras de erro e todos
os critérios locais passaram. Traces iguais bit a bit à seleção de linhas
do diagnóstico original768. Referências nominal/refinada têm mesmos índices
nas três grades; saída é quantidade limitante. Não promove execução nas
taxas originais. Evidências em validation/results/continuation-2026-11-04.

Foi enviada pergunta assíncrona ao usuário sobre aceitar revisão explícita
do contrato de taxas para permitir subpassos. Aguardar resposta antes de
alterar produção ou liberar a matriz. Proposta concreta em
docs/designs/ts808_substep_revision.md. Sem aprovação registrada até aqui.
Testes Python reais39/30, CTest checked/release e doctor F: passaram.

## Encerramento da sessão anterior — 2026-11-04

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
