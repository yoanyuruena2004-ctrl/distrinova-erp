# Scheduling Problem 1||NT - Algoritmo de Moore

# Datos del problema
jobs = [1, 2, 3, 4, 5, 6, 7]
pj = [10, 3, 4, 8, 10, 6, 8]  # Tiempos de procesamiento
dj = [15, 6, 9, 23, 20, 30, 10]  # Fechas de entrega

print("Algoritmo de Moore para minimizar NT (Número de trabajos tardíos)")
print("=" * 70)

# Paso 1: Ordenar por EDD (Earliest Due Date)
job_data = list(zip(jobs, pj, dj))
job_data_sorted = sorted(job_data, key=lambda x: x[2])

print("\nPASO 1: Secuencia EDD inicial")
print(f"{'JOB':>4} | {'Pj':>3} | {'Dj':>3}")
print("-" * 20)
for job, process, due in job_data_sorted:
    print(f"{job:4} | {process:3} | {due:3}")

# Algoritmo de Moore
current_sequence = job_data_sorted.copy()
rejected_jobs = []
iteration = 1

while True:
    print(f"\n--- ITERACIÓN {iteration} ---")
    
    # Calcular tiempos de completación y tardanza
    current_time = 0
    completion_data = []
    tardy_jobs = []
    
    for job, process, due in current_sequence:
        completion_time = current_time + process
        tardiness = max(0, completion_time - due)
        completion_data.append((job, process, due, completion_time, tardiness))
        
        if tardiness > 0:
            tardy_jobs.append((job, process, due, completion_time, tardiness))
        
        current_time = completion_time
    
    # Mostrar secuencia actual
    print(f"{'JOB':>4} | {'Pj':>3} | {'Cj':>3} | {'Dj':>3} | {'Tj':>3} | {'Tardío':>8}")
    print("-" * 45)
    for job, process, due, completion, tardiness in completion_data:
        tardio_str = "Sí" if tardiness > 0 else "No"
        print(f"{job:4} | {process:3} | {completion:3} | {due:3} | {tardiness:3} | {tardio_str:>8}")
    
    # Paso 2: Verificar si hay trabajos tardíos
    if not tardy_jobs:
        print("\n✓ No hay trabajos tardíos - FIN DEL ALGORITMO")
        break
    
    # Paso 3: Encontrar el primer trabajo tardío y rechazar el de mayor Pj
    first_tardy_index = None
    for i, (job, process, due, completion, tardiness) in enumerate(completion_data):
        if tardiness > 0:
            first_tardy_index = i
            break
    
    if first_tardy_index is not None:
        # Encontrar el trabajo con mayor Pj entre [1] hasta [first_tardy_index]
        jobs_to_consider = current_sequence[:first_tardy_index + 1]
        job_to_reject = max(jobs_to_consider, key=lambda x: x[1])
        
        print(f"\nPrimer trabajo tardío encontrado en posición: {first_tardy_index + 1}")
        print(f"Trabajos considerados para rechazo: {[job[0] for job in jobs_to_consider]}")
        print(f"Trabajo rechazado: J{job_to_reject[0]} (Pj = {job_to_reject[1]})")
        
        # Rechazar el trabajo
        rejected_jobs.append(job_to_reject)
        current_sequence.remove(job_to_reject)
    
    iteration += 1

# Paso 4: Formar secuencia final
final_sequence = current_sequence + rejected_jobs

print(f"\n" + "=" * 70)
print("PASO 4: Secuencia final óptima")
print(f"Secuencia principal (a tiempo): {[job[0] for job in current_sequence]}")
print(f"Trabajos rechazados (tardíos): {[job[0] for job in rejected_jobs]}")

# Calcular métricas finales
current_time = 0
final_completion_data = []
nt = 0  # Número de trabajos tardíos

print(f"\n{'JOB':>4} | {'Pj':>3} | {'Cj':>3} | {'Dj':>3} | {'Tj':>3} | {'Estado':>10}")
print("-" * 50)
for job, process, due in final_sequence:
    completion_time = current_time + process
    tardiness = max(0, completion_time - due)
    estado = "Tardío" if tardiness > 0 else "A tiempo"
    
    if tardiness > 0:
        nt += 1
    
    final_completion_data.append((job, process, due, completion_time, tardiness))
    print(f"{job:4} | {process:3} | {completion_time:3} | {due:3} | {tardiness:3} | {estado:>10}")
    
    current_time = completion_time

print(f"\nRESULTADOS FINALES:")
print(f"Secuencia óptima: {[job[0] for job in final_sequence]}")
print(f"NT (Número de trabajos tardíos): {nt}")
print(f"Cmax (Makespan): {current_time}")
print(f"Trabajos a tiempo: {len(current_sequence)}")
print(f"Trabajos tardíos: {len(rejected_jobs)}")

# Mostrar trabajos tardíos específicos
tardy_jobs_list = [job[0] for job in final_completion_data if job[4] > 0]
print(f"Trabajos tardíos: {tardy_jobs_list}")