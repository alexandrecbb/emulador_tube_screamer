# Revisão de estabilização DC — evidência parcial

Foram registrados 25 casos explicitamente revisados para 2 s de aquecimento
e uma janela final de 0,5 s. A matriz original permanece reprovada.
Circuito, estímulos, equações e critérios não foram alterados.

Dois casos representativos foram executados nas duas saídas, com integração
interna de 768 kHz. Os quatro diagnósticos C++ passaram em fundamental, DC
e THD. Valores aproximados de DC, iguais no arredondamento nas duas taxas:

| Caso | Janela original | Janela revisada | Limite |
| --- | ---: | ---: | ---: |
| Tone=0, 5 kHz, 100 mV | 182,46 µV | 0,308 µV | 10 µV |
| High, 82 Hz, 500 mV | 220,81 µV | 0,348 µV | 10 µV |

O decaimento é compatível com o transiente de polarização da rede de Vref,
cuja constante RC nominal é 0,235 s. Esse diagnóstico não substitui novas
referências nativas independentes nem os gates de WAV dos casos revisados.

A requalificação dos 25 casos requer aproximadamente 232,55 GiB livres em F:,
incluindo o crescimento medido dos RAWs e margem. Restaram cerca de 29 GiB;
o gate bloqueou a etapa nativa antes de iniciar produtores. Nenhuma evidência
original foi apagada ou movida. Uma tentativa de compressão NTFS em um RAW
preservou seu SHA256, mas não liberou espaço relevante; não houve lote.

Testes: 66 aprovados, 28 subtestes aprovados e 1 teste nativo opcional pulado.
Não houve alteração no executável ou no hash do validador de métricas.
Os JSONs e logs pequenos são cópias dos originais; `provenance.json` registra
os caminhos e hashes. Payloads e referências permanecem em F:.

Estado: diagnósticos C++ concluídos, requalificação nativa/WAV bloqueada por
espaço, MVP não aceito. ABX humano anterior preservado separadamente.
Execução e critérios: [revisão de duração](../../../docs/designs/ts808_settling_revision.md).
