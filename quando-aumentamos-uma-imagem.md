# Quando aumentamos uma imagem, de onde vêm os novos pixels?

<!-- Post 4 | Fonte do conteúdo de post-4/index.html | URL: /computacaoVisual/post-4/ -->

No [último post](post-3/), fui atrás de entender como uma cena do mundo real se transforma em uma matriz de pixels. Mas isso me deixou com outra dúvida: se esses pixels já estão definidos, o que acontece quando aumentamos uma imagem? Se uma imagem de 500 × 500 pixels passa para 1000 × 1000, de onde vêm todos os pixels que não existiam antes?

Essa pergunta me fez olhar com mais atenção para algo bem comum: uma foto pequena que fica cheia de quadradinhos quando ampliada. Em outros casos, ela fica mais suave, mas meio borrada. Fui entender o que muda entre esses resultados, e a diferença está em como o computador escolhe os valores dos novos pixels.

## De 9 pixels para 36

Uma imagem digital pode ser representada como uma matriz de pixels: uma organização em linhas e colunas, em que cada posição guarda valores que representam uma cor. Em uma imagem em tons de cinza de 8 bits, por exemplo, podemos usar um número entre 0, para preto, e 255, para branco. Nas imagens coloridas, é comum ter valores separados para vermelho, verde e azul.

Agora imagine uma imagem bem pequena, de 3 × 3 pixels. São apenas 9 posições. Se dobrarmos sua largura e sua altura, ela passa a ter 6 × 6 pixels, ou seja, 36 posições. Dobrar as duas dimensões quadruplica a quantidade de pixels.

O arquivo original não traz 36 amostras de cor para preencher essa nova matriz. O computador precisa determinar qual valor colocar em cada posição da imagem ampliada.

É aí que entra a **interpolação**: uma forma de estimar valores em posições para as quais não temos uma amostra original. No redimensionamento, podemos imaginar a nova grade sobre a imagem antiga. Para cada posição de saída, o programa encontra o local correspondente na imagem original e usa uma regra para escolher seu valor.

## A solução mais direta: copiar o vizinho

O método do **vizinho mais próximo**, também chamado de *Nearest Neighbor*, faz uma escolha simples: usa o valor do pixel original mais próximo da posição correspondente.

Para enxergar isso, vamos usar uma matriz ainda menor, de 2 × 2, com quatro intensidades de cinza. Ao dobrar suas dimensões com esse método, temos:

```text
Original: 2 × 2              Ampliada: 4 × 4

 10    50                    10    10    50    50
100   200                    10    10    50    50
                            100   100   200   200
                            100   100   200   200
```

Cada valor passa a ocupar um bloco de 2 × 2 pixels. Não surgem tons intermediários: o programa apenas copia os valores existentes para mais posições.

Isso explica a aparência blocada. Vários pixels de saída repetem a mesma cor, e a passagem para a cor seguinte continua abrupta. Quando ampliamos bastante, esses grupos ficam visíveis como quadrados, e contornos diagonais parecem escadinhas.

Como a escolha exige pouco cálculo, o método é simples e rápido. E os blocos nem sempre são um problema: em pixel art, uma ampliação por um fator inteiro pode preservar justamente os quadradinhos e a paleta que fazem parte do desenho.

## E se, em vez de copiar, a gente misturar?

Antes de pensar na imagem inteira, ajuda imaginar dois valores em uma linha: 100 e 200. Se queremos estimar o valor exatamente no meio, faz sentido dar a mesma importância aos dois. O resultado é 150.

Se a posição estiver mais perto de 100, o resultado deve ficar mais perto de 100 também. A um quarto do caminho até 200, por exemplo, chegamos a 125. Essa é a ideia da interpolação linear.

A conta pode ser escrita assim:

```text
V = (1 − α)V₀ + αV₁
```

Aqui, `V₀` e `V₁` são os valores das duas pontas. O símbolo `α` indica quanto do caminho percorremos da primeira até a segunda: 0 é o início, 1 é o fim e 0,5 é o meio. Conforme avançamos, a primeira ponta perde influência e a segunda ganha.

No meio do nosso exemplo, fica:

```text
V = (1 − 0,5) × 100 + 0,5 × 200
V = 150
```

## Só que uma imagem tem duas direções

Uma linha tem apenas uma direção para percorrer. Uma imagem tem largura e altura. Quando a posição que queremos estimar fica entre linhas e colunas da grade original, precisamos considerar as duas direções.

A **interpolação bilinear** faz isso usando os quatro pixels que cercam essa posição. Podemos imaginar uma interpolação linear na horizontal e, depois, outra na vertical.

Neste exemplo, o ponto `P` está exatamente no centro dos quatro pixels:

```text
 10 ●───────────────────● 50
    │                   │
    │         P         │
    │                   │
100 ●───────────────────● 200
```

Primeiro, encontramos o valor no meio da linha de cima: entre 10 e 50, temos 30. Depois, fazemos o mesmo na linha de baixo: entre 100 e 200, temos 150. Por fim, estimamos o meio do caminho vertical entre esses dois resultados:

```text
Linha de cima:   10 ────── 30 ────── 50
                           │
Centro:                    90
                           │
Linha de baixo: 100 ───── 150 ───── 200
```

O valor estimado para `P` é 90. Como ele está no centro, os quatro pixels têm o mesmo peso. Se deslocarmos o ponto para a esquerda, a coluna da esquerda ganha influência; se o movermos para cima, a linha superior ganha influência. É nesse sentido que os vizinhos mais próximos pesam mais: os pesos dependem da posição em cada direção.

Em uma imagem colorida, essa combinação pode ser feita separadamente para cada canal de cor. Na prática, os valores calculados também precisam ser representados no formato usado pela imagem; se ele só aceita inteiros, pode ser necessário arredondar.

Como a bilinear produz valores intermediários, as transições tendem a ficar mais suaves. Isso reduz o aspecto de blocos, mas também pode deixar bordas menos definidas. Suavizar não significa necessariamente deixar mais nítido.

## Dois jeitos de preencher a imagem

Depois de acompanhar os exemplos, a comparação fica mais concreta:

| Vizinho mais próximo | Bilinear |
| --- | --- |
| Copia o valor de um vizinho. | Combina os valores de quatro vizinhos. |
| É mais simples e, em geral, mais rápido. | Exige mais cálculos por pixel. |
| Usa valores já presentes na imagem original. | Pode produzir valores intermediários. |
| Pode deixar blocos e escadinhas visíveis. | Tende a suavizar transições, podendo borrar bordas. |

Os dois métodos estão disponíveis em ferramentas de processamento de imagens. No OpenCV, por exemplo, aparecem como `INTER_NEAREST` e `INTER_LINEAR` — apesar do nome abreviado, o segundo corresponde à interpolação bilinear em imagens. A página de [redimensionamento do OpenCV](https://opencv.org/resizing-and-rescaling-images-with-opencv/) mostra como escolher entre eles.

## Mais pixels não garantem mais informação

O que mais me chamou a atenção é que aumentar a resolução, no sentido de aumentar a quantidade de pixels, não significa recuperar um detalhe que nunca foi capturado.

Se uma foto pequena mostra uma placa cujas letras já não podem ser distinguidas, a interpolação pode suavizar a ampliação. Mas misturar ou repetir os pixels disponíveis não revela, por si só, o que estava escrito. Ter mais posições na matriz não equivale a ter novas observações da cena.

Isso também ajuda a entender a diferença para a super-resolução baseada em IA. Enquanto os métodos tradicionais que vimos aplicam regras fixas aos pixels existentes, modelos de super-resolução podem usar padrões aprendidos durante o treinamento para estimar estruturas e texturas. O trabalho que apresentou o [SRGAN](https://openaccess.thecvf.com/content_cvpr_2017/html/Ledig_Photo-Realistic_Single_Image_CVPR_2017_paper.html), por exemplo, explora esse caminho para produzir ampliações visualmente mais realistas.

Só que uma textura convincente não é garantia de fidelidade. Uma mesma imagem pequena pode ser compatível com diferentes versões em alta resolução, uma ambiguidade discutida em [pesquisa sobre os limites da super-resolução](https://openaccess.thecvf.com/content/CVPR2021/html/Jo_Tackling_the_Ill-Posedness_of_Super-Resolution_Through_Adaptive_Target_Generation_CVPR_2021_paper.html). A IA pode estimar um detalhe plausível sem que ele corresponda ao que existia na cena.

Volto, então, à pergunta que começou essa curiosidade: de onde vêm os novos pixels? Eles não estavam escondidos dentro da imagem. Quando aumentamos suas dimensões, algum método precisa estimar quais valores vão ocupar as novas posições. A diferença entre ver quadradinhos, transições suaves ou detalhes estimados está na maneira como essa escolha é feita.
