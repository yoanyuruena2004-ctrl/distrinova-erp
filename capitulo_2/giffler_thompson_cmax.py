def giffler_thompson_start_lrpt(jobs):
    num_machines = 3
    machine_free = [0] * num_machines
    job_next = [0] * len(jobs)
    job_ready = [0] * len(jobs)
    schedule = []
    
    # Función para calcular el tiempo de procesamiento restante de un trabajo
    def remaining_time(job_index):
        total = 0
        for op_index in range(job_next[job_index], len(jobs[job_index])):
            total += jobs[job_index][op_index][1]
        return total
    
    while any(job_next[j] < len(jobs[j]) for j in range(len(jobs))):
        available_ops = []
        for j in range(len(jobs)):
            if job_next[j] < len(jobs[j]):
                op_index = job_next[j]
                machine, time = jobs[j][op_index]
                m_index = machine - 1
                start_time = max(job_ready[j], machine_free[m_index])
                available_ops.append((j, op_index, machine, start_time, time))
        
        if not available_ops:
            break
        
        # Encontrar el tiempo de inicio más pequeño
        min_start = min(available_ops, key=lambda x: x[3])[3]
        candidate_ops = [op for op in available_ops if op[3] == min_start]
        
        # Desempate: LRPT (mayor tiempo de procesamiento restante)
        if len(candidate_ops) > 1:
            candidate_ops.sort(key=lambda x: remaining_time(x[0]), reverse=True)
        
        chosen_op = candidate_ops[0]
        j, op_index, machine, start, time = chosen_op
        end = start + time
        m_index = machine - 1
        schedule.append((j, op_index, machine, start, end))
        machine_free[m_index] = end
        job_ready[j] = end
        job_next[j] += 1
    
    makespan = max(job_ready)
    return schedule, makespan

# Definición de los trabajos basada en el ejemplo de las páginas 157-160
jobs = [
    [(1, 7), (3, 8), (2, 10)],  # Job 1: (M1,7), (M3,8), (M2,10)
    [(2, 6), (1, 4), (3, 12)],  # Job 2: (M2,6), (M1,4), (M3,12)
    [(1, 8), (2, 8), (3, 7)]    # Job 3: (M1,8), (M2,8), (M3,7)
]

schedule, makespan = giffler_thompson_start_lrpt(jobs)

print("Programación de operaciones (Inicio Más Próximo con LRPT):")
print("Job | Op | Máquina | Inicio | Fin")
for s in schedule:
    print(f"{s[0]+1:3} | {s[1]+1:2} | {s[2]:7} | {s[3]:5} | {s[4]:3}")
print(f"\nMakespan (Cmax): {makespan}")