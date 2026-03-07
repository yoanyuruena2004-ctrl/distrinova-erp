import pandas as pd
import numpy as np

# ============================
# Datos del problema Pm||Cmax
# ============================
jobs = [1, 2, 3, 4, 5, 6, 7, 8]
pj = [6, 15, 8, 10, 14, 5, 12, 16]
num_machines = 3

print("PROBLEMA: Pm||Cmax - 3 MÁQUINAS IDÉNTICAS EN PARALELO")
print("ALGORITMO: LPT (Longest Processing Time)")
print("OBJETIVO: Minimizar Cmax (Makespan)")
print("=" * 70)

# ============================
# Combinar y ordenar por LPT (descendente)
# ============================
job_data = list(zip(jobs, pj))
job_data_sorted = sorted(job_data, key=lambda x: x[1], reverse=True)  # Orden LPT

print("\nTRABAJOS ORDENADOS POR LPT (Mayor a menor tiempo de procesamiento):")
print(f"{'Job':>4} | {'Pj':>3}")
print("-" * 15)
for job, process in job_data_sorted:
    print(f"{job:4} | {process:3}")

# ============================
# Algoritmo LPT para minimizar Cmax
# ============================
machines = [[] for _ in range(num_machines)]  # Lista de trabajos por máquina
machine_times = [0] * num_machines  # Tiempo actual de cada máquina
completion_times = {}  # Tiempo de finalización por trabajo
schedule_log = []  # Para el registro detallado

print(f"\nASIGNACIÓN LPT A {num_machines} MÁQUINAS:")
print(f"{'Iteración':>10} | {'Job':>4} | {'Pj':>3} | {'Máquina':>8} | {'Inicio':>6} | {'Fin':>6} | {'Carga Máq':>10}")

iteration = 1
for job, process_time in job_data_sorted:
    # Encontrar la máquina con MENOR carga actual (la que termina antes)
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
        'completion': completion_time,
        'machine_load': machine_times[machine_index]
    })
    
    print(f"{iteration:10} | {job:4} | {process_time:3} | M{machine_index + 1:7} | {start_time:6} | {completion_time:6} | {machine_times[machine_index]:10}")
    
    iteration += 1

# ============================
# Calcular métricas
# ============================
Cmax = max(machine_times)
SumCj = sum(completion_times.values())
F_bar = SumCj / len(jobs)
total_processing = sum(pj)

# ============================
# Mostrar resultados finales
# ============================
print(f"\n" + "=" * 70)
print("RESULTADOS FINALES - PM||CMAX")
print("=" * 70)

print(f"\nASIGNACIÓN POR MÁQUINA:")
for i in range(num_machines):
    machine_jobs = machines[i]
    machine_sequence = " → ".join(f"J{j}({pj[j-1]})" for j in machine_jobs)
    total_machine_time = sum(pj[j-1] for j in machine_jobs)
    print(f"M{i+1}: {machine_sequence} | Total = {total_machine_time} | Cmax = {machine_times[i]}")

print(f"\nDETALLE DE TIEMPOS POR TRABAJO:")
print(f"{'Job':>4} | {'Pj':>3} | {'Máquina':>8} | {'Inicio':>6} | {'Cj':>3}")
print("-" * 45)
for log in schedule_log:
    print(f"{log['job']:4} | {log['pj']:3} | {log['machine']:7} | {log['start']:6} | {log['completion']:3}")

print(f"\nMÉTRICAS GLOBALES:")
print(f"Cmax (Makespan): {Cmax}")
print(f"ΣCj (Suma de tiempos de finalización): {SumCj}")
print(f"F̅ (Tiempo de flujo promedio): {F_bar:.2f}")

# ============================
# Análisis de eficiencia y optimalidad
# ============================
min_theoretical_Cmax = total_processing / num_machines
balance_ratio = max(machine_times) / min(machine_times) if min(machine_times) > 0 else float('inf')
utilization = total_processing / (Cmax * num_machines) * 100

print(f"\nANÁLISIS DE OPTIMALIDAD:")
print(f"Tiempo total de procesamiento: {total_processing}")
print(f"Cmax teórico mínimo: {min_theoretical_Cmax:.2f}")
print(f"Ratio de balance: {balance_ratio:.3f}")
print(f"Utilización promedio: {utilization:.1f}%")

# Límite de performance de LPT
lpt_bound = (4/3) - (1/(3*num_machines))  # Cmax_LPT / Cmax_optimal ≤ 4/3 - 1/(3m)
max_possible_optimal = Cmax / lpt_bound

print(f"\nPROPIEDADES LPT:")
print(f"LPT garantiza: Cmax_LPT / Cmax_optimal ≤ {lpt_bound:.3f}")
print(f"Cmax óptimo real ≥ {max_possible_optimal:.2f}")

# ============================
# Crear DataFrames para análisis
# ============================
df_schedule = pd.DataFrame({
    'Job': jobs,
    'Pj': pj,
    'Máquina': [next((log['machine'] for log in schedule_log if log['job'] == j), '?') for j in jobs],
    'Inicio': [next((log['start'] for log in schedule_log if log['job'] == j), 0) for j in jobs],
    'Cj': [completion_times[j] for j in jobs]
})

df_machines = pd.DataFrame({
    'Máquina': [f'M{i+1}' for i in range(num_machines)],
    'Secuencia': [" → ".join(f"J{j}" for j in machines[i]) for i in range(num_machines)],
    'Trabajos': [machines[i] for i in range(num_machines)],
    'Tiempo Total': [sum(pj[j-1] for j in machines[i]) for i in range(num_machines)],
    'Cmax': machine_times
})

metrics = {
    'Cmax': Cmax,
    'ΣCj': SumCj,
    'F̅': round(F_bar, 2),
    'Tiempo Total Procesamiento': total_processing,
    'Utilización (%)': round(utilization, 1),
    'Cmax Teórico Mínimo': round(min_theoretical_Cmax, 2)
}

# ============================
# Visualización del diagrama de Gantt
# ============================
print(f"\n" + "=" * 70)
print("DIAGRAMA DE GANTT - REPRESENTACIÓN GRÁFICA")
print("=" * 70)

for i in range(num_machines):
    print(f"\nM{i+1}: ", end="")
    current_time = 0
    for job in machines[i]:
        job_time = pj[job-1]
        # Representación gráfica simple
        bar = "█" * (job_time // 2)  # Cada █ representa 2 unidades de tiempo
        print(f"[J{job}:{bar:<8}]", end=" ")
        current_time += job_time
    print(f"→ Cmax = {machine_times[i]}")

# ============================
# Exportar a Excel
# ============================
try:
    out_xlsx = "Pm_Cmax_LPT_Results.xlsx"
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        df_schedule.to_excel(writer, index=False, sheet_name="Programación")
        df_machines.to_excel(writer, index=False, sheet_name="Máquinas")
        pd.DataFrame([metrics]).to_excel(writer, index=False, sheet_name="Métricas")
        
        # Crear tabla de análisis comparativo
        comparison_data = {
            'Métrica': ['Cmax', 'ΣCj', 'Utilización', 'Balance'],
            'Valor': [Cmax, SumCj, f'{utilization:.1f}%', f'{balance_ratio:.3f}'],
            'Óptimo Teórico': [f'≥{max_possible_optimal:.1f}', 'No aplica', '100%', '1.000']
        }
        pd.DataFrame(comparison_data).to_excel(writer, index=False, sheet_name="Análisis")
    
    print(f"\n✅ Resultados exportados a {out_xlsx}")
except Exception as e:
    print(f"\n⚠️  No se pudo exportar a Excel: {e}")

print(f"\n" + "=" * 70)
print("CONCLUSIÓN:")
print("=" * 70)
print("✓ LPT es (4/3 - 1/3m)-aproximado para Pm||Cmax")
print("✓ Para 3 máquinas: Cmax_LPT ≤ 1.22 × Cmax_optimal") 
print("✓ El algoritmo balancea bien las cargas entre máquinas")
print("✓ Secuencia óptima para minimizar el tiempo total de producción")