import matplotlib.pyplot as plt
import pandas as pd

# ----------------------------
# Datos del problema
# ----------------------------
tasks = {
    "I": {"name": "Box Assembly", "time": 35, "type": "Man"},
    "II": {"name": "Insert Engine", "time": 60, "type": "Man"},
    "III": {"name": "Insert Card", "time": 50, "type": "Man"},
    "IV": {"name": "Welding", "time": 20, "type": "Machine"},
    "V": {"name": "Place Lids", "time": 70, "type": "Man"},
    "VI": {"name": "Performance Test", "time": 30, "type": "Machine"},
    "VII": {"name": "Packing", "time": 25, "type": "Man"}
}

# Alternativas (agrupamiento de tareas)
alternativas = {
    "I": [["I"], ["II"], ["III"], ["IV"], ["V"], ["VI"], ["VII"]],
    "II": [["I"], ["II"], ["III"], ["IV"], ["VI"], ["VII"]],
    "III": [["I"], ["II"], ["III"], ["IV"], ["VI"], ["VII"]]
}

# ----------------------------
# Función para calcular métricas
# ----------------------------
def analizar_alternativa(nombre, estaciones):
    print(f"\n--- Alternativa {nombre} ---")

    tiempos_estacion = []
    mano_obra_total = 0
    maquinaria_total = 0

    for est in estaciones:
        tiempo = sum(tasks[t]["time"] for t in est)
        tiempos_estacion.append(tiempo)
        for t in est:
            if tasks[t]["type"] == "Man":
                mano_obra_total += tasks[t]["time"]
            else:
                maquinaria_total += tasks[t]["time"]

    ciclo = max(tiempos_estacion)  # cuello de botella
    TH = 3600 / ciclo              # unidades por hora
    cuello = estaciones[tiempos_estacion.index(ciclo)]

    # Productividad
    prod_mano_obra = TH / (mano_obra_total/3600)
    prod_maquinaria = TH / (maquinaria_total/3600)

    # Eficiencia
    eficiencia = sum(tiempos_estacion) / (len(estaciones) * ciclo)

    # Costo de MO por producto
    costo_MO = (mano_obra_total/3600) * 5000

    # Resultados
    print(f"Tiempos estaciones: {tiempos_estacion}")
    print(f"Tiempo de ciclo: {ciclo} s")
    print(f"Tasa de producción: {TH:.2f} unid/hora")
    print(f"Cuello de botella: Estación {cuello}")
    print(f"Productividad MO: {prod_mano_obra:.2f} unid/hora-hombre")
    print(f"Productividad Maq: {prod_maquinaria:.2f} unid/hora-máquina")
    print(f"Eficiencia: {eficiencia:.2%}")
    print(f"Costo Mano de Obra por producto: ${costo_MO:.2f}")

    # Gráfico Gantt
    fig, ax = plt.subplots(figsize=(8,4))
    inicio = 0
    for i, est in enumerate(estaciones):
        dur = sum(tasks[t]["time"] for t in est)
        ax.barh(i, dur, left=inicio, color="skyblue", edgecolor="black")
        ax.text(inicio + dur/2, i, f"{','.join(est)} ({dur}s)", 
                ha="center", va="center", color="black")
        inicio += dur
    ax.set_yticks(range(len(estaciones)))
    ax.set_yticklabels([f"Est {i+1}" for i in range(len(estaciones))])
    ax.set_xlabel("Tiempo [s]")
    ax.set_title(f"Diagrama Operación-Tiempo - Alternativa {nombre}")
    plt.show()

# ----------------------------
# Ejecutar análisis
# ----------------------------
for alt, estaciones in alternativas.items():
    analizar_alternativa(alt, estaciones)


