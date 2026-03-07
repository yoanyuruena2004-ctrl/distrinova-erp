import pandas as pd

# ============================
# Datos del problema
# ============================
jobs = {
    "Job": [1, 2, 3, 4, 5, 6],
    "Pj":  [10, 3, 7, 8, 5, 10]
}

df = pd.DataFrame(jobs)

# ============================
# Aplicar la regla SPT
# ============================
df = df.sort_values(by="Pj").reset_index(drop=True)

# Calcular tiempos
start_times = []
completion_times = []
flow_times = []
wait_times = []

time = 0
for _, row in df.iterrows():
    start = time
    completion = start + row["Pj"]
    flow = completion  # sin tiempos de liberación
    wait = flow - row["Pj"]

    start_times.append(start)
    completion_times.append(completion)
    flow_times.append(flow)
    wait_times.append(wait)

    time = completion

# Agregar columnas al DataFrame
df["Start"] = start_times
df["Cj"] = completion_times
df["Fj"] = flow_times
df["Wj"] = wait_times

# ============================
# Calcular métricas globales
# ============================
Cmax = df["Cj"].max()
SumC = df["Cj"].sum()
F_bar = round(df["Fj"].mean(), 1)
W_bar = round(df["Wj"].mean(), 1)

metrics = {
    "Cmax": Cmax,
    "∑Cj": SumC,
    "F̅": F_bar,
    "W̅": W_bar
}

# ============================
# Mostrar resultados
# ============================
print("=== RESULTADOS SPT ===")
print(df)
print("\nMétricas globales:")
for k, v in metrics.items():
    print(f"{k}: {v}")

# ============================
# Exportar a Excel
# ============================
out_xlsx = "SPT_Scheduling_Results.xlsx"
with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="SPT_Schedule")
    pd.DataFrame([metrics]).to_excel(writer, index=False, sheet_name="Métricas")

print(f"\nResultados exportados a {out_xlsx}")
