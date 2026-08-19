from faker import Faker
import random
import pandas as pd

fake = Faker('es_ES')  # Español
random.seed(42)


def generate_fake_user_data(number_users):
    users = []
    for i in range(number_users):
        user = {"id_usuario": i+1, 
                "nombre": fake.name(), 
                "email": fake.email(), 
                "fecha_registro": fake.date_between(start_date='-60d', end_date='today')}
        users.append(user)
    return users


def generate_fake_post_data(number_posts):
    posts = []
    for i in range(number_posts):
        post = {"id_post": i+1,
            "id_usuario": random.randint(1,100),
            "contenido": fake.text(max_nb_chars=200),
            "fecha_publicacion": fake.date_between(start_date='-60d', end_date='today'),
            "likes": random.randint(0, 200),
            "comentarios": random.randint(0, 75),
            "compartidos": random.randint(0, 25)}
        posts.append(post)
    return posts


print("🔄 Generando datos...")

# Creamos un dataframe con los usuarios
usuarios = generate_fake_user_data(350)
df_usuarios = pd.DataFrame(usuarios)
df_usuarios.to_csv('usuarios.csv', index=False, encoding='utf-8-sig')
print(f"✅ usuarios.csv - {len(usuarios)} registros")

# Creamos un dataframe con los posts
posts = generate_fake_post_data(1250)
df_posts = pd.DataFrame(posts)
df_posts.to_csv('posts.csv', index=False, encoding='utf-8-sig')
print(f"✅ posts.csv - {len(posts)} registros")

print("\n📊 Resumen:")
print(f"Usuarios: {len(usuarios)}")
print(f"Posts: {len(posts)}")