def giffler_thompson(jobs):
    num_machines = 3
    machine_free = [0] * num_machines
    job_next = [0] * len(jobs)
    job_ready = [0] * len(jobs)
    schedule = []
    
    while any(job_next[j] < len(jobs[j]) for j in range(len(jobs))):
        available_ops = []
        for j in range(len(jobs)):
            if job_next[j] < len(jobs[j]):
                op_index = job_next[j]
                machine, time = jobs[j][op_index]
                m_index = machine - 1
                start_time = max(job_ready[j], machine_free[m_index])
                end_time = start_time + time
                available_ops.append((j, op_index, machine, start_time, end_time))
        
        if not available_ops:
            break
        
        chosen_op = min(available_ops, key=lambda x: x[4])
        j, op_index, machine, start, end = chosen_op
        m_index = machine - 1
        schedule.append((j, op_index, machine, start, end))
        machine_free[m_index] = end
        job_ready[j] = end
        job_next[j] += 1
    
    makespan = max(job_ready)
    return schedule, makespan

# Definición de los trabajos basada en el ejemplo del documento
jobs = [
    [(1, 7), (3, 8), (2, 10)],  # Job 1: (M1,7), (M3,8), (M2,10)
    [(2, 6), (1, 4), (3, 12)],  # Job 2: (M2,6), (M1,4), (M3,12)
    [(1, 8), (2, 8), (3, 7)]    # Job 3: (M1,8), (M2,8), (M3,7)
]

schedule, makespan = giffler_thompson(jobs)

print("Programación de operaciones:")
print("Job | Op | Máquina | Inicio | Fin")
for s in schedule:
    print(f"{s[0]+1:3} | {s[1]+1:2} | {s[2]:7} | {s[3]:5} | {s[4]:3}")
print(f"\nMakespan (Cmax): {makespan}")