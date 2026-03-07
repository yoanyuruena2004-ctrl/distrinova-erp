# crash_punto9_pulp.py
import pulp

# -----------------------------
# Datos del problema (tabla)
# -----------------------------
# Actividad: (P_normal, P_crash, CostoNormal, CostoCrash, predecesores list)
activities = {
    "A": (5, 5,  5000,  5000,  []),
    "B": (4, 2,  6000, 12000,  []),
    "C": (7, 4,   800,  2600, ["A"]),
    "D": (6, 6,  2000,  2000, ["B"]),
    "E": (13,7,  4000,  6400, ["C"]),
    "F": (9, 3,  1000,  7000, ["C"]),   # F depende de C (según tabla que usamos)
    "G": (11,7,  2000,  4000, ["D"]),
    "H": (5, 5,  5000,  5000, ["D"]),
    "I": (12,6, 8000, 20000, ["E","F"]),
    "J": (8, 4,   500,  2500, ["F","G"]),
    "K": (15,10,  700,  4700, ["H"]),
    "L": (10,5,  1200,  3200, ["I"]),
    "M": (7, 3, 10000, 16000, ["J","K"]),
    "N": (8, 4,  4000,  8000, ["L","M"]),
}

# Costo indirecto por periodo (unidad de tiempo usada en P_normal/P_crash)
indirect_cost_per_period = 1200.0

# -----------------------------
# Preparar el modelo MILP
# -----------------------------
model = pulp.LpProblem("Crashing_Punto9", pulp.LpMinimize)

# Variables:
# s[a] = start time of activity a (continuous >=0)
# x[a] = 1 if activity a is crashed (usamos tiempo acelerado), 0 otherwise
# T   = makespan (finish of project)
s = {a: pulp.LpVariable(f"s_{a}", lowBound=0, cat="Continuous") for a in activities}
x = {a: pulp.LpVariable(f"x_{a}", cat="Binary") for a in activities}
T = pulp.LpVariable("T", lowBound=0, cat="Continuous")

# Precompute parameters
Pn = {a: activities[a][0] for a in activities}
Pc = {a: activities[a][1] for a in activities}
CostN = {a: activities[a][2] for a in activities}
CostC = {a: activities[a][3] for a in activities}
preds = {a: activities[a][4] for a in activities}

# incremental cost to crash (assumed non-negative)
inc_cost = {a: max(0.0, CostC[a] - CostN[a]) for a in activities}

# Objective: sum(inc_cost[a]*x[a]) + indirect_cost * T
model += (pulp.lpSum(inc_cost[a] * x[a] for a in activities)
          + indirect_cost_per_period * T), "TotalCost"

# Constraints:
# 1) Precedence finish -> start: s_j >= s_i + duration_i
#    duration_i = Pn[i] - x_i*(Pn[i]-Pc[i])  (linear because Pn-Pc is constant)
for i in activities:
    for j in preds[i]:  # those j are predecessors of i; we want s_i >= s_j + dur_j
        # careful: preds dict is predecessors; we'll add constraint for each edge p->i
        pass

# We defined preds as preds[a] = predecessors of a.
# So for each a and each p in preds[a]: s_a >= s_p + duration_p
for a in activities:
    for p in preds[a]:
        reduction = Pn[p] - Pc[p]  # positive or zero
        # s_a >= s_p + Pn[p] - reduction * x_p
        model += s[a] >= s[p] + Pn[p] - reduction * x[p], f"prec_{p}_to_{a}"

# 2) Makespan T must be >= finish of each activity: T >= s_a + duration_a
for a in activities:
    reduction = Pn[a] - Pc[a]
    model += T >= s[a] + Pn[a] - reduction * x[a], f"T_ge_finish_{a}"

# (Optional) You may want to bound start times not to explode; not necessary here.

# Solve (default CBC)
solver = pulp.PULP_CBC_CMD(msg=True, timeLimit=300)
res = model.solve(solver)

# -----------------------------
# Imprimir resultados
# -----------------------------
status = pulp.LpStatus[model.status]
print("Status:", status)
if status != "Optimal" and status != "Not Solved":
    print("Aviso: el solver no devolvió solución óptima; estado:", status)

# Selected crash decisions
crashed = [a for a in activities if pulp.value(x[a]) > 0.5]
print("\nActividades aceleradas (x=1):", crashed)

# Duraciones efectivas y tiempos
dur_eff = {a: Pn[a] - (Pn[a]-Pc[a]) * (1 if a in crashed else 0) for a in activities}
starts = {a: pulp.value(s[a]) for a in activities}
finishes = {a: starts[a] + dur_eff[a] for a in activities}

print("\nActividad | Pn -> Pc | Dur. elegida | Start  | Finish | IncCost")
for a in activities:
    print(f"{a:>8} | {Pn[a]:>2} -> {Pc[a]:>2} | {dur_eff[a]:>12} | {starts[a]:7.2f} | {finishes[a]:7.2f} | {inc_cost[a]:8.2f}")

Tval = pulp.value(T)
direct_crash_cost = sum(inc_cost[a] * pulp.value(x[a]) for a in activities)
total_cost = pulp.value(model.objective)

print(f"\nMakespan (T) = {Tval:.2f} periodos")
print(f"Costo directo por crash = {direct_crash_cost:.2f}")
print(f"Costo indirecto ({indirect_cost_per_period} x T) = {indirect_cost_per_period * Tval:.2f}")
print(f"Coste total (objetivo) = {total_cost:.2f}")
