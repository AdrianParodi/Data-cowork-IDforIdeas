import numpy as np
import pandas as pd
from faker import Faker

fake = Faker()
np.random.seed(35)

n = 5000
tipo_categoria = ["tech", "design", "business"]
prob_por_categoria = [0.5, 0.3, 0.2]

print("🔄 Generando datos con sesgo horario y categorías...")

# Configuración de comportamiento según la categoría
# ctr: click-through rate
config_categoria = {
    "tech": {
        "ctr_likes": (0.02, 0.04),
        "ctr_comments": (0.005, 0.015),
        "ctr_shares": (0.008, 0.020),
        "long_media_y_desviacion": (400, 100),
    },
    "design": {
        "ctr_likes": (0.05, 0.09),
        "ctr_comments": (0.002, 0.008),
        "ctr_shares": (0.002, 0.006),
        "long_media_y_desviacion": (300, 50),
    },
    "business": {
        "ctr_likes": (0.01, 0.03),
        "ctr_comments": (0.003, 0.010),
        "ctr_shares": (0.004, 0.010),
        "long_media_y_desviacion": (150, 30),
    },
}

# 1. Asignar categoría y horario
categoria_post = np.random.choice(tipo_categoria, size=n, p=prob_por_categoria)

# Pesos de probabilidad de publicación por hora (24h: más publicaciones en horario laboral)
prob_horas = [
    0.01, 0.005, 0.005, 0.005, 0.005, 0.01, 0.02, 0.04,  # 00 - 07 hs
    0.08, 0.09, 0.10, 0.08, 0.065, 0.055, 0.05, 0.06,      # 08 - 15 hs
    0.07, 0.08, 0.07, 0.04, 0.025, 0.015, 0.01, 0.01     # 16 - 23 hs
]
horas_asignadas = np.random.choice(range(24), size=n, p=prob_horas)

# Generación de fechas con hora integrada
fechas_base = [fake.date_time_between(start_date="-180d") for _ in range(n)]
# Formato string limpio e inequívoco: "YYYY-MM-DD HH:MM:SS"
fecha_pub = [
    dt.replace(
        hour=int(h),
        minute=int(np.random.randint(0, 60)),
        second=int(np.random.randint(0, 60)),
    ).strftime("%Y-%m-%d %H:%M:%S")
    for dt, h in zip(fechas_base, horas_asignadas)
]

# 2. Impresiones base afectadas por el factor de hora
impresiones_base = np.random.lognormal(mean=8, sigma=1.2, size=n).astype(int) + 100

impresiones_finales = []
for imp, h in zip(impresiones_base, horas_asignadas):
    # Definir el multiplicador según la franja horaria
    if h in [8, 9, 10, 11, 17, 18]:  # Pico laboral
        factor_hora = np.random.uniform(1.3, 1.8)
    elif h in [1, 2, 3, 4, 5]:  # Madrugada / Valle
        factor_hora = np.random.uniform(0.3, 0.6)
    else:  # Horas normales
        factor_hora = np.random.uniform(0.8, 1.2)
        
    impresiones_finales.append(int(imp * factor_hora))

impresiones = np.array(impresiones_finales)

# 3. Vistas e interacciones
vistas = (impresiones * np.random.uniform(0.65, 0.95, size=n)).astype(int)

likes, comentarios, shares, longitud = [], [], [], []

for vista, categoria in zip(vistas, categoria_post):
    cfg = config_categoria[categoria]

    # Proporciones de vistas que seran likes, comentarios, shares...
    p_like = np.random.uniform(*cfg["ctr_likes"])
    p_comment = np.random.uniform(*cfg["ctr_comments"])
    p_share = np.random.uniform(*cfg["ctr_shares"])

    likes.append(int(vista * p_like))
    comentarios.append(int(vista * p_comment))
    shares.append(int(vista * p_share))
    
    # Generar la longitud y asegurar un mínimo de 30 caracteres
    val_long = np.random.normal(*cfg["long_media_y_desviacion"])
    longitud.append(max(30, int(val_long)))

# 4. Construcción de DataFrame
posts = pd.DataFrame({
    "id_post": range(1, n + 1),
    "fecha_publicacion": fecha_pub,
    "hora": horas_asignadas,
    "categoria": categoria_post,
    "impresiones": impresiones,
    "vistas": vistas,
    "likes": likes,
    "comentarios": comentarios,
    "shares": shares,
    "longitud": longitud,
})


posts.to_csv("posts_categorias.csv", index=False)

print("\n📊 Resumen:")
print(f"✅ posts_categorias.csv - {len(posts)} registros creados con éxito.")










# import numpy as np
# import pandas as pd
# from faker import Faker

# fake = Faker()

# np.random.seed(35)
# n = 5000
# tipo_categoria = ["tech", "design", "business"]
# prob_por_categoria = [0.5, 0.3, 0.2]

# print("🔄 Generando datos...")

# # Estructura de datos
# id_post = range(1, n+1)
# fecha_pub = [fake.date_between(start_date="-180d") for i in range(n)]
# categoria_post = np.random.choice(tipo_categoria, size=n, p=prob_por_categoria)
# impresiones = np.random.lognormal(mean=8, sigma=1.2, size=n).astype(int) + 100
# vistas = (impresiones*np.random.uniform(0.65, 0.95, size=n)).astype(int)

# likes, comentarios, shares, longitud = [], [], [], []

# # Configuración de comportamiento (tasas de conversión) según la categoría
# # ctr: click-through rate (valores minimos y maximos esperados por categoria)
# config_categoria = {
#     'tech':     {'ctr_likes': (0.02, 0.04), 
#                  'ctr_comments': (0.005, 0.015), 
#                  'ctr_shares': (0.008, 0.020),
#                  'long_media_y_desviacion': (400, 100)},  # Alto en shares y comments
#     'design':   {'ctr_likes': (0.05, 0.09), 
#                  'ctr_comments': (0.002, 0.008), 
#                  'ctr_shares': (0.002, 0.006),
#                  'long_media_y_desviacion': (300, 50)},  # Muy alto en likes
#     'business': {'ctr_likes': (0.01, 0.03), 
#                  'ctr_comments': (0.003, 0.010), 
#                  'ctr_shares': (0.004, 0.010),
#                  'long_media_y_desviacion': (150, 30)}   # Rendimiento moderado
# }

# for vista, categoria in zip(vistas, categoria_post):
#     cfg = config_categoria[categoria]

#     # Muestreo de tasas de conversion
#     p_like = np.random.uniform(*cfg["ctr_likes"])
#     p_comment = np.random.uniform(*cfg["ctr_comments"])
#     p_share = np.random.uniform(*cfg["ctr_shares"])

#     likes.append(int(vista*p_like))
#     comentarios.append(int(vista*p_comment))
#     shares.append(int(vista*p_share))
#     longitud.append(int(np.random.normal(*cfg['long_media_y_desviacion'])))


# # Creamos el DataFrame con todos los posts
# posts = pd.DataFrame({"id_post": id_post, 
# "fecha_publicacion": fecha_pub,
# "categoria": categoria_post,
# "impresiones": impresiones,
# "vistas": vistas,
# "likes": likes,
# "comentarios": comentarios,
# "shares": shares,
# "longitud": longitud,
# })

# posts.to_csv("posts_categorias.csv", index=False)


# print("\n📊 Resumen:")
# print(f"✅ posts_categorias.csv - {len(posts)} registros")

# prob_horas = [
#     0.01, 0.005, 0.005, 0.005, 0.005, 0.01, 0.02, 0.04,  # 00 - 07 hs
#     0.08, 0.09, 0.10, 0.08, 0.065, 0.055, 0.05, 0.06,      # 08 - 15 hs
#     0.07, 0.08, 0.07, 0.04, 0.025, 0.015, 0.01, 0.01     # 16 - 23 hs
# ]

