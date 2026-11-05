# Seleção de modelo com Jev

Preencha `JEV_API_KEY` no `.env` da raiz. O arquivo é ignorado pelo Git;
`.env.example` documenta as variáveis. `JEV_MODEL` é opcional (padrão `jev-latest`).
O script usa somente a biblioteca padrão do Python, sem instalar dependências.

```bash
python3 scripts/codex_jev.py "Revise a documentação do projeto"
python3 scripts/codex_jev.py --launch "Investigue a convergência de Newton"
python3 scripts/codex_jev.py --dry-run "Implemente uma função Python"
```

Sem `--launch`, consulta Jev e mostra a escolha. Com `--launch`, abre uma nova
sessão interativa do Codex neste projeto, com o modelo e esforço escolhidos.
Não troca o modelo de uma conversa aberta nem transfere seu histórico.
O Codex usa sua autenticação existente e conserva as configurações de permissões.
Os modelos precisam estar disponíveis na sua conta; indisponibilidade é reportada
pelo Codex. Antes de lançar, o script confere modelo e esforço no catálogo de
`codex debug models` da instalação em uso. Se indisponíveis, interrompe sem
abrir a sessão e sem substituir o modelo. A conferência do catálogo não garante
que o backend aceitará a requisição. Ajuste `PROFILES` se o acesso mudar.

Perfis: `gpt-6-luna/low` para tarefas simples; `gpt-6-sol/medium` para implementação;
`gpt-6-sol/high` para problemas numéricos; `gpt-6-astra/high` para investigações excepcionais.
São regras de seleção iniciais, não uma garantia de modelo ótimo ou de economia.
Confiança abaixo de 0,5 usa Sol/high; esse limiar ainda exige calibração real.
Resposta inválida ou falha de API interrompe a execução sem iniciar o Codex.

Somente a descrição fornecida e os critérios fixos são enviados à Typesafe.
O script não lê automaticamente código, logs, histórico ou arquivos do projeto.
Cada consulta real pode consumir créditos Jev; `--dry-run` não faz chamadas.
A chave não aparece nos argumentos do Codex nem na saída do script.
O estado da implementação e validação está no início de `SESSION_HANDOFF.md`.

Fontes: [API oficial Typesafe](https://docs.typesafe.ai/api/system-one),
[Choice](https://docs.typesafe.ai/primitives/choice) e
[modelos Codex](https://learn.chatgpt.com/docs/models).
