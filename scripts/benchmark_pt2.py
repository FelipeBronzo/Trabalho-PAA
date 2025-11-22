"""Benchmark script for PT2 partition problem.

Generates random instances and a couple of adversarial ones, then runs
`comparar_com_heuristica` from `logica.algoritmos.branch_and_boundpt2` to
collect metrics for brute-force (when feasible), branch-and-bound and the
heuristic. Results are written to a CSV file.

Usage:
    python scripts\benchmark_pt2.py [output.csv]

By default writes to `dados/bench_pt2.csv`.
"""

import csv
import random
import sys
from pathlib import Path

# garantir que o diretório do projeto esteja no sys.path quando executado como script
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logica.algoritmos.branch_and_boundpt2 import comparar_com_heuristica


def generate_instances(sizes, samples_per_size, seed=42):
    random.seed(seed)
    instances = []

    for n in sizes:
        for s in range(samples_per_size):
            # pesos inteiros entre 1 e 100
            inst = [random.randint(1, 100) for _ in range(n)]
            instances.append((n, inst, f"rand_{n}_{s}"))

    # adicionar casos adversariais
    # muitos pequenos e dois médios/grandes
    instances.append((12, [50, 49] + [1] * 10, "adversarial_12_a"))
    instances.append((12, [60, 40] + [2] * 10, "adversarial_12_b"))

    return instances


def run_benchmark(output_path: Path):
    sizes = [6, 8, 10, 12]
    samples_per_size = 5

    instances = generate_instances(sizes, samples_per_size)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "id",
            "n",
            "instance",
            "bf_melhor_dif",
            "bf_tempo",
            "bf_particoes",
            "bnb_melhor_dif",
            "bnb_tempo",
            "bnb_nos",
            "heur_melhor_dif",
            "heur_tempo",
            "heur_matches_optimal"
        ])

        for n, inst, inst_id in instances:
            print(f"Running instance {inst_id} (n={n})")
            res = comparar_com_heuristica(inst)

            bf = res["bruteforce"]
            bnb = res["branch_and_bound"]
            heur = res["heuristica_gulosa"]

            writer.writerow([
                inst_id,
                n,
                ";".join(map(str, inst)),
                bf["melhor_dif"],
                bf["tempo"],
                bf["particoes_avaliadas"],
                bnb["melhor_dif"],
                bnb["tempo"],
                bnb["nos_explorados"],
                heur["melhor_dif"],
                heur["tempo"],
                abs(bf["melhor_dif"] - heur["melhor_dif"]) < 1e-9,
            ])


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dados") / "bench_pt2.csv"
    run_benchmark(out)
    print(f"Benchmark saved to {out}")
