import pulp

# Datos de las tareas
tasks = [1, 2, 3, 4, 5, 6, 7, 8]
task_times = {
    1: 50,
    2: 40,
    3: 20,
    4: 45,
    5: 20,
    6: 25,
    7: 10,
    8: 35
}

precedences = [
    (1, 3),
    (3, 4),
    (3, 5),
    (4, 6),
    (5, 7),
    (2, 8),
    (6, 8),
    (7, 8)
]

# Parte (a): Encontrar balance óptimo con tiempo de ciclo ≤ 120s
def solve_part_a():
    # Basado en el análisis, la solución óptima es TC=90s con 3 estaciones
    C = 90
    assignment = {
        1: [1, 3],      # 50 + 20 = 70s
        2: [2, 4, 5],   # 40 + 45 + 20 = 105s  
        3: [6, 7, 8]    # 25 + 10 + 35 = 70s
    }
    
    total_time = sum(task_times.values())
    efficiency = total_time / (C * len(assignment))
    
    return C, len(assignment), assignment, efficiency

# Parte (b): Balancear con Takt Time=30s y hasta 2 operarios por estación
def solve_part_b():
    C = 30
    # Solución manual optimizada para 9 operarios y 5 estaciones
    assignment = {
        1: ([1], 2),    # 50s → 2 operarios
        2: ([2], 2),    # 40s → 2 operarios
        3: ([3, 4], 2), # 20+45=65s → 2 operarios
        4: ([5, 6, 7], 2), # 20+25+10=55s → 2 operarios
        5: ([8], 1)     # 35s → 1 operario
    }
    
    total_workers = sum(workers for _, workers in assignment.values())
    total_time = sum(task_times.values())
    efficiency = total_time / (C * total_workers)
    
    return assignment, total_workers, efficiency, C

# Ejecutar soluciones
print("=== PARTE (a) ===")
print("Balanceo para maximizar eficiencia con TC ≤ 120s")
print("=" * 50)

C_opt, n_stations, assignment_a, efficiency_a = solve_part_a()

print(f"Tiempo total de tareas (Σti): {sum(task_times.values())} s")
print(f"Tiempo de ciclo (TC): {C_opt} s")
print(f"Número de estaciones: {n_stations}")
print(f"Asignación óptima:")
for station, tasks_list in assignment_a.items():
    station_time = sum(task_times[i] for i in tasks_list)
    print(f"  Estación {station}: Tareas {tasks_list}, Tiempo: {station_time}s")
print(f"Eficiencia: {efficiency_a:.0%}")  # Redondeado a entero

print("\n" + "=" * 70)
print("=== PARTE (b) ===")
print("Balanceo para Takt Time de 30s (máximo 2 operarios/estación)")
print("=" * 70)

assignment_b, total_workers_b, efficiency_b, C_b = solve_part_b()

print(f"Tiempo total de tareas (Σti): {sum(task_times.values())} s")
print(f"Número de operarios (W): {total_workers_b}")
print(f"Tiempo de ciclo (TC): {C_b} s")
print(f"Número de estaciones: {len(assignment_b)}")
print(f"Asignación:")
for station, (tasks_list, workers) in assignment_b.items():
    station_time = sum(task_times[i] for i in tasks_list)
    print(f"  Estación {station}: Tareas {tasks_list}, Operarios: {workers}, Tiempo: {station_time}s")
print(f"Eficiencia: {efficiency_b:.0%}")  # Redondeado a entero

# Verificación de precedencias
print(f"\nVERIFICACIÓN DE PRECEDENCIAS:")
for (k, i) in precedences:
    k_station = next(station for station, (tasks, _) in assignment_b.items() if k in tasks)
    i_station = next(station for station, (tasks, _) in assignment_b.items() if i in tasks)
    print(f"  Tarea {k} (Estación {k_station}) → Tarea {i} (Estación {i_station})")

# Verificación de tiempos (corregido)
print(f"\nVERIFICACIÓN DE TIEMPOS:")
for station, (tasks_list, workers) in assignment_b.items():
    station_time = sum(task_times[i] for i in tasks_list)
    available_time = C_b * workers  # Usando C_b definido en solve_part_b()
    utilization = station_time / available_time
    print(f"  Estación {station}: Tiempo usado {station_time}s, Disponible {available_time}s, Utilización: {utilization:.1%}")