# Revisão aprovada: subpassos explícitos no MVP offline

Status: aprovada explicitamente pelo usuário em 2026-11-04:
“aprovo incorporar esses subpassos à implementação”. Esta revisão passa a
integrar o contrato vigente e substitui as exigências incompatíveis de taxas
internas do design anterior. Os resultados históricos continuam preservados.

## Evidência e problema

A recuperação da sobrecarga falha com integração trapezoidal estrita em
192/384 kHz por 33/7 amostras. As referências nominal e refinada dão o mesmo
índice de recuperação em cada grade, e a quantidade que determina a diferença
é `output`. Apertar Newton não resolveu o erro.

O novo diagnóstico integra o mesmo circuito em 768 kHz, avalia a fonte
analítica em cada passo e grava estados nas grades de 192/384 kHz. Não usa
interpolação de estados, ajuste de ganho, deslocamento de tempo ou filtragem.
As saídas são bit a bit iguais às respectivas linhas do diagnóstico original
de 768 kHz. Os critérios locais de RMS/pico passam nas duas grades de saída;
o erro de recuperação é zero amostras em ambas.

As diferenças RMS entre grades consecutivas caem de 20,751 para 4,912 uV,
compatíveis com a convergência temporal de segunda ordem. Isso é diagnóstico,
não demonstra que a implementação estrita nas taxas alvo passou.

Evidência: `validation/results/continuation-2026-11-04/overload-convergence.json`.
Receitas: `validation/scripts/diagnose_overload_convergence.py` e o alvo CMake
opt-in `ts808_substep_diagnostic`. O executável experimental não produz um
`run.json` consumível pela suíte de aceitação.

## Revisão aprovada

Permitir integração interna fixa em 768 kHz, preservando grades de saída
de 192/384 kHz, com respectivamente quatro/dois subpassos trapezoidais.
Registrar ambas as taxas e a contagem de subpassos em casos, execuções e
relatórios. Ausência do novo campo conserva a semântica histórica de um
passo por amostra. Não promover os relatórios anteriores nem substituir
identidades de execução existentes.

A fonte deve ser avaliada em todos os tempos internos. A saída é o estado
real no último subpasso, sem reconstrução. Cada subpasso usa o mesmo solver,
histórico trapezoidal e critérios de convergência. Falha em um subpasso
interrompe a execução e precisa identificar o tempo interno e a amostra
externa afetada; um estado externo incompleto não pode ser publicado.

A resposta discreta de pequeno sinal deve usar a taxa interna efetiva.
Os controles, equações físicas, parâmetros, partição Schur, tolerâncias
e critérios numéricos permanecem os mesmos. Não introduzir fallback
adaptativo ou outro integrador. A taxa de saída não pode ser apresentada
como taxa de integração do circuito.

Atualizar contratos, schemas, produtor C++,
comparador e testes de identidade/falha. Reexecutar os três pilotos nas
duas grades, incluindo WAV, e somente então liberar a matriz completa.
O experimento de sobrecarga ainda não qualifica senoides, AC, WAV ou ABX
com essa nova configuração.

## Contrato de implementação

`execution.rate_Hz` continua sendo a grade de saída. Os campos opcionais
`execution.integration_rate_Hz` e `execution.substeps` devem aparecer juntos.
Pares permitidos: saída 192000/interna 768000/4, saída 384000/interna 768000/2,
ou um subpasso com taxas iguais em 192000/384000/768000. Ausência de ambos
preserva a execução histórica de um passo por amostra. Saída768000 continua
restrita a propósito `pilot`. Campos inconsistentes são configuração inválida.

O `Model` continua avançando exatamente um passo interno por `advance`.
O executável offline avalia a fonte analítica a cada índice inteiro interno
e grava uma linha somente após todos os subpassos da amostra. Seu `run_id`
inclui a contagem de subpassos para distinguir a nova variante. Casos,
execuções e relatórios conservam as duas taxas e a contagem. O finalizador
e o comparador rejeitam divergência de configuração entre caso e execução.

Em falha transiente, `failure.failed_sample_index` e `failed_time_s` identificam
a amostra externa incompleta. Os diagnósticos adicionais
`failed_internal_sample_index`, `failed_internal_time_s` e `failed_substep_index`
identificam o passo interno real (índices iniciados em 1). O trace termina na
última amostra externa completa. As falhas continuam explícitas, sem retry.

Em AC, a transformação bilinear usa a taxa interna; a amostragem da fonte
analítica em todos os passos não pressupõe retenção da entrada na grade externa.
A observação da chave continua na grade de saída identificada pelo trace.

O par de referência compartilhada mantém o limite explícito do contrato T18:
maxstep nominal 1/(384000*8), refinado à metade com tolerâncias mais apertadas.
A incerteza medida continua obrigatória para cada grade de saída, inclusive
os critérios locais. A aprovação dos subpassos não promove uma referência
que falhe nesse gate e não relaxa seus limites.

Esta proposta revisa explicitamente a interpretação de taxas do design
canônico (seções de solver, validação e marco 6). Mantém T3 trapezoidal;
não satisfaz retroativamente o requisito original de integração em 192/384 kHz.
