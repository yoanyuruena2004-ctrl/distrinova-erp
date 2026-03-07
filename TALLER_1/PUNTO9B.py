import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# === Leer archivo Excel ===
df = pd.read_excel("PUNTO9.xlsx")
print("✅ Columnas originales:", df.columns.tolist())

# Quitar espacios en nombres de columnas
df.columns = df.columns.str.strip()

# Renombrar
df = df.rename(columns={
    "ACTIVIDAD": "Activity",
    "PRECEDENTE": "Predecessors",
    "TIEMPO NORMAL": "Normal",
    "TIEMPO ACELERADO": "Crash"
})

print("✅ Columnas renombradas:", df.columns.tolist())

# === Función para calcular ruta crítica ===
def calcular_ruta(df, usar="Crash"):
    G = nx.DiGraph()

    # Agregar nodos con duración
    for _, row in df.iterrows():
        G.add_node(row["Activity"], duration=row[usar])

    # Agregar arcos (peso = duración del destino)
    for _, row in df.iterrows():
        if pd.notna(row["Predecessors"]):
            for pred in str(row["Predecessors"]).split(","):
                pred = pred.strip()
                if pred != "":
                    G.add_edge(pred, row["Activity"], weight=row[usar])

    # Calcular ruta crítica
    longest_path = nx.dag_longest_path(G, weight="weight")
    longest_duration = nx.dag_longest_path_length(G, weight="weight")

    print(f"\n📌 Escenario: {usar}")
    print("Ruta crítica:", " → ".join(longest_path))
    print("Duración total del proyecto:", longest_duration)

    # === Graficar ===
    pos = nx.spring_layout(G, seed=42)
    edge_colors = [
        "red" if (u, v) in zip(longest_path, longest_path[1:]) else "lightblue"
        for u, v in G.edges()
    ]
    labels = {
        node: f"{node}\n({data['duration']})" if "duration" in data else str(node)
        for node, data in G.nodes(data=True)
    }

    nx.draw(
        G, pos, with_labels=True, labels=labels,
        node_size=2500, node_color="lightyellow",
        font_size=9, edge_color=edge_colors, arrows=True
    )
    plt.title(f"Diagrama de Red - Escenario {usar}")
    plt.show()

    return G, longest_path, longest_duration

# === Solo escenario acelerado ===
G_crash, ruta_crash, dur_crash = calcular_ruta(df, usar="Crash")
