import matplotlib.pyplot as plt
import networkx as nx
import math

# =============================================
# CÁLCULO DEL TAKT TIME
# =============================================

# Datos proporcionados
productos_por_semana = 1500
dias_por_semana = 5
horas_por_dia = 8
tiempo_descanso_minutos = 30

# Cálculos
tiempo_disponible_por_dia_minutos = (horas_por_dia * 60) - tiempo_descanso_minutos
tiempo_disponible_por_semana_minutos = tiempo_disponible_por_dia_minutos * dias_por_semana
tiempo_disponible_por_semana_segundos = tiempo_disponible_por_semana_minutos * 60

# Takt Time (tiempo disponible / demanda)
takt_time_segundos = tiempo_disponible_por_semana_segundos / productos_por_semana
takt_time_minutos = takt_time_segundos / 60

print("="*70)
print("CÁLCULO DEL TAKT TIME")
print("="*70)
print(f"Productos a fabricar por semana: {productos_por_semana} uni/semana")
print(f"Días laborales por semana: {dias_por_semana} días")
print(f"Horas laborales por día: {horas_por_dia} horas")
print(f"Tiempo de descanso: {tiempo_descanso_minutos} minutos/día")
print(f"Tiempo disponible por día: {tiempo_disponible_por_dia_minutos} minutos")
print(f"Tiempo disponible por semana: {tiempo_disponible_por_semana_minutos} minutos")
print(f"Tiempo disponible por semana: {tiempo_disponible_por_semana_segundos} segundos")
print(f"\nTAKT TIME = {takt_time_segundos:.2f} segundos/unidad")
print(f"TAKT TIME = {takt_time_minutos:.2f} minutos/unidad")

# =============================================
# DATOS DE LAS TAREAS
# =============================================

precedencias = {
    'A': [],
    'B': ['A'],
    'C': ['B'],
    'D': [],
    'E': ['D'],
    'F': ['C'],
    'G': ['C'],
    'H': ['E'],
    'I': ['E'],
    'J': ['F', 'G', 'H', 'I'],
    'K': ['J']
}

tiempos = {
    'A': 15, 'B': 50, 'C': 60, 'D': 45, 'E': 30,
    'F': 12, 'G': 65, 'H': 10, 'I': 8, 'J': 15, 'K': 5
}

# =============================================
# ALGORITMO DE BALANCE DE LÍNEA
# =============================================

def balancear_linea(tareas, precedencias, tiempos, takt_time):
    estaciones = []
    tareas_asignadas = set()
    tiempo_total = sum(tiempos.values())
    
    # Calcular número mínimo teórico de estaciones
    min_estaciones = math.ceil(tiempo_total / takt_time)
    
    # Ordenar tareas por tiempo descendente
    tareas_ordenadas = sorted([(tarea, tiempo) for tarea, tiempo in tiempos.items()], 
                             key=lambda x: x[1], reverse=True)
    
    estacion_actual = 1
    while len(tareas_asignadas) < len(tareas):
        tiempo_estacion = 0
        tareas_estacion = []
        
        for tarea, tiempo in tareas_ordenadas:
            if tarea in tareas_asignadas:
                continue
                
            # Verificar si todas las predecesoras están asignadas
            predecesoras_asignadas = all(p in tareas_asignadas for p in precedencias[tarea])
            
            if predecesoras_asignadas and (tiempo_estacion + tiempo) <= takt_time:
                tareas_estacion.append((tarea, tiempo))
                tiempo_estacion += tiempo
                tareas_asignadas.add(tarea)
        
        if tareas_estacion:
            estaciones.append({
                'estacion': estacion_actual,
                'tareas': tareas_estacion,
                'tiempo_total': tiempo_estacion,
                'eficiencia': (tiempo_estacion / takt_time) * 100
            })
            estacion_actual += 1
    
    return estaciones, tiempo_total, min_estaciones

# Realizar balance
estaciones, tiempo_total, min_estaciones = balancear_linea(list(tiempos.keys()), precedencias, tiempos, takt_time_segundos)

# =============================================
# VISUALIZACIÓN COMPLETA
# =============================================

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 12))

# SUBPLOT 1: Diagrama de Precedencia
G = nx.DiGraph()
for tarea, predecesores in precedencias.items():
    G.add_node(tarea, tiempo=tiempos[tarea])
    for predecesor in predecesores:
        G.add_edge(predecesor, tarea)

pos = {
    'A': (0, 2), 'D': (0, 0),
    'B': (2, 2), 'E': (2, 0),
    'C': (4, 2), 'H': (4, 0.5), 'I': (4, -0.5),
    'F': (6, 2.5), 'G': (6, 1.5),
    'J': (8, 1), 'K': (10, 1)
}

node_colors = ['lightblue' for _ in G.nodes()]
nx.draw_networkx_nodes(G, pos, node_size=1500, node_color=node_colors, 
                      edgecolors='black', linewidths=2, ax=ax1)
nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=20, 
                      edge_color='gray', width=2, ax=ax1)
labels = {node: f"{node}\n({tiempos[node]}s)" for node in G.nodes()}
nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, 
                       font_weight='bold', ax=ax1)

ax1.set_title("DIAGRAMA DE PRECEDENCIA", fontsize=14, fontweight='bold')
ax1.axis('off')

# SUBPLOT 2: Tabla de Precedencias
ax2.axis('off')
table_data = [
    ["TAREA", "PREDECESORES", "TIEMPO (s)"],
    ["A", "-", "15"],
    ["B", "A", "50"],
    ["C", "B", "60"],
    ["D", "-", "45"],
    ["E", "D", "30"],
    ["F", "C", "12"],
    ["G", "C", "65"],
    ["H", "E", "10"],
    ["I", "E", "8"],
    ["J", "F, G, H, I", "15"],
    ["K", "J", "5"]
]

table = ax2.table(cellText=table_data, cellLoc='center', loc='center', colWidths=[0.2, 0.4, 0.2])
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 2)

for i in range(len(table_data)):
    for j in range(len(table_data[0])):
        cell = table[i, j]
        if i == 0:  # Encabezado
            cell.set_facecolor('#4CAF50')
            cell.set_text_props(weight='bold', color='white')
        else:
            cell.set_facecolor('#f0f0f0')
        cell.set_edgecolor('black')

ax2.set_title("TABLA DE PRECEDENCIAS Y TIEMPOS", fontsize=12, fontweight='bold')

# SUBPLOT 3: Balance de Línea
ax3.axis('off')
balance_data = [["Estación", "Tareas", "Tiempo (s)", "Eficiencia (%)"]]
for est in estaciones:
    tareas_str = ", ".join([f"{t[0]}({t[1]}s)" for t in est['tareas']])
    balance_data.append([
        f"Estación {est['estacion']}",
        tareas_str,
        f"{est['tiempo_total']}",
        f"{est['eficiencia']:.1f}%"
    ])

balance_table = ax3.table(cellText=balance_data, cellLoc='center', loc='center', 
                         colWidths=[0.2, 0.4, 0.2, 0.2])
balance_table.auto_set_font_size(False)
balance_table.set_fontsize(10)
balance_table.scale(1, 1.5)

# Corregido: Sin usar key[2]
for i in range(len(balance_data)):
    for j in range(len(balance_data[0])):
        cell = balance_table[i, j]
        if i == 0:  # Encabezado
            cell.set_facecolor('#2196F3')
            cell.set_text_props(weight='bold', color='white')
        else:
            # Colorear según eficiencia (columna 3)
            if j == 3:  # Columna de eficiencia
                eficiencia = float(balance_data[i][3].replace('%', ''))
                if eficiencia > 90:
                    cell.set_facecolor('#C8E6C9')
                elif eficiencia > 70:
                    cell.set_facecolor('#FFF9C4')
                else:
                    cell.set_facecolor('#FFCDD2')
            else:
                cell.set_facecolor('#f5f5f5')
        cell.set_edgecolor('black')

ax3.set_title("BALANCE DE LÍNEA - ASIGNACIÓN A ESTACIONES", fontsize=12, fontweight='bold')

# SUBPLOT 4: Métricas del Balance
ax4.axis('off')
eficiencia_general = (tiempo_total / (len(estaciones) * takt_time_segundos)) * 100
tiempo_ciclo = max(est['tiempo_total'] for est in estaciones)

metricas_data = [
    ["MÉTRICA", "VALOR"],
    ["Takt Time", f"{takt_time_segundos:.2f} s"],
    ["Tiempo Total de Tareas", f"{tiempo_total} s"],
    ["Número Mínimo Teórico", f"{min_estaciones}"],
    ["Número Real de Estaciones", f"{len(estaciones)}"],
    ["Eficiencia General", f"{eficiencia_general:.1f}%"],
    ["Tiempo de Ciclo", f"{tiempo_ciclo} s"],
    ["Productividad", f"{productos_por_semana} uni/semana"]
]

metricas_table = ax4.table(cellText=metricas_data, cellLoc='center', loc='center', 
                          colWidths=[0.5, 0.5])
metricas_table.auto_set_font_size(False)
metricas_table.set_fontsize(11)
metricas_table.scale(1, 1.5)

for i in range(len(metricas_data)):
    for j in range(len(metricas_data[0])):
        cell = metricas_table[i, j]
        if i == 0:
            cell.set_facecolor('#FF9800')
            cell.set_text_props(weight='bold', color='white')
        else:
            cell.set_facecolor('#E3F2FD')
        cell.set_edgecolor('black')

ax4.set_title("MÉTRICAS DEL BALANCE", fontsize=12, fontweight='bold')

plt.suptitle(f"ASSEMBLY LINE BALANCING (SALBP-1) - TAKT TIME: {takt_time_segundos:.2f} segundos/unidad", 
             fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout()
plt.subplots_adjust(top=0.94)
plt.show()

# =============================================
# INFORMACIÓN ADICIONAL EN CONSOLA
# =============================================

print("\n" + "="*70)
print("ANÁLISIS DE BALANCE DE LÍNEA")
print("="*70)

print(f"\nRESUMEN DE ESTACIONES DE TRABAJO:")
for est in estaciones:
    tareas_nombres = [t[0] for t in est['tareas']]
    print(f"Estación {est['estacion']}: {tareas_nombres} | "
          f"Tiempo: {est['tiempo_total']}s | Eficiencia: {est['eficiencia']:.1f}%")

print(f"\nMÉTRICAS FINALES:")
print(f"- Takt Time: {takt_time_segundos:.2f} segundos/unidad")
print(f"- Número mínimo teórico de estaciones: {min_estaciones}")
print(f"- Número real de estaciones: {len(estaciones)}")
print(f"- Eficiencia general de la línea: {eficiencia_general:.1f}%")
print(f"- Tiempo de ciclo: {tiempo_ciclo} segundos")

print(f"\nRUTA CRÍTICA: A → B → C → G → J → K (Tiempo: 15+50+60+65+15+5 = 210s)")