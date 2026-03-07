import pandas as pd
import numpy as np
from itertools import product
import pulp

# ============================
# Datos del problema Pm||Cmax
# ============================
jobs = [1, 2, 3, 4, 5, 6, 7, 8]
pj = [6, 15, 8, 10, 14, 5, 12, 16]
num_machines = 3

print("PROBLEMA: Pm||Cmax - MODELO EXACTO")
print("FO: Min Z = C")
print("s.a.:")
print("   ∑ pj·Xjm ≤ C, ∀ m ∈ M")
print("   ∑ Xjm = 1, ∀ j ∈ J") 
print("   Xjm ∈ {0,1}")
print("=" * 70)

# ============================
# Crear el modelo de optimización
# ============================
model = pulp.LpProblem("Pm_Cmax_Minimization", pulp.LpMinimize)

# ============================
# Variables de decisión
# ============================
# Variable continua para el makespan
C = pulp.LpVariable("C", lowBound=0, cat='Continuous')

# Variables binarias para asignación de trabajos a máquinas
X = pulp.LpVariable.dicts("X", 
                         [(j, m) for j in jobs for m in range(1, num_machines + 1)],
                         cat='Binary')

print(f"Se crearon {len(X)} variables binarias de asignación")
print(f"Se creó 1 variable continua para Cmax")

# ============================
# Función objetivo
# ============================
model += C, "Minimizar_Makespan"

# ============================
# Restricciones
# ============================
print(f"\nAGREGANDO RESTRICCIONES:")

# Restricción 1: El tiempo total en cada máquina no puede exceder C
for m in range(1, num_machines + 1):
    machine_load = pulp.lpSum([pj[j-1] * X[(j, m)] for j in jobs])
    model += machine_load <= C, f"Machine_{m}_Load"
    print(f"  Máquina {m}: ∑ pj·Xj{m} ≤ C")

# Restricción 2: Cada trabajo debe asignarse exactamente a una máquina
for j in jobs:
    assignment_constraint = pulp.lpSum([X[(j, m)] for m in range(1, num_machines + 1)]) == 1
    model += assignment_constraint, f"Job_{j}_Assignment"
    print(f"  Trabajo {j}: ∑ Xj· = 1")

# ============================
# Resolver el modelo
# ============================
print(f"\nRESOLVIENDO EL MODELO...")
print("=" * 70)

# Configurar el solver (usando CBC que viene con pulp)
solver = pulp.PULP_CBC_CMD(msg=True, timeLimit=30)
model.solve(solver)

# ============================
# Mostrar resultados
# ============================
print(f"\n" + "=" * 70)
print("RESULTADOS DEL MODELO EXACTO")
print("=" * 70)

print(f"Estado: {pulp.LpStatus[model.status]}")
print(f"Valor óptimo de Cmax: {pulp.value(C):.2f}")

# ============================
# Recuperar la asignación óptima
# ============================
machines = [[] for _ in range(num_machines)]
machine_times = [0] * num_machines
completion_times = {}

print(f"\nASIGNACIÓN ÓPTIMA ENCONTRADA:")
print(f"{'Máquina':>8} | {'Trabajos':<20} | {'Carga Total':>12}")
print("-" * 55)

for m in range(1, num_machines + 1):
    machine_jobs = []
    machine_load = 0
    
    for j in jobs:
        if pulp.value(X[(j, m)]) > 0.5:  # Variable binaria = 1
            machine_jobs.append(j)
            machine_load += pj[j-1]
    
    machines[m-1] = machine_jobs
    machine_times[m-1] = machine_load
    
    jobs_str = " → ".join(f"J{j}({pj[j-1]})" for j in machine_jobs)
    print(f"M{m:7} | {jobs_str:<20} | {machine_load:12}")

# ============================
# Calcular métricas adicionales
# ============================
optimal_Cmax = pulp.value(C)
total_processing = sum(pj)
min_theoretical = total_processing / num_machines
utilization = total_processing / (optimal_Cmax * num_machines) * 100
balance_ratio = max(machine_times) / min(machine_times)

print(f"\nMÉTRICAS DE LA SOLUCIÓN ÓPTIMA:")
print(f"Cmax óptimo: {optimal_Cmax:.2f}")
print(f"Tiempo total de procesamiento: {total_processing}")
print(f"Cmax teórico mínimo: {min_theoretical:.2f}")
print(f"Utilización promedio: {utilization:.1f}%")
print(f"Ratio de balance: {balance_ratio:.3f}")

# ============================
# Comparación con LPT (heurístico)
# ============================
print(f"\n" + "=" * 70)
print("COMPARACIÓN CON ALGORITMO LPT (HEURÍSTICO)")
print("=" * 70)

# Calcular solución LPT para comparar
job_data = list(zip(jobs, pj))
job_data_sorted = sorted(job_data, key=lambda x: x[1], reverse=True)

lpt_machines = [[] for _ in range(num_machines)]
lpt_times = [0] * num_machines

for job, process_time in job_data_sorted:
    min_time = min(lpt_times)
    machine_index = lpt_times.index(min_time)
    lpt_machines[machine_index].append(job)
    lpt_times[machine_index] += process_time

lpt_Cmax = max(lpt_times)
lpt_ratio = lpt_Cmax / optimal_Cmax

print(f"Cmax LPT: {lpt_Cmax}")
print(f"Cmax Óptimo: {optimal_Cmax}")
print(f"Ratio LPT/Óptimo: {lpt_ratio:.3f}")
print(f"LPT es {((lpt_ratio - 1) * 100):.1f}% peor que el óptimo")

# ============================
# Análisis de optimalidad
# ============================
print(f"\nANÁLISIS DE OPTIMALIDAD:")
if abs(optimal_Cmax - min_theoretical) < 1e-6:
    print("✓ SOLUCIÓN ÓPTIMA GLOBAL ENCONTRADA")
    print("✓ El makespan alcanza el límite teórico inferior")
else:
    print("✓ SOLUCIÓN ÓPTIMA ENCONTRADA")
    print(f"  Brecha con límite teórico: {optimal_Cmax - min_theoretical:.2f}")

# ============================
# Crear DataFrames para exportación
# ============================
df_assignment = pd.DataFrame({
    'Trabajo': jobs,
    'Pj': pj,
    'Máquina Asignada': [f"M{next((m for m in range(1, num_machines+1) if pulp.value(X[(j, m)]) > 0.5), '?')}" for j in jobs]
})

df_machines = pd.DataFrame({
    'Máquina': [f'M{i+1}' for i in range(num_machines)],
    'Trabajos': [machines[i] for i in range(num_machines)],
    'Secuencia': [" → ".join(f"J{j}" for j in machines[i]) for i in range(num_machines)],
    'Carga Total': machine_times,
    'Porcentaje': [f"{(load/optimal_Cmax)*100:.1f}%" for load in machine_times]
})

metrics_comparison = {
    'Métrica': ['Cmax Óptimo', 'Cmax LPT', 'Límite Teórico', 'ΣPj', 'Utilización'],
    'Valor': [f"{optimal_Cmax:.2f}", f"{lpt_Cmax}", f"{min_theoretical:.2f}", 
              f"{total_processing}", f"{utilization:.1f}%"],
    'Ratio': ['1.000', f"{lpt_ratio:.3f}", f"{(min_theoretical/optimal_Cmax):.3f}", 
              'N/A', 'N/A']
}

# ============================
# Exportar a Excel
# ============================
try:
    out_xlsx = "Pm_Cmax_Exact_Model_Results.xlsx"
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        df_assignment.to_excel(writer, index=False, sheet_name="Asignación_Óptima")
        df_machines.to_excel(writer, index=False, sheet_name="Máquinas")
        pd.DataFrame(metrics_comparison).to_excel(writer, index=False, sheet_name="Comparación")
        
        # Agregar formulación del modelo
        model_formulation = {
            'Componente': ['Función Objetivo', 'Restricción Tipo 1', 'Restricción Tipo 2', 'Variables'],
            'Descripción': [
                'Min Z = C',
                '∑ pj·Xjm ≤ C, ∀ m ∈ M', 
                '∑ Xjm = 1, ∀ j ∈ J',
                f'Xjm binarias ({len(X)} vars) + C continua'
            ]
        }
        pd.DataFrame(model_formulation).to_excel(writer, index=False, sheet_name="Formulación")
    
    print(f"\n✅ Resultados exportados a {out_xlsx}")
except Exception as e:
    print(f"\n⚠️  No se pudo exportar a Excel: {e}")

print(f"\n" + "=" * 70)
print("DIAGRAMA DE GANTT - SOLUCIÓN ÓPTIMA")
print("=" * 70)

for i in range(num_machines):
    print(f"\nM{i+1}: ", end="")
    current_time = 0
    for job in machines[i]:
        job_time = pj[job-1]
        bar = "█" * job_time  # Cada █ representa 1 unidad de tiempo
        print(f"[J{job}:{bar:<16}]", end=" ")
    print(f"→ Total: {machine_times[i]}")

print(f"\n" + "=" * 70)
print("VERIFICACIÓN DE RESTRICCIONES:")
print("=" * 70)

# Verificar que todas las restricciones se cumplen
print("✓ Cada trabajo asignado a exactamente una máquina:")
for j in jobs:
    assigned_machines = sum(1 for m in range(1, num_machines+1) if pulp.value(X[(j, m)]) > 0.5)
    print(f"  J{j}: {assigned_machines} máquina(s) - {'✓' if assigned_machines == 1 else '✗'}")

print(f"\n✓ Carga de máquinas ≤ Cmax ({optimal_Cmax:.2f}):")
for i in range(num_machines):
    status = "✓" if machine_times[i] <= optimal_Cmax + 1e-6 else "✗"
    print(f"  M{i+1}: {machine_times[i]} ≤ {optimal_Cmax:.2f} {status}")