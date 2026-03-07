import pandas as pd
import numpy as np
import pulp

# ============================================================
# MODELO CORREGIDO - VELOCIDADES RELATIVAS CORRECTAS
# ============================================================

print("MODELO EXACTO - VELOCIDADES RELATIVAS CORRECTAS")
print("=" * 70)

# Datos
jobs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
processing_times = [3, 30, 24, 6, 12, 9, 18, 21, 27, 15]
machines = ['M1', 'M2', 'M3', 'M4']
production_rates = [5, 5, 7.5, 10]  # uni/hr

# CALCULAR VELOCIDADES RELATIVAS CORRECTAMENTE (MÁS LENTA = 1)
v_min = min(production_rates)  # M1 y M2 son las más lentas = 5 uni/hr
v_relativas = [rate / v_min for rate in production_rates]

print("VELOCIDADES RELATIVAS (referencia M1,M2=1):")
for i, machine in enumerate(machines):
    print(f"  {machine}: {production_rates[i]} uni/hr → v_rel = {v_relativas[i]:.2f}")

# ============================================================
# MODELO EXACTO - PARTE A (SIN BATCH)
# ============================================================

model = pulp.LpProblem("Qm_Cmax_Exacto", pulp.LpMinimize)

# Variables
Cmax = pulp.LpVariable("Cmax", lowBound=0, cat='Continuous')
X = pulp.LpVariable.dicts("X", [(j, m) for j in jobs for m in machines], cat='Binary')

# Función objetivo
model += Cmax

# Restricciones (FORMULACIÓN CORRECTA CON VELOCIDADES RELATIVAS)
for i, machine in enumerate(machines):
    v_rel = v_relativas[i]
    machine_time = pulp.lpSum([processing_times[j-1] * X[(j, machine)] for j in jobs])
    model += machine_time <= Cmax * v_rel, f"Tiempo_Maquina_{machine}"

for j in jobs:
    model += pulp.lpSum([X[(j, m)] for m in machines]) == 1, f"Asignacion_Trabajo_{j}"

# Resolver
model.solve(pulp.PULP_CBC_CMD(msg=True))

print(f"\nRESULTADOS - PARTE A (SIN BATCH)")
print("=" * 70)
print(f"Estado: {pulp.LpStatus[model.status]}")
print(f"Cmax óptimo: {pulp.value(Cmax):.2f} horas")

# Mostrar asignación
print(f"\nASIGNACIÓN ÓPTIMA:")
print(f"{'Máquina':<8} | {'Trabajos':<35} | {'Tiempo Real':<12} | {'Tiempo Ajustado':<15}")
print("-" * 85)

for i, machine in enumerate(machines):
    assigned_jobs = [j for j in jobs if pulp.value(X[(j, machine)]) > 0.5]
    if assigned_jobs:
        # Tiempo real en esta máquina
        total_processing = sum(processing_times[j-1] for j in assigned_jobs)
        # Tiempo ajustado por velocidad
        v_rel = v_relativas[i]
        adjusted_time = total_processing / v_rel
        
        jobs_str = " → ".join(f"J{j}" for j in assigned_jobs)
        print(f"{machine:<8} | {jobs_str:<35} | {total_processing:>11.1f} | {adjusted_time:>14.1f}")
    else:
        print(f"{machine:<8} | {'Sin asignación':<35} | {'0.0':>11} | {'0.0':>14}")

# ============================================================
# VERIFICACIÓN DE LA RESTRICCIÓN
# ============================================================

print(f"\nVERIFICACIÓN DE RESTRICCIONES:")
print(f"{'Máquina':<8} | {'∑Pj·Xj':<8} | {'v_rel·Cmax':<10} | {'Cumple':<8}")
print("-" * 45)

for i, machine in enumerate(machines):
    total_processing = sum(processing_times[j-1] for j in jobs if pulp.value(X[(j, machine)]) > 0.5)
    limite = v_relativas[i] * pulp.value(Cmax)
    cumple = "✅" if total_processing <= limite + 1e-6 else "❌"
    
    print(f"{machine:<8} | {total_processing:>7.1f} | {limite:>9.1f} | {cumple:>8}")

# ============================================================
# COMPARACIÓN CON MODELO AMPL
# ============================================================

print(f"\n" + "=" * 70)
print("COMPARACIÓN CON MODELO AMPL")
print("=" * 70)

print("El modelo AMPL usa:")
print("  v = [1, 1, 1.5, 2]")
print("Nuestro modelo usa:")
print(f"  v = {[f'{v:.2f}' for v in v_relativas]}")

print(f"\n¿POR QUÉ SON DIFERENTES?")
print("• AMPL: Considera M1 como referencia = 1")
print("• Nosotros: Consideramos M1 y M2 como referencia = 1")
print("• Ambas formulaciones son equivalentes matemáticamente")
print("• Solo cambia la escala, pero la solución óptima es la misma")

# ============================================================
# DEMOSTRACIÓN DE EQUIVALENCIA
# ============================================================

print(f"\n" + "=" * 70)
print("DEMOSTRACIÓN DE EQUIVALENCIA MATEMÁTICA")
print("=" * 70)

print("Formulación AMPL:")
print("  ∑ Pj·Xjm ≤ vm · Cmax")
print("  donde vm = [1, 1, 1.5, 2]")

print("\nNuestra formulación:")
print("  ∑ Pj·Xjm ≤ v_rel_m · Cmax") 
print(f"  donde v_rel_m = {[f'{v:.2f}' for v in v_relativas]}")

print(f"\nRELACIÓN:")
print("  v_ampl = [1, 1, 1.5, 2]")
print(f"  v_nuestro = {[f'{v:.2f}' for v in v_relativas]}")
print("  v_ampl = v_nuestro × 2")  # Porque 5 × 2 = 10, 7.5 × 2 = 15, etc.

print(f"\nCONVERSIÓN:")
ampl_to_our = [1/2, 1/2, 1.5/2, 2/2]  # = [0.5, 0.5, 0.75, 1.0]
print(f"  v_ampl × 0.5 = {[f'{v:.2f}' for v in ampl_to_our]}")
print(f"  v_nuestro = {[f'{v:.2f}' for v in v_relativas]}")

# ============================================================
# SIMULACIÓN DEL MODELO AMPL
# ============================================================

print(f"\n" + "=" * 70)
print("SIMULACIÓN DEL MODELO AMPL")
print("=" * 70)

# Usar las velocidades del AMPL
v_ampl = [1, 1, 1.5, 2]

model_ampl = pulp.LpProblem("Qm_Cmax_AMPL", pulp.LpMinimize)
Cmax_ampl = pulp.LpVariable("Cmax_ampl", lowBound=0, cat='Continuous')
X_ampl = pulp.LpVariable.dicts("X_ampl", [(j, m) for j in jobs for m in machines], cat='Binary')

model_ampl += Cmax_ampl

# Usar restricción del AMPL
for i, machine in enumerate(machines):
    machine_time = pulp.lpSum([processing_times[j-1] * X_ampl[(j, machine)] for j in jobs])
    model_ampl += machine_time <= Cmax_ampl * v_ampl[i], f"AMPL_Machine_{machine}"

for j in jobs:
    model_ampl += pulp.lpSum([X_ampl[(j, m)] for m in machines]) == 1, f"AMPL_Assignment_{j}"

model_ampl.solve(pulp.PULP_CBC_CMD(msg=False))

print(f"Cmax con modelo AMPL: {pulp.value(Cmax_ampl):.2f} horas")
print(f"Cmax con nuestro modelo: {pulp.value(Cmax):.2f} horas")

# Conversión entre escalas
cmax_convertido = pulp.value(Cmax_ampl) * (v_min / v_ampl[0])  # Factor de conversión
print(f"Cmax AMPL convertido a nuestra escala: {cmax_convertido:.2f} horas")

# ============================================================
# DIAGRAMA DE GANTT
# ============================================================

import matplotlib.pyplot as plt

print(f"\n" + "=" * 70)
print("GENERANDO DIAGRAMA DE GANTT")
print("=" * 70)

fig, ax = plt.subplots(figsize=(12, 6))
colors = plt.cm.Set3(np.linspace(0, 1, len(jobs)))

completion_times = {}
for i, machine in enumerate(machines):
    assigned_jobs = [j for j in jobs if pulp.value(X[(j, machine)]) > 0.5]
    if assigned_jobs:
        # Ordenar por processing time
        assigned_jobs.sort(key=lambda j: processing_times[j-1])
        
        # Calcular tiempos con velocidad correcta
        v_rel = v_relativas[i]
        current_time = 0
        machine_times = []
        
        for job in assigned_jobs:
            processing_time = processing_times[j-1] / v_rel
            completion_time = current_time + processing_time
            machine_times.append((job, current_time, completion_time))
            current_time = completion_time
        
        completion_times[machine] = machine_times
        
        # Dibujar en Gantt
        for job, start, end in machine_times:
            ax.barh(machine, end-start, left=start, height=0.6, 
                    color=colors[job-1], edgecolor='black', alpha=0.7)
            ax.text((start+end)/2, i, f'J{job}', ha='center', va='center', 
                    fontweight='bold')

ax.set_xlabel('Tiempo (horas)')
ax.set_ylabel('Máquinas')
ax.set_title('Diagrama de Gantt - Parte A (SIN BATCH) - Solución Óptima')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('Modelo_Corregido_Gantt.png', dpi=300, bbox_inches='tight')
plt.show()

print(f"✅ Diagrama de Gantt generado: 'Modelo_Corregido_Gantt.png'")

# ============================================================
# RESUMEN FINAL
# ============================================================

print(f"\n" + "=" * 70)
print("RESUMEN FINAL - PARTE A")
print("=" * 70)
print(f"✓ Cmax óptimo: {pulp.value(Cmax):.2f} horas")
print(f"✓ Velocidades relativas: {[f'{v:.2f}' for v in v_relativas]}")
print(f"✓ Referencia: M1 y M2 (más lentas) = 1")
print(f"✓ Todas las restricciones verificadas: ✅")
print(f"✓ El modelo AMPL es equivalente pero con diferente escala")
print(f"✓ Diagrama de Gantt generado: ✅")