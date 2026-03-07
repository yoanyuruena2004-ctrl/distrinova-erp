import pandas as pd
import numpy as np
import pulp
import time
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ============================================================
# PUNTO B - VERSIÓN CON DIAGRAMA DE GANTT GRÁFICO
# ============================================================

print("PUNTO B - SOLUCIÓN ÓPTIMA CON DIAGRAMA DE GANTT")
print("=" * 70)

start_time = time.time()

# Datos
jobs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
processing_times = [3, 30, 24, 6, 12, 9, 18, 21, 27, 15]
batch_sizes = [10, 3, 5, 20, 10, 5, 6, 12, 4, 20]
machines = ['M1', 'M2', 'M3', 'M4']
v_ampl = [1, 1, 1.5, 2]

print("Resolviendo con alta precisión...")

# Modelo
model = pulp.LpProblem("Punto_B_Exacto", pulp.LpMinimize)

# Variables
Cmax = pulp.LpVariable("Cmax", lowBound=0, cat='Continuous')
X = pulp.LpVariable.dicts("X", [(j, m) for j in jobs for m in machines], lowBound=0, cat='Integer')

# Función objetivo
model += Cmax

# Restricciones
for i, machine in enumerate(machines):
    machine_time = pulp.lpSum([processing_times[j-1] * X[(j, machine)] for j in jobs])
    model += machine_time <= Cmax * v_ampl[i]

for j in jobs:
    model += pulp.lpSum([X[(j, m)] for m in machines]) == batch_sizes[j-1]

# SOLVER CON MÁXIMA PRECISIÓN
solver = pulp.PULP_CBC_CMD(
    timeLimit=120,      # 2 minutos máximo
    msg=False,          # Silenciar para más rapidez
    gapRel=0.0001       # Brecha del 0.01% (MUY precisa)
)

print("Buscando solución exacta...")
model.solve(solver)

end_time = time.time()
execution_time = end_time - start_time

print(f"\n" + "=" * 70)
print(f"TIEMPO DE EJECUCIÓN: {execution_time:.2f} segundos")
print("=" * 70)

print(f"Estado: {pulp.LpStatus[model.status]}")
if pulp.LpStatus[model.status] == "Optimal":
    print(f"✅ SOLUCIÓN ÓPTIMA ENCONTRADA")
    print(f"Cmax: {pulp.value(Cmax):.0f} horas")
else:
    print(f"Cmax encontrado: {pulp.value(Cmax):.0f} horas")

# ============================================================
# CALCULAR SECUENCIACIÓN PARA GANTT
# ============================================================

print(f"\nCALCULANDO SECUENCIACIÓN PARA DIAGRAMA DE GANTT...")

completion_times = {}
machine_assignments = {}

for machine in machines:
    machine_jobs = []
    machine_idx = machines.index(machine)
    v_rel = v_ampl[machine_idx]
    
    for j in jobs:
        quantity = pulp.value(X[(j, machine)])
        if quantity > 0.1:
            total_time = (processing_times[j-1] * quantity) / v_rel
            machine_jobs.append((j, quantity, total_time))
    
    if machine_jobs:
        # Ordenar por tiempo (SPT)
        machine_jobs.sort(key=lambda x: x[2])
        
        current_time = 0
        job_times = []
        for job, quantity, job_time in machine_jobs:
            completion_time = current_time + job_time
            job_times.append((job, quantity, current_time, completion_time))
            current_time = completion_time
        
        completion_times[machine] = job_times
        machine_assignments[machine] = machine_jobs

# ============================================================
# CREAR DIAGRAMA DE GANTT GRÁFICO
# ============================================================

print(f"\nGENERANDO DIAGRAMA DE GANTT GRÁFICO...")

# Configurar la figura
fig, ax = plt.subplots(figsize=(14, 8))

# Colores para cada trabajo
colors = plt.cm.tab10(np.linspace(0, 1, len(jobs)))

# Dibujar las barras para cada máquina
for i, machine in enumerate(machines):
    if machine in completion_times:
        for job, quantity, start, end in completion_times[machine]:
            # Crear la barra horizontal
            ax.barh(machine, end - start, left=start, height=0.6, 
                   color=colors[job-1], edgecolor='black', alpha=0.8,
                   label=f'J{job}' if i == 0 else "")
            
            # Añadir etiqueta en el centro de la barra
            ax.text((start + end) / 2, i, f'J{job}\n({quantity} und)', 
                   ha='center', va='center', fontweight='bold', fontsize=8)

# Configurar el gráfico
ax.set_xlabel('Tiempo (horas)', fontsize=12, fontweight='bold')
ax.set_ylabel('Máquinas', fontsize=12, fontweight='bold')
ax.set_title('DIAGRAMA DE GANTT - PUNTO B (CON BATCH)\nCmax Óptimo: 236 horas', 
             fontsize=14, fontweight='bold', pad=20)

# Configurar ejes
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

# Añadir leyenda
handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys(), 
          title='Trabajos', bbox_to_anchor=(1.05, 1), loc='upper left')

# Ajustar layout
plt.tight_layout()

# Guardar la imagen
nombre_archivo = f"Gantt_PuntoB_Cmax_{pulp.value(Cmax):.0f}horas.png"
plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✅ Diagrama de Gantt guardado como: {nombre_archivo}")

# Mostrar el gráfico
plt.show()

# ============================================================
# RESULTADOS EN TEXTO (como antes)
# ============================================================

if pulp.LpStatus[model.status] in ["Optimal", "Feasible"]:
    print(f"\nASIGNACIÓN ÓPTIMA:")
    print(f"{'Máquina':<8} | {'Asignaciones':<50} | {'Tiempo':>8}")
    print("-" * 85)

    for i, machine in enumerate(machines):
        assignments = []
        total_processing = 0
        
        for j in jobs:
            quantity = pulp.value(X[(j, machine)])
            if quantity > 0.1:
                time_contribution = processing_times[j-1] * quantity
                assignments.append(f"J{j}({quantity:.0f}und)")
                total_processing += time_contribution
        
        if assignments:
            assignments_str = " + ".join(assignments)
            real_time = total_processing / v_ampl[i] if v_ampl[i] > 0 else 0
            print(f"{machine:<8} | {assignments_str:<50} | {real_time:>8.1f}h")

    # Verificación
    print(f"\nVERIFICACIÓN:")
    total_correct = 0
    for j in jobs:
        job_total = sum(pulp.value(X[(j, m)]) for m in machines)
        status = "✅" if abs(job_total - batch_sizes[j-1]) < 0.1 else "❌"
        if status == "✅":
            total_correct += 1
        print(f"J{j}: {job_total:.0f}/{batch_sizes[j-1]} {status}")

# ============================================================
# DIAGRAMA DE GANTT EN TEXTO (como respaldo)
# ============================================================

print(f"\n" + "=" * 70)
print("DIAGRAMA DE GANTT (Versión Texto)")
print("=" * 70)

for machine in machines:
    if machine in completion_times and completion_times[machine]:
        total_time = completion_times[machine][-1][3]
        print(f"\n{machine} ({total_time:.1f}h):")
        
        current_pos = 0
        for job, quantity, start, end in completion_times[machine]:
            duration = end - start
            bar_length = max(1, int(duration / 5))
            
            spaces_before = int(start / 5) - current_pos
            if spaces_before > 0:
                print(" " * spaces_before, end="")
            
            bar = "█" * bar_length
            print(f"[J{job}:{bar}]", end="")
            current_pos = int(start / 5) + bar_length + 2

# ============================================================
# RESUMEN FINAL
# ============================================================

ampl_cmax = 236
python_cmax = pulp.value(Cmax) if pulp.LpStatus[model.status] in ["Optimal", "Feasible"] else 0
diferencia = abs(python_cmax - ampl_cmax)

print(f"\n\n" + "=" * 70)
print("RESUMEN FINAL")
print("=" * 70)
print(f"⏱️  Tiempo ejecución: {execution_time:.1f} segundos")
print(f"🎯 Cmax encontrado: {python_cmax:.0f} horas")
print(f"📊 Diferencia con AMPL: {diferencia:.1f} horas")
print(f"✅ Lotes correctos: {total_correct}/{len(jobs)}")
print(f"📈 Diagrama de Gantt: {nombre_archivo}")
print(f"🚀 Precisión: gapRel=0.0001 (0.01%)")

print(f"\n¡PROGRAMA COMPLETADO EXITOSAMENTE! 🎉")