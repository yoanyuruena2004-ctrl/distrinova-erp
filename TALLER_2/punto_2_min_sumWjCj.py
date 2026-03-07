# problema2_scheduling_ponderado.py
"""
PROBLEMA 2 - SCHEDULING CON PONDERACIONES Y PRECEDENCIAS
Minimizar ΣWjCj con y sin restricciones de agrupamiento
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class SchedulingProblema2:
    def __init__(self):
        # =============================================
        # DATOS DEL PROBLEMA - FÁCILMENTE EDITABLES
        # =============================================
        self.jobs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        self.Pj = [12, 8, 15, 10, 11, 20, 18, 6, 4, 12, 2, 5]
        self.Wj = [10, 5, 3, 7, 5, 1, 5, 3, 10, 7, 1, 10]
        
        # Grupos con precedencias
        self.grupos = {
            "Grupo 1": [1, 4, 8, 11],
            "Grupo 2": [2, 3, 12],
            "Grupo 3": [5, 6], 
            "Grupo 4": [7, 9, 10]
        }
        
    # =============================================
    # PARTE a) WSPT SIN RESTRICCIONES
    # =============================================
    
    def wspt_sin_restricciones(self):
        """WSPT: Ordenar por Pj/Wj ascendente (menor a mayor)"""
        print("🔧 PARTE a) - WSPT SIN RESTRICCIONES")
        print("=" * 50)
        
        # Crear lista de trabajos con datos
        trabajos = []
        for i, job in enumerate(self.jobs):
            trabajos.append({
                "Job": job,
                "Pj": self.Pj[i],
                "Wj": self.Wj[i],
                "Ratio": self.Pj[i] / self.Wj[i] if self.Wj[i] > 0 else float('inf')
            })
        
        # Ordenar por ratio Pj/Wj ascendente
        trabajos_ordenados = sorted(trabajos, key=lambda x: x["Ratio"])
        
        print("Ordenamiento WSPT (por Pj/Wj ascendente):")
        print(f"{'Job':>4} | {'Pj':>4} | {'Wj':>4} | {'Pj/Wj':>8}")
        print("-" * 35)
        for job in trabajos_ordenados:
            print(f"{job['Job']:4} | {job['Pj']:4} | {job['Wj']:4} | {job['Ratio']:8.3f}")
        
        return trabajos_ordenados
    
    # =============================================
    # PARTE b) WSPT CON PRECEDENCIAS POR GRUPOS
    # =============================================
    
    def wspt_con_precedencias(self):
        """WSPT considerando agrupamiento con precedencias"""
        print("\n🔧 PARTE b) - WSPT CON PRECEDENCIAS POR GRUPOS")
        print("=" * 60)
        
        # Paso 1: Procesar cada grupo internamente
        grupos_procesados = {}
        
        for nombre_grupo, jobs_grupo in self.grupos.items():
            print(f"\n📁 {nombre_grupo}: Jobs {jobs_grupo}")
            
            # Obtener datos de los trabajos del grupo
            trabajos_grupo = []
            for job_id in jobs_grupo:
                idx = self.jobs.index(job_id)
                trabajos_grupo.append({
                    "Job": job_id,
                    "Pj": self.Pj[idx],
                    "Wj": self.Wj[idx],
                    "Ratio": self.Pj[idx] / self.Wj[idx] if self.Wj[idx] > 0 else float('inf')
                })
            
            # Ordenar internamente por Pj/Wj
            trabajos_ordenados = sorted(trabajos_grupo, key=lambda x: x["Ratio"])
            
            # Calcular ratio del grupo: (ΣPj)/(ΣWj)
            suma_Pj = sum(job["Pj"] for job in trabajos_ordenados)
            suma_Wj = sum(job["Wj"] for job in trabajos_ordenados)
            ratio_grupo = suma_Pj / suma_Wj if suma_Wj > 0 else float('inf')
            
            grupos_procesados[nombre_grupo] = {
                "trabajos": trabajos_ordenados,
                "suma_Pj": suma_Pj,
                "suma_Wj": suma_Wj,
                "ratio_grupo": ratio_grupo
            }
            
            print(f"   Orden interno: {[job['Job'] for job in trabajos_ordenados]}")
            print(f"   ΣPj = {suma_Pj}, ΣWj = {suma_Wj}, Ratio grupo = {ratio_grupo:.3f}")
        
        # Paso 2: Ordenar grupos por ratio_grupo ascendente
        grupos_ordenados = sorted(grupos_procesados.items(), key=lambda x: x[1]["ratio_grupo"])
        
        print("\n📊 ORDENAMIENTO DE GRUPOS (por ratio grupo ascendente):")
        for grupo, datos in grupos_ordenados:
            print(f"   {grupo}: ratio = {datos['ratio_grupo']:.3f}")
        
        # Paso 3: Construir secuencia final concatenando grupos ordenados
        secuencia_final = []
        for grupo, datos in grupos_ordenados:
            secuencia_final.extend(datos["trabajos"])
        
        print(f"\n🎯 SECUENCIA FINAL: {[job['Job'] for job in secuencia_final]}")
        
        return secuencia_final
    
    # =============================================
    # CÁLCULO DE MÉTRICAS Y SIMULACIÓN
    # =============================================
    
    def simular_secuencia(self, trabajos_ordenados, titulo):
        """Simula la ejecución y calcula ΣWjCj"""
        print(f"\n📈 SIMULACIÓN: {titulo}")
        print("=" * 60)
        
        tiempo_actual = 0
        resultados = []
        suma_WjCj = 0
        
        print(f"{'Job':>4} | {'Pj':>4} | {'Wj':>4} | {'Inicio':>6} | {'Cj':>4} | {'Wj*Cj':>8}")
        print("-" * 50)
        
        for job in trabajos_ordenados:
            inicio = tiempo_actual
            Cj = inicio + job["Pj"]
            WjCj = job["Wj"] * Cj
            suma_WjCj += WjCj
            
            resultados.append({
                "Job": job["Job"],
                "Pj": job["Pj"], 
                "Wj": job["Wj"],
                "Inicio": inicio,
                "Cj": Cj,
                "Wj*Cj": WjCj
            })
            
            print(f"{job['Job']:4} | {job['Pj']:4} | {job['Wj']:4} | {inicio:6} | {Cj:4} | {WjCj:8}")
            
            tiempo_actual = Cj
        
        print(f"{'TOTAL':>4} | {'':>4} | {'':>4} | {'':>6} | {'':>4} | {suma_WjCj:8}")
        
        return resultados, suma_WjCj
    
    # =============================================
    # DIAGRAMAS DE GANTT
    # =============================================
    
    def crear_diagrama_gantt(self, resultados, titulo, nombre_archivo):
        """Crea diagrama de Gantt para una secuencia"""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            jobs = [f"J{r['Job']}" for r in resultados]
            inicios = [r["Inicio"] for r in resultados]
            duraciones = [r["Pj"] for r in resultados]
            colores = plt.cm.Set3(np.linspace(0, 1, len(jobs)))
            
            # Crear barras
            bars = ax.barh(jobs, duraciones, left=inicios, color=colores, edgecolor='black', alpha=0.7)
            
            # Añadir etiquetas
            for bar, resultado in zip(bars, resultados):
                width = bar.get_width()
                x = bar.get_x() + width / 2
                y = bar.get_y() + bar.get_height() / 2
                ax.text(x, y, f"J{resultado['Job']}\n({resultado['Pj']})", 
                       ha='center', va='center', fontweight='bold')
            
            ax.set_xlabel('Tiempo')
            ax.set_ylabel('Trabajos')
            ax.set_title(f'Diagrama de Gantt - {titulo}\nΣWjCj = {sum(r["Wj*Cj"] for r in resultados)}')
            ax.grid(True, axis='x', alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
            plt.show()
            
            print(f"✅ Diagrama de Gantt guardado como: {nombre_archivo}")
            
        except Exception as e:
            print(f"⚠️ Error al crear diagrama de Gantt: {e}")
    
    # =============================================
    # EJECUCIÓN COMPLETA
    # =============================================
    
    def ejecutar_analisis_completo(self):
        """Ejecuta el análisis completo del Problema 2"""
        print("🎯 PROBLEMA 2 - SCHEDULING CON PONDERACIONES")
        print("=" * 70)
        
        # Parte a) WSPT sin restricciones
        secuencia_a = self.wspt_sin_restricciones()
        resultados_a, suma_WjCj_a = self.simular_secuencia(secuencia_a, "WSPT Sin Restricciones")
        
        # Parte b) WSPT con precedencias
        secuencia_b = self.wspt_con_precedencias() 
        resultados_b, suma_WjCj_b = self.simular_secuencia(secuencia_b, "WSPT Con Precedencias")
        
        # Resumen comparativo
        print(f"\n{'='*70}")
        print("📊 RESUMEN COMPARATIVO")
        print(f"{'='*70}")
        print(f"Parte a) WSPT sin restricciones: ΣWjCj = {suma_WjCj_a}")
        print(f"Parte b) WSPT con precedencias:   ΣWjCj = {suma_WjCj_b}")
        print(f"Diferencia: {suma_WjCj_b - suma_WjCj_a} ({(suma_WjCj_b/suma_WjCj_a - 1)*100:.1f}% mayor)")
        
        # Crear diagramas de Gantt
        self.crear_diagrama_gantt(resultados_a, "WSPT Sin Restricciones", "gantt_parte_a.png")
        self.crear_diagrama_gantt(resultados_b, "WSPT Con Precedencias", "gantt_parte_b.png")
        
        # Exportar a Excel
        self.exportar_a_excel(resultados_a, resultados_b, suma_WjCj_a, suma_WjCj_b)
        
        return resultados_a, resultados_b, suma_WjCj_a, suma_WjCj_b
    
    def exportar_a_excel(self, resultados_a, resultados_b, suma_a, suma_b):
        """Exporta resultados a Excel"""
        try:
            with pd.ExcelWriter("Resultados_Problema2.xlsx", engine="openpyxl") as writer:
                # Hoja Parte a)
                df_a = pd.DataFrame(resultados_a)
                df_a.to_excel(writer, sheet_name="WSPT_Sin_Restricciones", index=False)
                
                # Hoja Parte b) 
                df_b = pd.DataFrame(resultados_b)
                df_b.to_excel(writer, sheet_name="WSPT_Con_Precedencias", index=False)
                
                # Hoja Resumen
                resumen_data = {
                    "Configuración": ["WSPT Sin Restricciones", "WSPT Con Precedencias"],
                    "ΣWjCj": [suma_a, suma_b],
                    "Diferencia": [0, suma_b - suma_a],
                    "Incremento %": [0, (suma_b/suma_a - 1)*100]
                }
                pd.DataFrame(resumen_data).to_excel(writer, sheet_name="Resumen_Comparativo", index=False)
                
                # Hoja Datos Originales
                datos_originales = {
                    "Job": self.jobs,
                    "Pj": self.Pj, 
                    "Wj": self.Wj,
                    "Pj/Wj": [p/w if w>0 else float('inf') for p,w in zip(self.Pj, self.Wj)]
                }
                pd.DataFrame(datos_originales).to_excel(writer, sheet_name="Datos_Originales", index=False)
            
            print("✅ Resultados exportados a 'Resultados_Problema2.xlsx'")
            
        except Exception as e:
            print(f"❌ Error al exportar a Excel: {e}")

# =============================================
# FUNCIÓN PRINCIPAL
# =============================================

def main():
    """Función principal del Problema 2"""
    scheduler = SchedulingProblema2()
    
    print("🎯 INICIANDO ANÁLISIS DEL PROBLEMA 2")
    print("   - Parte a): Minimizar ΣWjCj sin restricciones")
    print("   - Parte b): Minimizar ΣWjCj con precedencias por grupos") 
    print("   - Diagramas de Gantt para ambas configuraciones\n")
    
    # Ejecutar análisis completo
    resultados_a, resultados_b, suma_a, suma_b = scheduler.ejecutar_analisis_completo()
    
    # Conclusiones
    print(f"\n{'='*70}")
    print("📝 CONCLUSIONES - PROBLEMA 2")
    print(f"{'='*70}")
    print("• WSPT (Pj/Wj) es óptimo para minimizar ΣWjCj en una máquina")
    print("• Las restricciones de agrupamiento incrementan ΣWjCj")
    print("• La estructura de grupos afecta la optimalidad pero es necesaria por setup times")
    print("• El trade-off entre optimalidad y restricciones prácticas es inevitable")
    print(f"• En este caso, las precedencias incrementan ΣWjCj en {(suma_b/suma_a - 1)*100:.1f}%")

if __name__ == "__main__":
    main()