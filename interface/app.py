import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from logica.leitor_arquivo import ler_pecas
from logica.algoritmos.forca_bruta import melhor_solucao_forca_bruta
from logica.algoritmos.branch_and_bound import BranchAndBound
from interface.desenhador import desenhar_layout

class App(tk.Tk):
    # ===============================================================
    # CONJUNTOS DE ALGORITMOS POR MODO
    # ===============================================================
    ALGORITMOS_PARTE1 = [
        "Força Bruta",
        "Branch and Bound",
        "Best-Fit Shelf"
    ]
    
    ALGORITMOS_PARTE2 = [
        "Força Bruta PT2",
        "Heurística PT2",
        "Branch and Bound PT2"
    ]
    
    # ===============================================================
    def __init__(self):
        super().__init__()
        self.title("Otimizador de Corte - PAA")
        self.geometry("1100x650")
        
        self.pecas = None
        self.layout = None
        self.modo = "PARTE 1"  # modo inicial
        
        self._construir_interface()
        self._configurar_menu()
        self._atualizar_algoritmos()
    
    # ===============================================================
    # CONSTRUIR MENU SUPERIOR
    # ===============================================================
    def _configurar_menu(self):
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        
        menu_modo = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Modo", menu=menu_modo)
        
        menu_modo.add_command(
            label="Calcular cortes das peças (PARTE 1)",
            command=self._ativar_parte1
        )
        menu_modo.add_command(
            label="Distribuir peças no navio (PARTE 2)",
            command=self._ativar_parte2
        )
    
    # ===============================================================
    # TROCA DE MODO
    # ===============================================================
    def _ativar_parte1(self):
        self.modo = "PARTE 1"
        self._limpar_tela()
        self._atualizar_algoritmos()
        self.label_modo.config(text="🔧 MODO: PARTE 1 - Calcular Cortes", bg="#4CAF50")
        self.info_var.set("Carregue um arquivo de peças para começar.")
    
    def _ativar_parte2(self):
        self.modo = "PARTE 2"
        self._limpar_tela()
        self._atualizar_algoritmos()
        self.label_modo.config(text="🚢 MODO: PARTE 2 - Distribuir no Navio", bg="#2196F3")
        self.info_var.set("Carregue um arquivo de peças para distribuir nos porões.")
    
    def _limpar_tela(self):
        """Limpa todo o conteúdo da área de visualização"""
        for widget in self.frame_placas.winfo_children():
            widget.destroy()
    
    # ===============================================================
    # RECARREGAR ALGORITMOS NO COMBOBOX
    # ===============================================================
    def _atualizar_algoritmos(self):
        self.algoritmo_cb["values"] = (
            self.ALGORITMOS_PARTE1 if self.modo == "PARTE 1" 
            else self.ALGORITMOS_PARTE2
        )
        self.algoritmo_var.set(self.algoritmo_cb["values"][0])
    
    # ===============================================================
    def _construir_interface(self):
        # === INDICADOR DE MODO (TOPO) ===
        self.label_modo = tk.Label(
            self, 
            text="🔧 MODO: PARTE 1 - Calcular Cortes",
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            pady=10
        )
        self.label_modo.pack(fill="x")
        
        # === TOPO: Inputs ===
        frame_input = tk.Frame(self, pady=10)
        frame_input.pack(fill="x")
        
        tk.Button(
            frame_input,
            text="Escolher arquivo de peças",
            command=self.carregar_arquivo
        ).grid(row=0, column=0, padx=5)
        
        tk.Label(frame_input, text="Algoritmo: ").grid(row=0, column=1)
        
        self.algoritmo_var = tk.StringVar(value="")
        self.algoritmo_cb = ttk.Combobox(
            frame_input,
            textvariable=self.algoritmo_var,
            values=[],
            width=20,
            state="readonly"
        )
        self.algoritmo_cb.grid(row=0, column=2)
        
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
            font=("Arial", 11),
            justify="left"
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
        
        self.frame_placas = tk.Frame(self.canvas_principal, bg="#f0f0f0")
        self.canvas_principal.create_window(
            (0, 0),
            window=self.frame_placas,
            anchor="nw"
        )
        
        self.frame_placas.bind(
            "<Configure>",
            lambda e: self.canvas_principal.configure(
                scrollregion=self.canvas_principal.bbox("all")
            )
        )
    
    # ===============================================================
    def carregar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo de peças",
            filetypes=[("Texto", "*.txt")]
        )
        if not caminho:
            return
        
        self.pecas = ler_pecas(caminho)
        self.info_var.set(f"{len(self.pecas)} peças carregadas. Selecione algoritmo e execute.")
    
    # ===============================================================
    def executar(self):
        if not self.pecas:
            messagebox.showwarning("Erro", "Carregue um arquivo primeiro!")
            return
        
        # Limpar tela antes de executar
        self._limpar_tela()
        
        algoritmo = self.algoritmo_var.get()
        
        import time
        inicio = time.perf_counter()
        
        # ==========================================================
        # PARTE 1 — Cortes das Peças
        # ==========================================================
        if self.modo == "PARTE 1":
            if algoritmo == "Força Bruta":
                custo, num_placas, layout, permutacoes = melhor_solucao_forca_bruta(self.pecas)
                nos_explorados = None
                
            elif algoritmo == "Best-Fit Shelf":
                from logica.algoritmos.best_fit_shelf import melhor_solucao_best_fit
                custo, num_placas, layout = melhor_solucao_best_fit(self.pecas)
                permutacoes = None
                nos_explorados = None
                
            else:  # Branch and Bound
                solver = BranchAndBound()
                custo, num_placas, layout, permutacoes = solver.resolver(self.pecas)
                nos_explorados = permutacoes  # Assumindo que retorna nós explorados
            
            fim = time.perf_counter()
            tempo = fim - inicio
            
            if layout:
                desenhar_layout(self.frame_placas, layout)
                
                # Mostrar informações apropriadas para cada algoritmo
                info_texto = (
                    f"Placas usadas: {num_placas} | "
                    f"Custo: R$ {custo:.2f} | "
                    f"Tempo: {tempo:.4f}s"
                )
                
                if algoritmo == "Branch and Bound" and nos_explorados:
                    info_texto += f" | Nós explorados: {nos_explorados}"
                elif permutacoes and algoritmo == "Força Bruta":
                    info_texto += f" | Permutações: {permutacoes}"
                
                self.info_var.set(info_texto)
        
        # ==========================================================
        # PARTE 2 — Particionamento do Navio
        # ==========================================================
        else:
            pesos = [p.obter_peso() for p in self.pecas]
            
            if algoritmo == "Força Bruta PT2":
                from logica.algoritmos.forca_brutapt2 import forca_bruta_particao
                dif, g1, g2, particoes = forca_bruta_particao(pesos)
                fim = time.perf_counter()
                tempo = fim - inicio
                self._desenhar_poroes(g1, g2, pesos, dif, tempo, particoes=particoes)
                
            elif algoritmo == "Heurística PT2":
                from logica.algoritmos.heuristica_pt2 import heuristica_gulosa_particao
                dif, g1, g2, t = heuristica_gulosa_particao(pesos)
                self._desenhar_poroes(g1, g2, pesos, dif, t)
                
            else:  # Branch and Bound PT2
                from logica.algoritmos.branch_and_boundpt2 import branch_and_bound_particao
                dif, g1, g2, nos = branch_and_bound_particao(pesos)
                fim = time.perf_counter()
                tempo = fim - inicio
                self._desenhar_poroes(g1, g2, pesos, dif, tempo, nos_explorados=nos)
    
    # ===============================================================
    # DESENHAR PORÕES - PARTE 2
    # ===============================================================
    def _desenhar_poroes(self, g1, g2, pesos, diferenca, tempo, particoes=None, nos_explorados=None):
        """Desenha visualização dos porões do navio"""
        
        # Calcular pesos totais
        peso_g1 = sum(pesos[i] for i in g1)
        peso_g2 = sum(pesos[i] for i in g2)
        
        # Atualizar info
        info_texto = f"⚖️ Diferença: {diferenca:.4f} kg | ⏱️ Tempo: {tempo:.4f}s"
        if particoes:
            info_texto += f" | 🔍 Partições avaliadas: {particoes}"
        if nos_explorados:
            info_texto += f" | 🌳 Nós explorados: {nos_explorados}"
        self.info_var.set(info_texto)
        
        # Frame principal
        frame_principal = tk.Frame(self.frame_placas, bg="#f0f0f0")
        frame_principal.pack(pady=20, padx=20, fill="both", expand=True)
        
        # ===== PORÃO 1 =====
        self._criar_porao(frame_principal, "PORÃO 1 (Proa)", g1, pesos, peso_g1, "#FF6B6B", 0)
        
        # ===== PORÃO 2 =====
        self._criar_porao(frame_principal, "PORÃO 2 (Popa)", g2, pesos, peso_g2, "#4ECDC4", 1)
    
    def _criar_porao(self, parent, titulo, indices, pesos, peso_total, cor, coluna):
        """Cria a visualização de um porão"""
        
        frame = tk.LabelFrame(
            parent,
            text=titulo,
            font=("Arial", 14, "bold"),
            bg="white",
            fg=cor,
            bd=3,
            relief="groove",
            padx=15,
            pady=15
        )
        frame.grid(row=0, column=coluna, padx=20, pady=10, sticky="nsew")
        parent.grid_columnconfigure(coluna, weight=1)
        
        # Peso total
        tk.Label(
            frame,
            text=f"⚖️ Peso Total: {peso_total} kg",
            font=("Arial", 13, "bold"),
            bg="white",
            fg=cor
        ).pack(pady=5)
        
        # Número de peças
        tk.Label(
            frame,
            text=f"📦 Quantidade de peças: {len(indices)}",
            font=("Arial", 11),
            bg="white"
        ).pack(pady=3)
        
        # Separator
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=10)
        
        # Frame para lista de peças com scroll
        frame_scroll = tk.Frame(frame, bg="white")
        frame_scroll.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(frame_scroll, bg="white", height=300)
        scrollbar = ttk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
        frame_pecas = tk.Frame(canvas, bg="white")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        canvas.create_window((0, 0), window=frame_pecas, anchor="nw")
        
        # Adicionar peças
        for idx in sorted(indices):
            peso = pesos[idx]
            frame_peca = tk.Frame(frame_pecas, bg="#f9f9f9", bd=1, relief="solid")
            frame_peca.pack(fill="x", padx=5, pady=3)
            
            tk.Label(
                frame_peca,
                text=f"Peça {idx + 1}:",
                font=("Arial", 10, "bold"),
                bg="#f9f9f9",
                width=10,
                anchor="w"
            ).pack(side="left", padx=5)
            
            tk.Label(
                frame_peca,
                text=f"{peso} kg",
                font=("Arial", 10),
                bg="#f9f9f9",
                fg=cor,
                width=10,
                anchor="e"
            ).pack(side="right", padx=5)
        
        frame_pecas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))