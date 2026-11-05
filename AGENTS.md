# Orientações do projeto

- Comunique-se em português, com respostas e atualizações concisas.
- O projeto é um emulador TS808 offline em C++20; a validação usa Python e LTspice nativo no Windows via WSL. Plugin e tempo real ficam fora do escopo atual.
- Consulte o início de `SESSION_HANDOFF.md` para o estado mais recente. As seções inferiores preservam histórico e podem conter instruções já superadas; não reexecute jobs, commit/push ou desligamento do Windows por constarem ali.
- A implementação e a validação estão pausadas por solicitação do usuário. Só retome quando ele pedir. Pedidos de documentação ou esclarecimento não revogam a pausa.

## Contratos e evidências

- Use `docs/designs/ts808_offline_design.md`, `docs/designs/ts808_substep_revision.md`, os contratos em `docs/` e `docs/validation_protocol.md` como referência. Não relaxe critérios nem altere o circuito para obter aprovação.
- Subpassos foram aprovados: saída em 192/384 kHz, integração interna em 768 kHz, respectivamente 4/2 passos. Ausência dos campos opcionais mantém o comportamento histórico.
- Preserve referências nativas originais, logs, hashes e proveniência. Use novos diretórios para novas tentativas; não sobrescreva evidências nem promova relatórios com identidade do validador desatualizada.
- Diferencie execução concluída, testes aprovados, qualificação numérica/WAV e aceitação do MVP. Não declare ABX realizado sem resultados humanos.

## Armazenamento e execução

- F: (`/mnt/f` no WSL) é o único volume autorizado com espaço para a validação completa. Grave novos artefatos volumosos em `/mnt/f/ts808-validation` e referências nativas em `/mnt/f/ts808-reference`, usando `validation/toolchain-pilot-f.json` quando aplicável.
- Antes de jobs longos, confira espaço, configuração de caminhos e processos existentes. Não inicie produtores duplicados. Preserve referências antigas em seus caminhos originais.
- Prefira scripts de execução e relatórios consolidados; leia logs detalhados quando necessário. Evite consultas repetidas, dumps extensos e carregar arquivos sem relação com a tarefa.
- Mantenha este arquivo curto e estável. Registre resultados, pendências e comandos de retomada em `SESSION_HANDOFF.md`, com o estado mais recente no topo.

## Verificação

- Use a toolchain local em `.tools` e o Python de `.venv`; veja `README.md` para configuração inicial.
- C++: `.tools/cmake-4.4.5-linux-x86_64/bin/cmake --build --preset offline-checks` e `.tools/cmake-4.4.5-linux-x86_64/bin/ctest --preset offline-checks`. Use `offline-release` para a variante normal.
- Python: `PYTHONPATH=validation .venv/bin/python -m pytest validation/tests -q`. Com `TS808_NATIVE_TESTS=1`, também executa testes nativos reais.
- Execute verificações proporcionais à alteração. Mudanças apenas em documentação não exigem simulações nem a matriz completa.
