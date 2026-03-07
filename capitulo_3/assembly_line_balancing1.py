import matplotlib.pyplot as plt
import networkx as nx

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
tiempo_disponible_por_dia_segundos = tiempo_disponible_por_dia_minutos * 60
demanda_por_dia = productos_por_semana / dias_por_semana
takt_time = tiempo_disponible_por_dia_segundos / demanda_por_dia

print("=" * 70)
print("CÁLCULO DEL TAKT TIME")
print("=" * 70)
print(f"Productos a fabricar por semana: {productos_por_semana} uni/semana")
print(f"Días laborales por semana: {dias_por_semana} días")
print(f"Horas laborales por día: {horas_por_dia} horas")
print(f"Tiempo de descanso: {tiempo_descanso_minutos} minutos/día")
print(f"Tiempo disponible por día: {tiempo_disponible_por_dia_minutos} minutos")
print(f"Tiempo disponible por día: {tiempo_disponible_por_dia_segundos} segundos")
print(f"Demanda por día: {demanda_por_dia:.0f} uni/día")
print(f"\nTAKT TIME = {takt_time:.2f} segundos/unidad")

# =============================================
# ASIGNACIÓN MANUAL SEGÚN EL MÓDULO (Páginas 54-58)
# =============================================

tiempos = {
    'A': 15, 'B': 50, 'C': 60, 'D': 45, 'E': 30,
    'F': 12, 'G': 65, 'H': 10, 'I': 8, 'J': 15, 'K': 5
}

# Asignación exacta del módulo
estaciones = [
    {'estacion': 1, 'tareas': ['A', 'B'], 'tiempo_total': 65},
    {'estacion': 2, 'tareas': ['D', 'E', 'H'], 'tiempo_total': 85},
    {'estacion': 3, 'tareas': ['C', 'F', 'I'], 'tiempo_total': 80},
    {'estacion': 4, 'tareas': ['G', 'J', 'K'], 'tiempo_total': 85}
]

# =============================================
# CÁLCULOS CORREGIDOS SEGÚN EL MÓDULO
# =============================================

tiempo_total = sum(tiempos.values())
tiempo_ciclo = max(est['tiempo_total'] for est in estaciones)  # 85 segundos (estación más lenta)

# CORRECCIÓN: Capacidad se calcula con tiempo de ciclo real, no con Takt Time
capacidad_produccion = tiempo_disponible_por_dia_segundos / tiempo_ciclo

# CORRECCIÓN: Eficiencia se calcula con tiempo de ciclo real
eficiencia_general = (tiempo_total / (len(estaciones) * tiempo_ciclo)) * 100

print("\n" + "=" * 70)
print("BALANCE DE LÍNEA - ASIGNACIÓN DE ESTACIONES")
print("=" * 70)
print(f"Número de estaciones: {len(estaciones)}")
print(f"Tiempo de ciclo real (estación más lenta): {tiempo_ciclo} s")

for est in estaciones:
    tareas_str = " + ".join([f"{t}({tiempos[t]}s)" for t in est['tareas']])
    eficiencia_estacion = (est['tiempo_total'] / takt_time) * 100
    print(f"\nEstación {est['estacion']}:")
    print(f"  Tareas: {tareas_str}")
    print(f"  Tiempo total: {est['tiempo_total']} s")
    print(f"  Tiempo ocioso: {takt_time - est['tiempo_total']} s")
    print(f"  Eficiencia estación: {eficiencia_estacion:.1f}%")

print("\n" + "=" * 70)
print("MÉTRICAS FINALES DEL BALANCE")
print("=" * 70)
print(f"Tiempo total de todas las tareas: {tiempo_total} s")
print(f"Takt Time: {takt_time:.2f} s/unidad")
print(f"Tiempo de ciclo real: {tiempo_ciclo} s")
print(f"Número de estaciones: {len(estaciones)}")
print(f"Eficiencia general: {eficiencia_general:.1f}%")
print(f"Capacidad de producción: {capacidad_produccion:.0f} unidades por día")
print(f"Demanda requerida: {demanda_por_dia:.0f} unidades por día")

# Verificar si cumple con la demanda
if capacidad_produccion >= demanda_por_dia:
    print("✅ La línea SÍ cumple con la demanda requerida")
else:
    print("❌ La línea NO cumple con la demanda requerida")

# =============================================
# VISUALIZACIÓN DEL DIAGRAMA DE PRECEDENCIA
# =============================================

plt.figure(figsize=(14, 8))

precedencias = {
    'A': [], 'B': ['A'], 'C': ['B'], 'D': [], 'E': ['D'], 
    'F': ['C'], 'G': ['C'], 'H': ['E'], 'I': ['E'], 
    'J': ['F', 'G', 'H', 'I'], 'K': ['J']
}

G = nx.DiGraph()
for tarea, predecesores in precedencias.items():
    G.add_node(tarea, tiempo=tiempos[tarea])
    for predecesor in predecesores:
        G.add_edge(predecesor, tarea)

# Layout organizado
pos = {
    'A': (0, 2), 'D': (0, 0),
    'B': (2, 2), 'E': (2, 0),
    'C': (4, 2), 'H': (4, 0.5), 'I': (4, -0.5),
    'F': (6, 2.5), 'G': (6, 1.5),
    'J': (8, 1), 'K': (10, 1)
}

node_colors = ['lightblue' for _ in G.nodes()]
nx.draw_networkx_nodes(G, pos, node_size=2000, node_color=node_colors, 
                      edgecolors='black', linewidths=2)
nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=20, 
                      edge_color='gray', width=2)
labels = {node: f"{node}\n({tiempos[node]}s)" for node in G.nodes()}
nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight='bold')

plt.title("DIAGRAMA DE PRECEDENCIA - ASSEMBLY LINE BALANCING (SALBP-1)", 
          fontsize=16, fontweight='bold')
plt.axis('off')
plt.tight_layout()
plt.show()

# =============================================
# GRÁFICA DE RESULTADOS
# =============================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Gráfica de tiempos por estación
estaciones_nums = [f"Estación {est['estacion']}" for est in estaciones]
tiempos_estaciones = [est['tiempo_total'] for est in estaciones]
colores = ['lightblue' if tiempo <= takt_time else 'lightcoral' for tiempo in tiempos_estaciones]

bars = ax1.bar(estaciones_nums, tiempos_estaciones, color=colores, edgecolor='black')
ax1.axhline(y=takt_time, color='red', linestyle='--', linewidth=2, label=f'Takt Time ({takt_time} s)')
ax1.axhline(y=tiempo_ciclo, color='green', linestyle='--', linewidth=2, label=f'Tiempo Ciclo Real ({tiempo_ciclo} s)')
ax1.set_ylabel('Tiempo (segundos)')
ax1.set_title('COMPARACIÓN: TIEMPO POR ESTACIÓN vs TAKT TIME', fontweight='bold')
ax1.legend()

# Añadir valores en las barras
for bar, tiempo in zip(bars, tiempos_estaciones):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
             f'{tiempo}s', ha='center', va='bottom', fontweight='bold')

# Tabla de métricas
ax2.axis('off')
metricas_data = [
    ["Métrica", "Valor"],
    ["Takt Time", f"{takt_time:.2f} s/uni"],
    ["Tiempo Ciclo Real", f"{tiempo_ciclo} s/uni"],
    ["Tiempo Total Tareas", f"{tiempo_total} s"],
    ["Número de Estaciones", f"{len(estaciones)}"],
    ["Eficiencia General", f"{eficiencia_general:.1f}%"],
    ["Capacidad Producción", f"{capacidad_produccion:.0f} uni/día"],
    ["Demanda Requerida", f"{demanda_por_dia:.0f} uni/día"]
]

metricas_table = ax2.table(cellText=metricas_data, cellLoc='center', loc='center', 
                          colWidths=[0.6, 0.4])
metricas_table.auto_set_font_size(False)
metricas_table.set_fontsize(10)
metricas_table.scale(1, 1.5)

for i in range(len(metricas_data)):
    for j in range(len(metricas_data[0])):
        cell = metricas_table[i, j]
        if i == 0:
            cell.set_facecolor('#4CAF50')
            cell.set_text_props(weight='bold', color='white')
        else:
            cell.set_facecolor('#E3F2FD')
        cell.set_edgecolor('black')

ax2.set_title('MÉTRICAS DEL BALANCE - SALBP-1', fontweight='bold')

plt.suptitle('ASSEMBLY LINE BALANCING (SALBP-1) - RESULTADOS SEGÚN MÓDULO', 
             fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()

# =============================================
# TABLA DETALLADA DE ASIGNACIÓN
# =============================================

print("\n" + "=" * 70)
print("DETALLE DE ASIGNACIÓN POR ESTACIÓN")
print("=" * 70)
print(f"{'Estación':<12} {'Tareas':<20} {'Tiempo (s)':<12} {'Eficiencia':<12} {'Tiempo Ocioso':<15}")
print("-" * 70)

for est in estaciones:
    tareas_str = " + ".join(est['tareas'])
    eficiencia_estacion = (est['tiempo_total'] / takt_time) * 100
    tiempo_ocioso = takt_time - est['tiempo_total']
    estacion_str = f"Estación {est['estacion']}"
    eficiencia_str = f"{eficiencia_estacion:.1f}%"
    print(f"{estacion_str:<12} {tareas_str:<20} {est['tiempo_total']:<12} {eficiencia_str:<12} {tiempo_ocioso:<15}")

print("-" * 70)
eficiencia_general_str = f"{eficiencia_general:.1f}%"
print(f"{'TOTAL':<12} {'11 tareas':<20} {tiempo_total:<12} {eficiencia_general_str:<12} {'':<15}")

# =============================================
# EXPLICACIÓN DE LA DIFERENCIA
# =============================================

print("\n" + "=" * 70)
print("EXPLICACIÓN DE LA DIFERENCIA EN CÁLCULOS")
print("=" * 70)
print("📌 En el módulo usan el TIEMPO DE CICLO REAL (85 segundos) para calcular:")
print("   - Capacidad de producción = Tiempo disponible / Tiempo de ciclo real")
print(f"   - 27,000 s/día / 85 s/uni = 318 uni/día")
print("\n📌 No usan el TAKT TIME (90 segundos) porque la línea puede producir más rápido")
print("   que lo requerido por el cliente")
print("\n📌 La eficiencia se calcula respecto al tiempo de ciclo real:")
print(f"   - Eficiencia = Tiempo total / (Estaciones × Tiempo ciclo real)")
print(f"   - 315 / (4 × 85) = 315 / 340 = 92.6%")