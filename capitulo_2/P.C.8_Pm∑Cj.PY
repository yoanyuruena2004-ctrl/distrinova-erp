import pandas as pd
import numpy as np

# ============================
# Datos del problema Pm||ΣCj
# ============================
jobs = [1, 2, 3, 4, 5, 6, 7, 8]
pj = [6, 15, 8, 10, 14, 5, 12, 16]
num_machines = 3

print("PROBLEMA: Pm||ΣCj - 3 MÁQUINAS IDÉNTICAS EN PARALELO")
print("ALGORITMO: SPT (Shortest Processing Time)")
print("=" * 60)

# ============================
# Combinar y ordenar por SPT
# ============================
job_data = list(zip(jobs, pj))
job_data_sorted = sorted(job_data, key=lambda x: x[1])  # Orden SPT

print("\nTRABAJOS ORDENADOS POR SPT:")
print(f"{'Job':>4} | {'Pj':>3}")
print("-" * 15)
for job, process in job_data_sorted:
    print(f"{job:4} | {process:3}")

# ============================
# Algoritmo SPT para máquinas paralelas
# ============================
machines = [[] for _ in range(num_machines)]  # Lista de trabajos por máquina
machine_times = [0] * num_machines  # Tiempo actual de cada máquina
completion_times = {}  # Tiempo de finalización por trabajo
schedule_log = []  # Para el registro detallado

print(f"\nASIGNACIÓN SPT A {num_machines} MÁQUINAS:")
print(f"{'Iteración':>10} | {'Job':>4} | {'Pj':>3} | {'Máquina':>8} | {'Inicio':>6} | {'Fin':>6}")

iteration = 1
for job, process_time in job_data_sorted:
    # Encontrar la máquina que termina antes
    min_time = min(machine_times)
    machine_index = machine_times.index(min_time)
    
    # Asignar trabajo a esta máquina
    start_time = machine_times[machine_index]
    completion_time = start_time + process_time
    
    machines[machine_index].append(job)
    machine_times[machine_index] = completion_time
    completion_times[job] = completion_time
    
    # Registrar la asignación
    schedule_log.append({
        'iteration': iteration,
        'job': job,
        'pj': process_time,
        'machine': f'M{machine_index + 1}',
        'start': start_time,
        'completion': completion_time
    })
    
    print(f"{iteration:10} | {job:4} | {process_time:3} | M{machine_index + 1:7} | {start_time:6} | {completion_time:6}")
    
    iteration += 1

# ============================
# Calcular métricas
# ============================
Cmax = max(machine_times)
SumCj = sum(completion_times.values())
F_bar = SumCj / len(jobs)

# ============================
# Mostrar resultados finales
# ============================
print(f"\n" + "=" * 60)
print("RESULTADOS FINALES")
print("=" * 60)

print(f"\nASIGNACIÓN POR MÁQUINA:")
for i in range(num_machines):
    machine_jobs = machines[i]
    machine_sequence = " → ".join(f"J{j}" for j in machine_jobs)
    print(f"M{i+1}: {machine_sequence} | Cmax = {machine_times[i]}")

print(f"\nTIEMPOS DE FINALIZACIÓN POR TRABAJO:")
print(f"{'Job':>4} | {'Pj':>3} | {'Cj':>3}")
print("-" * 20)
for job in jobs:
    print(f"{job:4} | {pj[job-1]:3} | {completion_times[job]:3}")

print(f"\nMÉTRICAS GLOBALES:")
print(f"Cmax (Makespan): {Cmax}")
print(f"ΣCj (Suma de tiempos de finalización): {SumCj}")
print(f"F̅ (Tiempo de flujo promedio): {F_bar:.2f}")

# ============================
# Análisis de eficiencia
# ============================
total_processing = sum(pj)
min_possible_Cmax = total_processing / num_machines
balance_metric = max(machine_times) / min(machine_times) if min(machine_times) > 0 else float('inf')

print(f"\nANÁLISIS DE EFICIENCIA:")
print(f"Tiempo total de procesamiento: {total_processing}")
print(f"Cmax teórico mínimo: {min_possible_Cmax:.2f}")
print(f"Balance entre máquinas: {balance_metric:.3f}")

# ============================
# Crear DataFrame para exportación
# ============================
df_schedule = pd.DataFrame({
    'Job': jobs,
    'Pj': pj,
    'Cj': [completion_times[j] for j in jobs],
    'Máquina': [next((log['machine'] for log in schedule_log if log['job'] == j), '?') for j in jobs]
})

df_machines = pd.DataFrame({
    'Máquina': [f'M{i+1}' for i in range(num_machines)],
    'Secuencia': [" → ".join(f"J{j}" for j in machines[i]) for i in range(num_machines)],
    'Cmax': machine_times
})

metrics = {
    'Cmax': Cmax,
    'ΣCj': SumCj,
    'F̅': round(F_bar, 2),
    'Tiempo Total Procesamiento': total_processing
}

# ============================
# Exportar a Excel
# ============================
try:
    out_xlsx = "Pm_SPT_Scheduling_Results.xlsx"
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        df_schedule.to_excel(writer, index=False, sheet_name="Programación")
        df_machines.to_excel(writer, index=False, sheet_name="Máquinas")
        pd.DataFrame([metrics]).to_excel(writer, index=False, sheet_name="Métricas")
    
    print(f"\n✅ Resultados exportados a {out_xlsx}")
except Exception as e:
    print(f"\n⚠️  No se pudo exportar a Excel: {e}")

print(f"\n" + "=" * 60)
print("EXPLICACIÓN DEL ALGORITMO SPT:")
print("=" * 60)
print("1. Se ordenan todos los trabajos por tiempo de procesamiento (Pj) ascendente")
print("2. Se asignan secuencialmente a la máquina que esté libre primero")
print("3. Esto minimiza ΣCj pero puede no ser óptimo para Cmax")
print("4. Para Pm||ΣCj, SPT es óptimo")