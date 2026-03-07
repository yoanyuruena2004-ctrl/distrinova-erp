reset;

model;



# ---------- Conjuntos ----------

set Tarea;                          

set Tarea_precede within {Tarea,Tarea};  



# ---------- Parámetros ----------

param Tn {i in Tarea} >= 0;      # Tiempo normal

param Ta {i in Tarea} >= 0;      # Tiempo acelerado

param C  {i in Tarea} >= 0;      # Costo normal

param S  {i in Tarea} >= 0;      # Costo acelerado

param H >= 0;                    # Costo indirecto por unidad de tiempo



# ---------- Variables ----------

var X {i in Tarea} >= 0;          # Tiempo de finalización de cada tarea

var Y {i in Tarea} binary;        # 0 = normal, 1 = acelerado

var T {i in Tarea} >= 0;          # Duración efectiva

var Z >= 0;                       # Tiempo total del proyecto (makespan)



# ---------- Relación de duración ----------

s.t. Duracion {i in Tarea}:

    T[i] = Tn[i]*(1 - Y[i]) + Ta[i]*Y[i];



# ---------- Restricciones de precedencia ----------

s.t. Precedencia {(j,i) in Tarea_precede}:

    X[i] >= X[j] + T[i];



# ---------- Definición de makespan ----------

s.t. DefZ {i in Tarea}:

    Z >= X[i];



# ---------- Función objetivo ----------

minimize Costo_Total:

    H*Z + sum {i in Tarea} ( C[i]*(1 - Y[i]) + S[i]*Y[i] );



# -------------------

# Datos de ejemplo

# -------------------

data;



set Tarea := 0 1 2 3 4 5 6 7 8;     



param Tn :=

0 0

1 10

2 5

3 8

4 3

5 7

6 5

7 10

8 2 ;



param Ta :=

0 0

1 5

2 5

3 4

4 1

5 5

6 3

7 7

8 2 ;



param C :=

0 0

1 5000

2 500

3 3000

4 1000

5 4500

6 8000

7 5000

8 5000 ;



param S :=

0 0

1 10000

2 500

3 6000

4 3500

5 9500

6 12000

7 7400

8 5000 ;



param H := 1500;



set Tarea_precede :=

(0,1)

(1,2)

(1,3)

(2,4)

(2,5)

(3,5)

(3,6)

(4,7)

(5,7)

(6,7)

(7,8);



# ---------- Ejecución ----------

option solver "cplex";

option cplex_options "mipdisplay=2 mipgap=0";



solve;



display X, T, Y, Z, Costo_Total;