# -- coding: utf-8 --
# Implementación de 1|prec|ΣWjCj según las diapositivas:
#  - Dentro de cada color: ordenar por p_j/w_j ascendente
#  - Entre colores: ordenar por (sum p_j)/(sum w_j) ascendente

# Datos
trabajos = [1,2,3,4,5,6,7,8,9,10,11]
p =    [16,20,12, 5,22,18,14,14,13,22,20]
w =    [ 4, 7, 3, 5,11, 8, 2, 7, 6, 9,10]

# Colores (según enunciado)
colores = {
    "Rojo":   [2,3,6,7],
    "Blanco": [1,5,8],
    "Azul":   [4,9,10,11]
}

# Helper: obtener índice en listas (trabajos comienza en 1)
def idx(j): return trabajos.index(j)

# 1) Orden interno por p_j/w_j y cálculo de razón del grupo como sum(p)/sum(w)
grupos = []
for color, lista in colores.items():
    datos = []
    for j in lista:
        pj = p[idx(j)]
        wj = w[idx(j)]
        ratio = pj / wj
        datos.append((j, pj, wj, ratio))
    # ordenar internamente por (ratio, pj) para desempates coherentes
    datos.sort(key=lambda x: (x[3], x[1]))
    sum_p = sum(d[1] for d in datos)
    sum_w = sum(d[2] for d in datos)
    group_ratio = sum_p / sum_w
    grupos.append({
        "color": color,
        "jobs_sorted": datos,
        "sum_p": sum_p,
        "sum_w": sum_w,
        "group_ratio": group_ratio
    })

# 2) Mostrar cada grupo (en el orden original de colores)
print("Orden interno por color (p_j/w_j ascendente) y razón de grupo (sum p / sum w):\n")
for g in grupos:
    print(f"{g['color']}:")
    for j, pj, wj, r in g['jobs_sorted']:
        print(f"   Trabajo {j}  p={pj}  w={wj}  p/w={r:.4g}")
    print(f"   suma p = {g['sum_p']}, suma w = {g['sum_w']},  (sum p)/(sum w) = {g['group_ratio']:.3f}\n")

# 3) Ordenar los grupos por group_ratio ascendente (esto da la prioridad entre colores)
grupos_ord = sorted(grupos, key=lambda x: x['group_ratio'])
print("Orden entre colores (por (sum p)/(sum w) ascendente):")
for g in grupos_ord:
    print(f"  {g['color']:7s} -> (sum p)/(sum w) = {g['group_ratio']:.3f}")
print()

# 4) Secuencia final: concatenar los jobs en el orden de los grupos ordenados
secuencia = []
for g in grupos_ord:
    secuencia.extend([t[0] for t in g['jobs_sorted']])

print("Secuencia final de trabajos (ejecución):")
print(" -> ".join(f"{j}" for j in secuencia))
print()

# 5) Calcular tiempos de finalización Cj y Σ wj*Cj para la secuencia final
t = 0
C = {}
wC_sum = 0
print("Detalle Cj y wj*Cj:")
for j in secuencia:
    pj = p[idx(j)]
    wj = w[idx(j)]
    t += pj
    C[j] = t
    contrib = wj * t
    wC_sum += contrib
    print(f"  J{j}: p={pj}, w={wj}, C={t}, w*C={contrib}")

print(f"\nΣ wj*Cj = {wC_sum}")