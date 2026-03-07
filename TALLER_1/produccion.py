# gantt_y_red_punto5.py
import matplotlib.pyplot as plt
import networkx as nx

# Datos del Punto 5 (segundos)
actividades = [
    {"act":"A","C":5,  "L":10, "start":0,   "end":50},
    {"act":"B","C":30, "L":2,  "start":50,  "end":350},
    {"act":"C","C":20, "L":1,  "start":110, "end":390},
    {"act":"D","C":15, "L":1,  "start":130, "end":405},
    {"act":"E","C":25, "L":1,  "start":145, "end":435},
    {"act":"F","C":20, "L":10, "start":170, "end":455},
    {"act":"G","C":10, "L":2,  "start":415, "end":555},
]

# 1) Imprimir resumen y cálculos
Q = 10
ts_s = max(a["end"] for a in actividades) - min(a["start"] for a in actividades)
ts_min = ts_s / 60
th_order_u_per_min = Q / ts_min
C_max = max(a["C"] for a in actividades)
bottleneck_u_per_min = (1.0 / C_max) * 60.0

print("Throughput time (s):", ts_s)
print("Throughput time (min):", ts_min)
print("Throughput de la orden Q=10 (u/min):", th_order_u_per_min)
print("Cuello de botella C_max (s/u):", C_max)
print("Capacidad cuello (u/min):", bottleneck_u_per_min)

# 2) Diagrama de Gantt (usando start,end)
fig, ax = plt.subplots(figsize=(12, 4))
y_pos = range(len(actividades))
labels = [a["act"] for a in actividades]
starts = [a["start"] for a in actividades]
ends = [a["end"] for a in actividades]
widths = [e - s for s,e in zip(starts, ends)]
ax.barh(y_pos, widths, left=starts, height=0.6, color="skyblue", edgecolor="k")
for i,(s,w,e,lab) in enumerate(zip(starts,widths,ends,labels)):
    ax.text(s + w/2, i, f"{int(s)}→{int(e)}", va='center', ha='center', fontsize=9, color='k')
ax.set_yticks(y_pos)
ax.set_yticklabels(labels)
ax.invert_yaxis()
ax.set_xlabel("Tiempo (s)")
ax.set_title("Diagrama de Gantt — Punto 5 (orden Q=10)")
ax.grid(axis='x', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig("gantt_punto5.png", dpi=300)
print("Gantt guardado como gantt_punto5.png")
plt.show()

# 3) Diagrama de nodos (CPM) usando las precedencias del enunciado
G = nx.DiGraph()
# Precedencias según el enunciado:
precedencias = {
    "A": [],
    "B": ["A"],
    "C": ["B"],
    "D": ["C"],
    "E": ["D"],
    "F": ["D"],
    "G": ["E","F"]
}
# Añadir nodos con duración (usamos C como duración)
for a in actividades:
    G.add_node(a["act"], dur=a["C"])
for v, preds in precedencias.items():
    for p in preds:
        G.add_edge(p, v)

# Calcular ES/EF para posicionamiento (simple topological forward)
ES = {}
EF = {}
for n in nx.topological_sort(G):
    preds = list(G.predecessors(n))
    ES[n] = 0 if not preds else max(EF[p] for p in preds)
    EF[n] = ES[n] + G.nodes[n]['dur']

# Create hierarchical positions left->right using levels
levels = {}
for node in nx.topological_sort(G):
    preds = list(G.predecessors(node))
    levels[node] = 0 if not preds else max(levels[p] for p in preds) + 1
for n,l in levels.items():
    G.nodes[n]['level'] = l

pos = nx.multipartite_layout(G, subset_key='level', align='horizontal')

plt.figure(figsize=(10,4))
# draw nodes, edges
critical = [n for n in G.nodes if (EF[n]-ES[n]==EF[n]-ES[n] and True)]  # placeholder, we'll compute slack next
nx.draw_networkx_nodes(G, pos, node_size=2500, node_color='skyblue')
nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle='->', arrowsize=15)
# labels: show name \n duration
labels = {n: f"{n}\n{G.nodes[n]['dur']}s" for n in G.nodes}
nx.draw_networkx_labels(G, pos, labels=labels, font_size=10)
plt.title("Diagrama de red (CPM) — Punto 5 (duraciones en s)")
plt.axis('off')
plt.tight_layout()
plt.savefig("cpm_punto5.png", dpi=300)
print("Diagrama de red guardado como cpm_punto5.png")
plt.show()
