import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# ==============================
# 1. Leer datos del Excel
# ==============================
df = pd.read_excel("diagrama_gantt.xlsx")

print("✅ Columnas originales:", df.columns.tolist())

# Renombrar columnas a inglés para estandarizar
df = df.rename(columns={
    "Actividad": "Activity",
    "Precedente": "Predecessors",
    "Tiempo": "Duration"
})

print("✅ Columnas renombradas:", df.columns.tolist())

# ==============================
# 2. Construir el grafo dirigido
# ==============================
G = nx.DiGraph()

# Agregar nodos con duración
for _, row in df.iterrows():
    G.add_node(row["Activity"], Duration=row["Duration"])

    if pd.notna(row["Predecessors"]):
        preds = str(row["Predecessors"]).split(",")
        for p in preds:
            p = p.strip()
            if p not in ["", "0", "nan"]:  # 🚀 evitar nodos falsos
                G.add_edge(p, row["Activity"])

# ==============================
# 3. Calcular ruta crítica (CPM)
# ==============================
# Peso de los arcos = duración de la actividad origen
for u, v in G.edges():
    G[u][v]["weight"] = G.nodes[u].get("Duration", 0)

# Ruta crítica y duración total
critical_path = nx.dag_longest_path(G, weight="weight")
critical_length = nx.dag_longest_path_length(G, weight="weight")

print("📌 Ruta crítica:", " → ".join(critical_path))
print("⏳ Duración total del proyecto:", critical_length)

# ==============================
# 4. Dibujar diagrama de red
# ==============================
pos = nx.spring_layout(G, seed=42)

edge_colors = []
for u, v in G.edges():
    if u in critical_path and v in critical_path and critical_path.index(v) == critical_path.index(u) + 1:
        edge_colors.append("red")
    else:
        edge_colors.append("skyblue")

plt.figure(figsize=(12, 7))
nx.draw(G, pos, with_labels=True, node_size=2000, node_color="lightyellow",
        arrows=True, edge_color=edge_colors, font_size=10)

# Etiquetas: actividad y duración (si existe)
labels = {node: f"{node}\n({data.get('Duration','-')})" for node, data in G.nodes(data=True)}
nx.draw_networkx_labels(G, pos, labels=labels)

plt.title("Diagrama de Red (PERT/CPM)", fontsize=14)
plt.show()
