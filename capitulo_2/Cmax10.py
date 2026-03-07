import pandas as pd
import numpy as np
import pulp

# ============================================================
# MODELO PYTHON - PROBLEMA Qm || Cmax (Máquinas con distinta velocidad)
# Objetivo: Minimizar el makespan total
# ============================================================

# --------------------------
# DATOS
# --------------------------

# Conjuntos
J = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Trabajos
M = ['M1', 'M2', 'M3']               # Máquinas

# Tiempos de procesamiento base (en la máquina más lenta)
Pj = {
    1: 15, 2: 20, 3: 10, 4: 30, 5: 25,
    6: 18, 7: 12, 8: 6, 9: 4, 10: 2
}

# Velocidades relativas
# M1 = 8/4 = 2
# M2 = 10/4 = 2.5  
# M3 = 4/4 = 1
v = {
    'M1': 2,
    'M2': 2.5,
    'M3': 1
}

# --------------------------
# CÁLCULO DE TIEMPOS EFECTIVOS
# --------------------------
print("CALCULANDO TIEMPOS EFECTIVOS DE PROCESAMIENTO:")
print("=" * 60)
print(f"{'Trabajo':<8} {'Pj':<6} {'M1 (v=2)':<10} {'M2 (v=2.5)':<12} {'M3 (v=1)':<10}")
print("-" * 60)

p = {}  # Diccionario para tiempos efectivos p[j,m]
for j in J:
    p_jm = []
    for m in M:
        tiempo_efectivo = Pj[j] / v[m]
        p[(j, m)] = tiempo_efectivo
        p_jm.append(f"{tiempo_efectivo:.2f}")
    
    print(f"J{j:<7} {Pj[j]:<6} {p_jm[0]:<10} {p_jm[1]:<12} {p_jm[2]:<10}")

# --------------------------
# MODELO DE OPTIMIZACIÓN
# --------------------------
model = pulp.LpProblem("Qm_Cmax_Optimization", pulp.LpMinimize)

# --------------------------
# VARIABLES
# --------------------------
print(f"\nCREANDO VARIABLES...")

# Variable binaria: 1 si el trabajo j se asigna a la máquina m
x = pulp.LpVariable.dicts("x", 
                         [(j, m) for j in J for m in M],
                         cat='Binary')

# Variable continua: Tiempo total (makespan)
Cmax = pulp.LpVariable("Cmax", lowBound=0, cat='Continuous')

# Variables continuas: Carga total en cada máquina
load = pulp.LpVariable.dicts("load", M, lowBound=0, cat='Continuous')

print(f"✓ {len(x)} variables binarias x[j,m] creadas")
print(f"✓ 1 variable continua Cmax creada")  
print(f"✓ {len(load)} variables continuas load[m] creadas")

# --------------------------
# RESTRICCIONES
# --------------------------
print(f"\nAGREGANDO RESTRICCIONES...")

# Restricción 1: Cada trabajo se asigna exactamente a una máquina
for j in J:
    model += pulp.lpSum([x[(j, m)] for m in M]) == 1, f"Asignacion_Trabajo_{j}"
print("✓ Restricción de asignación única por trabajo agregada")

# Restricción 2: Carga total de trabajo en cada máquina
for m in M:
    model += load[m] == pulp.lpSum([p[(j, m)] * x[(j, m)] for j in J]), f"Carga_Maquina_{m}"
print("✓ Restricción de carga por máquina agregada")

# Restricción 3: El makespan debe ser mayor o igual a la carga de cualquier máquina
for m in M:
    model += Cmax >= load[m], f"Restriccion_Makespan_{m}"
print("✓ Restricción de makespan agregada")

# --------------------------
# FUNCIÓN OBJETIVO
# --------------------------
model += Cmax, "Min_Cmax"
print("✓ Función objetivo: Minimizar Cmax")

# --------------------------
# RESOLUCIÓN
# --------------------------
print(f"\n" + "=" * 60)
print("RESOLVIENDO EL MODELO...")
print("=" * 60)

solver = pulp.PULP_CBC_CMD(msg=True)
model.solve(solver)

# --------------------------
# RESULTADOS
# --------------------------
print(f"\n" + "=" * 60)
print("RESULTADOS OBTENIDOS")
print("=" * 60)

print(f"Estado de la solución: {pulp.LpStatus[model.status]}")
print(f"Valor óptimo de Cmax: {pulp.value(Cmax):.6f}")

print(f"\nCARGAS POR MÁQUINA:")
print(f"{'Máquina':<8} {'Velocidad':<10} {'Carga':<12} {'% del Cmax':<12}")
print("-" * 50)

for m in M:
    carga_valor = pulp.value(load[m])
    porcentaje = (carga_valor / pulp.value(Cmax)) * 100 if pulp.value(Cmax) > 0 else 0
    print(f"{m:<8} {v[m]:<10} {carga_valor:<12.6f} {porcentaje:<12.2f}%")

# --------------------------
# ASIGNACIÓN DETALLADA
# --------------------------
print(f"\n" + "=" * 60)
print("ASIGNACIÓN DETALLADA POR MÁQUINA")
print("=" * 60)

for m in M:
    print(f"\nMáquina {m} (Velocidad: {v[m]}):")
    print("-" * 40)
    
    # Obtener trabajos asignados a esta máquina
    trabajos_asignados = []
    carga_total = 0
    
    for j in J:
        if pulp.value(x[(j, m)]) > 0.5:
            tiempo_procesamiento = p[(j, m)]
            trabajos_asignados.append((j, tiempo_procesamiento))
            carga_total += tiempo_procesamiento
    
    # Ordenar trabajos por tiempo de procesamiento
    trabajos_asignados.sort(key=lambda x: x[1])
    
    # Mostrar trabajos
    if trabajos_asignados:
        print("Trabajos asignados: ", end="")
        secuencia = []
        for job, tiempo in trabajos_asignados:
            secuencia.append(f"J{job}({tiempo:.2f})")
        print(" → ".join(secuencia))
        
        print(f"Carga total: {carga_total:.6f}")
        print(f"Número de trabajos: {len(trabajos_asignados)}")
    else:
        print("No hay trabajos asignados")

# --------------------------
# TABLA COMPLETA DE ASIGNACIONES
# --------------------------
print(f"\n" + "=" * 60)
print("TABLA COMPLETA DE ASIGNACIONES")
print("=" * 60)

print(f"{'Trabajo':<8} {'Pj_base':<10} {'Máquina':<10} {'Tiempo_Real':<12} {'Cj':<12}")
print("-" * 60)

# Calcular tiempos de finalización (Cj)
cj_values = {}
for m in M:
    tiempo_acumulado = 0
    trabajos_maquina = [(j, p[(j, m)]) for j in J if pulp.value(x[(j, m)]) > 0.5]
    # Ordenar por tiempo de procesamiento para secuenciación SPT
    trabajos_maquina.sort(key=lambda x: x[1])
    
    for job, tiempo in trabajos_maquina:
        tiempo_acumulado += tiempo
        cj_values[job] = tiempo_acumulado

# Mostrar tabla ordenada por trabajo
for j in sorted(J):
    maquina_asignada = next((m for m in M if pulp.value(x[(j, m)]) > 0.5), "Ninguna")
    tiempo_real = p[(j, maquina_asignada)] if maquina_asignada != "Ninguna" else 0
    cj = cj_values.get(j, 0)
    
    print(f"J{j:<7} {Pj[j]:<10} {maquina_asignada:<10} {tiempo_real:<12.6f} {cj:<12.6f}")

# --------------------------
# ESTADÍSTICAS
# --------------------------
print(f"\n" + "=" * 60)
print("ESTADÍSTICAS DEL PROGRAMA")
print("=" * 60)

# Calcular métricas
cargas = [pulp.value(load[m]) for m in M]
carga_max = max(cargas)
carga_min = min(cargas)
balance_ratio = carga_max / carga_min if carga_min > 0 else float('inf')

suma_cj = sum(cj_values.values())
promedio_cj = suma_cj / len(J) if J else 0

print(f"Cmax (Makespan): {pulp.value(Cmax):.6f}")
print(f"ΣCj (Suma de tiempos de finalización): {suma_cj:.6f}")
print(f"Cj promedio: {promedio_cj:.6f}")
print(f"Balance (carga_max/carga_min): {balance_ratio:.6f}")
print(f"Utilización promedio: {(sum(cargas) / (pulp.value(Cmax) * len(M))) * 100:.2f}%")

# --------------------------
# VERIFICACIÓN DE RESTRICCIONES
# --------------------------
print(f"\n" + "=" * 60)
print("VERIFICACIÓN DE RESTRICCIONES")
print("=" * 60)

# Verificar asignación única
asignaciones_correctas = True
for j in J:
    total_asignado = sum(pulp.value(x[(j, m)]) for m in M)
    if abs(total_asignado - 1.0) > 1e-6:
        print(f"❌ Trabajo J{j} asignado a {total_asignado} máquinas")
        asignaciones_correctas = False

if asignaciones_correctas:
    print("✓ Todos los trabajos asignados exactamente a una máquina")

# Verificar makespan
makespan_correcto = True
for m in M:
    if pulp.value(load[m]) > pulp.value(Cmax) + 1e-6:
        print(f"❌ Carga de {m} ({pulp.value(load[m]):.6f}) > Cmax ({pulp.value(Cmax):.6f})")
        makespan_correcto = False

if makespan_correcto:
    print("✓ Cmax es mayor o igual a todas las cargas de máquinas")

# --------------------------
# EXPORTACIÓN DE RESULTADOS
# --------------------------
try:
    # Crear DataFrames para exportación
    df_asignaciones = pd.DataFrame({
        'Trabajo': J,
        'Pj_Base': [Pj[j] for j in J],
        'Maquina_Asignada': [next((m for m in M if pulp.value(x[(j, m)]) > 0.5), "Ninguna") for j in J],
        'Tiempo_Real': [p[(j, next((m for m in M if pulp.value(x[(j, m)]) > 0.5), "Ninguna"))] for j in J],
        'Cj': [cj_values.get(j, 0) for j in J]
    })
    
    df_maquinas = pd.DataFrame({
        'Maquina': M,
        'Velocidad': [v[m] for m in M],
        'Carga_Total': [pulp.value(load[m]) for m in M],
        'Num_Trabajos': [sum(1 for j in J if pulp.value(x[(j, m)]) > 0.5) for m in M],
        'Porcentaje_Uso': [(pulp.value(load[m]) / pulp.value(Cmax)) * 100 for m in M]
    })
    
    df_metricas = pd.DataFrame([{
        'Cmax': pulp.value(Cmax),
        'Sigma_Cj': suma_cj,
        'Cj_Promedio': promedio_cj,
        'Ratio_Balance': balance_ratio,
        'Utilizacion_Promedio': (sum(cargas) / (pulp.value(Cmax) * len(M))) * 100
    }])
    
    # Exportar a Excel
    out_xlsx = "Qm_Cmax_Modelo_Completo.xlsx"
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        df_asignaciones.to_excel(writer, index=False, sheet_name="Asignaciones")
        df_maquinas.to_excel(writer, index=False, sheet_name="Maquinas")
        df_metricas.to_excel(writer, index=False, sheet_name="Metricas")
    
    print(f"\n✅ Resultados exportados a {out_xlsx}")
    
except Exception as e:
    print(f"\n⚠️ Error en la exportación: {e}")

print(f"\n" + "=" * 60)
print("PROGRAMA COMPLETADO")
print("=" * 60)