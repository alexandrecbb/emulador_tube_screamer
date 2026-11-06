# Limpeza autorizada — 2026-11-05

O usuário autorizou remover tentativas incompletas e arquivos redundantes
exclusivamente em `F:\ts808-reference` e `F:\ts808-validation`.

- Removidos RAWs de 12 tentativas explicitamente falhadas, expiradas ou
  rejeitadas/canceladas, sem consumidor importado ou auditado: 7,7701 GiB.
- Quatro traces idênticos passaram a compartilhar armazenamento por links
  físicos: aproximadamente 0,2335 GiB. Caminhos e bytes preservados.
- Ganho real de espaço livre: 8,0036 GiB; espaço livre final: 37,0286 GiB.

Antes de cada remoção, foi conferido o hash e gravado um registro junto aos
metadados do produtor. Logs, circuitos, pedidos, resultados e os hashes
originais foram mantidos. Referências nativas válidas não foram removidas.
Os metadados das 12 remoções foram conferidos novamente após a operação.

Os 3.174 caminhos da auditoria canônica continuam presentes. Foram conferidos
os hashes dos arquivos de até 1 MiB e, individualmente, os traces deduplicados.
Os demais payloads grandes preservados não foram todos rehashados. Três
testes de proteção da limpeza passaram. Não houve novas simulações.

`journal.json` contém as operações; `audit-check.json`, a verificação;
`summary.json`, as contagens; `provenance.json`, caminhos e hashes originais.
Inventário completo, plano e script executado permanecem no diretório
`/mnt/f/ts808-validation/cleanup-20261105-r1`.

A requalificação continua bloqueada: ainda faltam cerca de 195,53 GiB livres
para o orçamento de 232,55 GiB. Esta limpeza não muda a qualificação anterior
nem aceita o MVP.
