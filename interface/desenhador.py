# interface/desenhador.py

import tkinter as tk

def desenhar_layout(frame_placas, placas):

    escala = 1.2
    margem_cm = 10
    margem_px = margem_cm * escala

    placas_por_linha = 2

    for i, placa in enumerate(placas):

        # Frame para cada placa
        f = tk.Frame(frame_placas, bd=2, relief="groove", padx=10, pady=10)
        f.grid(row=i // placas_por_linha, column=i % placas_por_linha, padx=10, pady=10)

        # Tamanho real da placa em pixels
        largura_px = placa.largura_util * escala
        altura_px = placa.altura_util * escala

        # ALTURA DINÂMICA DO CANVAS = placa + margens
        canvas_altura = int(altura_px + margem_px + 40)
        canvas_largura = int(largura_px + 40)

        canvas = tk.Canvas(f, width=canvas_largura, height=canvas_altura, bg="white")
        canvas.pack()

        # Desenhar placa com margem superior (10 cm)
        canvas.create_rectangle(
            20,
            margem_px,
            20 + largura_px,
            margem_px + altura_px,
            outline="black",
            width=3
        )

        # Desenhar peças
        for prateleira in placa.prateleiras:
            for peca in prateleira.pecas:

                x1 = 20 + peca.x * escala
                y1 = margem_px + peca.y * escala
                x2 = x1 + peca.largura * escala
                y2 = y1 + peca.altura * escala

                canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="#add8e6",
                    outline="black"
                )

                canvas.create_text(
                    (x1 + x2) / 2,
                    (y1 + y2) / 2,
                    text=f"{peca.altura}x{peca.largura}",
                    font=("Arial", 8)
                )
