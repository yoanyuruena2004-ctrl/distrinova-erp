import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================
# Datos de entrada
# ==========================
data = {
    "Job":[1,2,3,4,5,6,7,8,9,10],
    "Rj":[8,0,4,8,3,0,12,2,5,15],
    "Pj":[6,1,3,7,6,2,8,4,5,3],
    "Dj":[22,3,10,20,16,5,30,8,18,29]
}
df = pd.DataFrame(data)

# ==========================
# Función para construir un schedule
# ==========================
def build_schedule(jobs):
    time = 0
    schedule = []
    for job in jobs:
        r, p, d = df.loc[df.Job==job, ["Rj","Pj","Dj"]].values[0]
        start = max(time, r)
        c = start + p
        f = c - r
        t = max(0, c - d)
        w = f - p
        schedule.append([job,r,p,d,start,c,f,t,w])
        time = c
    sched_df = pd.DataFrame(schedule, columns=["Job","Rj","Pj","Dj","Sj","Cj","Fj","Tj","Wj"])
    return sched_df

# ==========================
# Reglas de despacho
# ==========================
def rule_fcfs():
    return df.sort_values("Rj")["Job"].tolist()

def rule_spt():
    return df.sort_values(["Pj","Rj"])["Job"].tolist()

def rule_lpt():
    return df.sort_values(["Pj","Rj"], ascending=[False,True])["Job"].tolist()

def rule_edd():
    return df.sort_values(["Dj","Rj"])["Job"].tolist()

def rule_str():
    slack = df["Dj"]-df["Pj"]
    return df.assign(Slack=slack).sort_values(["Slack","Rj"])["Job"].tolist()

rules = {
    "FCFS": rule_fcfs,
    "SPT": rule_spt,
    "LPT": rule_lpt,
    "EDD": rule_edd,
    "STR": rule_str
}

# ==========================
# Calcular métricas
# ==========================
def calc_metrics(schedule):
    Cmax = schedule["Cj"].max()
    SumC = schedule["Cj"].sum()
    F_bar = schedule["Fj"].mean()
    W_bar = schedule["Wj"].mean()
    NT = (schedule["Tj"]>0).sum()
    Tmax = schedule["Tj"].max()
    SumT = schedule["Tj"].sum()
    return {
        "Cmax":Cmax,"SumC":SumC,"F_bar":round(F_bar,1),
        "W_bar":round(W_bar,1),"NT":NT,"Tmax":Tmax,"SumT":SumT
    }

# ==========================
# Ejecutar reglas y guardar resultados
# ==========================
results = {}
for name,rule in rules.items():
    order = rule()
    sched = build_schedule(order)
    metrics = calc_metrics(sched)
    results[name] = {"order":order,"schedule":sched,"metrics":metrics}

# Exportar a Excel
out_xlsx = "scheduling_results.xlsx"
with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
    for name in results:
        results[name]["schedule"].to_excel(writer, sheet_name=name, index=False)
    metrics_df = pd.DataFrame({r:results[r]["metrics"] for r in results}).T
    metrics_df.to_excel(writer, sheet_name="Metrics")

print("Resultados exportados a", out_xlsx)

# ==========================
# RADIAL: Comparación de métricas por regla
# ==========================
metric_keys = ["Cmax","SumC","F_bar","W_bar","NT","Tmax","SumT"]
rules_list = list(results.keys())

matrix = np.array([[results[r]["metrics"][k] for k in metric_keys] for r in rules_list])
maxs = matrix.max(axis=0)
maxs[maxs==0]=1
norm = matrix / maxs  # normalización 0-1

N = len(metric_keys)
angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
angles += angles[:1]

plt.figure(figsize=(10,8))
ax = plt.subplot(111, polar=True)
for i,r in enumerate(rules_list):
    vals = norm[i].tolist()
    vals += vals[:1]
    ax.plot(angles, vals, label=r, linewidth=2)
    ax.fill(angles, vals, alpha=0.15)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(metric_keys)
ax.set_yticklabels([])
ax.set_title("Comparación radial: métricas por regla de despacho", y=1.1)
ax.legend(loc="upper right", bbox_to_anchor=(1.2,1.1))
plt.tight_layout()
plt.savefig("radial_metrics.png", dpi=300)
plt.show()
