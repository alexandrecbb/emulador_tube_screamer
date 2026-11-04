# Revisão proposta: equilibração algébrica de linhas

Estado: aprovada explicitamente pelo usuário em 2026-11-01 e aplicada ao solver de produção. A aprovação inclui a atualização de T22 e a bateria dos 27 controles. Os valores abaixo preservam o experimento anterior à aprovação.
Medição em 2026-11-01 com GCC 15.3.0, Eigen 5.0.1, binary64 e os flags T23.

O bloco interior de clipping 6×6, no palpite DC aprovado, Drive=0.5,
apresenta `rcond=3.65023e-13` após as escalas físicas de T22.
O limite aprovado é `1e-12`: o caso encerra como
`ill_conditioned_internal`, bloco 1. O efeito aparece antes de convergir;
não é um resultado de comparação com LTspice.

A linha do estado tem coeficientes de ordem 100000 enquanto linhas KCL
têm coeficientes de ordem 0.1. Proposta: após as escalas físicas de
1 V/1 mA, multiplicar cada linha do sistema completo por
`1/max(abs(coeficientes_da_linha))`, calculado novamente para cada Jacobiana.
Linha nula permanece nula e falha no teste de posto. Não mudar incógnitas,
modelo físico, partição, integrador, tolerâncias ou limite de rcond.
Aplicar a mesma transformação ao lado direito; avaliar rank/rcond das
matrizes equilibradas, e verificar erro reverso também no sistema original
nondimensionalizado, como em T22. O solve completo de diagnóstico recebe
a mesma transformação. Registrar a política em metadados de execução.

Experimento algébrico isolado nesse bloco: equilibração só de linhas
resultou em `rcond=2.17395e-08`. Equilibração adicional de colunas resultou
em `0.000722245`, mas não é proposta: a transformação de linhas é suficiente
nesse exemplo e mantém as escalas das incógnitas.

Essa medição isolada não qualifica os 27 controles, o DC, os transientes
ou a ausência de alocação. Após a aprovação, executar essas verificações
e registrar qualquer falha restante sem relaxar critérios automaticamente.

Alternativa: manter literalmente T22. Nesse caso, casos que violam seu
critério continuam reprovados e o MVP não pode ser declarado qualificado.
