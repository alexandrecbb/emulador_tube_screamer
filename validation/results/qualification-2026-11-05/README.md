# Qualificação completa — avaliação concluída e reprovada

A auditoria cobriu 91 casos físicos e 128 entradas,
com 3174 arquivos verificados. Qualificação automática:
**failed**; avaliação: **completed**.

50 entradas reprovaram. Falhas obrigatórias: `{'cpp_settling_dc': 50, 'reference_settling_dc': 50}`.
Os dois produtores reprovaram no assentamento DC: a diferença DC entre as
metades da janela deve ser no máximo 10 µV. Por exemplo, o tom central de
1 kHz/10 mV mediu cerca de 58,74 µV no C++ e no LTspice.
Isso bloqueia o WAV desses casos, sem demonstrar uma discrepância entre os
produtores. Nenhuma equação, janela ou tolerância de aceitação foi relaxada.

Resultados por categoria: `{'reference': {'passed': 128}, 'numerical': {'passed': 78, 'failed': 50}, 'wav': {'not_applicable': 54, 'passed': 24, 'pending': 50}}`.
Os pares lineares foram avaliados conjuntamente; os WAVs elegíveis foram
qualificados. A execução interna é de 768 kHz, com saídas em 192/384 kHz
(4/2 subpassos). Referências antigas e tentativas incompletas foram preservadas.
A importação interrompida na pausa foi recuperada sem repetir a simulação.
A primeira auditoria bloqueou um manifesto WAV legado sem `native_options`;
a nova auditoria aceita exclusivamente essa omissão de campo derivado,
conferindo todas as opções no pedido/deck originais e rejeitando divergências.
Novos manifestos WAV persistem as configurações completas do pedido.

O ABX humano **foi realizado**: uma pessoa, uma sessão, 20 tentativas,
10 acertos, p unilateral = 0.588099.
Alexandre relatou não perceber diferenças e não demonstrou distinção acima
do acaso nessa condição. Ausência de significância não prova equivalência
universal. O gate `listening` permanece `pending` pelo protocolo.
**O MVP não está aceito.**

`automatic-qualification.json` e `human-abx-result.json` são cópias exatas de
registros de escopos/momentos diferentes. O primeiro audita apenas a matriz
(`outside_automatic_audit`); o segundo registra o ABX
humano anterior à conclusão da matriz (`full_matrix_qualification=pending`
naquela data). `summary.json` integra o estado atual sem alterar os originais.
Hashes e caminhos estão em `provenance.json`; a cadeia auditada de arquivos
está em `integrity.json`. RAWs, traces e WAVs permanecem em F:.

Verificações: 64 testes Python e 28 subtestes passaram; um teste nativo opcional
não foi executado. CTest offline-checks e offline-release passaram.
O script do produtor é uma cópia de arquivo de evidência; seus caminhos
relativos pressupõem o diretório original indicado na proveniência.

A próxima etapa técnica exige revisar explicitamente a duração de
assentamento para uma nova tentativa da matriz, com novo orçamento de espaço,
sem substituir ou promover as reprovações desta execução.
