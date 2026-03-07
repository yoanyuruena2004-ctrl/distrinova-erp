# calculadora_basica.py

# Pedir dos números al usuario
a = float(input("Ingrese el primer número: "))
b = float(input("Ingrese el segundo número: "))

# Operaciones
suma = a + b
resta = a - b
multiplicacion = a * b
division = a / b if b != 0 else "No se puede dividir entre cero"

# Mostrar resultados
print("\n--- Resultados ---")
print(f"Suma: {suma}")
print(f"Resta: {resta}")
print(f"Multiplicación: {multiplicacion}")
print(f"División: {division}")
