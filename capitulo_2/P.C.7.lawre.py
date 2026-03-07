# Algoritmo de Lawler para 1|prec|Tmax
import numpy as np

class Job:
    def __init__(self, id, processing_time, due_date, predecessors):
        self.id = id
        self.p = processing_time
        self.d = due_date
        self.predecessors = predecessors

def get_successors(jobs):
    """Obtener lista de sucesores para cada trabajo"""
    successors = {job.id: [] for job in jobs}
    for job in jobs:
        for pred in job.predecessors:
            successors[pred].append(job.id)
    return successors

def lawler_algorithm(jobs):
    """
    Implementación del Algoritmo de Lawler para minimizar Tmax
    con restricciones de precedencia
    """
    # Calcular tiempo total
    total_time = sum(job.p for job in jobs)
    
    # Obtener sucesores
    successors = get_successors(jobs)
    
    # Inicializar estructuras
    scheduled = []  # Secuencia final (del último al primero)
    unscheduled = jobs.copy()
    job_dict = {job.id: job for job in jobs}
    
    print("=== ALGORITMO DE LAWLER - EJECUCIÓN PASO A PASO ===")
    print(f"Tiempo total de procesamiento: {total_time}")
    print()
    
    iteration = 1
    while unscheduled:
        print(f"Iteración {iteration}: t = {total_time}")
        
        # Encontrar trabajos sin sucesores en los no programados
        candidate_jobs = []
        unscheduled_ids = [job.id for job in unscheduled]
        
        for job in unscheduled:
            # Verificar si tiene sucesores no programados
            has_unscheduled_successors = any(
                succ in unscheduled_ids for succ in successors[job.id]
            )
            if not has_unscheduled_successors:
                candidate_jobs.append(job)
        
        print(f"  Candidatos: {[job.id for job in candidate_jobs]}")
        
        # Calcular Tardanza para cada candidato
        tardanzas = []
        for job in candidate_jobs:
            tardanza = max(total_time - job.d, 0)
            tardanzas.append((job, tardanza))
            print(f"    J{job.id}: C={total_time}, d={job.d}, T={tardanza}")
        
        # Elegir el que minimiza la tardanza
        best_job, best_tardanza = min(tardanzas, key=lambda x: x[1])
        
        print(f"  → Elegido: J{best_job.id} con T={best_tardanza}")
        print()
        
        # Programar al inicio de la secuencia
        scheduled.insert(0, best_job)
        unscheduled.remove(best_job)
        total_time -= best_job.p
        
        iteration += 1
    
    return scheduled

def calculate_schedule_times(sequence):
    """Calcular tiempos de inicio, finalización y tardanzas"""
    current_time = 0
    schedule_data = []
    
    for job in sequence:
        start_time = current_time
        completion_time = current_time + job.p
        tardiness = max(completion_time - job.d, 0)
        
        schedule_data.append({
            'job': job.id,
            'start': start_time,
            'completion': completion_time,
            'tardiness': tardiness
        })
        
        current_time = completion_time
    
    return schedule_data, current_time

def main():
    # Definir los trabajos con sus precedencias
    jobs = [
        Job(1, 5, 20, []),      # J1
        Job(2, 4, 12, [1]),     # J2 después de J1
        Job(3, 10, 25, [2]),    # J3 después de J2
        Job(4, 8, 15, []),      # J4
        Job(5, 10, 20, [4]),    # J5 después de J4
        Job(6, 5, 30, [4]),     # J6 después de J4
        Job(7, 8, 10, [5])      # J7 después de J5
    ]
    
    print("PROBLEMA DE SCHEDULING: 1|prec|Tmax")
    print("=" * 50)
    print("Datos de los trabajos:")
    print("J | Pj | Dj | Predecesores")
    print("-" * 30)
    for job in jobs:
        pred_str = ", ".join(str(p) for p in job.predecessors) if job.predecessors else "-"
        print(f"{job.id} | {job.p:2} | {job.d:2} | {pred_str}")
    print()
    
    # Aplicar algoritmo de Lawler
    optimal_sequence = lawler_algorithm(jobs)
    
    # Calcular tiempos
    schedule_data, cmax = calculate_schedule_times(optimal_sequence)
    
    # Mostrar resultados
    print("=" * 60)
    print("RESULTADOS FINALES")
    print("=" * 60)
    
    print("\nSECUENCIA ÓPTIMA:")
    sequence_str = " → ".join(f"J{job.id}" for job in optimal_sequence)
    print(sequence_str)
    
    print("\nDETALLE DE TIEMPOS:")
    print("J | Inicio | Cj | Dj | Tj")
    print("-" * 25)
    for data in schedule_data:
        print(f"{data['job']} | {data['start']:6} | {data['completion']:2} | {next(job.d for job in jobs if job.id == data['job']):2} | {data['tardiness']:2}")
    
    # Calcular Tmax
    tmax = max(data['tardiness'] for data in schedule_data)
    
    print("\nMÉTRICAS:")
    print(f"Cmax (Makespan): {cmax}")
    print(f"Tmax (Tardanza máxima): {tmax}")
    
    # Verificar precedencias
    print("\nVERIFICACIÓN DE PRECEDENCIAS:")
    sequence_ids = [job.id for job in optimal_sequence]
    precedences_ok = True
    
    for job in jobs:
        for pred in job.predecessors:
            pred_index = sequence_ids.index(pred)
            job_index = sequence_ids.index(job.id)
            if pred_index > job_index:
                print(f"❌ J{pred} debería ir antes de J{job.id}")
                precedences_ok = False
            else:
                print(f"✅ J{pred} antes de J{job.id} (pos {pred_index+1} → {job_index+1})")
    
    if precedences_ok:
        print("\n🎯 TODAS LAS PRECEDENCIAS SE RESPETAN CORRECTAMENTE")

if __name__ == "__main__":
    main()