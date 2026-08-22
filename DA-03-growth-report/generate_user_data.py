import random
import pandas as pd

random.seed(42)

meses = range(1,13)

nuevos_usuarios = []
usuarios_activos = []
usuarios_retenidos = []
usuarios_totales = []

for i in range(12):

    # Nuevos usuarios
    nuevos = random.randint(80 + i * 7, 150 + i * 12)
    nuevos_usuarios.append(nuevos)

    # Usuarios totales acumulados
    total = nuevos if i == 0 else usuarios_totales[i - 1] + nuevos
    usuarios_totales.append(total)

    # Nuevos usuarios que se vuelven activos
    nuevos_activos = random.randint(
        int(nuevos * 0.65),
        int(nuevos * 0.90)
    )

    if i == 0:
        # No podemos calcular retención para el primer mes
        retenidos = None
        activos = nuevos_activos
    else:
        # Entre 70% y 90% de los activos del mes anterior se retienen
        retenidos = random.randint(
            int(usuarios_activos[i - 1] * 0.70),
            int(usuarios_activos[i - 1] * 0.90)
        )

        activos = retenidos + nuevos_activos

    usuarios_retenidos.append(retenidos)
    usuarios_activos.append(activos)

df = pd.DataFrame({
    "mes": meses,
    "nuevos_usuarios": nuevos_usuarios,
    "usuarios_totales": usuarios_totales,
    "usuarios_activos": usuarios_activos,
    "usuarios_retenidos": usuarios_retenidos
})

print(df.head(12))

df.to_csv("user_data.csv", index=False)