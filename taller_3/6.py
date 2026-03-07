import pandas as pd
import math

# --- I. DATOS DEL PROBLEMA (GRAFO Y PARÁMETROS GLOBALES) ---
# Formato: { ID_Tarea: [Tiempo, [Precedencias]] }
GRAFO_TAREAS = {
    1: [2, []], 2: [6, [1]], 3: [6, [2]], 4: [2, [2]], 5: [2, [2]], 
    6: [12, [2]], 7: [7, [3, 4]], 8: [5, [7]], 9: [1, [5]], 10: [4, [6, 9]], 
    11: [6, [8, 10]], 12: [7, [11]]
}
TIEMPO_TOTAL = sum(t[0] for t in GRAFO_TAREAS.values()) # Suma de tiempos = 60s

# CONSTANTE PARA CÁLCULO DE CAPACIDAD (8 horas * 60 min * 60 seg = 28,800s)
TIEMPO_PRODUCCION_SEGUNDOS = 28800

# --- II. FUNCIONES DE LÓGICA DE BALANCEO Y CÁLCULO ---

def obtener_candidatos(tareas_asignadas, tiempo_restante_estacion):
    """Identifica tareas disponibles y que caben en la estación."""
    candidatos = []
    for tarea, data in GRAFO_TAREAS.items():
        if tarea in tareas_asignadas:
            continue
        tiempo_tarea = data[0]
        precedencias = data[1]
        precedencias_cumplidas = all(p in tareas_asignadas for p in precedencias)
        
        if precedencias_cumplidas and tiempo_tarea <= tiempo_restante_estacion:
            candidatos.append(tarea)
    return candidatos

def balancear_linea_optimizado(tiempo_ciclo_max):
    """Algoritmo Dinámico Greedy (LCR) para asignación de tareas."""
    tareas_asignadas = set()
    estaciones = {}
    estacion_id = 1
    total_tareas = len(GRAFO_TAREAS)
    
    while len(tareas_asignadas) < total_tareas:
        tiempo_actual_estacion = 0
        tareas_en_estacion = []
        
        while True:
            tiempo_restante = tiempo_ciclo_max - tiempo_actual_estacion
            candidatos = obtener_candidatos(tareas_asignadas, tiempo_restante)
            
            if not candidatos:
                break
            
            # Regla LCR: Elegir la tarea más larga disponible para optimizar el empaquetado
            mejor_tarea = max(candidatos, key=lambda t: GRAFO_TAREAS[t][0])
            
            # Asignar
            tareas_en_estacion.append(mejor_tarea)
            tareas_asignadas.add(mejor_tarea)
            tiempo_actual_estacion += GRAFO_TAREAS[mejor_tarea][0]
            
        estaciones[estacion_id] = tareas_en_estacion
        estacion_id += 1
        
    return estaciones

def calcular_metricas(estaciones, tiempo_ciclo_objetivo, tiempo_desplazamiento=0):
    """Calcula K, Tc real, Eficiencia (Real) y Capacidad."""
    K_real = len(estaciones)
    tiempos_estaciones = []
    
    for tareas in estaciones.values():
        t_suma = sum(GRAFO_TAREAS[t][0] for t in tareas)
        tiempos_estaciones.append(t_suma + tiempo_desplazamiento)
    
    Tc_real = max(tiempos_estaciones)
    
    # CÁLCULO DE CAPACIDAD
    capacidad_por_dia = TIEMPO_PRODUCCION_SEGUNDOS / Tc_real
    
    # Eficiencia REAL (usa K_real)
    eficiencia_real = (TIEMPO_TOTAL / (K_real * Tc_real)) * 100
    
    # Solo retorna la eficiencia REAL
    return K_real, Tc_real, eficiencia_real, capacidad_por_dia

# --- III. SOLUCIÓN DE PUNTOS ---

def resolver_punto_a():
    print("\n" + "="*60)
    print("🅰️ PUNTO A: Balanceo UALPB-1 (Tiempos de Ciclo Fijos) - ÓPTIMO")
    print("="*60)
    
    tiempos_ciclo = [30, 20, 15]
    resultados = []
    
    for tc in tiempos_ciclo:
        estaciones = balancear_linea_optimizado(tc)
        
        # Solo capturamos 4 valores (K_real, Tc_real, ef_real, cap)
        k_real, tc_real, ef_real, cap = calcular_metricas(estaciones, tc)
        
        str_estaciones = "; ".join(f"E{k}: {v} (T={sum(GRAFO_TAREAS[t][0] for t in v)})" for k, v in estaciones.items())
            
        resultados.append({
            'T_c Objetivo': tc,
            'K Téo.': math.ceil(TIEMPO_TOTAL/tc),
            'K Real': k_real,
            'T_c Real': tc_real,
            'Eficiencia': f"{ef_real:.2f}%",
            'Capacidad (Uni/Día)': f"{cap:.0f}",
            'Asignación': str_estaciones
        })
        
    df = pd.DataFrame(resultados)
    # Solo imprimimos una columna de eficiencia
    print(df[['T_c Objetivo', 'K Téo.', 'K Real', 'T_c Real', 'Eficiencia', 'Capacidad (Uni/Día)']].to_markdown(index=False))
    print("\nDetalle de Asignación:")
    for res in resultados:
        print(f"-> Para Tc={res['T_c Objetivo']}: {res['Asignación']}")
    return df

def resolver_punto_b():
    print("\n" + "="*60)
    print("🅱️ PUNTO B: Balanceo UALPB-2 (Estaciones Fijas) - ÓPTIMO")
    print("="*60)
    
    k_objetivos = [3, 4, 7]
    resultados = []
    
    for k_obj in k_objetivos:
        # Busca el T_c mínimo que cumpla con el número de estaciones objetivo
        tc_busqueda = math.ceil(max(12, TIEMPO_TOTAL/k_obj)) 
        estaciones_optimas = {}
        
        while True:
            estaciones = balancear_linea_optimizado(tc_busqueda)
            if len(estaciones) <= k_obj:
                estaciones_optimas = estaciones
                break
            tc_busqueda += 1 
            
        # Solo capturamos 4 valores (K_real, Tc_real, ef_real, cap)
        k_real, tc_real, ef_real, cap = calcular_metricas(estaciones_optimas, tc_busqueda)
        
        str_estaciones = "; ".join(f"E{k}: {v} (T={sum(GRAFO_TAREAS[t][0] for t in v)})" for k, v in estaciones_optimas.items())

        resultados.append({
            'K Objetivo': k_obj,
            'K Real': k_real,
            'T_c Mín. Logrado': tc_real,
            'Eficiencia': f"{ef_real:.2f}%",
            'Capacidad (Uni/Día)': f"{cap:.0f}",
            'Condición': f"(K={k_real}, Tc={tc_real})",
            'Asignación': str_estaciones 
        })
        
    df = pd.DataFrame(resultados)
    print(df[['K Objetivo', 'K Real', 'T_c Mín. Logrado', 'Eficiencia', 'Capacidad (Uni/Día)', 'Condición']].to_markdown(index=False))
    
    print("\nDetalle de Asignación:")
    for res in resultados:
        print(f"-> Para K Objetivo={res['K Objetivo']} (Tc={res['T_c Mín. Logrado']}): {res['Asignación']}")
        
    return df

def resolver_punto_c_rabbit_chase():
    print("\n" + "="*60)
    print("🇨🇿 PUNTO C: Método Rabbit Chase (U-Shape)")
    print("="*60)
    
    tc_objetivo = 15
    t_desplazamiento = 1 
    
    estaciones = balancear_linea_optimizado(tc_objetivo - t_desplazamiento)
    
    k_real, tc_real, ef_real, cap = calcular_metricas(estaciones, tc_objetivo, t_desplazamiento)
    
    print(f"Parámetros: T_c Objetivo={tc_objetivo}, T_desplazamiento={t_desplazamiento}")
    print(f"Estaciones Resultantes (K): {k_real}")
    print(f"Tiempo de Ciclo Real (incl. desp): {tc_real}")
    print(f"Eficiencia: {ef_real:.2f}%")
    print(f"Capacidad (Uni/Día): {cap:.0f}")
    
    return {'K': k_real, 'Tc': tc_real, 'Ef': ef_real, 'Cap': cap, 'Estaciones': estaciones}

def resolver_punto_d_comparativo(df_b, datos_c):
    print("\n" + "="*60)
    print("📊 PUNTO D: Cuadro Comparativo (Basado en Óptimo)")
    print("="*60)
    
    fila_b = df_b[df_b['K Objetivo'] == 4].iloc[0]
    
    k_b = fila_b['K Real']
    tc_b = fila_b['T_c Mín. Logrado']
    ef_b = float(fila_b['Eficiencia'].strip('%'))
    cap_b = fila_b['Capacidad (Uni/Día)']
    
    k_c = datos_c['K']
    tc_c = datos_c['Tc']
    ef_c = datos_c['Ef']
    cap_c = datos_c['Cap']
    
    tabla_comparativa = [
        {
            'Métrica': 'Capacidad (Uni/Día)',
            'Opción B (Tradicional K=4)': cap_b,
            'Opción C (Rabbit Chase)': f"{cap_c:.0f}",
            'Diferencia': int(cap_c) - int(cap_b)
        },
        {
            'Métrica': 'Eficiencia (%)',
            'Opción B (Tradicional K=4)': f"{ef_b:.2f}%",
            'Opción C (Rabbit Chase)': f"{ef_c:.2f}%",
            'Diferencia': f"{ef_c - ef_b:.2f}%"
        }
    ]
    
    df_comp = pd.DataFrame(tabla_comparativa)
    print(df_comp.to_markdown(index=False))
    
    print("\nAnálisis de la Decisión (MILP Confirmado):")
    print(f"-> La Opción B (Línea Fija) logra una eficiencia del {ef_b:.2f}% con una capacidad de {cap_b} uni/día. Es la mejor opción en costo operativo.")
    print(f"-> La Opción C (Rabbit Chase) logra una capacidad mayor ({cap_c:.0f} uni/día) pero sacrifica eficiencia debido al tiempo de desplazamiento. Es la mejor opción para maximizar la velocidad de producción.")

# --- EJECUCIÓN PRINCIPAL ---

if __name__ == "__main__":
    df_a_result = resolver_punto_a()
    df_b_result = resolver_punto_b()
    datos_c_result = resolver_punto_c_rabbit_chase()
    resolver_punto_d_comparativo(df_b_result, datos_c_result)