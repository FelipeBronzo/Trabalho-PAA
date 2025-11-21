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
            values=["Força Bruta", "Branch and Bound", "Best-Fit Shelf"],  # adicionado aqui
            width=15
        ).grid(row=0, column=2)

        tk.Button(
            frame_input,
            text="Executar",
            command=self.executar
        ).grid(row=0, column=3, padx=10)

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
        elif algoritmo == "Best-Fit Shelf":
            from logica.algoritmos.best_fit_shelf import melhor_solucao_best_fit
            custo, num_placas, layout = melhor_solucao_best_fit(self.pecas)
        else:
            solver = BranchAndBound()
            custo, num_placas, layout, permutacoes = solver.resolver(self.pecas)

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
        elif algoritmo == "Best-Fit Shelf":
            self.info_var.set(
                f"Placas usadas: {num_placas}  |  "
                f"Custo: R$ {custo:.2f}  |  "
                f"Tempo: {tempo:.2f}s"
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
