import pandas as pd
import numpy as np
import pulp

# ============================================================
# MODELO Rm | batch | Cmax - MÁQUINAS NO RELACIONADAS CON LOTES
# ============================================================

# --------------------------
# DATOS DEL PROBLEMA
# --------------------------
print("PROBLEMA: Rm | batch | Cmax")
print("=" * 70)

# Trabajos (lotes)
jobs = [1, 2, 3, 4]
machines = ['M1', 'M2', 'M3']

# Tiempos de procesamiento por lote en cada máquina (horas/lote)
Pjm = {
    (1, 'M1'): 10, (1, 'M2'): 4,  (1, 'M3'): 8,
    (2, 'M1'): 6,  (2, 'M2'): 3,  (2, 'M3'): 5,
    (3, 'M1'): 12, (3, 'M2'): 16, (3, 'M3'): 10,
    (4, 'M1'): 8,  (4, 'M2'): 12, (4, 'M3'): 15
}

# Tamaños de los lotes (unidades)
Bj = {1: 19, 2: 21, 3: 59, 4: 33}

print("DATOS DE PROCESAMIENTO (Pjm - horas/lote):")
print(f"{'Lote/Máquina':<12} {'M1':<8} {'M2':<8} {'M3':<8}")
print("-" * 45)
for j in jobs:
    tiempos = [Pjm.get((j, m), 0) for m in machines]
    print(f"Lote {j:<9} {tiempos[0]:<8} {tiempos[1]:<8} {tiempos[2]:<8}")

print(f"\nTAMAÑOS DE LOTE (Bj - unidades):")
for j in jobs:
    print(f"Lote {j}: {Bj[j]} unidades")

# --------------------------
# MODELO DE OPTIMIZACIÓN
# --------------------------
model = pulp.LpProblem("Rm_Batch_Cmax", pulp.LpMinimize)

print(f"\nFORMULACIÓN DEL MODELO:")
print("FO: Min Z = C")
print("s.a.:")
print("   ∑ Pjm·Xjm ≤ C, ∀ m ∈ M")
print("   ∑ Xjm = Bj, ∀ j ∈ J") 
print("   Xjm ∈ Entero")

# Variables de decisión
C = pulp.LpVariable("C", lowBound=0, cat='Continuous')  # Makespan

# Variables enteras: cantidad del lote j asignada a la máquina m
X = pulp.LpVariable.dicts("X", 
                         [(j, m) for j in jobs for m in machines],
                         lowBound=0, cat='Integer')

print(f"\nVARIABLES CREADAS:")
print(f"✓ 1 variable continua C (makespan)")
print(f"✓ {len(X)} variables enteras Xjm")

# --------------------------
# RESTRICCIONES
# --------------------------
print(f"\nAGREGANDO RESTRICCIONES...")

# Restricción 1: El tiempo total en cada máquina no puede exceder C
for m in machines:
    machine_time = pulp.lpSum([Pjm[(j, m)] * X[(j, m)] for j in jobs])
    model += machine_time <= C, f"Machine_Time_{m}"
    print(f"  {m}: ∑ Pjm·Xjm ≤ C")

# Restricción 2: Todo el lote de cada trabajo debe ser asignado
for j in jobs:
    total_assigned = pulp.lpSum([X[(j, m)] for m in machines])
    model += total_assigned == Bj[j], f"Batch_Assignment_{j}"
    print(f"  Lote {j}: ∑ Xj· = {Bj[j]}")

# --------------------------
# FUNCIÓN OBJETIVO
# --------------------------
model += C, "Minimizar_Makespan"
print(f"\n✓ Función objetivo: Minimizar C")

# --------------------------
# RESOLUCIÓN
# --------------------------
print(f"\n" + "=" * 70)
print("RESOLVIENDO EL MODELO...")
print("=" * 70)

solver = pulp.PULP_CBC_CMD(msg=True)
model.solve(solver)

# --------------------------
# RESULTADOS
# --------------------------
print(f"\n" + "=" * 70)
print("RESULTADOS ÓPTIMOS")
print("=" * 70)

print(f"Estado: {pulp.LpStatus[model.status]}")
print(f"Makespan óptimo (C): {pulp.value(C):.2f} horas")

# --------------------------
# ASIGNACIÓN POR MÁQUINA
# --------------------------
print(f"\nASIGNACIÓN ÓPTIMA DE LOTES:")
print(f"{'Máquina':<8} | {'Asignaciones':<40} | {'Tiempo Total':>12}")
print("-" * 75)

machine_assignments = {}
machine_times = {}

for m in machines:
    assignments = []
    total_time = 0
    
    for j in jobs:
        quantity = pulp.value(X[(j, m)])
        if quantity > 0.1:  # Si se asignó algo de este lote
            time_contribution = Pjm[(j, m)] * quantity
            assignments.append(f"Lote{j}({quantity:.0f} und)")
            total_time += time_contribution
    
    machine_assignments[m] = assignments
    machine_times[m] = total_time
    
    assignments_str = " + ".join(assignments) if assignments else "Sin asignación"
    print(f"{m:<8} | {assignments_str:<40} | {total_time:>12.2f} h")

# --------------------------
# DETALLE POR LOTE
# --------------------------
print(f"\nDISTRIBUCIÓN DETALLADA POR LOTE:")
print(f"{'Lote':<6} | {'Tamaño':<8} | {'M1':<8} | {'M2':<8} | {'M3':<8} | {'Total Asignado':<15}")
print("-" * 85)

for j in jobs:
    m1_qty = pulp.value(X[(j, 'M1')])
    m2_qty = pulp.value(X[(j, 'M2')]) 
    m3_qty = pulp.value(X[(j, 'M3')])
    total_assigned = m1_qty + m2_qty + m3_qty
    
    print(f"{j:<6} | {Bj[j]:<8} | {m1_qty:<8.0f} | {m2_qty:<8.0f} | {m3_qty:<8.0f} | {total_assigned:<15.0f}")

# --------------------------
# ANÁLISIS DE EFICIENCIA
# --------------------------
print(f"\n" + "=" * 70)
print("ANÁLISIS DE EFICIENCIA")
print("=" * 70)

# Calcular utilización por máquina
print(f"{'Máquina':<8} | {'Tiempo Usado':<12} | {'Tiempo Total':<12} | {'Utilización':<12}")
print("-" * 55)

for m in machines:
    time_used = machine_times[m]
    total_time = pulp.value(C)
    utilization = (time_used / total_time) * 100 if total_time > 0 else 0
    
    print(f"{m:<8} | {time_used:>12.2f} | {total_time:>12.2f} | {utilization:>11.1f}%")

# Balance de carga
max_time = max(machine_times.values())
min_time = min(machine_times.values())
balance_ratio = max_time / min_time if min_time > 0 else float('inf')

print(f"\nBalance de carga:")
print(f"Tiempo máximo: {max_time:.2f} horas")
print(f"Tiempo mínimo: {min_time:.2f} horas")
print(f"Ratio de balance: {balance_ratio:.3f}")

# --------------------------
# DIAGRAMA DE GANTT SIMPLIFICADO
# --------------------------
print(f"\n" + "=" * 70)
print("DIAGRAMA DE GANTT (Representación simplificada)")
print("=" * 70)

for m in machines:
    print(f"\n{m}:")
    print("Tiempo: ", end="")
    
    # Escala simplificada
    scale_factor = 2  # cada carácter = 0.5 horas
    total_chars = int(pulp.value(C) * scale_factor)
    
    # Línea de tiempo
    for i in range(total_chars + 1):
        if i % (scale_factor * 2) == 0:  # marcas cada 1 hora
            print(f"{i//scale_factor}", end="")
        else:
            print("-", end="")
    print()
    
    # Barras de trabajos
    current_pos = 0
    for j in jobs:
        quantity = pulp.value(X[(j, m)])
        if quantity > 0.1:
            job_time = Pjm[(j, m)] * quantity
            bar_length = int(job_time * scale_factor)
            bar = "█" * bar_length
            
            # Encontrar posición
            assigned_time = 0
            for k in jobs:
                if k == j:
                    break
                k_quantity = pulp.value(X[(k, m)])
                if k_quantity > 0.1:
                    assigned_time += Pjm[(k, m)] * k_quantity
            
            spaces_before = int(assigned_time * scale_factor)
            if spaces_before > current_pos:
                print(" " * (spaces_before - current_pos), end="")
            
            print(f"[L{j}]", end="")
            current_pos = spaces_before + 4
    
    print(f" → Total: {machine_times[m]:.2f}h")

# --------------------------
# COMPARACIÓN CON ASIGNACIÓN DIRECTA
# --------------------------
print(f"\n" + "=" * 70)
print("COMPARACIÓN CON ASIGNACIÓN DIRECTA (NAIVE)")
print("=" * 70)

# Estrategia naive: asignar cada lote completo a su máquina más rápida
naive_cmax = 0
naive_times = {m: 0 for m in machines}

for j in jobs:
    # Encontrar máquina más rápida para este lote
    best_machine = min(machines, key=lambda m: Pjm[(j, m)])
    naive_times[best_machine] += Pjm[(j, m)] * Bj[j]

naive_cmax = max(naive_times.values())

print(f"Makespan con asignación naive: {naive_cmax:.2f} horas")
print(f"Makespan óptimo: {pulp.value(C):.2f} horas")
print(f"Mejora: {((naive_cmax - pulp.value(C)) / naive_cmax * 100):.1f}%")

# --------------------------
# EXPORTACIÓN DE RESULTADOS
# --------------------------
try:
    # DataFrames para exportación
    df_assignments = pd.DataFrame({
        'Lote': jobs,
        'Tamaño_Lote': [Bj[j] for j in jobs],
        'Asignado_M1': [pulp.value(X[(j, 'M1')]) for j in jobs],
        'Asignado_M2': [pulp.value(X[(j, 'M2')]) for j in jobs],
        'Asignado_M3': [pulp.value(X[(j, 'M3')]) for j in jobs],
        'Total_Asignado': [sum(pulp.value(X[(j, m)]) for m in machines) for j in jobs]
    })

    df_machines = pd.DataFrame({
        'Máquina': machines,
        'Tiempo_Total': [machine_times[m] for m in machines],
        'Utilización_%': [(machine_times[m] / pulp.value(C)) * 100 for m in machines],
        'Número_Lotes': [len(machine_assignments[m]) for m in machines]
    })

    df_metrics = pd.DataFrame([{
        'Makespan_Optimo': pulp.value(C),
        'Makespan_Naive': naive_cmax,
        'Mejora_%': ((naive_cmax - pulp.value(C)) / naive_cmax * 100),
        'Balance_Ratio': balance_ratio,
        'Tiempo_Total_Produccion': sum(Pjm[(j, m)] * Bj[j] for j in jobs for m in machines) / len(machines)
    }])

    # Exportar a Excel
    out_xlsx = "Rm_Batch_Cmax_Results.xlsx"
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        df_assignments.to_excel(writer, index=False, sheet_name="Asignaciones_Lotes")
        df_machines.to_excel(writer, index=False, sheet_name="Carga_Máquinas")
        df_metrics.to_excel(writer, index=False, sheet_name="Métricas")
        
        # Agregar formulación
        formulation_data = {
            'Componente': ['Función Objetivo', 'Restricción Tipo 1', 'Restricción Tipo 2'],
            'Descripción': [
                'Min Z = C',
                '∑ Pjm·Xjm ≤ C, ∀ m ∈ M',
                '∑ Xjm = Bj, ∀ j ∈ J'
            ]
        }
        pd.DataFrame(formulation_data).to_excel(writer, index=False, sheet_name="Formulación")
    
    print(f"\n✅ Resultados exportados a {out_xlsx}")
    
except Exception as e:
    print(f"\n⚠️ Error en exportación: {e}")

print(f"\n" + "=" * 70)
print("RESUMEN EJECUTIVO")
print("=" * 70)
print(f"✓ Makespan óptimo: {pulp.value(C):.2f} horas")
print(f"✓ {sum(Bj.values())} unidades distribuidas en {len(jobs)} lotes")
print(f"✓ Utilización promedio: {(sum(machine_times.values()) / (pulp.value(C) * len(machines)) * 100):.1f}%")
print(f"✓ Balance de carga: {balance_ratio:.3f}")
print(f"✓ Mejora vs asignación naive: {((naive_cmax - pulp.value(C)) / naive_cmax * 100):.1f}%")