import random
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from faker import Faker

fake = Faker('es_ES')  # Español
random.seed(42)

# Configuración de la página
st.set_page_config(
    page_title="CoWork Social - Dashboard",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Dashboard de Engagement - CoWork Social")
st.markdown("---")


# ==== CARGAR DATOS SINTETICOS ====
@st.cache_data
def load_data():
    df_usuarios = pd.read_csv("usuarios.csv", encoding="utf-8-sig", parse_dates=["fecha_registro"])
    df_posts = pd.read_csv("posts.csv", encoding="utf-8-sig", parse_dates=["fecha_publicacion"])
    df_interacciones = pd.read_csv("interacciones.csv", encoding="utf-8-sig", parse_dates=["fecha_interaccion"])
    top_usuarios = pd.read_csv("top_10_usuarios.csv", encoding="utf-8-sig")

    return df_usuarios, df_posts, df_interacciones, top_usuarios

usuarios, posts, interacciones, top_usuarios = load_data()


# st.success(f"✅ Datos cargados: {len(usuarios)} usuarios, {len(posts)} posts, {len(interacciones)} interacciones")



# ==== CALCULO DE METRICAS ====
# Interacciones
df_dau = interacciones.groupby("fecha_interaccion").agg(
    usuarios_activos=("id_usuario","nunique")).reset_index()

usuarios_nuevos = usuarios.groupby("fecha_registro").agg(
    usuarios_nuevos=("id_usuario","nunique")).reset_index()


# Calculo de Engagement Rate por dia
interacciones['es_engagement'] = interacciones['tipo_interaccion'].isin(['like', 'comentario'])

# 2. Agrupamos por fecha y con .agg aplicamos las funciones de agregación necesarias
df_diario = interacciones.groupby('fecha_interaccion').agg(
    likes_y_comentarios=('es_engagement', 'sum'),
    total_posts=('id_post', 'nunique') # o el total de posts publicados ese día según tu tabla de posts
).reset_index()

# 3. Calculamos la métrica final por fila
df_diario['engagement_rate'] = df_diario['likes_y_comentarios'] / df_diario['total_posts'] * 100

# POSTS POR DIA
df_posts_diario = posts.groupby('fecha_publicacion').size().reset_index(name='total_posts')




# === DESPLIEGUE DE MÉTRICAS PRINCIPALES ===
col1, col2, col3 = st.columns(3)

with col1:
    total_posts = len(posts)
    st.metric("Total Posts (60 d)", f"{total_posts:}")

with col2:
    total_likes = interacciones[interacciones['tipo_interaccion'] == 'like'].shape[0]
    st.metric("Total Likes (60 d)", f"{total_likes:,}")

with col3:
    st.metric("Nuevos Usuarios (60 d)", f"{len(usuarios):,}")


st.markdown("---")

# === GRÁFICO 1: TIMELINE DE INTERACCIONES ===
# st.subheader("📈 Interacciones en el Tiempo")

st.subheader("👥 Usuarios Activos vs Nuevos")

fig_interactions = go.Figure()
fig_interactions.add_trace(go.Bar(
    x=df_dau['fecha_interaccion'],
    y=df_dau['usuarios_activos'],
    name='Activos',
    marker_color='#3b82f6'
))

fig_interactions.add_trace(go.Bar(
    x=usuarios_nuevos['fecha_registro'], 
    y=usuarios_nuevos['usuarios_nuevos'],
    name='Nuevos',
    marker_color="#ec3c1d"
))

fig_interactions.update_layout(
    hovermode='x unified',
    xaxis_title="Fecha",
    yaxis_title="Cantidad",
    height=400,
    showlegend=True
)
st.plotly_chart(fig_interactions, width='stretch')

col1, col2 = st.columns(2)
with col1:
    st.subheader("🎭 Engagement Rate Diario")
    fig_engagement = px.line(
        df_diario, 
        x="fecha_interaccion",
        y="engagement_rate",
        markers=True,
        line_shape='spline'
    )

    fig_engagement.update_traces(line_color='#8b5cf6', line_width=3)
    fig_engagement.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Engagement Rate (%)",
        height=400
    )

    st.plotly_chart(fig_engagement, width='stretch')

with col2:
    st.subheader("🧾 Posts por día")
    fig_posts = px.line(
        df_posts_diario, 
        x="fecha_publicacion",
        y="total_posts",
        markers=True,
        line_shape='spline'
    )

    fig_posts.update_traces(line_color="#3b2bcc", line_width=3)
    fig_posts.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Cantidad de posts",
        height=400
    )
    
    st.plotly_chart(fig_posts, width='stretch')


# ===== TABLA TOP 10 USUARIOS CON MAS INTERACCIONES =====
st.markdown("---")
st.subheader("🏆 Top 10 usuarios más activos")

tabla_top = top_usuarios[['Score', 'nombre', 'email', 'total_interacciones','total_posts', 'comentarios', 'likes', 'compartir', 'vistas' ]].copy()
tabla_top.insert(0, 'Posición', range(1, len(tabla_top) + 1))

st.dataframe(tabla_top.style.background_gradient(subset=['Score'], cmap='Blues'), width='stretch', hide_index=True)



# === INSIGHTS AUTOMÁTICOS ===
st.markdown("---")
st.subheader("💡 Insights Automáticos")

col1, col2 = st.columns(2)

with col1:
    # df_diario['engagement_rate']
    best_day = df_diario.loc[df_diario['engagement_rate'].idxmax()]
    st.success(f"**🏆 Mejor día**: {best_day['fecha_interaccion'].strftime('%d/%m/%Y')} con {best_day['engagement_rate']:.1f}% engagement")

with col2:
    promedio_posts = df_posts_diario['total_posts'].mean()
    st.info(f"**📝 Promedio**: {promedio_posts:.1f} posts por día")

# with col3:
#     growth_rate = ((df['new_users'].iloc[-7:].sum() / df['new_users'].iloc[-14:-7].sum()) - 1) * 100
#     st.warning(f"**📊 Crecimiento**: {growth_rate:+.1f}% vs semana anterior")

# === FOOTER ===
st.markdown("---")
st.caption("🔄 Dashboard actualizado en tiempo real | 📅 Datos de los últimos 60 días | 🚀 CoWork Social")