reset;
model;

set I; # productos
set M; # maquinas

param tiempo {I,M};          # tiempo requerido por producto en cada máquina (minutos)
param demanda_minima {I};    # demanda mínima de cada producto
param tiempo_maquina {M};    # capacidad normal de cada máquina (minutos)
param utilidad {I};          # utilidad por producto

# =====================
# Nuevos parámetros
# =====================
param costo_normal := 3000;   # costo hora normal
param costo_extra  := 3750;   # costo hora extra
param max_extra := 60*60;       # total minutos de horas extras disponibles (12 h * 60)

# =====================
# Variables
# =====================
var X {I} >= 0 integer;     # producción
var Hnorm {M} >= 0;         # minutos normales usados
var Hext  {M} >= 0;         # minutos extras usados
var Hext_total >= 0;        # total de minutos extras usados en todas las máquinas

# =====================
# Función objetivo
# =====================
maximize Z:
    sum{i in I} utilidad[i] * X[i]
  - sum{m in M} ( (costo_normal/60) * Hnorm[m] + (costo_extra/60) * Hext[m] );

# =====================
# Restricciones
# =====================

# Balance de tiempo en cada máquina
subject to balance_tiempo {m in M}:
    sum{i in I} tiempo[i,m] * X[i] <= Hnorm[m] + Hext[m];

# No pasarse de la capacidad normal
subject to limite_normal {m in M}:
    Hnorm[m] <= tiempo_maquina[m];

# Límite global de horas extras
subject to limite_extra_total:
    sum{m in M} Hext[m] <= max_extra;

# Definir la variable total (opcional, por transparencia)
subject to definir_total:
    Hext_total = sum{m in M} Hext[m];

# Cumplir la demanda mínima
subject to restriccion_demanda_min {i in I}:
    X[i] >= demanda_minima[i];

# =====================
# Datos
# =====================
data;

set I := A B C D E F G H I J;
set M := 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16;

param utilidad :=
A 1200 B 1420 C 980 D 1250 E 1600
F 1150 G 880 H 1000 I 1320 J 1280 ;

param tiempo_maquina :=
1 9600 2 9600 3 9600 4 9600 5 9600
6 9600 7 9600 8 9600 9 9600 10 9600
11 9600 12 9600 13 9600 14 9600 15 9600 16 9600 ;

param demanda_minima :=
A 140 B 300 C 380 D 140 E 210
F 180 G 200 H 250 I 150 J 180 ;

param tiempo:
        1   2   3   4   5   6   7   8   9   10  11  12  13 14 15 16 :=
A       1   0   4   0   6   5   6   4   8   4   8   2   4   2   2   2
B       0   5   0   7   8   4   4   0   0   0   0   0   0   5   2   4
C       2   0   4   0   0   6   5   3   4   6   4   2   0   2   2   5
D       2   0   5   4   0   4   4   8   8    8   5  3   0   4   2   4
E       0   8   0   8  10   0   0   0   0   0   4   2   2   5   4   4
F       3   0   4   0   0   6   5   4   5   6   4   0   8   4   3   2
G       4   0   5  10   6   6   8   5   6   8   0   2   0   4   2   2
H       2   0   3   0   0   5   5   0   4   6   5   0   0   4   4   2
I       0   6   0   5   8   0   0   0   8   8   5   5   8   2   2   4
J       0   4   0   2   7   8   6   6   9   4   5   2   8   2   2   4 ;

# =====================
# Solver y resultados
# =====================
option solver cplex;
solve;

display Z;
display X;
display Hnorm, Hext, Hext_total;
