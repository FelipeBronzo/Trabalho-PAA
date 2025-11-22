# interface/app.py

import tkinter as tk
from tkinter import filedialog, ttk, messagebox

from logica.leitor_arquivo import ler_pecas
from logica.algoritmos.forca_bruta import melhor_solucao_forca_bruta
from logica.algoritmos.branch_and_bound import BranchAndBound
from .desenhador import desenhar_layout


class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Otimizador de Corte - PAA")
        self.geometry("1000x600")

        self.pecas = None
        self.layout = None

        self._construir_interface()


    # ---------------------------------------------------------
    def _construir_interface(self):

        # === TOPO: Inputs ===
        frame_input = tk.Frame(self, pady=10)
        frame_input.pack()

        tk.Button(
            frame_input,
            text="Escolher arquivo de peças",
            command=self.carregar_arquivo
        ).grid(row=0, column=0, padx=5)

        tk.Label(frame_input, text="Algoritmo: ").grid(row=0, column=1)

        self.algoritmo_var = tk.StringVar(value="Branch and Bound")
        ttk.Combobox(
            frame_input,
            textvariable=self.algoritmo_var,
            values=["Força Bruta", "Força Bruta PT2", "Heurística PT2", "Branch and Bound", "Branch and Bound PT2", "Best-Fit Shelf"],  # adicionado heurística e PT2
            width=22
        ).grid(row=0, column=2)

        # Nota: as opções "... PT2" resolvem o problema de PARTIÇÃO (parte 2):
        # particionamento por peso entre dois porões. Essas opções NÃO executam a
        # simulação/avaliação de empacotamento em placas (2D) — isso evita
        # mensagens/erros do tipo "Peça AxB maior que área útil da placa" que
        # pertencem ao problema de corte em placas. Em vez disso a interface
        # chama diretamente as funções de partição e mostra grupos/pesos.

        tk.Button(
            frame_input,
            text="Executar",
            command=self.executar
        ).grid(row=0, column=3, padx=10)

        tk.Button(
            frame_input,
            text="Comparar BF vs B&B PT2",
            command=self.comparar_pt2
        ).grid(row=0, column=4, padx=5)

        # === MÉTRICAS FIXAS NA TELA ===
        self.info_var = tk.StringVar(value="Carregue um arquivo para começar.")
        tk.Label(
            self,
            textvariable=self.info_var,
            font=("Arial", 12, "bold")
        ).pack(pady=5)

        # === ÁREA ROLÁVEL PARA AS PLACAS ===
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.canvas_principal = tk.Canvas(container, bg="#f0f0f0")
        self.canvas_principal.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=self.canvas_principal.yview
        )
        scrollbar.pack(side="right", fill="y")

        self.canvas_principal.configure(yscrollcommand=scrollbar.set)

        # Frame interno
        self.frame_placas = tk.Frame(self.canvas_principal, bg="#f0f0f0")
        self.canvas_principal.create_window(
            (0, 0),
            window=self.frame_placas,
            anchor="nw"
        )

        # Atualizar scroll
        self.frame_placas.bind(
            "<Configure>",
            lambda e: self.canvas_principal.configure(
                scrollregion=self.canvas_principal.bbox("all")
            )
        )


    # ---------------------------------------------------------
    def carregar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo de peças",
            filetypes=[("Texto", "*.txt")]
        )

        if not caminho:
            return

        self.pecas = ler_pecas(caminho)
        self.info_var.set(f"{len(self.pecas)} peças carregadas. Execute para calcular.")


    def comparar_pt2(self):
        """
        Botão: compara Força Bruta vs Branch-and-Bound (parte 2) usando os pesos
        das peças (peso explícito ou área como fallback). Mostra tempos e métricas
        na `info_var`.
        """
        if not self.pecas:
            messagebox.showwarning("Erro", "Carregue um arquivo primeiro!")
            return

        pesos = [p.obter_peso() for p in self.pecas]
        from logica.algoritmos.branch_and_boundpt2 import comparar_com_bruteforce

        res = comparar_com_bruteforce(pesos)

        bf = res["bruteforce"]
        bnb = res["branch_and_bound"]
        consistente = res.get("consistente", False)

        def grupo_str(grupo_indices):
            return ", ".join(f"{i}(p={pesos[i]})" for i in grupo_indices)
        def peso_total(grupo_indices):
            return sum(pesos[i] for i in grupo_indices)

        bf_g1 = grupo_str(bf["grupo1"])
        bf_g2 = grupo_str(bf["grupo2"])
        bf_p1 = peso_total(bf["grupo1"])
        bf_p2 = peso_total(bf["grupo2"])

        bnb_g1 = grupo_str(bnb["grupo1"])
        bnb_g2 = grupo_str(bnb["grupo2"])
        bnb_p1 = peso_total(bnb["grupo1"])
        bnb_p2 = peso_total(bnb["grupo2"])

        msg = (
            f"BF: dif={bf['melhor_dif']} particoes={bf.get('particoes_avaliadas', 'N/A')} t={bf['tempo']:.4f}s\n"
            f"  Grupo1: [{bf_g1}] | Peso total: {bf_p1}\n"
            f"  Grupo2: [{bf_g2}] | Peso total: {bf_p2}\n"
            f"B&B: dif={bnb['melhor_dif']} nos={bnb['nos_explorados']} t={bnb['tempo']:.4f}s\n"
            f"  Grupo1: [{bnb_g1}] | Peso total: {bnb_p1}\n"
            f"  Grupo2: [{bnb_g2}] | Peso total: {bnb_p2}\n"
            f"Consistente: {consistente}"
        )
        self.info_var.set(msg)


    # ---------------------------------------------------------
    def executar(self):
        if not self.pecas:
            messagebox.showwarning("Erro", "Carregue um arquivo primeiro!")
            return

        algoritmo = self.algoritmo_var.get()

        # executa algoritmo
        import time
        inicio = time.perf_counter()
        if algoritmo == "Força Bruta":
            custo, num_placas, layout, permutacoes = melhor_solucao_forca_bruta(self.pecas)
        elif algoritmo == "Força Bruta PT2":
            # executar apenas o partionador (força bruta parte 2) — não chamar o avaliador de placas
            pesos = [p.obter_peso() for p in self.pecas]
            from logica.algoritmos.forca_brutapt2 import brute_force_partition
            dif, g1, g2, particoes = brute_force_partition(pesos)
            # não há custo/layout relacionado a placas para o problema da parte 2
            custo = 0.0
            num_placas = 0
            layout = None
        elif algoritmo == "Heurística PT2":
            # aplica heurística de partição: não chamar o avaliador de placas
            pesos = [p.obter_peso() for p in self.pecas]
            from logica.algoritmos.branch_and_boundpt2 import heuristic_greedy_partition
            dif, g1, g2, heur_time = heuristic_greedy_partition(pesos)

            custo = 0.0
            num_placas = 0
            layout = None

            # armazenar métricas da heurística para exibição
            self._heur_pt2_diff = dif
            self._heur_pt2_time = heur_time
        elif algoritmo == "Branch and Bound PT2":
            # aplica B&B de partição: não chamar o avaliador de placas
            pesos = [p.obter_peso() for p in self.pecas]
            from logica.algoritmos.branch_and_boundpt2 import branch_and_bound_partition
            dif, g1, g2, nos = branch_and_bound_partition(pesos)

            custo = 0.0
            num_placas = 0
            layout = None

            # armazenar métricas para exibição abaixo
            particoes = None
            permutacoes = None
            # manter 'nos' para mostrar
            self._branch_pt2_nodes = nos
            self._branch_pt2_diff = dif
        elif algoritmo == "Best-Fit Shelf":
            from logica.algoritmos.best_fit_shelf import melhor_solucao_best_fit
            custo, num_placas, layout = melhor_solucao_best_fit(self.pecas)
        else:
            solver = BranchAndBound()
            custo, num_placas, layout, permutacoes = solver.resolver(self.pecas)

        # calcula tempo total da execução
        fim = time.perf_counter()
        tempo = fim - inicio

        self.layout = layout

        # Atualiza métricas na tela
        if algoritmo == "Força Bruta":
            self.info_var.set(
                f"Placas usadas: {num_placas}  |  "
                f"Custo: R$ {custo:.2f}  |  "
                f"Tempo: {tempo:.2f}s |  "
                f"Permutações Analisadas: {permutacoes}"
            )
        elif algoritmo == "Força Bruta PT2":
            # particoes contém o número de partições avaliadas retornado pelo adaptador
            # mostrar divisão dos grupos e pesos
            from logica.algoritmos.forca_brutapt2 import brute_force_partition
            pesos = [p.obter_peso() for p in self.pecas]
            _, g1, g2, _ = brute_force_partition(pesos)
            def grupo_str(grupo_indices):
                return ", ".join(f"{i}(p={pesos[i]})" for i in grupo_indices)
            def peso_total(grupo_indices):
                return sum(pesos[i] for i in grupo_indices)
            g1_str = grupo_str(g1)
            g2_str = grupo_str(g2)
            p1 = peso_total(g1)
            p2 = peso_total(g2)
            self.info_var.set(
                f"Placas usadas: {num_placas}  |  "
                f"Custo: R$ {custo:.2f}  |  "
                f"Tempo: {tempo:.2f}s |  "
                f"Partições Analisadas: {particoes}\n"
                f"Grupo1: [{g1_str}] | Peso total: {p1}\n"
                f"Grupo2: [{g2_str}] | Peso total: {p2}"
            )
        elif algoritmo == "Heurística PT2":
            dif = getattr(self, "_heur_pt2_diff", None)
            heur_time = getattr(self, "_heur_pt2_time", None)
            # mostrar divisão dos grupos e pesos
            pesos = [p.obter_peso() for p in self.pecas]
            from logica.algoritmos.branch_and_boundpt2 import heuristic_greedy_partition
            _, g1, g2, _ = heuristic_greedy_partition(pesos)
            def grupo_str(grupo_indices):
                return ", ".join(f"{i}(p={pesos[i]})" for i in grupo_indices)
            def peso_total(grupo_indices):
                return sum(pesos[i] for i in grupo_indices)
            g1_str = grupo_str(g1)
            g2_str = grupo_str(g2)
            p1 = peso_total(g1)
            p2 = peso_total(g2)
            self.info_var.set(
                f"Placas usadas: {num_placas}  |  "
                f"Custo: R$ {custo:.2f}  |  "
                f"Tempo: {tempo:.2f}s |  "
                f"Diferença PT2 (heur): {dif} | Heur time: {heur_time:.4f}s\n"
                f"Grupo1: [{g1_str}] | Peso total: {p1}\n"
                f"Grupo2: [{g2_str}] | Peso total: {p2}"
            )
        elif algoritmo == "Best-Fit Shelf":
            self.info_var.set(
                f"Placas usadas: {num_placas}  |  "
                f"Custo: R$ {custo:.2f}  |  "
                f"Tempo: {tempo:.2f}s"
            )
        elif algoritmo == "Branch and Bound PT2":
            # exibe métricas específicas do B&B PT2
            nos = getattr(self, "_branch_pt2_nodes", None)
            dif = getattr(self, "_branch_pt2_diff", None)
            # mostrar divisão dos grupos e pesos
            pesos = [p.obter_peso() for p in self.pecas]
            from logica.algoritmos.branch_and_boundpt2 import branch_and_bound_partition
            _, g1, g2, _ = branch_and_bound_partition(pesos)
            def grupo_str(grupo_indices):
                return ", ".join(f"{i}(p={pesos[i]})" for i in grupo_indices)
            def peso_total(grupo_indices):
                return sum(pesos[i] for i in grupo_indices)
            g1_str = grupo_str(g1)
            g2_str = grupo_str(g2)
            p1 = peso_total(g1)
            p2 = peso_total(g2)
            self.info_var.set(
                f"Placas usadas: {num_placas}  |  "
                f"Custo: R$ {custo:.2f}  |  "
                f"Tempo: {tempo:.2f}s |  "
                f"Diferença PT2: {dif} | Nós explorados: {nos}\n"
                f"Grupo1: [{g1_str}] | Peso total: {p1}\n"
                f"Grupo2: [{g2_str}] | Peso total: {p2}"
            )
        else:
            self.info_var.set(
                f"Placas usadas: {num_placas}  |  "
                f"Custo: R$ {custo:.2f}  |  "
                f"Tempo: {tempo:.2f}s |  "
                f"Nós explorados: {permutacoes}"
            )

        # limpar interface
        for w in self.frame_placas.winfo_children():
            w.destroy()

        # desenhar placas
        desenhar_layout(self.frame_placas, layout)
