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
Para evitar comportamentos confusos, a interface (`interface/app.py`) chama as
funções de partição diretamente quando você seleciona uma opção "PT2" (por
exemplo "Força Bruta PT2", "Branch and Bound PT2", "Heurística PT2").
Dessa forma o avaliador de placas **não** é executado para as opções PT2 e
mensagens relacionadas a placas não aparecem durante a resolução do problema
de partição.

Formato de entrada suportado
----------------------------
Cada linha do arquivo de peças pode ter:
- 1 valor: peso (ex.: "12.5")
- 2 valores: altura largura (ex.: "10 20") — peso será calculado como área
- 3 valores: altura largura peso (ex.: "10 20 12.5")

Execução
--------
Para abrir a interface GUI (assumindo Python 3 disponível):

```powershell
python main.py
```

Selecione o arquivo de peças, escolha o algoritmo no combo e clique em
"Executar". Para comparar Força Bruta vs Branch-and-Bound parte 2, use o
botão "Comparar BF vs B&B PT2".

Notas finais
------------
- PT2 é focado no problema de partição (navio). Se você quiser avaliar custo do
  empacotamento 2D para uma ordem específica, use os algoritmos de corte/placa
  e o avaliador (`custo_total_para_ordem`).
- Sugestões de melhorias: adicionarmos logs configuráveis (módulo `logging`),
  limites/avisos para execução de força-bruta em instâncias grandes, e
  relatórios gráficos para os benchmarks PT2.
