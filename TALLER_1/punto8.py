import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# ==============================
# 1. Leer datos del Excel
# ==============================
df = pd.read_excel("diagrama_gantt.xlsx")

df = df.rename(columns={
    "Actividad": "Activity",
    "Precedente": "Predecessors",
    "Tiempo": "Duration"
})

# ==============================
# 2. Construir el grafo dirigido
# ==============================
G = nx.DiGraph()

for _, row in df.iterrows():
    G.add_node(row["Activity"], Duration=row["Duration"])
    if pd.notna(row["Predecessors"]):
        preds = str(row["Predecessors"]).split(",")
        for p in preds:
            p = p.strip()
            if p not in ["", "0", "nan"]:
                G.add_edge(p, row["Activity"])

# ==============================
# 3. Calcular tiempos tempranos (Forward Pass)
# ==============================
ES, EF = {}, {}

for node in nx.topological_sort(G):
    preds = list(G.predecessors(node))
    if preds:
        ES[node] = max(EF[p] for p in preds)
    else:
        ES[node] = 0
    EF[node] = ES[node] + G.nodes[node]["Duration"]

# ==============================
# 4. Calcular tiempos tardíos (Backward Pass)
# ==============================
LF, LS = {}, {}
project_duration = max(EF.values())

for node in reversed(list(nx.topological_sort(G))):
    succs = list(G.successors(node))
    if succs:
        LF[node] = min(LS[s] for s in succs)
    else:
        LF[node] = project_duration
    LS[node] = LF[node] - G.nodes[node]["Duration"]

# ==============================
# 5. Calcular holguras y clasificar actividades
# ==============================
slack = {node: LS[node] - ES[node] for node in G.nodes()}
critical_activities = [n for n, s in slack.items() if s == 0]
non_critical = {n: s for n, s in slack.items() if s > 0}

print("📌 Ruta crítica:", " → ".join(critical_activities))
print("⏳ Duración total del proyecto:", project_duration)
print("\n✅ Actividades no críticas y sus holguras:")
for act, h in non_critical.items():
    print(f"   - {act}: holgura {h}")

# ==============================
# 6. Dibujar diagrama de red
# ==============================
pos = nx.spring_layout(G, seed=42, k=1.2, iterations=200)

edge_colors = []
for u, v in G.edges():
    if u in critical_activities and v in critical_activities and critical_activities.index(v) == critical_activities.index(u) + 1:
        edge_colors.append("red")
    else:
        edge_colors.append("skyblue")

plt.figure(figsize=(14, 8))
nx.draw(G, pos, with_labels=False, node_size=3000, node_color="lightyellow",
        arrows=True, edge_color=edge_colors)

# Etiquetas personalizadas con duración y holgura
labels = {node: f"{node}\nDur:{G.nodes[node]['Duration']}, H:{slack[node]}" for node in G.nodes()}
nx.draw_networkx_labels(G, pos, labels=labels, font_size=9, font_weight="bold")

plt.title("Diagrama de Red (PERT/CPM) con Holguras", fontsize=16, fontweight="bold")
plt.axis("off")
plt.tight_layout()
plt.show()
