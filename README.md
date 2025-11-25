Trabalho-PAA
=============

Resumo do projeto
-----------------
Este repositório contém implementações para dois problemas relacionados à
organização de peças:

1. Corte/empacotamento em placas (2D): distribuir peças retangulares em placas
   (placas têm largura/altura úteis). O avaliador de custo e os algoritmos como
   `forca_bruta`, `branch_and_bound` e `best_fit_shelf` lidam com posicionamento
   e cálculo de custo (neste contexto a área/área útil é relevante).

2. Partição ("Parte 2" / problema do navio): particionar um conjunto de
   peças em dois grupos (por peso) para minimizar a diferença entre as somas
   dos dois grupos. As implementações PT2 incluem força-bruta (brute_force),
   branch-and-bound e uma heurística gulosa. Aqui usamos `Peca.obter_peso()`
   (se o arquivo de entrada fornecer um peso explícito, ele será usado; caso
   contrário usamos área como fallback).

Distinção importante
--------------------
- Corte/empacotamento em placas: usa dimensões (altura/largura) e simula
  posicionamento em placas; o avaliador pode lançar erros do tipo
  "Peça HxW maior que área útil da placa" se uma peça não couber.
- Partição (PT2): usa apenas pesos e NÃO realiza simulação de empacotamento
  em placas. As soluções PT2 calculam apenas os dois grupos e suas somas.

Como a interface trata PT2
--------------------------
Para evitar comportamentos confusos, a interface (`interface/app.py`) possui o botão "Modo", onde é
possível selecionar qual parte do projeto será executada. Troque de modo no canto superior esquerdo.

Formato de entrada suportado
----------------------------
Cada linha do arquivo de peças deve ter:
- 2 valores: altura largura (ex.: "10 20") — peso será calculado como (altura*largura)/1000

Execução
--------
Para abrir a interface GUI (assumindo Python 3 disponível):

```powershell
python main.py      # dentro da pasta raíz 
```

Selecione o arquivo de peças (dentro da pasta dados já existe alguns), escolha o algoritmo e clique em
"Executar". Troque de modo no canto superior esquerdo.

