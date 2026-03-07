import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# PROBLEMA FLOW SHOP - ALGORITMO DE JOHNSON (DATOS REALES)
# ============================================================

print("PROBLEMA FLOW SHOP - 7 TRABAJOS, 2 MÁQUINAS")
print("=" * 70)

# --------------------------
# DATOS REALES DEL PROBLEMA
# --------------------------
jobs = [1, 2, 3, 4, 5, 6, 7]

# Tiempos de procesamiento en cada máquina (horas)
processing_times = {
    1: [9, 6],   # J1: 9h en M1, 6h en M2
    2: [8, 5],   # J2: 8h en M1, 5h en M2
    3: [7, 7],   # J3: 7h en M1, 7h en M2
    4: [6, 3],   # J4: 6h en M1, 3h en M2
    5: [1, 2],   # J5: 1h en M1, 2h en M2
    6: [2, 6],   # J6: 2h en M1, 6h en M2
    7: [4, 7]    # J7: 4h en M1, 7h en M2
}

# Fechas de entrega (due dates)
due_dates = {
    1: 16, 2: 25, 3: 30, 4: 10, 5: 12, 6: 8, 7: 20
}

print("DATOS DE PROCESAMIENTO (horas):")
print(f"{'Job':>4} | {'M1':>4} | {'M2':>4} | {'Dj':>4}")
print("-" * 30)
for j in jobs:
    print(f"{j:4} | {processing_times[j][0]:4} | {processing_times[j][1]:4} | {due_dates[j]:4}")

# ============================================================
# a) ALGORITMO DE JOHNSON
# ============================================================

print(f"\n" + "=" * 70)
print("a) APLICACIÓN DEL ALGORITMO DE JOHNSON")
print("=" * 70)

def johnson_algorithm(jobs, processing_times):
    """
    Implementa el algoritmo de Johnson para 2 máquinas
    """
    # Listas para trabajos con menor tiempo en M1 y M2
    list1 = []  # Trabajos con p1j <= p2j
    list2 = []  # Trabajos con p1j > p2j
    
    for j in jobs:
        p1 = processing_times[j][0]
        p2 = processing_times[j][1]
        
        if p1 <= p2:
            list1.append((j, p1, p2))
        else:
            list2.append((j, p1, p2))
    
    # Ordenar list1 por tiempo en M1 (ascendente)
    list1_sorted = sorted(list1, key=lambda x: x[1])
    
    # Ordenar list2 por tiempo en M2 (descendente)
    list2_sorted = sorted(list2, key=lambda x: x[2], reverse=True)
    
    # Secuencia óptima
    optimal_sequence = [job[0] for job in list1_sorted] + [job[0] for job in list2_sorted]
    
    return optimal_sequence

# Aplicar algoritmo de Johnson
optimal_sequence = johnson_algorithm(jobs, processing_times)

print("PASOS DEL ALGORITMO:")
print("1. Separar trabajos donde p1j ≤ p2j y p1j > p2j")

list1 = []
list2 = []
for j in jobs:
    p1, p2 = processing_times[j]
    if p1 <= p2:
        list1.append((j, p1, p2))
    else:
        list2.append((j, p1, p2))

print(f"   Grupo 1 (p1j ≤ p2j): {[f'J{j[0]}' for j in list1]}")
print(f"   Grupo 2 (p1j > p2j): {[f'J{j[0]}' for j in list2]}")

print("2. Ordenar grupo 1 por p1j ascendente")
list1_sorted = sorted(list1, key=lambda x: x[1])
print(f"   Grupo 1 ordenado: {[f'J{j[0]}' for j in list1_sorted]}")

print("3. Ordenar grupo 2 por p2j descendente")
list2_sorted = sorted(list2, key=lambda x: x[2], reverse=True)
print(f"   Grupo 2 ordenado: {[f'J{j[0]}' for j in list2_sorted]}")

print("4. Concatenar secuencias")
print(f"   Secuencia final: {[f'J{j[0]}' for j in list1_sorted]} + {[f'J{j[0]}' for j in list2_sorted]}")

print(f"\nSECUENCIA ÓPTIMA (Johnson):")
sequence_str = " → ".join(f"J{j}" for j in optimal_sequence)
print(f" {sequence_str}")

# ============================================================
# b) CÁLCULO DE Cj Y Cmax
# ============================================================

print(f"\n" + "=" * 70)
print("b) CÁLCULO DE Cj Y Cmax")
print("=" * 70)

def calculate_completion_times(sequence, processing_times):
    """
    Calcula tiempos de finalización para secuencia dada
    """
    n = len(sequence)
    completion_m1 = [0] * n
    completion_m2 = [0] * n
    start_m2 = [0] * n
    
    # Calcular tiempos en M1
    for i, job in enumerate(sequence):
        if i == 0:
            completion_m1[i] = processing_times[job][0]
        else:
            completion_m1[i] = completion_m1[i-1] + processing_times[job][0]
    
    # Calcular tiempos en M2
    for i, job in enumerate(sequence):
        if i == 0:
            start_m2[i] = completion_m1[i]
            completion_m2[i] = start_m2[i] + processing_times[job][1]
        else:
            start_m2[i] = max(completion_m1[i], completion_m2[i-1])
            completion_m2[i] = start_m2[i] + processing_times[job][1]
    
    return completion_m1, completion_m2, start_m2

# Calcular tiempos de finalización
comp_m1, comp_m2, start_m2 = calculate_completion_times(optimal_sequence, processing_times)

print(f"{'Job':>4} | {'Inicio M1':>9} | {'Fin M1':>6} | {'Inicio M2':>9} | {'Fin M2':>6} | {'Cj':>4}")
print("-" * 65)

cj_values = {}
for i, job in enumerate(optimal_sequence):
    cj_values[job] = comp_m2[i]
    print(f"J{job:3} | {comp_m1[i]-processing_times[job][0]:9.1f} | {comp_m1[i]:6.1f} | "
          f"{start_m2[i]:9.1f} | {comp_m2[i]:6.1f} | {comp_m2[i]:4.1f}")

Cmax = max(comp_m2)
print(f"\nCmax (Makespan): {Cmax:.1f} horas")

# ============================================================
# c) DIAGRAMA DE GANTT
# ============================================================

print(f"\n" + "=" * 70)
print("c) DIAGRAMA DE GANTT")
print("=" * 70)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))

colors = plt.cm.Set3(np.linspace(0, 1, len(jobs)))

# Diagrama para M1
for i, job in enumerate(optimal_sequence):
    start = comp_m1[i] - processing_times[job][0]
    end = comp_m1[i]
    ax1.barh('M1', end-start, left=start, height=0.4, 
            color=colors[job-1], edgecolor='black', alpha=0.8)
    ax1.text((start+end)/2, 0, f'J{job}', ha='center', va='center', 
            fontweight='bold', fontsize=10)

# Diagrama para M2
for i, job in enumerate(optimal_sequence):
    start = start_m2[i]
    end = comp_m2[i]
    ax2.barh('M2', end-start, left=start, height=0.4, 
            color=colors[job-1], edgecolor='black', alpha=0.8)
    ax2.text((start+end)/2, 0, f'J{job}', ha='center', va='center', 
            fontweight='bold', fontsize=10)

ax1.set_xlabel('Tiempo (horas)')
ax1.set_title('MÁQUINA 1')
ax1.grid(True, alpha=0.3)
ax1.set_xlim(0, Cmax + 5)

ax2.set_xlabel('Tiempo (horas)')
ax2.set_title('MÁQUINA 2')
ax2.grid(True, alpha=0.3)
ax2.set_xlim(0, Cmax + 5)

plt.suptitle('DIAGRAMA DE GANTT - FLOW SHOP (Algoritmo de Johnson)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('FlowShop_Johnson_Gantt.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Diagrama de Gantt generado: 'FlowShop_Johnson_Gantt.png'")

# ============================================================
# d) MEDIDAS DE DESEMPEÑO
# ============================================================

print(f"\n" + "=" * 70)
print("d) MEDIDAS DE DESEMPEÑO")
print("=" * 70)

# Calcular medidas de desempeño
completion_times = [comp_m2[i] for i in range(len(optimal_sequence))]
tardiness = [max(0, comp_m2[i] - due_dates[optimal_sequence[i]]) for i in range(len(optimal_sequence))]
flow_times = [comp_m2[i] for i in range(len(optimal_sequence))]  # Cj mismo que flow time

# NT - Número de trabajos tardíos
NT = sum(1 for t in tardiness if t > 0)

# Tmax - Tardanza máxima
Tmax = max(tardiness) if tardiness else 0

# ΣTj - Suma de tardanzas
sum_Tj = sum(tardiness)

# F̅ - Tiempo de flujo promedio
F_bar = np.mean(flow_times)

# Im - Tiempo inactivo de M2
idle_m2 = 0
for i in range(len(optimal_sequence)):
    if i == 0:
        idle_m2 += start_m2[i]  # Tiempo antes del primer trabajo en M2
    else:
        idle_m2 += max(0, start_m2[i] - comp_m2[i-1])  # Tiempo entre trabajos en M2

print(f"MEDIDAS CALCULADAS:")
print(f"NT (Número de trabajos tardíos): {NT}")
print(f"Tmax (Tardanza máxima): {Tmax:.1f} horas")
print(f"ΣTj (Suma de tardanzas): {sum_Tj:.1f} horas")
print(f"F̅ (Tiempo de flujo promedio): {F_bar:.1f} horas")
print(f"Im (Tiempo inactivo M2): {idle_m2:.1f} horas")

# Tabla detallada
print(f"\nDETALLE POR TRABAJO:")
print(f"{'Job':>4} | {'Cj':>6} | {'Dj':>6} | {'Tj':>6} | {'Tardío':>8}")
print("-" * 45)
for i, job in enumerate(optimal_sequence):
    tardio = "Sí" if tardiness[i] > 0 else "No"
    print(f"J{job:3} | {comp_m2[i]:6.1f} | {due_dates[job]:6.1f} | {tardiness[i]:6.1f} | {tardio:>8}")

# ============================================================
# e) PROGRAMA ALTERNATIVO PARA MINIMIZAR TARDANZAS
# ============================================================

print(f"\n" + "=" * 70)
print("e) PROGRAMA ALTERNATIVO - MINIMIZAR TARDANZAS")
print("=" * 70)

print("ANÁLISIS DE ALTERNATIVAS:")

# Alternativa 1: EDD (Earliest Due Date)
edd_sequence = sorted(jobs, key=lambda x: due_dates[x])
comp_m1_edd, comp_m2_edd, start_m2_edd = calculate_completion_times(edd_sequence, processing_times)
tardiness_edd = [max(0, comp_m2_edd[i] - due_dates[edd_sequence[i]]) for i in range(len(edd_sequence))]
sum_Tj_edd = sum(tardiness_edd)
NT_edd = sum(1 for t in tardiness_edd if t > 0)
Cmax_edd = max(comp_m2_edd)

# Alternativa 2: SPT en M1 (Shortest Processing Time)
spt_sequence = sorted(jobs, key=lambda x: processing_times[x][0])
comp_m1_spt, comp_m2_spt, start_m2_spt = calculate_completion_times(spt_sequence, processing_times)
tardiness_spt = [max(0, comp_m2_spt[i] - due_dates[spt_sequence[i]]) for i in range(len(spt_sequence))]
sum_Tj_spt = sum(tardiness_spt)
NT_spt = sum(1 for t in tardiness_spt if t > 0)
Cmax_spt = max(comp_m2_spt)

# Alternativa 3: SPT en M2
spt_m2_sequence = sorted(jobs, key=lambda x: processing_times[x][1])
comp_m1_spt2, comp_m2_spt2, start_m2_spt2 = calculate_completion_times(spt_m2_sequence, processing_times)
tardiness_spt2 = [max(0, comp_m2_spt2[i] - due_dates[spt_m2_sequence[i]]) for i in range(len(spt_m2_sequence))]
sum_Tj_spt2 = sum(tardiness_spt2)
NT_spt2 = sum(1 for t in tardiness_spt2 if t > 0)
Cmax_spt2 = max(comp_m2_spt2)

print(f"COMPARACIÓN DE ESTRATEGIAS:")
print(f"{'Estrategia':<15} | {'ΣTj':>8} | {'NT':>4} | {'Cmax':>6}")
print("-" * 50)
print(f"{'Johnson':<15} | {sum_Tj:>8.1f} | {NT:>4} | {Cmax:>6.1f}")
print(f"{'EDD':<15} | {sum_Tj_edd:>8.1f} | {NT_edd:>4} | {Cmax_edd:>6.1f}")
print(f"{'SPT-M1':<15} | {sum_Tj_spt:>8.1f} | {NT_spt:>4} | {Cmax_spt:>6.1f}")
print(f"{'SPT-M2':<15} | {sum_Tj_spt2:>8.1f} | {NT_spt2:>4} | {Cmax_spt2:>6.1f}")

# Recomendación
strategies = [
    (sum_Tj, "Johnson", NT, Cmax, optimal_sequence),
    (sum_Tj_edd, "EDD", NT_edd, Cmax_edd, edd_sequence),
    (sum_Tj_spt, "SPT-M1", NT_spt, Cmax_spt, spt_sequence),
    (sum_Tj_spt2, "SPT-M2", NT_spt2, Cmax_spt2, spt_m2_sequence)
]

best_strategy = min(strategies, key=lambda x: x[0])

print(f"\n🎯 RECOMENDACIÓN PARA MINIMIZAR TARDANZAS:")
print(f"Estrategia: {best_strategy[1]}")
print(f"ΣTj: {best_strategy[0]:.1f} horas")
print(f"NT: {best_strategy[2]} trabajos tardíos")
print(f"Cmax: {best_strategy[3]:.1f} horas")
print(f"Secuencia: {' → '.join(f'J{j}' for j in best_strategy[4])}")

# Análisis adicional
print(f"\nANÁLISIS DETALLADO:")
print(f"• Johnson: Optimiza Cmax pero puede tener altas tardanzas")
print(f"• EDD: Minimiza trabajos tardíos pero puede tener alto Cmax")  
print(f"• SPT-M1: Rápido inicio pero depende de M2")
print(f"• SPT-M2: Considera la máquina cuello de botella")

# ============================================================
# RESUMEN FINAL
# ============================================================

print(f"\n" + "=" * 70)
print("RESUMEN FINAL - FLOW SHOP")
print("=" * 70)
print(f"a) Secuencia óptima (Johnson): {sequence_str}")
print(f"b) Cmax: {Cmax:.1f} horas")
print(f"c) Diagrama de Gantt generado")
print(f"d) Medidas: NT={NT}, Tmax={Tmax:.1f}, ΣTj={sum_Tj:.1f}, F̅={F_bar:.1f}, Im={idle_m2:.1f}")
print(f"e) Estrategia recomendada para tardanzas: {best_strategy[1]}")

print(f"\n¡ANÁLISIS COMPLETADO! ✅")