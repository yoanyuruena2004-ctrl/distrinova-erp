# Scheduling Problem 1||Tmax - Earliest Due Date (EDD) Rule

# Datos del problema
jobs = [1, 2, 3, 4, 5, 6, 7]
pj = [10, 3, 4, 8, 10, 6, 8]  # Tiempos de procesamiento
dj = [15, 6, 9, 23, 20, 30, 10]  # Fechas de entrega

# Combinar trabajos con sus tiempos de procesamiento y fechas de entrega
job_data = list(zip(jobs, pj, dj))

# Ordenar por fecha de entrega (dj) - Regla EDD
job_data_sorted = sorted(job_data, key=lambda x: x[2])

print("Scheduling Problem 1||Tmax - EDD Rule")
print("=" * 65)
print(f"{'J':>3} | {'Pj':>3} | {'Dj':>3} | {'Cj':>3} | {'Tj':>3} | {'Retraso':>8}")
print("-" * 65)

# Calcular tiempos de finalización y retrasos
current_time = 0
completion_times = []
tardiness = []
max_tardiness = 0

for job, process, due in job_data_sorted:
    completion_time = current_time + process
    job_tardiness = max(0, completion_time - due)
    max_tardiness = max(max_tardiness, job_tardiness)
    
    completion_times.append((job, process, due, completion_time, job_tardiness))
    tardiness.append(job_tardiness)
    current_time = completion_time
    
    retraso_str = "Sí" if job_tardiness > 0 else "No"
    print(f"{job:3} | {process:3} | {due:3} | {completion_time:3} | {job_tardiness:3} | {retraso_str:>8}")

print("-" * 65)

# Resultados
print(f"\nRESULTADOS:")
print(f"Secuencia EDD: {[job[0] for job in job_data_sorted]}")
print(f"Tmax (Máximo retraso): {max_tardiness}")
print(f"Tiempo de finalización del último trabajo (Cmax): {current_time}")

# Tabla resumen en orden de secuencia
print(f"\nTabla resumen completa:")
print(f"{'J':>3} | {'Pj':>3} | {'Cj':>3} | {'Dj':>3} | {'Tj':>3}")
print("-" * 30)
for job, process, due, completion, tard in completion_times:
    print(f"{job:3} | {process:3} | {completion:3} | {due:3} | {tard:3}")

# Estadísticas adicionales
num_tardy = sum(1 for t in tardiness if t > 0)
print(f"\nEstadísticas:")
print(f"Número de trabajos con retraso: {num_tardy}")
print(f"Suma total de retrasos: {sum(tardiness)}")