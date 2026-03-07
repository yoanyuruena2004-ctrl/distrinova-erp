# Scheduling Problem 1|rj|Cmax
# First-Come First-Served (FCFS) Rule

# Datos del problema
jobs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
rj = [5, 0, 5, 10, 0, 15, 30, 10, 25, 2]
pj = [5, 3, 4, 8, 7, 2, 5, 8, 6, 8]

# Combinar trabajos con sus tiempos de liberación y procesamiento
job_data = list(zip(jobs, rj, pj))

# Ordenar por tiempo de liberación (rj) - FCFS
job_data_sorted = sorted(job_data, key=lambda x: x[1])

print("Scheduling Problem 1|rj|Cmax - FCFS Rule")
print("=" * 60)
print(f"{'J':>3} | {'rj':>3} | {'pj':>3} | {'Cj':>3} | {'Tiempo Inicio':>12}")
print("-" * 60)

# Calcular tiempos de finalización
current_time = 0
completion_times = []
total_completion = 0

for job, release, process in job_data_sorted:
    # El trabajo comienza en el máximo entre el tiempo actual y su tiempo de liberación
    start_time = max(current_time, release)
    completion_time = start_time + process
    completion_times.append((job, release, process, completion_time))
    total_completion += completion_time
    current_time = completion_time
    
    print(f"{job:3} | {release:3} | {process:3} | {completion_time:3} | {start_time:12}")

print("-" * 60)

# Encontrar Cmax (makespan)
cmax = current_time
print(f"\nCmax (Makespan): {cmax}")
print(f"Suma de tiempos de finalización (∑Cj): {total_completion}")

# Mostrar secuencia final
print(f"\nSecuencia FCFS: {[job[0] for job in job_data_sorted]}")
print(f"\nTabla resumen:")
print(f"{'J':>3} | {'rj':>3} | {'pj':>3} | {'Cj':>3}")
print("-" * 25)
for job, release, process, completion in completion_times:
    print(f"{job:3} | {release:3} | {process:3} | {completion:3}")

# Verificación adicional
print(f"\nVerificación:")
print(f"Último trabajo completado: J{completion_times[-1][0]} en tiempo {cmax}")
print(f"Número total de trabajos: {len(jobs)}")
