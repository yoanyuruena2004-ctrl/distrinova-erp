import pandas as pd

# ============================
# Datos del problema
# ============================
jobs = {
    "Job": [1, 2, 3, 4, 5, 6],
    "Pj":  [10, 3, 7, 8, 5, 10],
    "Wj":  [200, 600, 1000, 1000, 800, 400]  # utilidad = peso
}

df = pd.DataFrame(jobs)

# ============================
# Regla WSPT: ordenar por Pj/Wj
# ============================
df["Pj/Wj"] = df["Pj"] / df["Wj"]
df = df.sort_values(by="Pj/Wj").reset_index(drop=True)

# ============================
# Calcular tiempos
# ============================
start_times = []
completion_times = []
weighted_completion = []

time = 0
for _, row in df.iterrows():
    start = time
    completion = start + row["Pj"]
    weighted_c = row["Wj"] * completion

    start_times.append(start)
    completion_times.append(completion)
    weighted_completion.append(weighted_c)

    time = completion

# Agregar columnas
df["Start"] = start_times
df["Cj"] = completion_times
df["Wj*Cj"] = weighted_completion

# ============================
# Calcular métricas
# ============================
Cmax = df["Cj"].max()
SumC = df["Cj"].sum()
SumWjCj = df["Wj*Cj"].sum()
F_bar = round(df["Cj"].mean(), 1)

metrics = {
    "Cmax": Cmax,
    "∑Cj": SumC,
    "F̅": F_bar,
    "∑(Wj*Cj)": SumWjCj
}

# ============================
# Mostrar resultados
# ============================
print("=== RESULTADOS WSPT ===")
print(df)
print("\nMétricas globales:")
for k, v in metrics.items():
    print(f"{k}: {v}")

# ============================
# Exportar a Excel
# ============================
out_xlsx = "WSPT_Scheduling_Results.xlsx"
with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="WSPT_Schedule")
    pd.DataFrame([metrics]).to_excel(writer, index=False, sheet_name="Métricas")

print(f"\nResultados exportados a {out_xlsx}")
