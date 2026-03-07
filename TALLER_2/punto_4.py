import pandas as pd
import numpy as np
import pulp
import matplotlib.pyplot as plt

# ============================================================
# PUNTO 4 - MÁQUINAS NO RELACIONADAS EN PARALELO
# ============================================================

print("TALLER MÓDULO 2 - PUNTO 4 COMPLETO")
print("=" * 70)

# --------------------------
# DATOS DEL PROBLEMA
# --------------------------
jobs = [1, 2, 3, 4, 5, 6]
machines = ['M1', 'M2', 'M3', 'M4', 'M5']

# Tiempos de ciclo (minutos/unidad) - Matriz Pjm
Pjm = {
    (1, 'M1'): 10, (1, 'M2'): 10, (1, 'M3'): 15, (1, 'M4'): 20, (1, 'M5'): 15,
    (2, 'M1'): 10, (2, 'M2'): 15, (2, 'M3'): 15, (2, 'M4'): 20, (2, 'M5'): 10,
    (3, 'M1'): 5,  (3, 'M2'): 10, (3, 'M3'): 5,  (3, 'M4'): 10, (3, 'M5'): 10,
    (4, 'M1'): 10, (4, 'M2'): 15, (4, 'M3'): 15, (4, 'M4'): 15, (4, 'M5'): 10,
    (5, 'M1'): 5,  (5, 'M2'): 5,  (5, 'M3'): 10, (5, 'M4'): 15, (5, 'M5'): 15,
    (6, 'M1'): 20, (6, 'M2'): 25, (6, 'M3'): 25, (6, 'M4'): 30, (6, 'M5'): 25
}

batch_sizes = {1: 50, 2: 30, 3: 40, 4: 60, 5: 20, 6: 10}

print("DATOS DE TIEMPOS DE CICLO (minutos/unidad):")
print(f"{'Job/Maq':<8}", end="")
for machine in machines:
    print(f" | {machine:>6}", end="")
print("\n" + "-" * 55)

for j in jobs:
    print(f"Job {j:<6}", end="")
    for machine in machines:
        print(f" | {Pjm[(j, machine)]:>6}", end="")
    print(f" | Batch: {batch_sizes[j]}")

# ============================================================
# PARTE A: SIN CONSIDERAR BATCH
# ============================================================

print(f"\n" + "=" * 70)
print("PARTE A: MODELO EXACTO SIN CONSIDERAR BATCH")
print("=" * 70)

model_a = pulp.LpProblem("Punto4A_Sin_Batch", pulp.LpMinimize)

# Variables
Cmax_a = pulp.LpVariable("Cmax_a", lowBound=0, cat='Continuous')
X_a = pulp.LpVariable.dicts("X_a", [(j, m) for j in jobs for m in machines], cat='Binary')

# Función objetivo
model_a += Cmax_a

# Restricciones
for machine in machines:
    machine_time = pulp.lpSum([Pjm[(j, machine)] * X_a[(j, machine)] for j in jobs])
    model_a += machine_time <= Cmax_a, f"Capacidad_A_{machine}"

for j in jobs:
    model_a += pulp.lpSum([X_a[(j, m)] for m in machines]) == 1, f"Asignacion_A_{j}"

# Resolver
print("Resolviendo Parte A...")
model_a.solve(pulp.PULP_CBC_CMD(msg=False))

print(f"✅ Cmax óptimo (sin batch): {pulp.value(Cmax_a):.0f} minutos")

# Procesar resultados Parte A
assignments_a = {}
completion_times_a = {}

for machine in machines:
    assigned_jobs = [j for j in jobs if pulp.value(X_a[(j, machine)]) > 0.5]
    if assigned_jobs:
        # Ordenar por tiempo de ciclo
        assigned_jobs.sort(key=lambda j: Pjm[(j, machine)])
        
        current_time = 0
        job_times = []
        for job in assigned_jobs:
            proc_time = Pjm[(job, machine)]
            completion_time = current_time + proc_time
            job_times.append((job, current_time, completion_time))
            current_time = completion_time
        
        assignments_a[machine] = assigned_jobs
        completion_times_a[machine] = job_times

# Mostrar resultados Parte A
print(f"\nASIGNACIÓN PARTE A:")
print(f"{'Máquina':<8} | {'Trabajos':<35} | {'Tiempo':>8}")
print("-" * 75)
for machine in machines:
    if machine in assignments_a:
        jobs_str = " → ".join(f"J{j}" for j in assignments_a[machine])
        total_time = completion_times_a[machine][-1][2] if completion_times_a[machine] else 0
        print(f"{machine:<8} | {jobs_str:<35} | {total_time:>8.0f}m")
    else:
        print(f"{machine:<8} | {'Sin asignación':<35} | {'0':>8}m")

# ============================================================
# PARTE B: CONSIDERANDO BATCH
# ============================================================

print(f"\n" + "=" * 70)
print("PARTE B: MODELO EXACTO CONSIDERANDO BATCH")
print("=" * 70)

model_b = pulp.LpProblem("Punto4B_Con_Batch", pulp.LpMinimize)

# Variables
Cmax_b = pulp.LpVariable("Cmax_b", lowBound=0, cat='Continuous')
X_b = pulp.LpVariable.dicts("X_b", [(j, m) for j in jobs for m in machines], lowBound=0, cat='Integer')

# Función objetivo
model_b += Cmax_b

# Restricciones
for machine in machines:
    machine_time = pulp.lpSum([Pjm[(j, machine)] * X_b[(j, machine)] for j in jobs])
    model_b += machine_time <= Cmax_b, f"Capacidad_B_{machine}"

for j in jobs:
    model_b += pulp.lpSum([X_b[(j, m)] for m in machines]) == batch_sizes[j], f"Lote_Completo_{j}"

# Resolver
print("Resolviendo Parte B...")
model_b.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=120, gapRel=0.01))

print(f"✅ Cmax óptimo (con batch): {pulp.value(Cmax_b):.0f} minutos")

# Procesar resultados Parte B
assignments_b = {}
completion_times_b = {}

for machine in machines:
    machine_assignments = []
    for j in jobs:
        quantity = pulp.value(X_b[(j, machine)])
        if quantity > 0.1:
            total_time = Pjm[(j, machine)] * quantity
            machine_assignments.append((j, quantity, total_time))
    
    if machine_assignments:
        # Ordenar por tiempo total
        machine_assignments.sort(key=lambda x: x[2])
        
        current_time = 0
        job_times = []
        for job, quantity, job_time in machine_assignments:
            completion_time = current_time + job_time
            job_times.append((job, quantity, current_time, completion_time))
            current_time = completion_time
        
        assignments_b[machine] = machine_assignments
        completion_times_b[machine] = job_times

# Mostrar resultados Parte B
print(f"\nASIGNACIÓN PARTE B:")
print(f"{'Máquina':<8} | {'Asignaciones':<45} | {'Tiempo':>8}")
print("-" * 85)
for machine in machines:
    if machine in assignments_b:
        assignments_str = " + ".join([f"J{j}({q}und)" for j, q, _ in assignments_b[machine]])
        total_time = completion_times_b[machine][-1][3] if completion_times_b[machine] else 0
        print(f"{machine:<8} | {assignments_str:<45} | {total_time:>8.0f}m")
    else:
        print(f"{machine:<8} | {'Sin asignación':<45} | {'0':>8}m")

# ============================================================
# DIAGRAMAS DE GANTT
# ============================================================

print(f"\n" + "=" * 70)
print("GENERANDO DIAGRAMAS DE GANTT")
print("=" * 70)

# Crear figura con dos subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
colors = plt.cm.Set3(np.linspace(0, 1, len(jobs)))

# Diagrama Gantt Parte A
for i, machine in enumerate(machines):
    if machine in completion_times_a:
        for job, start, end in completion_times_a[machine]:
            ax1.barh(machine, end-start, left=start, height=0.6, 
                    color=colors[job-1], edgecolor='black', alpha=0.8)
            ax1.text((start+end)/2, i, f'J{job}', ha='center', va='center', 
                    fontweight='bold', fontsize=9)

ax1.set_xlabel('Tiempo (minutos)')
ax1.set_ylabel('Máquinas')
ax1.set_title('PARTE A: Diagrama de Gantt - Sin Considerar Batch')
ax1.grid(True, alpha=0.3)

# Diagrama Gantt Parte B
for i, machine in enumerate(machines):
    if machine in completion_times_b:
        for job, quantity, start, end in completion_times_b[machine]:
            ax2.barh(machine, end-start, left=start, height=0.6, 
                    color=colors[job-1], edgecolor='black', alpha=0.8)
            ax2.text((start+end)/2, i, f'J{job}\n({quantity}und)', 
                    ha='center', va='center', fontweight='bold', fontsize=7)

ax2.set_xlabel('Tiempo (minutos)')
ax2.set_ylabel('Máquinas')
ax2.set_title('PARTE B: Diagrama de Gantt - Considerando Batch')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('Punto4_Completo_Gantt.png', dpi=300, bbox_inches='tight')
plt.show()

print(f"✅ Diagramas de Gantt guardados como 'Punto4_Completo_Gantt.png'")

# ============================================================
# ANÁLISIS COMPARATIVO
# ============================================================

print(f"\n" + "=" * 70)
print("ANÁLISIS COMPARATIVO")
print("=" * 70)

total_units = sum(batch_sizes.values())
units_per_minute_a = len(jobs) / pulp.value(Cmax_a) if pulp.value(Cmax_a) > 0 else 0
units_per_minute_b = total_units / pulp.value(Cmax_b) if pulp.value(Cmax_b) > 0 else 0

print(f"COMPARACIÓN:")
print(f"{'Métrica':<25} | {'Parte A':<12} | {'Parte B':<12}")
print("-" * 55)
print(f"{'Cmax (minutos)':<25} | {pulp.value(Cmax_a):<12.0f} | {pulp.value(Cmax_b):<12.0f}")
print(f"{'Volumen producido':<25} | {len(jobs):<12} | {total_units:<12}")
print(f"{'Unidades/minuto':<25} | {units_per_minute_a:<12.3f} | {units_per_minute_b:<12.3f}")
print(f"{'Tiempo total producción':<25} | {pulp.value(Cmax_a):<12.0f} | {pulp.value(Cmax_b):<12.0f}")

# Verificación de lotes Parte B
print(f"\nVERIFICACIÓN PARTE B:")
total_correct = 0
for j in jobs:
    job_total = sum(pulp.value(X_b[(j, m)]) for m in machines)
    status = "✅" if abs(job_total - batch_sizes[j]) < 0.1 else "❌"
    if status == "✅":
        total_correct += 1
    print(f"J{j}: {job_total:.0f}/{batch_sizes[j]} {status}")

# ============================================================
# EXPORTACIÓN DE RESULTADOS
# ============================================================

try:
    # DataFrames para exportación
    df_parte_a = pd.DataFrame({
        'Trabajo': jobs,
        'Maquina_Asignada': [next((m for m in machines if pulp.value(X_a[(j, m)]) > 0.5), '?') for j in jobs],
        'Tiempo_Ciclo_Asignado': [Pjm[(j, next((m for m in machines if pulp.value(X_a[(j, m)]) > 0.5), '?'))] for j in jobs]
    })
    
    df_parte_b = pd.DataFrame({
        'Trabajo': jobs,
        'Batch_Size': [batch_sizes[j] for j in jobs],
        'Asignado_M1': [pulp.value(X_b[(j, 'M1')]) for j in jobs],
        'Asignado_M2': [pulp.value(X_b[(j, 'M2')]) for j in jobs],
        'Asignado_M3': [pulp.value(X_b[(j, 'M3')]) for j in jobs],
        'Asignado_M4': [pulp.value(X_b[(j, 'M4')]) for j in jobs],
        'Asignado_M5': [pulp.value(X_b[(j, 'M5')]) for j in jobs],
        'Total_Asignado': [sum(pulp.value(X_b[(j, m)]) for m in machines) for j in jobs]
    })
    
    df_comparacion = pd.DataFrame({
        'Metrica': ['Cmax (minutos)', 'Volumen_Produccion', 'Unidades_Minuto', 'Lotes_Correctos'],
        'Parte_A': [pulp.value(Cmax_a), len(jobs), units_per_minute_a, len(jobs)],
        'Parte_B': [pulp.value(Cmax_b), total_units, units_per_minute_b, total_correct]
    })
    
    # Exportar a Excel
    out_xlsx = "Punto4_Completo_Resultados.xlsx"
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        df_parte_a.to_excel(writer, index=False, sheet_name="Parte_A_Sin_Batch")
        df_parte_b.to_excel(writer, index=False, sheet_name="Parte_B_Con_Batch")
        df_comparacion.to_excel(writer, index=False, sheet_name="Comparacion")
    
    print(f"\n✅ Resultados exportados a {out_xlsx}")
    
except Exception as e:
    print(f"\n⚠️ Error en exportación: {e}")

print(f"\n" + "=" * 70)
print("RESUMEN FINAL - PUNTO 4")
print("=" * 70)
print(f"🎯 PARTE A: Cmax = {pulp.value(Cmax_a):.0f} minutos (sin batch)")
print(f"🎯 PARTE B: Cmax = {pulp.value(Cmax_b):.0f} minutos (con batch)")
print(f"📊 Volumen total: {total_units} unidades")
print(f"✅ Lotes correctos: {total_correct}/{len(jobs)}")
print(f"📈 Diagramas de Gantt generados")
print(f"📁 Resultados exportados a Excel")