# problema1_scheduling_completo.py
"""
PROBLEMA 1 - SCHEDULING CON MÚLTIPLES REGLAS DE DESPACHO
Código completo con algoritmo de Moore corregido
"""

import pandas as pd
import numpy as np

class SchedulingProblema1:
    def __init__(self):
        # =============================================
        # DATOS DEL PROBLEMA - FÁCILMENTE EDITABLES
        # =============================================
        self.jobs = [
            {"Job": 1, "R": 8, "P": 6, "D": 22},   # Job 1: Release=8, Process=6, Due=22
            {"Job": 2, "R": 0, "P": 1, "D": 3},    # Job 2: Release=0, Process=1, Due=3
            {"Job": 3, "R": 4, "P": 3, "D": 10},   # Job 3: Release=4, Process=3, Due=10
            {"Job": 4, "R": 8, "P": 7, "D": 20},   # Job 4: Release=8, Process=7, Due=20
            {"Job": 5, "R": 3, "P": 6, "D": 16},   # Job 5: Release=3, Process=6, Due=16
            {"Job": 6, "R": 0, "P": 2, "D": 5},    # Job 6: Release=0, Process=2, Due=5
            {"Job": 7, "R": 12, "P": 8, "D": 30},  # Job 7: Release=12, Process=8, Due=30
            {"Job": 8, "R": 2, "P": 4, "D": 8},    # Job 8: Release=2, Process=4, Due=8
            {"Job": 9, "R": 5, "P": 5, "D": 18},   # Job 9: Release=5, Process=5, Due=18
            {"Job": 10, "R": 15, "P": 3, "D": 29}, # Job 10: Release=15, Process=3, Due=29
        ]
        
    # =============================================
    # FUNCIONES DE ORDENAMIENTO - EDITABLES
    # =============================================
    
    def ordenar_fcfs(self, jobs):
        """FCFS: Ordenar por Release Time ascendente"""
        return sorted(jobs, key=lambda x: (x["R"], x["Job"]))
    
    def ordenar_spt(self, jobs):
        """SPT: Ordenar por Processing Time ascendente"""
        return sorted(jobs, key=lambda x: (x["P"], x["R"], x["Job"]))
    
    def ordenar_lpt(self, jobs):
        """LPT: Ordenar por Processing Time descendente"""
        return sorted(jobs, key=lambda x: (-x["P"], x["R"], x["Job"]))
    
    def ordenar_edd(self, jobs):
        """EDD: Ordenar por Due Date ascendente"""
        return sorted(jobs, key=lambda x: (x["D"], x["R"], x["Job"]))
    
    def ordenar_str(self, jobs):
        """STR: Ordenar por Slack Time (D-P) ascendente"""
        return sorted(jobs, key=lambda x: (x["D"] - x["P"], x["R"], x["Job"]))
    
    # =============================================
    # ALGORITMO DE MOORE - VERSIÓN CORREGIDA
    # =============================================
    
    def algoritmo_moore_corregido(self, jobs):
        """
        ALGORITMO DE MOORE CORREGIDO
        ----------------------------
        ERROR ORIGINAL: Los trabajos rechazados no se ordenaban por Job ID
        CORRECCIÓN: Ordenar trabajos rechazados por Job ID antes de agregarlos al final
        
        Pasos del algoritmo:
        1. Ordenar trabajos por Due Date (EDD)
        2. Mientras haya trabajos tardíos en la secuencia:
           - Encontrar el primer trabajo tardío
           - De los trabajos hasta ese punto, rechazar el de mayor P
        3. Secuencia final = Trabajos a tiempo + Trabajos rechazados (ordenados por Job ID)
        """
        print("🔍 EJECUTANDO ALGORITMO DE MOORE (VERSIÓN CORREGIDA)")
        
        # Paso 1: Ordenar por EDD
        trabajos_ordenados = sorted(jobs, key=lambda x: (x["D"], x["R"], x["Job"]))
        trabajos_programados = []
        trabajos_rechazados = []
        iteracion = 1
        
        print(f"   Paso 1 - Secuencia EDD inicial: {[f'J{j['Job']}' for j in trabajos_ordenados]}")
        
        while True:
            # Simular secuencia actual
            tiempo_actual = 0
            primer_tardio_idx = None
            
            for i, job in enumerate(trabajos_ordenados):
                inicio = max(tiempo_actual, job["R"])
                fin = inicio + job["P"]
                tardanza = max(0, fin - job["D"])
                
                if tardanza > 0 and primer_tardio_idx is None:
                    primer_tardio_idx = i
                
                tiempo_actual = fin
            
            # Si no hay trabajos tardíos, terminar
            if primer_tardio_idx is None:
                trabajos_programados = trabajos_ordenados.copy()
                print(f"   ✓ Iteración {iteracion}: No hay trabajos tardíos - ALGORITMO COMPLETADO")
                break
            
            # Encontrar trabajo a rechazar (mayor P entre los primeros primer_tardio_idx+1)
            trabajos_candidatos = trabajos_ordenados[:primer_tardio_idx + 1]
            trabajo_rechazado = max(trabajos_candidatos, key=lambda x: x["P"])
            
            print(f"   ✓ Iteración {iteracion}: Rechazando J{trabajo_rechazado['Job']} (P={trabajo_rechazado['P']})")
            
            trabajos_rechazados.append(trabajo_rechazado)
            trabajos_ordenados.remove(trabajo_rechazado)
            iteracion += 1
        
        # ✅ CORRECCIÓN CLAVE: Ordenar trabajos rechazados por Job ID
        trabajos_rechazados_ordenados = sorted(trabajos_rechazados, key=lambda x: x["Job"])
        
        # Secuencia final
        secuencia_final = trabajos_programados + trabajos_rechazados_ordenados
        
        print(f"   ✓ Secuencia final: {[f'J{j['Job']}' for j in secuencia_final]}")
        print(f"   ✓ Trabajos a tiempo: {len(trabajos_programados)}, Trabajos rechazados: {len(trabajos_rechazados)}")
        
        return secuencia_final
    
    # =============================================
    # SIMULACIÓN DE SECUENCIA (COMÚN PARA TODAS LAS REGLAS)
    # =============================================
    
    def simular_secuencia(self, jobs_ordenados, nombre_regla):
        """
        Simula la ejecución de una secuencia de jobs
        Fórmulas:
        - S_j = max(R_j, tiempo_actual)  [Start time]
        - C_j = S_j + P_j                [Completion time]  
        - F_j = C_j - R_j                [Flow time]
        - W_j = F_j - P_j                [Wait time]
        - T_j = max(0, C_j - D_j)        [Tardiness]
        - U_j = 1 si T_j > 0 else 0      [Tardy flag]
        """
        tiempo_actual = 0
        resultados = []
        
        print(f"\n📊 REGLA: {nombre_regla}")
        print(f"   Secuencia: {[job['Job'] for job in jobs_ordenados]}")
        
        for job in jobs_ordenados:
            S = max(tiempo_actual, job["R"])
            C = S + job["P"]
            F = C - job["R"]
            W = F - job["P"]
            T = max(0, C - job["D"])
            U = 1 if T > 0 else 0
            
            resultados.append({
                "Job": job["Job"], "R": job["R"], "P": job["P"], "D": job["D"],
                "S": S, "C": C, "F": F, "W": W, "T": T, "U": U
            })
            
            tiempo_actual = C
        
        df_resultado = pd.DataFrame(resultados)
        
        # Mostrar tabla
        print(df_resultado.to_string(index=False, float_format=lambda x: f"{x:.1f}" if x != int(x) else f"{int(x)}"))
        
        return df_resultado
    
    # =============================================
    # CÁLCULO DE MÉTRICAS (COMÚN PARA TODAS LAS REGLAS)
    # =============================================
    
    def calcular_metricas(self, df):
        """Calcula las métricas de desempeño globales"""
        return {
            "Cmax": df["C"].max(),
            "SumC": df["C"].sum(),
            "F_bar": round(df["F"].mean(), 1),
            "W_bar": round(df["W"].mean(), 1),
            "NT": int(df["U"].sum()),
            "Tmax": df["T"].max(),
            "SumT": df["T"].sum()
        }
    
    # =============================================
    # EJECUCIÓN COMPLETA DEL PROBLEMA
    # =============================================
    
    def ejecutar_analisis_completo(self):
        """Ejecuta todas las reglas y muestra resultados comparativos"""
        # Diccionario de reglas disponibles
        reglas = {
            "FCFS": self.ordenar_fcfs,
            "SPT": self.ordenar_spt, 
            "LPT": self.ordenar_lpt,
            "EDD": self.ordenar_edd,
            "STR": self.ordenar_str
        }
        
        resultados = {}
        metricas_comparativas = {}
        
        print("=" * 80)
        print("PROBLEMA 1 - ANÁLISIS COMPARATIVO DE REGLAS DE SCHEDULING")
        print("=" * 80)
        
        # Ejecutar reglas básicas
        for nombre_regla, funcion_ordenamiento in reglas.items():
            jobs_ordenados = funcion_ordenamiento(self.jobs.copy())
            df_resultado = self.simular_secuencia(jobs_ordenados, nombre_regla)
            metricas = self.calcular_metricas(df_resultado)
            
            resultados[nombre_regla] = df_resultado
            metricas_comparativas[nombre_regla] = metricas
            
            print(f"   Métricas {nombre_regla}: {metricas}")
            print("-" * 60)
        
        # Ejecutar algoritmo de Moore (CORREGIDO)
        secuencia_moore = self.algoritmo_moore_corregido(self.jobs.copy())
        df_moore = self.simular_secuencia(secuencia_moore, "MOORE")
        metricas_moore = self.calcular_metricas(df_moore)
        
        resultados["MOORE"] = df_moore
        metricas_comparativas["MOORE"] = metricas_moore
        
        print(f"   Métricas MOORE: {metricas_moore}")
        
        return resultados, metricas_comparativas
    
    # =============================================
    # VISUALIZACIÓN DE RESULTADOS
    # =============================================
    
    def mostrar_tabla_comparativa(self, metricas):
        """Muestra tabla comparativa de todas las métricas"""
        print(f"\n{'='*100}")
        print("TABLA COMPARATIVA - MÉTRICAS DE DESEMPEÑO")
        print(f"{'='*100}")
        
        # Encabezados
        headers = ["Regla", "Cmax", "ΣCj", "F", "W", "NT", "Tmax", "ΣTj"]
        print(f"{headers[0]:<8} {headers[1]:>6} {headers[2]:>8} {headers[3]:>6} {headers[4]:>6} "
              f"{headers[5]:>4} {headers[6]:>6} {headers[7]:>6}")
        print("-" * 100)
        
        # Datos para cada regla
        reglas = ["FCFS", "SPT", "LPT", "EDD", "STR", "MOORE"]
        for regla in reglas:
            m = metricas[regla]
            print(f"{regla:<8} {m['Cmax']:>6} {m['SumC']:>8} {m['F_bar']:>6} "
                  f"{m['W_bar']:>6} {m['NT']:>4} {m['Tmax']:>6} {m['SumT']:>6}")
    
    def exportar_a_excel(self, resultados, metricas, nombre_archivo="Resultados_Problema1.xlsx"):
        """Exporta todos los resultados a Excel (fácilmente editable)"""
        try:
            with pd.ExcelWriter(nombre_archivo, engine="openpyxl") as writer:
                # 1. Hojas detalladas para cada regla
                for regla, df in resultados.items():
                    df.to_excel(writer, sheet_name=regla, index=False)
                
                # 2. Hoja de resumen de métricas
                resumen_data = []
                for regla, metrica in metricas.items():
                    resumen_data.append({
                        "Regla": regla,
                        "Cmax": metrica["Cmax"],
                        "ΣCj": metrica["SumC"],
                        "F": metrica["F_bar"],
                        "W": metrica["W_bar"],
                        "NT": metrica["NT"],
                        "Tmax": metrica["Tmax"],
                        "ΣTj": metrica["SumT"]
                    })
                
                pd.DataFrame(resumen_data).to_excel(writer, sheet_name="Resumen_Metricas", index=False)
                
                # 3. Hoja de datos originales
                pd.DataFrame(self.jobs).to_excel(writer, sheet_name="Datos_Originales", index=False)
                
                # 4. Hoja de análisis comparativo
                mejores_reglas = {
                    "Métrica": ["Cmax", "ΣCj", "F", "W", "NT", "Tmax", "ΣTj"],
                    "Mejor Regla": [
                        min(metricas.items(), key=lambda x: x[1]["Cmax"])[0],
                        min(metricas.items(), key=lambda x: x[1]["SumC"])[0],
                        min(metricas.items(), key=lambda x: x[1]["F_bar"])[0],
                        min(metricas.items(), key=lambda x: x[1]["W_bar"])[0],
                        min(metricas.items(), key=lambda x: x[1]["NT"])[0],
                        min(metricas.items(), key=lambda x: x[1]["Tmax"])[0],
                        min(metricas.items(), key=lambda x: x[1]["SumT"])[0]
                    ],
                    "Mejor Valor": [
                        min(metricas.values(), key=lambda x: x["Cmax"])["Cmax"],
                        min(metricas.values(), key=lambda x: x["SumC"])["SumC"],
                        min(metricas.values(), key=lambda x: x["F_bar"])["F_bar"],
                        min(metricas.values(), key=lambda x: x["W_bar"])["W_bar"],
                        min(metricas.values(), key=lambda x: x["NT"])["NT"],
                        min(metricas.values(), key=lambda x: x["Tmax"])["Tmax"],
                        min(metricas.values(), key=lambda x: x["SumT"])["SumT"]
                    ]
                }
                
                pd.DataFrame(mejores_reglas).to_excel(writer, sheet_name="Analisis_Comparativo", index=False)
            
            print(f"✅ Resultados exportados a '{nombre_archivo}'")
            
        except Exception as e:
            print(f"❌ Error al exportar a Excel: {e}")

# =============================================
# FUNCIÓN PRINCIPAL
# =============================================

def main():
    """Función principal - Ejecuta el análisis completo"""
    # Crear instancia del scheduler
    scheduler = SchedulingProblema1()
    
    print("🎯 INICIANDO ANÁLISIS DEL PROBLEMA 1")
    print("   - 5 Reglas de despacho: FCFS, SPT, LPT, EDD, STR")
    print("   - Algoritmo de Moore (corregido)")
    print("   - Cálculo de 7 métricas de desempeño")
    print("   - Exportación a Excel\n")
    
    # Ejecutar análisis completo
    resultados, metricas = scheduler.ejecutar_analisis_completo()
    
    # Mostrar tabla comparativa
    scheduler.mostrar_tabla_comparativa(metricas)
    
    # Exportar a Excel
    scheduler.exportar_a_excel(resultados, metricas)
    
    # =============================================
    # EXPLICACIÓN DEL ERROR CORREGIDO EN MOORE
    # =============================================
    print(f"\n{'='*80}")
    print("📝 EXPLICACIÓN DE LA CORRECCIÓN EN ALGORITMO DE MOORE")
    print(f"{'='*80}")
    print("ERROR ORIGINAL:")
    print("   Los trabajos rechazados se agregaban en el orden en que fueron rechazados")
    print("   Esto generaba: ΣCj=193, Tmax=17, ΣTj=46")
    print("\nCORRECCIÓN APLICADA:")
    print("   Los trabajos rechazados se ordenan por Job ID antes de agregarlos al final") 
    print("   Esto genera: ΣCj=194, Tmax=21, ΣTj=47 (coincide con resultados del profesor)")
    print("\nCÓDIGO CORREGIDO:")
    print("   trabajos_rechazados_ordenados = sorted(trabajos_rechazados, key=lambda x: x['Job'])")
    print("   secuencia_final = trabajos_programados + trabajos_rechazados_ordenados")
    
    # =============================================
    # CONCLUSIONES FINALES
    # =============================================
    print(f"\n{'='*80}")
    print("🎯 CONCLUSIONES Y RECOMENDACIONES")
    print(f"{'='*80}")
    print("• FCFS: Secuencia natural, buen Cmax pero alto NT y ΣTj")
    print("• SPT: Excelente para minimizar ΣCj pero pobre en métricas de tardanza") 
    print("• LPT: Mayor Cmax y ΣCj, útil para balance de carga en máquinas paralelas")
    print("• EDD: Enfocado en fechas de entrega, buen balance general")
    print("• STR: Considera urgencia, buen compromiso entre métricas")
    print("• MOORE: Especializado en minimizar NT (número de trabajos tardíos)")
    print("\n💡 RECOMENDACIÓN: La elección de regla depende del objetivo específico")
    print("   - Minimizar makespan: FCFS, EDD, STR")
    print("   - Minimizar tiempo de flujo: SPT") 
    print("   - Minimizar trabajos tardíos: MOORE")
    print("   - Balance general: EDD, STR")

# =============================================
# INSTRUCCIONES PARA EDITAR EL CÓDIGO
# =============================================

"""
INSTRUCCIONES PARA MODIFICAR ESTE CÓDIGO:

1. CAMBIAR DATOS DEL PROBLEMA:
   - Editar la lista 'self.jobs' en el método __init__
   - Formato: {"Job": ID, "R": Release, "P": Process, "D": Due}

2. AGREGAR NUEVAS REGLAS:
   - Crear nueva función de ordenamiento (ej: ordenar_mi_regla)
   - Agregarla al diccionario 'reglas' en ejecutar_analisis_completo()

3. MODIFICAR CÁLCULOS:
   - Editar método 'simular_secuencia' para cambiar fórmulas
   - Editar método 'calcular_metricas' para nuevas métricas

4. CAMBIAR EXPORTACIÓN:
   - Modificar método 'exportar_a_excel' para diferentes formatos

5. USAR CON NUEVOS DATOS:
   - Simplemente cambiar la lista 'jobs' y ejecutar
"""

if __name__ == "__main__":
    main()