# Archivo: P_5.py
# Sistema interactivo de ensamble escrito en Python usando Streamlit
# ---------------------------------------------------------------
# Para ejecutar este programa:
#   streamlit run P_5.py
# ---------------------------------------------------------------

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import math

# -------------------------------
# DATOS DE LOS MODELOS
# -------------------------------
model_data = {
    "K6": [
        ("A", 48, "---"), ("B", 30, "---"), ("C", 28, "A, B"), ("D", 32, "C"),
        ("E", 26, "D"), ("F", 42, "D"), ("G", 36, "E"), ("I", 58, "F, G")
    ],
    "UK": [
        ("A", 48, "---"), ("B", 22, "---"), ("C", 18, "A, B"), ("D", 32, "C"),
        ("E", 36, "D"), ("F", 42, "E"), ("G", 40, "E"), ("H", 44, "F"), ("I", 62, "G, H")
    ],
    "KZ": [
        ("A", 58, "---"), ("B", 32, "---"), ("C", 24, "A, B"), ("D", 38, "C"),
        ("E", 44, "D"), ("F", 28, "D"), ("G", 34, "E"), ("H", 40, "F"), ("I", 48, "H"), ("J", 54, "G, I")
    ],
    "K Premium": [
        ("A", 62, "---"), ("B", 38, "---"), ("C", 28, "A, B"), ("D", 32, "C"),
        ("E", 20, "D"), ("F", 24, "D"), ("G", 30, "E"), ("H", 34, "F"), ("I", 48, "H"), ("J", 52, "G"),
        ("K", 50, "I"), ("L", 32, "K")
    ]
}

# Demandas mensuales
monthly_demand = {
    "K6": 4000,
    "UK": 3500,
    "KZ": 1500,
    "K Premium": 1000
}

# Parámetros de producción
dias_mes = 24
horas_dia = 8
segundos_hora = 3600
tiempo_disponible_mensual = dias_mes * horas_dia * segundos_hora

# -------------------------------
# FUNCIONES DEL SISTEMA
# -------------------------------
def calcular_demanda_diaria(model):
    return monthly_demand[model] / dias_mes

def tiempo_compuesto(df):
    return df["Tiempo (s)"].sum()

def tiempo_ciclo_minimo(num_estaciones, t_compuesto):
    return t_compuesto / num_estaciones

def calcular_takt_time(demanda_total):
    tiempo_disponible_diario = horas_dia * segundos_hora
    demanda_diaria_total = demanda_total / dias_mes
    return tiempo_disponible_diario / demanda_diaria_total

# -------------------------------
# DIAGRAMA DE RED CON NETWORKX Y MATPLOTLIB
# -------------------------------
def generar_diagrama(df, modelo):
    # Crear grafo dirigido
    G = nx.DiGraph()
    
    # Agregar nodos con atributos de tiempo
    for _, row in df.iterrows():
        G.add_node(row["Tarea"], tiempo=row["Tiempo (s)"])
    
    # Agregar enlaces según precedencias
    for _, row in df.iterrows():
        if row["Predecesores"] != "---":
            preds = [p.strip() for p in row["Predecesores"].split(',')]
            for p in preds:
                G.add_edge(p, row["Tarea"])
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Diseño del grafo
    pos = nx.spring_layout(G, k=3, iterations=50)
    
    # Dibujar nodos
    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='lightblue', 
                          alpha=0.9, ax=ax)
    
    # Dibujar etiquetas de nodos
    labels = {node: f"{node}\n{data['tiempo']}s" for node, data in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, ax=ax)
    
    # Dibujar aristas
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, 
                          arrowsize=20, ax=ax)
    
    ax.set_title(f"Diagrama de Red - {modelo}", fontsize=16, pad=20)
    ax.axis('off')
    
    return fig

# -------------------------------
# CÁLCULO DE ESTACIONES ÓPTIMAS (SALBP-1 - RPW)
# -------------------------------
def calcular_pesos_posicionales(df):
    pesos = {}

    def obtener_peso(tarea):
        if tarea in pesos:
            return pesos[tarea]

        fila = df[df["Tarea"] == tarea].iloc[0]
        tiempo = fila["Tiempo (s)"]

        if fila["Predecesores"] == "---":
            pesos[tarea] = tiempo
        else:
            preds = [p.strip() for p in fila["Predecesores"].split(',')]
            pesos[tarea] = tiempo + sum(obtener_peso(p) for p in preds)
        return pesos[tarea]

    for tarea in df["Tarea"]:
        obtener_peso(tarea)

    return pesos

def salbp1_rpw(df, ciclo):
    df_local = df.copy()
    pesos = calcular_pesos_posicionales(df_local)
    df_local["Peso"] = df_local["Tarea"].map(pesos)
    df_local = df_local.sort_values(by="Peso", ascending=False)

    estaciones = []
    tiempo_estacion = 0
    actual = []

    for _, row in df_local.iterrows():
        t = row["Tiempo (s)"]
        if tiempo_estacion + t <= ciclo:
            actual.append(row["Tarea"])
            tiempo_estacion += t
        else:
            estaciones.append(actual)
            actual = [row["Tarea"]]
            tiempo_estacion = t

    if actual:
        estaciones.append(actual)

    return estaciones

def calcular_eficiencia(df, estaciones, tiempo_ciclo):
    """Calcula la eficiencia del balanceo"""
    tiempo_total = tiempo_compuesto(df)
    tiempo_total_estaciones = len(estaciones) * tiempo_ciclo
    return (tiempo_total / tiempo_total_estaciones) * 100 if tiempo_total_estaciones > 0 else 0

# -------------------------------
# CÁLCULOS PARA MODELOS MIXTOS (MALBP)
# -------------------------------
def calcular_tiempos_ponderados():
    """Calcula tiempos ponderados según participación en la demanda (MALBP)"""
    demanda_total = sum(monthly_demand.values())
    participaciones = {modelo: demanda / demanda_total for modelo, demanda in monthly_demand.items()}
    
    # Crear conjunto único de todas las tareas
    todas_tareas = set()
    for modelo, tareas in model_data.items():
        for tarea in tareas:
            todas_tareas.add(tarea[0])
    
    # Calcular tiempos ponderados para cada tarea
    tiempos_ponderados = {}
    for tarea in todas_tareas:
        tiempo_ponderado = 0
        for modelo, participacion in participaciones.items():
            # Buscar si la tarea existe en este modelo
            tiempo_tarea = 0
            for tarea_data in model_data[modelo]:
                if tarea_data[0] == tarea:
                    tiempo_tarea = tarea_data[1]
                    break
            tiempo_ponderado += tiempo_tarea * participacion
        tiempos_ponderados[tarea] = tiempo_ponderado
    
    return tiempos_ponderados, participaciones

def crear_df_modelo_mixto():
    """Crea DataFrame con tiempos ponderados para el modelo mixto"""
    tiempos_ponderados, participaciones = calcular_tiempos_ponderados()
    
    # Crear lista de tareas con precedencias (usamos K6 como base para precedencias)
    tareas_mixtas = []
    for tarea_data in model_data["K6"]:
        tarea = tarea_data[0]
        tiempo_pond = tiempos_ponderados.get(tarea, 0)
        precedencias = tarea_data[2]
        tareas_mixtas.append((tarea, tiempo_pond, precedencias))
    
    return pd.DataFrame(tareas_mixtas, columns=["Tarea", "Tiempo (s)", "Predecesores"])

# -------------------------------
# INTERFAZ STREAMLIT
# -------------------------------
st.title("📱 Sistema Interactivo de Ensamble – Archivo: P_5.py")
st.write("**Problema:** Balanceo de línea para 4 modelos de teléfonos (K6, UK, KZ, K Premium)")

# Mostrar información general
st.sidebar.header("📊 Información del Sistema")
st.sidebar.write(f"**Demandas mensuales:**")
for modelo, demanda in monthly_demand.items():
    st.sidebar.write(f"- {modelo}: {demanda:,} unidades")
st.sidebar.write(f"**Tiempo disponible:** {dias_mes} días × {horas_dia} horas = {tiempo_disponible_mensual:,} segundos/mes")

pregunta = st.selectbox(
    "Selecciona la pregunta a resolver:",
    [
        "a) Diagrama de red de operaciones para el ensamble de los teléfonos",
        "b) Coeficiente de demanda dj para cada teléfono",
        "c) Tiempo Compuesto para el ensamble de los cuatro modelos de teléfono",
        "d) Tiempo de ciclo mínimo con 4 estaciones y evaluación de demanda",
        "e) Condición de balanceo para cumplir demanda y eficiencia"
    ]
)

st.subheader("📌 Respuesta:")

# -------------------------------
# RESPUESTAS ESPECÍFICAS AL EJERCICIO
# -------------------------------
if pregunta.startswith("a)"):
    st.write("🔷 **a) Diagrama de red de operaciones para el ensamble de los teléfonos:**")
    
    modelo = st.selectbox("Selecciona el modelo para ver su diagrama:", list(model_data.keys()))
    
    df = pd.DataFrame(model_data[modelo], columns=["Tarea", "Tiempo (s)", "Predecesores"])
    
    try:
        fig = generar_diagrama(df, modelo)
        st.pyplot(fig)
        st.write(f"**Modelo:** {modelo}")
        st.write("**Leyenda:** Cada nodo muestra la tarea y su tiempo en segundos")
    except Exception as e:
        st.error(f"Error al generar el diagrama: {e}")
        st.info("Mostrando información de precedencias en formato tabla:")
        st.dataframe(df[["Tarea", "Predecesores"]])

elif pregunta.startswith("b)"):
    st.write("📉 **b) Coeficiente de demanda dj para cada teléfono:**")
    
    # Calcular para todos los modelos
    resultados = []
    demanda_total = sum(monthly_demand.values())
    
    for modelo_dj in model_data.keys():
        demanda_mensual = monthly_demand[modelo_dj]
        demanda_diaria = calcular_demanda_diaria(modelo_dj)
        participacion = (demanda_mensual / demanda_total) * 100
        
        resultados.append({
            "Modelo": modelo_dj,
            "Demanda Mensual": f"{demanda_mensual:,}",
            "Demanda Diaria (dj)": f"{demanda_diaria:.2f} unidades/día",
            "Participación en Mix": f"{participacion:.1f}%"
        })
    
    df_resultados = pd.DataFrame(resultados)
    st.dataframe(df_resultados)
    
    st.write("**Fórmula:** dj = Demanda Mensual / 24 días")
    st.write("**Nota:** Se asume un mes de 24 días laborales")
    st.write(f"**Demanda total mensual:** {demanda_total:,} unidades")
    st.write(f"**Demanda total diaria:** {demanda_total/dias_mes:.2f} unidades/día")

elif pregunta.startswith("c)"):
    st.write("🧮 **c) Tiempo Compuesto para el ensamble de los cuatro modelos de teléfono:**")
    
    # Calcular tiempo compuesto para todos los modelos
    tiempos_compuestos = {}
    tiempo_total_compuesto = 0
    
    for modelo_tc in model_data.keys():
        df_tc = pd.DataFrame(model_data[modelo_tc], columns=["Tarea", "Tiempo (s)", "Predecesores"])
        tiempo_modelo = tiempo_compuesto(df_tc)
        tiempos_compuestos[modelo_tc] = tiempo_modelo
        tiempo_total_compuesto += tiempo_modelo
    
    # Mostrar resultados en tabla
    resultados_tc = []
    for modelo_tc, tiempo in tiempos_compuestos.items():
        resultados_tc.append({
            "Modelo": modelo_tc,
            "Tiempo Compuesto (s)": tiempo,
            "Tiempo Compuesto (min)": f"{tiempo/60:.2f}"
        })
    
    df_tc_resultados = pd.DataFrame(resultados_tc)
    st.dataframe(df_tc_resultados)
    
    # Resumen
    st.write("**Resumen:**")
    st.write(f"**Suma total de tiempos compuestos:** {tiempo_total_compuesto} segundos ({tiempo_total_compuesto/60:.2f} minutos)")
    
    # Mostrar tiempos ponderados para modelo mixto
    st.write("---")
    st.write("**Tiempos ponderados para modelo mixto (MALBP):**")
    tiempos_ponderados, participaciones = calcular_tiempos_ponderados()
    
    df_ponderado = pd.DataFrame([
        {"Tarea": tarea, "Tiempo Ponderado (s)": f"{tiempo:.2f}"} 
        for tarea, tiempo in tiempos_ponderados.items()
    ])
    st.dataframe(df_ponderado)
    
    tiempo_compuesto_ponderado = sum(tiempos_ponderados.values())
    st.write(f"**Tiempo compuesto ponderado:** {tiempo_compuesto_ponderado:.2f} segundos")

elif pregunta.startswith("d)"):
    st.write("⏱ **d) Si el departamento de ingeniería decide realizar el ensamble de los teléfonos en una celda con cuatro estaciones de ensamble. ¿Cuál sería el tiempo de ciclo mínimo a obtener? ¿Puede cubrir con la totalidad de la demanda?**")
    
    modelo = st.selectbox("Selecciona el modelo para análisis:", list(model_data.keys()))
    
    df = pd.DataFrame(model_data[modelo], columns=["Tarea", "Tiempo (s)", "Predecesores"])
    t_comp = tiempo_compuesto(df)
    num_estaciones = 4  # Fijo según la pregunta
    
    # a) Tiempo de ciclo mínimo
    tc_min = tiempo_ciclo_minimo(num_estaciones, t_comp)
    
    st.write(f"**Cálculos para el modelo {modelo}:**")
    st.write(f"- Tiempo compuesto: {t_comp} segundos")
    st.write(f"- Número de estaciones: {num_estaciones}")
    st.write(f"- **Tiempo de ciclo mínimo:** {tc_min:.2f} segundos")
    
    # b) Evaluación de capacidad vs demanda
    capacidad_mensual = tiempo_disponible_mensual / tc_min
    demanda_modelo = monthly_demand[modelo]
    
    st.write("**Evaluación de capacidad:**")
    st.write(f"- Capacidad mensual: {capacidad_mensual:.0f} unidades")
    st.write(f"- Demanda mensual requerida: {demanda_modelo:,} unidades")
    
    # Evaluación
    if capacidad_mensual >= demanda_modelo:
        st.success("✅ **RESULTADO:** La línea con 4 estaciones SÍ puede cubrir la totalidad de la demanda")
        excedente = capacidad_mensual - demanda_modelo
        st.write(f"**Excedente de capacidad:** {excedente:.0f} unidades")
    else:
        st.error("❌ **RESULTADO:** La línea con 4 estaciones NO puede cubrir la totalidad de la demanda")
        deficit = demanda_modelo - capacidad_mensual
        st.write(f"**Déficit de capacidad:** {deficit:.0f} unidades")
        st.write(f"**Capacidad faltante:** {deficit/demanda_modelo*100:.1f}%")

elif pregunta.startswith("e)"):
    st.write("🔧 **e) Encuentre la condición de balanceo que permita cumplir con la demanda del siguiente mes y su eficiencia:**")
    
    st.write("**Enfoque: Modelo Mixto (MALBP) - Todos los modelos en la misma línea**")
    
    # Calcular demanda total y takt time
    demanda_total = sum(monthly_demand.values())
    takt_time = calcular_takt_time(demanda_total)
    
    st.write("**Cálculo del Takt Time requerido:**")
    st.write(f"- Demanda mensual total: {demanda_total:,} unidades")
    st.write(f"- Demanda diaria total: {demanda_total/dias_mes:.2f} unidades/día")
    st.write(f"- Tiempo disponible diario: {horas_dia * segundos_hora:,} segundos")
    st.write(f"- **Takt Time requerido:** {takt_time:.2f} segundos/unidad")
    
    # Usar modelo mixto con tiempos ponderados
    df_mixto = crear_df_modelo_mixto()
    tiempo_comp_mixto = tiempo_compuesto(df_mixto)
    
    st.write("**Balanceo del modelo mixto:**")
    st.write(f"- Tiempo compuesto del modelo mixto: {tiempo_comp_mixto:.2f} segundos")
    
    # Calcular número mínimo de estaciones
    num_estaciones_min = math.ceil(tiempo_comp_mixto / takt_time)
    st.write(f"- Número mínimo de estaciones requeridas: {num_estaciones_min}")
    
    # Balancear con RPW
    estaciones = salbp1_rpw(df_mixto, takt_time)
    eficiencia = calcular_eficiencia(df_mixto, estaciones, takt_time)
    
    st.write("**Resultado del balanceo (MALBP - Ranked Positional Weight):**")
    
    for i, estacion in enumerate(estaciones, 1):
        tiempo_estacion = sum(df_mixto[df_mixto["Tarea"].isin(estacion)]["Tiempo (s)"])
        st.write(f"**Estación {i}:** {estacion} (Tiempo: {tiempo_estacion:.2f}s)")
    
    st.write("**Métricas de balanceo:**")
    st.write(f"- Número de estaciones resultantes: {len(estaciones)}")
    st.write(f"- Tiempo de ciclo (Takt Time): {takt_time:.2f} segundos")
    st.write(f"- Tiempo ocioso total: {(len(estaciones) * takt_time) - tiempo_comp_mixto:.2f} segundos")
    st.write(f"- **Eficiencia del balanceo:** {eficiencia:.2f}%")
    
    # Evaluación final
    capacidad_linea = (tiempo_disponible_mensual / takt_time)
    st.write(f"- **Capacidad de la línea balanceada:** {capacidad_linea:.0f} unidades/mes")
    st.write(f"- **Demanda total:** {demanda_total:,} unidades/mes")
    
    if capacidad_linea >= demanda_total:
        st.success("✅ **La línea balanceada SÍ puede cumplir con la demanda total**")
    else:
        st.error("❌ **La línea balanceada NO puede cumplir con la demanda total**")
    
    if eficiencia >= 80:
        st.success("✅ **El balanceo es EFICIENTE**")
    elif eficiencia >= 60:
        st.warning("⚠ **El balanceo es ACEPTABLE**")
    else:
        st.error("❌ **El balanceo necesita mejora**")

# -------------------------------
# INFORMACIÓN ADICIONAL
# -------------------------------
st.sidebar.header("🔍 Métodos Utilizados")
st.sidebar.write("- RPW (Ranked Positional Weight)")
st.sidebar.write("- SALBP-1 (Simple Assembly Line Balancing)")
st.sidebar.write("- MALBP (Mixed-Product Assembly Line Balancing)")
st.sidebar.write("- Graph Theory para diagramas de red")

st.sidebar.header("📋 Supuestos")
st.sidebar.write(f"- Mes laboral: {dias_mes} días")
st.sidebar.write(f"- Jornada diaria: {horas_dia} horas")
st.sidebar.write("- Tiempo de setup entre modelos: Despreciable")
st.sidebar.write("- Eficiencia mínima aceptable: 80%")