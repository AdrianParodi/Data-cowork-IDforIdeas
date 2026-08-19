import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
import plotly.graph_objects as go

# -------------------------------------------------------------------
# 1. Configuración de la página
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard de Engagement de Posts",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Análisis de Performance y Engagement en Redes Sociales")
st.markdown(
    "Explora el rendimiento de las publicaciones según categoría, longitud y horarios."
)


# -------------------------------------------------------------------
# 2. Carga y preparación de datos
# -------------------------------------------------------------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("DA-02-content-analysis/posts_ampliado.csv")
    df["fecha_publicacion"] = pd.to_datetime(df["fecha_publicacion"])

    post_mes_categorias = pd.read_csv("DA-02-content-analysis/posts_por_mes_y_categoria.csv")
    engage_por_hora = pd.read_csv("DA-02-content-analysis/engage_por_hora.csv")


    return df, post_mes_categorias, engage_por_hora


df_posts, df_posts_mes, df_engage = cargar_datos()

# -------------------------------------------------------------------
# 3. Barra Lateral (Filtros)
# -------------------------------------------------------------------
st.sidebar.header("🔍 Filtros de Análisis")

# Filtro por Categorías
categorias_disponibles = list(df_posts["categoria"].unique())
categorias_sel = st.sidebar.multiselect(
    "Categoría:",
    options=categorias_disponibles,
    default=categorias_disponibles,
)

# Filtro por Rango Horario
hora_min, hora_max = int(df_posts["hora"].min()), int(df_posts["hora"].max())
rango_horas = st.sidebar.slider(
    "Rango Horario (Horas del día):",
    min_value=hora_min,
    max_value=hora_max,
    value=(hora_min, hora_max),
)

# Aplicar filtros
df_filtrado = df_posts[
    (df_posts["categoria"].isin(categorias_sel))
    & (df_posts["hora"].between(rango_horas[0], rango_horas[1]))
]

# -------------------------------------------------------------------
# 4. Métricas Principales (KPIs)
# -------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de Posts", f"{len(df_filtrado):,}")
col2.metric("Impresiones Promedio", f"{int(df_filtrado['impresiones'].mean()):,}")
col3.metric(
    "Engagement Ponderado Mediana",
    f"{df_filtrado['engage_pond'].median():.2f}%",
)
col4.metric(
    "Engagement Ponderado Promedio",
    f"{df_filtrado['engage_pond'].mean():.2f}%",
)

st.markdown("---")

# -------------------------------------------------------------------
# 5. Visualizaciones organizadas en Pestañas (Tabs)
# -------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Distribución por Categorias", "⚡Engagment por categoria", "⏰ Comportamiento por Hora", "📏 Longitud del Post", "🗂️ Datos Raw"]
)

# --- PESTAÑA 1: DISTRIBUCION MENSUAL DE POSTS POR CATEGORIA ---
with tab1:
    st.subheader("Distribución de los posts por categoría")

    # Requiere que df_posts_mes tenga los meses como índice y las categorías como columnas
    df_chart = df_posts_mes.set_index("mes")

    paleta_moderna = ['#6C5CE7', '#00CEC9', '#FF7675']
    st.bar_chart(df_chart, stack=True, height=400, color=paleta_moderna)


# --- PESTAÑA 2: ENGAGEMENT POR CATEGORIA ---
with tab2:
    st.subheader("📐 Fórmulas y Métricas por Categoría")

    # 1. Fórmulas LaTeX
    st.latex(
        r"\text{Tasa de engagement (clásico)} = \frac{\text{likes} +"
        r" \text{shares} + \text{comentarios}}{\text{vistas}} \times 100"
    )

    st.latex(
        r"\text{Tasa de engagement ponderado (\%)} = \frac{\text{likes} +"
        r" (\text{comentarios} \times 4) + (\text{shares} \times"
        r" 8)}{\text{vistas}} \times 100"
    )

    st.markdown("---")

    # 2. Configuración de gráficos
    st.subheader("📊 Comparación de Engagement por Categoría")

    paleta_azul = ["#2B4C7E", "#4A90E2", "#70A1D7"]
    paleta_naranja = ["#D35400", "#E67E22", "#F39C12"]

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8, 6))

    # --- PRIMER GRÁFICO ---
    sns.barplot(
        data=df_filtrado,
        x="categoria",
        y="engagement",
        estimator="mean",
        errorbar=None,
        palette=paleta_azul,
        hue="categoria",
        legend=False,
        ax=axes[0],
        width=0.5
    )
    axes[0].set_title("Engagement Promedio por Categoría", fontsize=12, pad=10)
    axes[0].set_xlabel("Categoría", fontsize=10)
    axes[0].set_ylabel("Engagement Promedio", fontsize=10)

    # Margen vertical extra (15%) para dar aire a las etiquetas
    axes[0].margins(y=0.15)

    for container in axes[0].containers:
        axes[0].bar_label(container, fmt="%.1f", padding=4)

    # --- SEGUNDO GRÁFICO ---
    sns.barplot(
        data=df_filtrado,
        x="categoria",
        y="engage_pond",
        estimator="mean",
        errorbar=None,
        palette=paleta_naranja,
        hue="categoria",
        legend=False,
        ax=axes[1],
        width=0.5
    )
    axes[1].set_title(
        "Engagement Ponderado Promedio por Categoría", fontsize=12, pad=10
    )
    axes[1].set_xlabel("Categoría", fontsize=10)
    axes[1].set_ylabel("Engagement Ponderado (%)", fontsize=10)

    # Margen vertical extra (15%)
    axes[1].margins(y=0.15)

    for container in axes[1].containers:
        axes[1].bar_label(container, fmt="%.2f%%", padding=4)

    plt.tight_layout()
    st.pyplot(fig)


# --- PESTAÑA 3: EVOLUCIÓN HORARIA (Doble Eje Y) ---
# --- PESTAÑA 3: EVOLUCIÓN HORARIA (Doble Eje Y Interactivo) ---
with tab3:
    st.subheader("Evolución del Engagement por Hora de Publicación")

    df_hora = (
        df_filtrado.groupby("hora")[["engagement", "engage_pond"]]
        .mean()
        .reset_index()
    )

    fig = go.Figure()

    # 1. Eje Izquierdo: Engagement Estándar
    fig.add_trace(
        go.Scatter(
            x=df_hora["hora"],
            y=df_hora["engagement"],
            name="Engagement Estándar",
            mode="lines+markers",
            line=dict(color="#1f77b4", width=2.5),
            marker=dict(size=8, symbol="circle"),
            hovertemplate="Hora: %{x}:00 hs<br>Engagement: %{y:.2f}<extra></extra>",
        )
    )

    # 2. Eje Derecho: Engagement Ponderado (%)
    fig.add_trace(
        go.Scatter(
            x=df_hora["hora"],
            y=df_hora["engage_pond"],
            name="Engagement Ponderado (%)",
            mode="lines+markers",
            line=dict(color="#ff7f0e", width=2.5, dash="dash"),
            marker=dict(size=8, symbol="square"),
            yaxis="y2",
            hovertemplate="Hora: %{x}:00 hs<br>Eng. Ponderado: %{y:.2f}%<extra></extra>",
        )
    )

    # 3. Configurar Layout (Sintaxis actualizada de Plotly v5+)
    fig.update_layout(
        xaxis=dict(
            title=dict(text="Hora del Día (0-23)"),
            tickmode="linear",
            tick0=0,
            dtick=1,
            gridcolor="#E2E8F0",
        ),
        yaxis=dict(
            title=dict(text="Engagement Estándar", font=dict(color="#1f77b4")),
            tickfont=dict(color="#1f77b4"),
            gridcolor="#E2E8F0",
        ),
        yaxis2=dict(
            title=dict(
                text="Engagement Ponderado (%)", font=dict(color="#ff7f0e")
            ),
            tickfont=dict(color="#ff7f0e"),
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)

# --- PESTAÑA 4: LONGITUD VS ENGAGEMENT ---
with tab4:
    st.subheader("Relación entre Longitud del Post y Engagement")

    # Configuración de estilo
    sns.set_theme(style="whitegrid")

    # 1. Crear figura con 2 filas y 1 columna (apilados verticalmente)
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 10))

    # -------------------------------------------------------------------
    # SUBPLOT 1 (Arriba): Scatter Plot por Categoría
    # -------------------------------------------------------------------
    sns.scatterplot(
        data=df_filtrado,
        x="longitud",
        y="engage_pond",
        hue="categoria",
        palette="Set2",
        alpha=0.7,
        s=60,
        ax=axes[0],
    )

    sns.regplot(
        data=df_filtrado,
        x="longitud",
        y="engage_pond",
        scatter=False,
        ax=axes[0],
        color="black",
        line_kws={
            "linestyle": "--",
            "linewidth": 2,
            "label": "Tendencia general",
        },
    )

    axes[0].set_title(
        "Relación entre Longitud del Post y Engagement Ponderado", fontsize=12
    )
    axes[0].set_xlabel("Longitud del Post (Caracteres)", fontsize=10)
    axes[0].set_ylabel("Engagement Ponderado (%)", fontsize=10)
    axes[0].legend(
        title="Categoría", bbox_to_anchor=(1.02, 1), loc="upper left"
    )

    # -------------------------------------------------------------------
    # SUBPLOT 2 (Abajo): Boxplot por Rangos de Longitud
    # -------------------------------------------------------------------
    # Crear la columna de rangos de forma segura sobre el dataframe
    df_filtrado["rango_longitud"] = pd.cut(
        df_filtrado["longitud"],
        bins=4,
        labels=["Muy Corto", "Corto", "Medio", "Largo"],
    )

    sns.boxplot(
        data=df_filtrado,
        x="rango_longitud",
        y="engage_pond",
        hue="rango_longitud",
        legend=False,
        palette="Pastel1",
        ax=axes[1],
    )

    axes[1].set_title(
        "Distribución del Engagement según el Rango de Longitud", fontsize=12
    )
    axes[1].set_xlabel("Rango de Longitud", fontsize=10)
    axes[1].set_ylabel("Engagement Ponderado (%)", fontsize=10)

    # Ajuste de diseño y renderizado en Streamlit
    plt.tight_layout()
    st.pyplot(fig)

    # Agregar resumen numérico interactivo
    st.markdown("#### 📊 Resumen Estadístico por Rango")
    resumen_rangos = (
        df_filtrado.groupby("rango_longitud")["engage_pond"]
        .agg(
            Mediana="median",
            Promedio="mean",
            Mínimo="min",
            Máximo="max",
            Posts="count",
        )
        .reset_index()
    )

    st.dataframe(resumen_rangos, use_container_width=True)

# --- PESTAÑA 5: TABLA DE DATOS ---
with tab5:
    st.subheader("Explorador de Datos")
    st.dataframe(df_filtrado, use_container_width=True)


# -------------------------------------------------------------------
# 6. Footer / Pie de página
# -------------------------------------------------------------------
st.markdown("---")

footer_html = """
<div style="text-align: center; color: #6c757d; padding: 10px 0; font-size: 0.9em;">
    <p style="margin-bottom: 5px;">
        Desarrollado usando <b>Streamlit</b> y <b>Plotly</b>
    </p>
    <p style="margin: 0;">
        📊 <b>Dashboard de Engagement</b> | Datos actualizados a Agosto de 2026 | 
        <a href="https://www.linkedin.com/in/adrian-parodi/" target="_blank" style="color: #4A90E2; text-decoration: none;">LinkedIn</a> • 
        <a href="https://github.com/AdrianParodi" target="_blank" style="color: #4A90E2; text-decoration: none;">GitHub</a>
    </p>
</div>
"""

st.markdown(footer_html, unsafe_allow_html=True)