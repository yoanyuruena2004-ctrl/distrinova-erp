import matplotlib.pyplot as plt

def calcular_sistema(etapas):
    # --- Capacidad de cada tarea ---
    capacidades_tarea = {}
    for t in etapas:
        capacidad = 3600 / t["tiempo"] * t["maquinas"]   # unidades/hora
        capacidades_tarea[t["tarea"]] = capacidad

    # --- Agrupar por etapas ---
    etapas_dict = {}
    for t in etapas:
        if t["etapa"] not in etapas_dict:
            etapas_dict[t["etapa"]] = 0
        etapas_dict[t["etapa"]] += capacidades_tarea[t["tarea"]]

    # --- Capacidad del sistema ---
    capacidad_sistema = min(etapas_dict.values())   # TH
    CT = 3600 / capacidad_sistema                   # Tiempo de ciclo
    tiempos_etapa = {e: 3600 / cap for e, cap in etapas_dict.items()}
    T0 = sum(tiempos_etapa.values())                # Tiempo total en el sistema
    WIP = capacidad_sistema * (T0 / 3600)           # Ley de Little

    # --- Eficiencia ---
    N = len(etapas_dict)
    eficiencia = (T0 / (N * CT)) * 100

    # --- Productividad por máquina ---
    total_maquinas = sum(t["maquinas"] for t in etapas)
    prod_maquina = capacidad_sistema / total_maquinas

    # --- Mostrar resultados ---
    print("========================================")
    print("RESULTADOS DEL SISTEMA")
    print("========================================")
    print("Capacidades por tarea (u/h):")
    for t, cap in capacidades_tarea.items():
        print(f" - {t}: {cap:.2f}")
    print()
    print("Capacidades por etapa (u/h):")
    for e, cap in etapas_dict.items():
        print(f" - Etapa {e}: {cap:.2f}")
    print()
    print(f"Capacidad del sistema (TH): {capacidad_sistema:.2f} u/h")
    print(f"Tiempo de ciclo (CT): {CT:.2f} s/unidad")
    print(f"Tiempo total en el sistema (T0): {T0:.2f} s")
    print(f"WIP (Ley de Little): {WIP:.2f} unidades")
    print(f"Eficiencia del sistema: {eficiencia:.2f}%")
    print(f"Productividad por máquina: {prod_maquina:.2f} u/h-máquina")
    print("========================================")

    # --- Graficar capacidades por etapa ---
    etapas_labels = list(etapas_dict.keys())
    capacidades = list(etapas_dict.values())
    cuello = min(capacidades)

    colores = ["red" if cap == cuello else "skyblue" for cap in capacidades]

    plt.figure(figsize=(8,5))
    plt.bar(etapas_labels, capacidades, color=colores)
    plt.xlabel("Etapas")
    plt.ylabel("Capacidad (u/h)")
    plt.title("Capacidad por Etapa (cuello de botella en rojo)")
    plt.show()


# -----------------------------
# Datos del ejercicio
# -----------------------------
if __name__ == "__main__":
    etapas = [
        {"etapa": 1, "tarea": "A", "tiempo": 50, "maquinas": 1},
        {"etapa": 1, "tarea": "B", "tiempo": 60, "maquinas": 1},
        {"etapa": 2, "tarea": "C1", "tiempo": 40, "maquinas": 1},
        {"etapa": 2, "tarea": "C2", "tiempo": 60, "maquinas": 1},
        {"etapa": 3, "tarea": "D", "tiempo": 40, "maquinas": 1},
        {"etapa": 4, "tarea": "E1", "tiempo": 100, "maquinas": 1},
        {"etapa": 4, "tarea": "E2", "tiempo": 100, "maquinas": 1},
        {"etapa": 5, "tarea": "F", "tiempo": 45, "maquinas": 1},
    ]

    calcular_sistema(etapas)
