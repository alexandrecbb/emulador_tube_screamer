# Leis do modelo reduzido

Identidade: `ts808-cerutti-reduced-v1`. Os valores numéricos preparados
constam em [component_map.json](component_map.json), grupo `device_parameters`.
Aplicam-se igualmente aos dois canais e aos dois buffers. As leis seguem os
[contratos aprovados](../../docs/designs/ts808_model_contract.md).

Temperatura fixa T=298.15 K; kB=1.380649e-23 J/K, q=1.602176634e-19 C,
VT=kB*T/q. As constantes publicadas a 300.15 K foram preparadas conforme
T20; não se aplica uma segunda correção de temperatura. As omissões são
parte da identidade do modelo.

Correntes são positivas entrando no dispositivo. Para resistor orientado
a→b, i=(va-vb)/R. Para capacitor externo, i=C*d(va-vb)/dt; em DC, i=0.
A implementação C++ usará integração trapezoidal e históricos transacionais.
Não há ESR, fuga, tolerância ou dependência da capacitância com tensão.

Para o diodo, v=va-vk:

```text
i = Is*expm1(v/(n*VT))
di/dv = Is*exp(v/(n*VT))/(n*VT)
```

Para NPN, VBE=vb-ve e VBC=vb-vc:

```text
alphaF = BF/(BF+1); alphaR = BR/(BR+1)
F = (Is/alphaF)*expm1(VBE/(NF*VT))
R = (Is/alphaR)*expm1(VBC/(NR*VT))
Ic = alphaF*F-R
Ib = (1-alphaF)*F+(1-alphaR)*R
Ie = -F+alphaR*R
```

Logo Ic+Ib+Ie=0. Não há resistências internas, Early, alta injeção,
recombinação adicional, ruptura reversa nem cargas de junção/difusão.
As correntes LTspice são fontes comportamentais C→E e B→E.

Para cada op-amp, Vm=(9+0)/2 é apenas uma origem interna, sem conexão
ideal a `vref`. H=4.5-37/51, W=0.25 e L=H-W. Cada canal tem seu estado z:

```text
S(z) = -L-W*tanh((-z-L)/W), z < -L
S(z) = z,                 -L <= z <= L
S(z) = L+W*tanh((z-L)/W),  z > L
e = vplus-vminus+Vos
omega = 2*pi*GBW/A0
drive = omega*(A0*e-z)-(z-S(z))/tau_r
dz/dt = SR*tanh(drive/SR)
iout = (vout-(Vm+S(z)))/Ro
iplus = (vplus-vminus)/Rid+Ibias_plus
iminus = (vminus-vplus)/Rid+Ibias_minus
```

S é exatamente identidade no centro; recuperação z-S é exatamente zero.
Nas caudas, S'=4*exp(-2s)/(1+exp(-2s))² com s=(abs(z)-L)/W.
As junções são C2. Não há tanh global de amplitude; a tanh da derivada
do estado limita slew e permanece ativa conforme a equação acima.
Correntes de bias e fonte de saída retornam ao trilho negativo (`gnd`).
Não há lei adicional de corrente de alimentação, limite de corrente ou
ruptura de modo comum. O estado usa capacitor unitário na realização nativa. Para evitar o aviso
estrutural de nó flutuante do LTspice, a realização usa um resistor de 1 GOhm
entre z e o trilho negativo e uma fonte com corrente f+1e-9*z: as parcelas
1e-9*z se cancelam exatamente na equação constitutiva. Não há shunt físico
adicional. A corrente líquida continua f. A identidade nativa usa
`xclip:z` e `xtone:z`, conforme o RAW produzido pelo LTspice 26.1.1.

Cada segmento de controle satisfaz va-vb-R*i=0, inclusive em R=0.
O equivalente estático de `J_wet` é finito; `J_dry` não tem parasitas.
Não se permite limitar exponenciais para aceitar uma lei diferente;
avaliação não finita precisa produzir falha explícita na implementação C++.

As leis nativas ainda precisam ser verificadas com o produtor LTspice
selecionado, contra oráculos matemáticos independentes. Arquivos existentes
não constituem evidência de convergência ou equivalência.
