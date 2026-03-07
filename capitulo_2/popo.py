import numpy as np
from collections import defaultdict, deque
import heapq
import copy
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from ortools.sat.python import cp_model

class MasterSchedulingSolver:
    """
    SOLUCIONADOR MAESTRO DE SCHEDULING JOB SHOP
    Combina los mejores algoritmos y visualizaciones de ambos códigos
    """
    
    def __init__(self, jobs_data=None, processing_times=None, machines_sequence=None):
        """
        Inicializa con cualquiera de los dos formatos de datos
        """
        if jobs_data is not None:
            # Formato: {job: [(machine, processing_time), ...]}
            self.jobs_data = jobs_data
            self.jobs = list(jobs_data.keys())
            self._convert_from_jobs_format()
        else:
            # Formato: processing_times y machines_sequence
            self.processing_times = processing_times
            self.machines_sequence = machines_sequence
            self.num_jobs = len(processing_times)
            self.num_machines = len(processing_times[0])
            self._convert_to_jobs_format()
        
        self.machines = self._get_machines()
        
    def _get_machines(self):
        """Obtiene lista de máquinas únicas"""
        machines = set()
        for job_ops in self.jobs_data.values():
            for machine, _ in job_ops:
                machines.add(machine)
        return sorted(machines)
    
    def _convert_from_jobs_format(self):
        """Convierte de formato jobs_data a processing_times/machines_sequence"""
        self.num_jobs = len(self.jobs_data)
        self.num_machines = max(len(ops) for ops in self.jobs_data.values())
        
        self.processing_times = []
        self.machines_sequence = []
        
        for job in sorted(self.jobs_data.keys()):
            job_times = []
            job_machines = []
            for machine, processing_time in self.jobs_data[job]:
                job_times.append(processing_time)
                job_machines.append(machine)
            self.processing_times.append(job_times)
            self.machines_sequence.append(job_machines)
    
    def _convert_to_jobs_format(self):
        """Convierte de processing_times/machines_sequence a jobs_data"""
        self.jobs_data = {}
        for job in range(self.num_jobs):
            operations = []
            for op in range(self.num_machines):
                machine = self.machines_sequence[job][op]
                processing_time = self.processing_times[job][op]
                operations.append((machine, processing_time))
            self.jobs_data[job] = operations
        self.jobs = list(self.jobs_data.keys())

    # =========================================================================
    # ALGORITMOS DE SOLUCIÓN (Lo mejor de ambos códigos)
    # =========================================================================
    
    def solve_optimal_mathematical(self, time_limit=60):
        """
        SOLUCIÓN EXACTA usando modelo matemático (OR-Tools)
        Devuelve la solución óptima garantizada
        """
        print("🔍 EJECUTANDO SOLUCIÓN MATEMÁTICA EXACTA...")
        
        model = cp_model.CpModel()
        
        # Horizonte temporal
        horizon = sum(sum(job) for job in self.processing_times) * 2
        
        # Variables
        start_vars = {}
        end_vars = {}
        interval_vars = {}
        
        for job in range(self.num_jobs):
            for op in range(self.num_machines):
                machine = self.machines_sequence[job][op] - 1
                processing_time = self.processing_times[job][op]
                
                suffix = f"j{job}_op{op}_m{machine}"
                start_vars[(job, op)] = model.NewIntVar(0, horizon, f"start_{suffix}")
                end_vars[(job, op)] = model.NewIntVar(0, horizon, f"end_{suffix}")
                interval_vars[(job, op)] = model.NewIntervalVar(
                    start_vars[(job, op)], processing_time, end_vars[(job, op)], 
                    f"interval_{suffix}"
                )
        
        # Makespan
        makespan = model.NewIntVar(0, horizon, "makespan")
        
        # Constraints
        # Precedencia dentro de jobs
        for job in range(self.num_jobs):
            for op in range(self.num_machines - 1):
                model.Add(end_vars[(job, op)] <= start_vars[(job, op + 1)])
        
        # No superposición en máquinas
        for machine in range(len(self.machines)):
            intervals = []
            for job in range(self.num_jobs):
                for op in range(self.num_machines):
                    if self.machines_sequence[job][op] - 1 == machine:
                        intervals.append(interval_vars[(job, op)])
            model.AddNoOverlap(intervals)
        
        # Makespan constraint
        for job in range(self.num_jobs):
            last_op = self.num_machines - 1
            model.Add(end_vars[(job, last_op)] <= makespan)
        
        # Objective
        model.Minimize(makespan)
        
        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit
        status = solver.Solve(model)
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            makespan_value = solver.Value(makespan)
            
            # Construir schedule
            schedule = {machine: [] for machine in range(len(self.machines))}
            for job in range(self.num_jobs):
                for op in range(self.num_machines):
                    machine = self.machines_sequence[job][op] - 1
                    start = solver.Value(start_vars[(job, op)])
                    end = start + self.processing_times[job][op]
                    schedule[machine].append((job, op, start, end))
            
            print(f"✅ SOLUCIÓN {'ÓPTIMA' if status == cp_model.OPTIMAL else 'FACTIBLE'} ENCONTRADA")
            print(f"📊 Makespan: {makespan_value}")
            
            return makespan_value, schedule, "MATHEMATICAL"
        else:
            print("❌ No se encontró solución con el modelo matemático")
            return None, None, "MATHEMATICAL"
    
    def solve_advanced_heuristic(self):
        """
        ALGORITMO SHIFTING BOTTLENECK AVANZADO
        Combina EDD + Carga de Máquinas + Cálculo de Camino Crítico
        """
        print("🔧 EJECUTANDO ALGORITMO SHIFTING BOTTLENECK AVANZADO...")
        
        # Calcular cargas iniciales
        machine_loads = {}
        for machine in range(len(self.machines)):
            total_load = 0
            for job in range(self.num_jobs):
                for op in range(self.num_machines):
                    if self.machines_sequence[job][op] - 1 == machine:
                        total_load += self.processing_times[job][op]
            machine_loads[machine] = total_load
        
        print("📈 Cargas de máquinas:")
        for machine, load in sorted(machine_loads.items(), key=lambda x: x[1], reverse=True):
            print(f"   M{machine + 1}: {load}")
        
        # Inicializar estructuras
        current_schedule = {machine: [] for machine in range(len(self.machines))}
        scheduled_machines = set()
        machines_by_load = sorted(range(len(self.machines)), 
                                key=lambda m: machine_loads[m], reverse=True)
        
        best_makespan = float('inf')
        best_schedule = None
        
        for iteration, machine in enumerate(machines_by_load):
            print(f"\n🔄 Iteración {iteration + 1}: Programando M{machine + 1}")
            
            # Resolver single machine con precedencias
            machine_schedule = self._solve_single_machine_advanced(machine, current_schedule)
            current_schedule[machine] = machine_schedule
            scheduled_machines.add(machine)
            
            # Calcular makespan actual
            current_makespan = self._calculate_critical_path_makespan(current_schedule)
            
            print(f"   📊 Makespan actual: {current_makespan}")
            
            if current_makespan < best_makespan:
                best_makespan = current_makespan
                best_schedule = copy.deepcopy(current_schedule)
        
        print(f"\n🎯 MEJOR MAKESPAN HEURÍSTICO: {best_makespan}")
        return best_makespan, best_schedule, "HEURISTIC"
    
    def _solve_single_machine_advanced(self, machine, current_schedule):
        """Algoritmo single machine mejorado con EDD"""
        operations = []
        
        # Calcular release times y due dates
        release_times = self._calculate_advanced_release_times(current_schedule)
        
        for job in range(self.num_jobs):
            for op in range(self.num_machines):
                if self.machines_sequence[job][op] - 1 == machine:
                    release_time = release_times[(job, op)]
                    processing_time = self.processing_times[job][op]
                    
                    # Due date inteligente
                    remaining_time = self._estimate_remaining_time(job, op, current_schedule)
                    due_date = release_time + processing_time + remaining_time
                    
                    operations.append((job, op, processing_time, release_time, due_date))
        
        # Ordenar por due date (EDD)
        operations.sort(key=lambda x: x[4])
        
        # Programar respetando release times
        schedule = []
        current_time = 0
        
        for job, op, pt, release, due in operations:
            start_time = max(current_time, release)
            end_time = start_time + pt
            schedule.append((job, op, start_time, end_time))
            current_time = end_time
        
        return schedule
    
    def _calculate_advanced_release_times(self, current_schedule):
        """Cálculo avanzado de release times considerando todas las dependencias"""
        release_times = {}
        
        # Inicializar
        for job in range(self.num_jobs):
            for op in range(self.num_machines):
                release_times[(job, op)] = 0
        
        # Forward pass recursivo
        for job in range(self.num_jobs):
            for op in range(self.num_machines):
                current_release = release_times[(job, op)]
                
                # Dependencia de operación anterior
                if op > 0:
                    prev_end = self._find_operation_end(job, op - 1, current_schedule)
                    if prev_end is not None:
                        current_release = max(current_release, prev_end)
                
                # Dependencia de máquina
                machine = self.machines_sequence[job][op] - 1
                machine_schedule = current_schedule.get(machine, [])
                for scheduled_job, scheduled_op, start, end in machine_schedule:
                    if scheduled_job == job and scheduled_op == op:
                        current_release = max(current_release, start)
                        break
                
                release_times[(job, op)] = current_release
        
        return release_times
    
    def _calculate_critical_path_makespan(self, schedule):
        """Calcula makespan usando método de camino crítico"""
        early_finish = {}
        
        for job in range(self.num_jobs):
            for op in range(self.num_machines):
                machine = self.machines_sequence[job][op] - 1
                processing_time = self.processing_times[job][op]
                
                # Encontrar start time
                start_time = 0
                if op > 0:
                    start_time = max(start_time, early_finish.get((job, op - 1), 0))
                
                # Buscar en schedule de máquina
                machine_ops = [s for s in schedule.get(machine, []) 
                             if s[0] == job and s[1] == op]
                if machine_ops:
                    start_time = max(start_time, machine_ops[0][2])
                
                early_finish[(job, op)] = start_time + processing_time
        
        return max(early_finish.values()) if early_finish else 0

    def _find_operation_end(self, job, op, schedule):
        """Encuentra end time de una operación específica"""
        machine = self.machines_sequence[job][op] - 1
        machine_schedule = schedule.get(machine, [])
        
        for scheduled_job, scheduled_op, start, end in machine_schedule:
            if scheduled_job == job and scheduled_op == op:
                return end
        return None
    
    def _estimate_remaining_time(self, job, current_op, schedule):
        """Estima tiempo restante para un job"""
        remaining = 0
        for op in range(current_op + 1, self.num_machines):
            remaining += self.processing_times[job][op]
        return remaining

    # =========================================================================
    # VISUALIZACIÓN AVANZADA (Lo mejor de ambos códigos)
    # =========================================================================
    
    def plot_comprehensive_gantt(self, schedule, makespan, title_suffix=""):
        """
        DIAGRAMA DE GANTT COMPLETO con múltiples vistas
        """
        fig = plt.figure(figsize=(16, 12))
        
        # 1. Vista por Máquinas
        ax1 = plt.subplot(2, 2, 1)
        self._plot_machine_view(ax1, schedule, makespan, "Vista por Máquinas")
        
        # 2. Vista por Trabajos
        ax2 = plt.subplot(2, 2, 2)
        self._plot_job_view(ax2, schedule, makespan, "Vista por Trabajos")
        
        # 3. Vista de Recursos
        ax3 = plt.subplot(2, 2, 3)
        self._plot_resource_view(ax3, schedule, makespan, "Utilización de Recursos")
        
        # 4. Vista de Carga
        ax4 = plt.subplot(2, 2, 4)
        self._plot_load_analysis(ax4, schedule, makespan, "Análisis de Carga")
        
        plt.suptitle(f'ANÁLISIS COMPLETO DE SCHEDULING - Makespan: {makespan} {title_suffix}', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    def _plot_machine_view(self, ax, schedule, makespan, title):
        """Vista tradicional por máquinas"""
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3']
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel('Máquinas', fontsize=12)
        ax.set_xlabel('Tiempo', fontsize=12)
        
        for machine in range(len(self.machines)):
            machine_schedule = schedule.get(machine, [])
            for job, op, start, end in machine_schedule:
                color = colors[job % len(colors)]
                ax.barh(machine, end - start, left=start, height=0.6, 
                       color=color, edgecolor='black', alpha=0.8)
                ax.text((start + end) / 2, machine, 
                       f'J{job+1}O{op+1}', ha='center', va='center', 
                       fontweight='bold', fontsize=9)
        
        ax.set_yticks(range(len(self.machines)))
        ax.set_yticklabels([f'Máquina {i+1}' for i in range(len(self.machines))])
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, makespan + 2)
    
    def _plot_job_view(self, ax, schedule, makespan, title):
        """Vista por flujo de trabajos"""
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3']
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel('Trabajos', fontsize=12)
        ax.set_xlabel('Tiempo', fontsize=12)
        
        # Recolectar operaciones por trabajo
        job_operations = [[] for _ in range(self.num_jobs)]
        for machine in range(len(self.machines)):
            for job, op, start, end in schedule.get(machine, []):
                job_operations[job].append((op, start, end, machine))
        
        for job in range(self.num_jobs):
            operations = sorted(job_operations[job], key=lambda x: x[0])
            
            # Dibujar flechas de dependencia
            for i in range(len(operations) - 1):
                op1, start1, end1, machine1 = operations[i]
                op2, start2, end2, machine2 = operations[i + 1]
                
                ax.annotate('', xy=(start2, job), xytext=(end1, job),
                          arrowprops=dict(arrowstyle='->', color='gray', lw=1.5, alpha=0.7))
            
            # Dibujar operaciones
            for op, start, end, machine in operations:
                color = colors[job % len(colors)]
                ax.barh(job, end - start, left=start, height=0.6, 
                       color=color, edgecolor='black', alpha=0.8)
                ax.text((start + end) / 2, job, 
                       f'O{op+1}(M{machine+1})', ha='center', va='center', 
                       fontweight='bold', fontsize=8)
        
        ax.set_yticks(range(self.num_jobs))
        ax.set_yticklabels([f'Trabajo {i+1}' for i in range(self.num_jobs)])
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, makespan + 2)
    
    def _plot_resource_view(self, ax, schedule, makespan, title):
        """Vista de utilización de recursos"""
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3']
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel('Máquinas', fontsize=12)
        ax.set_xlabel('Tiempo', fontsize=12)
        
        for machine in range(len(self.machines)):
            for job, op, start, end in schedule.get(machine, []):
                color = colors[job % len(colors)]
                rect = patches.Rectangle((start, machine - 0.3), end - start, 0.6,
                                       linewidth=1, edgecolor='black', facecolor=color, alpha=0.8)
                ax.add_patch(rect)
                ax.text((start + end) / 2, machine, 
                       f'J{job+1}', ha='center', va='center', fontweight='bold')
        
        ax.set_xlim(0, makespan)
        ax.set_ylim(-0.5, len(self.machines) - 0.5)
        ax.set_yticks(range(len(self.machines)))
        ax.set_yticklabels([f'M{i+1}' for i in range(len(self.machines))])
        ax.grid(True, alpha=0.3)
        ax.axvline(x=makespan, color='red', linestyle='--', linewidth=2, 
                  label=f'Makespan = {makespan}')
        ax.legend()
    
    def _plot_load_analysis(self, ax, schedule, makespan, title):
        """Análisis de carga y utilización"""
        machine_utilization = []
        machine_names = []
        
        for machine in range(len(self.machines)):
            total_busy_time = 0
            for job, op, start, end in schedule.get(machine, []):
                total_busy_time += (end - start)
            
            utilization = (total_busy_time / makespan) * 100 if makespan > 0 else 0
            machine_utilization.append(utilization)
            machine_names.append(f'M{machine+1}')
        
        colors = ['#4ECDC4' if util > 70 else '#FF6B6B' for util in machine_utilization]
        bars = ax.bar(machine_names, machine_utilization, color=colors, alpha=0.8)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel('Utilización (%)', fontsize=12)
        ax.set_xlabel('Máquinas', fontsize=12)
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Añadir valores en las barras
        for bar, util in zip(bars, machine_utilization):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{util:.1f}%', ha='center', va='bottom', fontweight='bold')

    # =========================================================================
    # INTERFAZ UNIFICADA
    # =========================================================================
    
    def solve_complete_problem(self, method='AUTO', plot_results=True):
        """
        INTERFAZ UNIFICADA PARA RESOLVER CUALQUIER PROBLEMA DE SCHEDULING
        
        Args:
            method: 'MATHEMATICAL', 'HEURISTIC', or 'AUTO'
            plot_results: Si genera gráficos automáticamente
        """
        print("=" * 70)
        print("🎯 SOLUCIONADOR MAESTRO DE SCHEDULING JOB SHOP")
        print("=" * 70)
        
        # Mostrar datos del problema
        self._print_problem_info()
        
        # Seleccionar método de solución
        if method == 'AUTO':
            if self.num_jobs * self.num_machines <= 20:  # Problema pequeño
                method = 'MATHEMATICAL'
            else:
                method = 'HEURISTIC'
        
        # Resolver
        if method == 'MATHEMATICAL':
            makespan, schedule, solver_type = self.solve_optimal_mathematical()
        else:
            makespan, schedule, solver_type = self.solve_advanced_heuristic()
        
        if makespan is None:
            print("❌ No se pudo encontrar solución")
            return None, None
        
        # Mostrar resultados
        self._print_schedule_details(schedule, makespan, solver_type)
        
        # Generar gráficos
        if plot_results:
            print("\n📊 GENERANDO ANÁLISIS VISUAL COMPLETO...")
            self.plot_comprehensive_gantt(schedule, makespan, f"({solver_type})")
        
        return makespan, schedule
    
    def _print_problem_info(self):
        """Imprime información del problema"""
        print("\n📋 INFORMACIÓN DEL PROBLEMA:")
        print(f"   • Número de trabajos: {self.num_jobs}")
        print(f"   • Número de máquinas: {len(self.machines)}")
        print(f"   • Número de operaciones por trabajo: {self.num_machines}")
        
        print("\n⚙️  TIEMPOS DE PROCESAMIENTO:")
        for i, times in enumerate(self.processing_times):
            print(f"   Trabajo {i+1}: {times}")
        
        print("\n🔄 SECUENCIA DE MÁQUINAS:")
        for i, seq in enumerate(self.machines_sequence):
            print(f"   Trabajo {i+1}: {seq}")
    
    def _print_schedule_details(self, schedule, makespan, solver_type):
        """Imprime detalles del schedule encontrado"""
        print(f"\n✅ SOLUCIÓN ENCONTRADA ({solver_type})")
        print(f"🎯 MAKESPAN: {makespan}")
        
        print("\n📅 SCHEDULE DETALLADO:")
        for machine in range(len(self.machines)):
            machine_schedule = schedule.get(machine, [])
            if machine_schedule:
                print(f"\n   Máquina {machine + 1}:")
                for job, op, start, end in sorted(machine_schedule, key=lambda x: x[2]):
                    print(f"      J{job+1} O{op+1}: [{start:.1f} - {end:.1f}]")


# =============================================================================
# EJEMPLO DE USO - RESOLVIENDO NUESTRO PROBLEMA
# =============================================================================

def main():
    print("DEMOSTRACIÓN DEL SOLUCIONADOR MAESTRO")
    print("Resolviendo el problema con Makespan Objetivo: 37\n")
    
    # Datos en formato processing_times y machines_sequence
    processing_times = [
        [7, 10, 8],   # Trabajo 1
        [4, 6, 12],   # Trabajo 2  
        [8, 8, 7]     # Trabajo 3
    ]
    
    machines_sequence = [
        [1, 3, 2],    # Trabajo 1: M1 -> M3 -> M2
        [2, 1, 3],    # Trabajo 2: M2 -> M1 -> M3
        [1, 2, 3]     # Trabajo 3: M1 -> M2 -> M3
    ]
    
    # Crear solucionador
    solver = MasterSchedulingSolver(
        processing_times=processing_times,
        machines_sequence=machines_sequence
    )
    
    # Resolver con método automático
    makespan, schedule = solver.solve_complete_problem(method='AUTO', plot_results=True)
    
    # Comparar con objetivo
    objetivo = 37
    if makespan == objetivo:
        print(f"\n🎉 ¡OBJETIVO ALCANZADO! Makespan = {objetivo}")
    else:
        print(f"\n📊 Comparación: Objetivo {objetivo} vs Resultado {makespan}")
        print(f"   Diferencia: {makespan - objetivo}")

if __name__ == "__main__":
    main()