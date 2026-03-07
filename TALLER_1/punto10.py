import pulp as pl

# ==============================
# Definición del modelo
# ==============================
model = pl.LpProblem("Crashing", pl.LpMinimize)

# Conjunto de actividades
ACTIVIDADES = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N"]

# Duraciones normales y crash
DurNormal = {
    "A":5,"B":4,"C":7,"D":6,"E":13,"F":9,"G":11,"H":5,"I":12,"J":8,"K":15,"L":10,"M":7,"N":8
}
DurCrash = {
    "A":5,"B":2,"C":4,"D":6,"E":7,"F":3,"G":7,"H":5,"I":6,"J":4,"K":10,"L":5,"M":3,"N":4
}

# Costos normal y crash
CostoNormal = {
    "A":5000,"B":6000,"C":800,"D":2000,"E":4000,"F":1000,"G":2000,"H":5000,"I":8000,"J":500,
    "K":700,"L":1200,"M":10000,"N":4000
}
CostoCrash = {
    "A":5000,"B":12000,"C":2600,"D":2000,"E":6400,"F":7000,"G":4000,"H":5000,"I":20000,"J":2500,
    "K":4700,"L":3200,"M":16000,"N":8000
}

# Precedencias (según tu modelo AMPL)
Precedencias = [
    ("A","C"),("C","E"),("C","F"),("B","D"),("D","G"),("D","H"),
    ("E","I"),("F","I"),("F","J"),("G","J"),("H","K"),("I","L"),
    ("J","M"),("K","M"),("L","N"),("M","N")
]

CostoIndirecto = 1200

# ==============================
# Variables de decisión
# ==============================
y = pl.LpVariable.dicts("Crash", ACTIVIDADES, 0, 1, pl.LpBinary)
Dur = pl.LpVariable.dicts("Dur", ACTIVIDADES, lowBound=0)
CostoAct = pl.LpVariable.dicts("CostoAct", ACTIVIDADES, lowBound=0)
Start = pl.LpVariable.dicts("Start", ACTIVIDADES, lowBound=0)
TFin = pl.LpVariable("TFin", lowBound=0)

# ==============================
# Restricciones
# ==============================
for i in ACTIVIDADES:
    model += Dur[i] == (1 - y[i]) * DurNormal[i] + y[i] * DurCrash[i]
    model += CostoAct[i] == (1 - y[i]) * CostoNormal[i] + y[i] * CostoCrash[i]

for (i,j) in Precedencias:
    model += Start[j] >= Start[i] + Dur[i]

for i in ACTIVIDADES:
    model += TFin >= Start[i] + Dur[i]

# ==============================
# Función objetivo
# ==============================
model += pl.lpSum(CostoAct[i] for i in ACTIVIDADES) + CostoIndirecto * TFin

# ==============================
# Resolver
# ==============================
model.solve(pl.PULP_CBC_CMD(msg=0))

print("Estado:", pl.LpStatus[model.status])
print("Tiempo final (TFin):", pl.value(TFin))
print("Costo total:", pl.value(model.objective))
print("\nResultados por actividad:")
print("{:<3} {:<6} {:<6} {:<6} {:<8}".format("Act","Dur","Start","Crash","Costo"))
for i in ACTIVIDADES:
    print("{:<3} {:<6} {:<6} {:<6} {:<8}".format(
        i,
        round(Dur[i].value(),2),
        round(Start[i].value(),2),
        int(y[i].value()),
        round(CostoAct[i].value(),2)
    ))
