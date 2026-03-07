import pulp as pl
import networkx as nx
import matplotlib.pyplot as plt

# ==============================
# Modelo original (crashing)
# ==============================
model = pl.LpProblem("Crashing", pl.LpMinimize)

ACTIVIDADES = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N"]

DurNormal = {"A":5,"B":4,"C":7,"D":6,"E":13,"F":9,"G":11,"H":5,"I":12,"J":8,"K":15,"L":10,"M":7,"N":8}
DurCrash  = {"A":5,"B":2,"C":4,"D":6,"E":7,"F":3,"G":7,"H":5,"I":6,"J":4,"K":10,"L":5,"M":3,"N":4}

CostoNormal = {"A":5000,"B":6000,"C":800,"D":2000,"E":4000,"F":1000,"G":2000,"H":5000,
               "I":8000,"J":500,"K":700,"L":1200,"M":10000,"N":4000}
CostoCrash  = {"A":5000,"B":12000,"C":2600,"D":2000,"E":6400,"F":7000,"G":4000,"H":5000,
               "I":20000,"J":2500,"K":4700,"L":3200,"M":16000,"N":8000}

Precedencias = [
    ("A","C"),("C","E"),("C","F"),("B","D"),("D","G"),("D","H"),
    ("E","I"),("F","I"),("F","J"),("G","J"),("H","K"),("I","L"),
    ("J","M"),("K","M"),("L","N"),("M","N")
]

CostoIndirecto = 1200

# Variables
y = pl.LpVariable.dicts("Crash", ACTIVIDADES, 0, 1, pl.LpBinary)
Dur = pl.LpVariable.dicts("Dur", ACTIVIDADES, lowBound=0)
CostoAct = pl.LpVariable.dicts("CostoAct", ACTIVIDADES, lowBound=0)
Start = pl.LpVariable.dicts("Start", ACTIVIDADES, lowBound=0)
TFin = pl.LpVariable("TFin", lowBound=0)

# Restricciones
for i in ACTIVIDADES:
    model += Dur[i] == (1 - y[i]) * DurNormal[i] + y[i] * DurCrash[i]
    model += CostoAct[i] == (1 - y[i]) * CostoNormal[i] + y[i] * CostoCrash[i]

for (i,j) in Precedencias:
    model += Start[j] >= Start[i] + Dur[i]

for i in ACTIVIDADES:
    model += TFin >= Start[i] + Dur[i]

# Objetivo
model += pl.lpSum(CostoAct[i] for i in ACTIVIDADES) + CostoIndirecto * TFin

# Resolver
model.solve(pl.PULP_CBC_CMD(msg=0))

print("Estado:", pl.LpStatus[model.status])
print("TFin (LP) =", pl.value(TFin))
print("Costo total (LP) =", pl.value(model.objective))
print("\nResultados por actividad:")
print("{:<3} {:<6} {:<6} {:<6} {:<8}".format("Act","Dur","Start","Crash","Costo"))
for i in ACTIVIDADES:
    print("{:<3} {:<6} {:<6} {:<6} {:<8}".format(
        i,
        round(Dur[i].value(),2),
        round(Start[i].value(),2),
        int(y[i].value()),
        round(CostoAct[i].value(),2)
    ))

# ==============================
# Calcular ruta crítica desde la solución (DP sobre DAG)
# ==============================
# valores resueltos
start_vals = {i: float(Start[i].value()) for i in ACTIVIDADES}
dur_vals   = {i: float(Dur[i].value())   for i in ACTIVIDADES}

# construir grafo
G = nx.DiGraph()
G.add_nodes_from(ACTIVIDADES)
G.add_edges_from(Precedencias)

# topological DP para la suma de duraciones por camino (incluye duración del nodo)
topo = list(nx.topological_sort(G))

# longest_total[node] = máxima suma de duraciones desde alguna fuente hasta node (incluye node)
longest_total = {}
prev = {}  # para reconstrucción
for node in topo:
    preds = list(G.predecessors(node))
    if not preds:
        longest_total[node] = dur_vals[node]
        prev[node] = None
    else:
        # elegir pred con máximo longest_total
        best_pred = max(preds, key=lambda p: longest_total[p])
        longest_total[node] = longest_total[best_pred] + dur_vals[node]
        prev[node] = best_pred

# nodo final de mayor longitud
end_node = max(longest_total, key=lambda n: longest_total[n])
critical_duration = longest_total[end_node]

# reconstruir camino
critical_path = []
n = end_node
while n is not None:
    critical_path.append(n)
    n = prev[n]
critical_path = list(reversed(critical_path))

print("\nRuta crítica (reconstruida):", " → ".join(critical_path))
print("Duración ruta crítica (suma Dur):", critical_duration)

# Verificación con Start+Dur
max_finish = max(start_vals[i] + dur_vals[i] for i in ACTIVIDADES)
print("Max(Start+Dur) calculado =", max_finish)

# comparaciones (con tolerancia)
tol = 1e-6
if abs(critical_duration - max_finish) < 1e-5 and abs(max_finish - pl.value(TFin)) < 1e-5:
    print("✅ La TFin del LP, Max(Start+Dur) y la suma de la ruta crítica coinciden (dentro de tolerancia).")
else:
    print("⚠️ Hay una pequeña diferencia entre valores: TFin(LP) vs ruta crítica vs Max(Start+Dur).")

# ==============================
# Dibujar la red y resaltar ruta crítica
# ==============================
# preparar etiquetas (Start/Finish/Dur)
labels = {}
for i in ACTIVIDADES:
    s = start_vals[i]
    d = dur_vals[i]
    f = s + d
    labels[i] = f"{i}\nS={s:.1f}\nF={f:.1f}\nDur={d:.1f}"

# layout: intentar graphviz dot para jerarquía, si no, usar spring
try:
    pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
except Exception:
    pos = nx.spring_layout(G, seed=42)

plt.figure(figsize=(12,7))
# nodos no criticos
noncrit = [n for n in ACTIVIDADES if n not in critical_path]
nx.draw_networkx_nodes(G, pos, nodelist=noncrit, node_color="skyblue", node_size=1300)
# nodos criticos
nx.draw_networkx_nodes(G, pos, nodelist=critical_path, node_color="red", node_size=1500)
nx.draw_networkx_labels(G, pos, labels=labels, font_size=9)
nx.draw_networkx_edges(G, pos, edgelist=list(G.edges()), arrows=True)

# resaltar aristas de la ruta critica (pares consecutivos)
crit_edges = [(critical_path[i], critical_path[i+1]) for i in range(len(critical_path)-1)]
nx.draw_networkx_edges(G, pos, edgelist=crit_edges, edge_color="red", width=3, arrows=True)

plt.title(f"Ruta crítica: {' → '.join(critical_path)} (Duración = {critical_duration:.2f})")
plt.axis("off")
plt.show()
