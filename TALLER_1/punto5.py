# simulador_lotes_final.py
import math
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------
# Parámetros del problema
# ---------------------------
Q = 10  # unidades totales a producir
MODE = "unit"   # "unit" (recomendado) o "batch" (procesa lotes enteros por estación)

# Actividades: desc, C (s/unidad), L (lote transferencia), preds (predecesores)
activities = {
    "A": {"desc": "CUT (inicio)", "C": 5,  "L": 10, "preds": []},
    "B": {"desc": "PREFORMED",    "C": 30, "L": 2,  "preds": ["A"]},
    "C": {"desc": "ASSEMBLY 1",   "C": 20, "L": 1,  "preds": ["B"]},
    "D": {"desc": "ASSEMBLY 2",   "C": 15, "L": 1,  "preds": ["C"]},
    "E": {"desc": "ASSEMBLY 3",   "C": 25, "L": 1,  "preds": ["D"]},
    # << CORRECCIÓN: F depende de E (no de D). Así F puede arrancar cuando E le entregue unidades >>
    "F": {"desc": "ASSEMBLY 4",   "C": 20, "L": 10, "preds": ["E"]},
    "G": {"desc": "PACKED",       "C": 10, "L": 2,  "preds": ["E", "F"]}
}

# ---------------------------
# Topological order (Kahn)
# ---------------------------
nodes = list(activities.keys())
preds_map = {n: list(activities[n]["preds"]) for n in nodes}
indeg = {n: 0 for n in nodes}
succ = {n: [] for n in nodes}
for n, p_list in preds_map.items():
    for p in p_list:
        succ[p].append(n)
        indeg[n] += 1

Qnodes = [n for n in nodes if indeg[n] == 0]
topo = []
while Qnodes:
    n = Qnodes.pop(0)
    topo.append(n)
    for s in succ[n]:
        indeg[s] -= 1
        if indeg[s] == 0:
            Qnodes.append(s)
if len(topo) != len(nodes):
    raise RuntimeError("El grafo de precedencias tiene ciclos o está mal definido.")

# ---------------------------
# Estructuras por unidad
# ---------------------------
start_per_unit = {}    # start_per_unit[act] = list length Q
finish_per_unit = {}
release_per_unit = {}  # release_per_unit[act][k] = tiempo en que pred libera la unidad k a sucesores

# ---------------------------
# Simulación (por topological order)
# ---------------------------
for act in topo:
    C = activities[act]["C"]
    L = activities[act]["L"]
    preds = activities[act]["preds"]

    # caso sin predecesores
    if not preds:
        if MODE == "unit":
            starts = [ (k-1) * C for k in range(1, Q+1) ]
            finishes = [ s + C for s in starts ]
        else:  # MODE == "batch"
            starts = [0.0]*Q
            finishes = [0.0]*Q
            machine_free = 0.0
            num_batches = math.ceil(Q / L)
            for b in range(1, num_batches+1):
                k0 = (b-1)*L + 1
                k1 = min(b*L, Q)
                batch_start = machine_free
                for k in range(k0, k1+1):
                    idx = k-1
                    st = batch_start + (k - k0)*C
                    fin = st + C
                    starts[idx] = st
                    finishes[idx] = fin
                machine_free = finishes[k1-1]
    else:
        # llegadas/arrivals por unidad: momento en que la unidad k está disponible
        # arrival[k] = max_over_preds( release_per_unit[p][k-1] )
        arrivals = []
        for k in range(1, Q+1):
            arr_k = 0.0
            for p in preds:
                # release_per_unit[p] ya fue calculado porque p está antes en topo
                arr_k = max(arr_k, release_per_unit[p][k-1])
            arrivals.append(arr_k)

        if MODE == "unit":
            # procesado unidad a unidad: la máquina procesa secuencialmente cuando hay unidades disponibles
            starts = [0.0]*Q
            finishes = [0.0]*Q
            prev_finish = 0.0
            for idx in range(Q):
                st = max(prev_finish, arrivals[idx])
                fin = st + C
                starts[idx] = st
                finishes[idx] = fin
                prev_finish = fin
        else:
            # MODE == "batch": procesar por batches del propio L (espera a formar su lote L)
            starts = [0.0]*Q
            finishes = [0.0]*Q
            machine_free = 0.0
            num_batches = math.ceil(Q / L)
            for b in range(1, num_batches+1):
                k0 = (b-1)*L + 1
                k1 = min(b*L, Q)
                # batch disponible cuando TODOS los preds han liberado hasta unit k1
                batch_avail = 0.0
                for p in preds:
                    batch_avail = max(batch_avail, release_per_unit[p][k1-1])
                batch_start = max(machine_free, batch_avail)
                for k in range(k0, k1+1):
                    idx = k-1
                    st = batch_start + (k - k0)*C
                    fin = st + C
                    starts[idx] = st
                    finishes[idx] = fin
                machine_free = finishes[k1-1]

    # calcular release_per_unit para esta actividad:
    # la actividad libera (hace disponible para sucesores) la unidad k en el finish del unit que cierra su propio lote que contiene k
    releases = [0.0]*Q
    for k in range(1, Q+1):
        batch_end = min(math.ceil(k / L) * L, Q)
        releases[k-1] = finishes[batch_end - 1]

    # almacenar
    start_per_unit[act] = starts
    finish_per_unit[act] = finishes
    release_per_unit[act] = releases

# ---------------------------
# Resumen por actividad y detalle por lote (para Gantt)
# ---------------------------
rows = []
gantt_rows = []
for act in topo:
    starts = start_per_unit[act]
    finishes = finish_per_unit[act]
    L = activities[act]["L"]
    num_batches = math.ceil(Q / L)
    rows.append({
        "Act": act,
        "Desc": activities[act]["desc"],
        "C": activities[act]["C"],
        "L": L,
        "Start_first_unit": starts[0],
        "Finish_last_unit": finishes[-1]
    })
    for b in range(1, num_batches+1):
        first_unit_idx = (b-1)*L
        last_unit_idx = min(b*L, Q) - 1
        batch_start = starts[first_unit_idx]
        batch_finish = finishes[last_unit_idx]
        gantt_rows.append({
            "Act": act,
            "Batch": b,
            "Start": batch_start,
            "Finish": batch_finish
        })

df_summary = pd.DataFrame(rows)
df_gantt = pd.DataFrame(gantt_rows).sort_values(["Start", "Act", "Batch"])

# ---------------------------
# Mostrar resultados
# ---------------------------
print("\nResumen por actividad (inicio primera unidad / fin última unidad):")
print(df_summary[["Act","Desc","C","L","Start_first_unit","Finish_last_unit"]].to_string(index=False))

print("\nDetalle por lote (para Gantt):")
print(df_gantt.to_string(index=False))

makespan = df_summary["Finish_last_unit"].max()
print(f"\nMakespan (Throughput time) = {makespan:.0f} s  (Q={Q})")

# ---------------------------
# Gantt por lotes (visual)
# ---------------------------
plt.figure(figsize=(12,6))
acts = topo
y_pos = {act: i for i, act in enumerate(acts[::-1])}
colors = plt.cm.get_cmap("tab20").colors
for _, r in df_gantt.iterrows():
    y = y_pos[r["Act"]]
    plt.barh(y, r["Finish"]-r["Start"], left=r["Start"], height=0.6,
             color=colors[int(r["Batch"]) % len(colors)], edgecolor="k")
    plt.text(r["Start"] + (r["Finish"]-r["Start"])/2, y,
             f"B{int(r['Batch'])}", va='center', ha='center', fontsize=8, color='white')

plt.yticks(list(y_pos.values()), list(y_pos.keys()))
plt.xlabel("Tiempo (s)")
plt.title(f"Gantt por lotes (MODE={MODE}, Q={Q})")
plt.grid(axis='x', linestyle='--', alpha=0.4)
plt.tight_layout()
plt.show()
