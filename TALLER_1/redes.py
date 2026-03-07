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
# 3. Ruta crítica (CPM)
# ==============================
for u, v in G.edges():
    G[u][v]["weight"] = G.nodes[u].get("Duration", 0)

critical_path = nx.dag_longest_path(G, weight="weight")
critical_length = nx.dag_longest_path_length(G, weight="weight")

print("📌 Ruta crítica:", " → ".join(critical_path))
print("⏳ Duración total del proyecto:", critical_length)

# ==============================
# 4. Dibujar diagrama de red con spring_layout optimizado
# ==============================
# Layout con más separación
pos = nx.spring_layout(G, seed=42, k=1.2, iterations=200)

# Colores de arcos: rojo si está en ruta crítica
edge_colors = []
for u, v in G.edges():
    if u in critical_path and v in critical_path and critical_path.index(v) == critical_path.index(u) + 1:
        edge_colors.append("red")
    else:
        edge_colors.append("skyblue")

plt.figure(figsize=(14, 8))
nx.draw(
    G, pos, with_labels=False,
    node_size=3000, node_color="lightyellow",
    arrows=True, edge_color=edge_colors
)

# Etiquetas personalizadas (solo nombre + duración)
labels = {node: f"{node}\n({data.get('Duration','-')})" for node, data in G.nodes(data=True)}
nx.draw_networkx_labels(G, pos, labels=labels, font_size=11, font_weight="bold")

plt.title("Diagrama de Red (PERT/CPM)", fontsize=16, fontweight="bold")
plt.axis("off")
plt.tight_layout()
plt.show()
