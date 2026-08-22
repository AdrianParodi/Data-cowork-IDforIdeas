import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
from sklearn.linear_model import LinearRegression

# -------------------------------------------------------------------
# 1. Configuración de la página
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard de Retención y Proyección de Usuarios",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Análisis de Retención y Proyección de Usuarios")
st.markdown(
    "Monitoreo de crecimiento, tasas de retención y proyecciones basadas en Regresión Lineal."
)


# -------------------------------------------------------------------
# 2. Carga y Procesamiento de Datos
# -------------------------------------------------------------------
@st.cache_data
def cargar_y_procesar_datos():

    file_id = "1Km6ldVmWVEXV-ne1vj-xJB-TDAAylWrZ"

    url_datos = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{file_id}/export?format=csv&gid=1740686942"
    )

    df = pd.read_csv(url_datos)

    columnas_numericas = [
    "mes",
    "nuevos_usuarios",
    "usuarios_totales",
    "usuarios_activos",
    "usuarios_retenidos",
    "retention_rate",
    "growth_rate_nuevos",
    "usuarios_inactivos",
    ]

    df[columnas_numericas] = df[columnas_numericas].apply(
        pd.to_numeric,
        errors="coerce"
    )

    return df


df = cargar_y_procesar_datos()

# -------------------------------------------------------------------
# 3. Barra Lateral: Parámetros de Proyección
# -------------------------------------------------------------------
st.sidebar.header("⚙️ Configuración del Modelo")

# Permitir al usuario elegir la cantidad de meses a proyectar
meses_a_proyectar = st.sidebar.slider(
    "Meses a proyectar hacia el futuro:",
    min_value=1,
    max_value=12,
    value=3,
    step=1,
)

# -------------------------------------------------------------------
# 4. Entrenamiento del Modelo de Regresión Lineal
# -------------------------------------------------------------------
X = df[["mes"]]
y = df["nuevos_usuarios"]

model = LinearRegression()
model.fit(X, y)

# Generar rango extendido de meses (histórico + proyección seleccionada)
ultimo_mes = int(df["mes"].max())
meses_futuros = range(1, ultimo_mes + meses_a_proyectar + 1)
df_tendencia = pd.DataFrame({"mes": meses_futuros})
df_tendencia["proyeccion"] = model.predict(df_tendencia[["mes"]])

# -------------------------------------------------------------------
# 5. KPIs Principales
# -------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

total_activos = int(df["usuarios_activos"].iloc[-1])
retencion_actual = df["retention_rate"].iloc[-1]
crecimiento_actual = df["growth_rate_nuevos"].iloc[-1]
proxima_proyeccion = int(
    df_tendencia[df_tendencia["mes"] == ultimo_mes + 1]["proyeccion"].values[0]
)

col1.metric("Usuarios Activos (Último mes)", f"{total_activos:,}")
col2.metric("Tasa de Retención", f"{retencion_actual:.2f}%")
col3.metric("Crecimiento Nuevos Usuarios", f"{crecimiento_actual:.2f}%")
col4.metric(
    f"Proyección Mes {ultimo_mes + 1}", f"{max(0, proxima_proyeccion):,}"
)

st.markdown("---")

# -------------------------------------------------------------------
# 6. Pestañas de Visualización
# -------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "🔮 Proyección de Crecimiento",
    "👥 Activos vs Inactivos",
    "📊 Tasas de Crecimiento y Retención",
])

# ===================================================================
# PESTAÑA 1: PROYECCIÓN Y TENDENCIA (Plotly Interactivo)
# ===================================================================
with tab1:
    st.subheader(
        f"Proyección de Nuevos Usuarios (Regresión Lineal a {meses_a_proyectar} meses)"
    )

    fig_proy = go.Figure()

    # Serie Histórica
    fig_proy.add_trace(
        go.Scatter(
            x=df["mes"],
            y=df["nuevos_usuarios"],
            name="Datos Históricos",
            mode="lines+markers",
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=8),
            hovertemplate="Mes %{x}: %{y:,} usuarios<extra></extra>",
        )
    )

    # Línea de Tendencia
    fig_proy.add_trace(
        go.Scatter(
            x=df_tendencia["mes"],
            y=df_tendencia["proyeccion"],
            name="Tendencia Regresión Lineal",
            mode="lines",
            line=dict(color="#e74c3c", width=2, dash="dash"),
            hovertemplate="Mes %{x} (Proyección): %{y:.0f} usuarios<extra></extra>",
        )
    )

    fig_proy.update_layout(
        xaxis=dict(
            title=dict(text="Mes"),
            dtick=1,
            gridcolor="#E2E8F0",
        ),
        yaxis=dict(
            title=dict(text="Cantidad de Nuevos Usuarios"),
            gridcolor="#E2E8F0",
        ),
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=30, b=20),
    )

    st.plotly_chart(fig_proy, use_container_width=True)

    # Tabla de Proyección Futura
    with st.expander("👀 Ver valores numéricos proyectados"):
        df_mostrar = df_tendencia[
            df_tendencia["mes"] > ultimo_mes
        ].reset_index(drop=True)
        df_mostrar.columns = ["Mes Proyectado", "Nuevos Usuarios Estimados"]
        df_mostrar["Nuevos Usuarios Estimados"] = df_mostrar[
            "Nuevos Usuarios Estimados"
        ].astype(int)
        st.dataframe(df_mostrar, use_container_width=True)

# ===================================================================
# PESTAÑA 2: USUARIOS ACTIVOS VS INACTIVOS (Barras Apiladas)
# ===================================================================
with tab2:
    st.subheader("Distribución de Usuarios Activos e Inactivos por Mes")

    # Preparar DataFrame para st.bar_chart con índice en 'mes'
    df_act_inact = df.set_index("mes")[["usuarios_activos", "usuarios_inactivos"]]
    df_act_inact.columns = ["Activos", "Inactivos"]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df_act_inact.index,
            y=df_act_inact["Activos"],
            name="Activos",
        )
    )

    fig.add_trace(
        go.Bar(
            x=df_act_inact.index,
            y=df_act_inact["Inactivos"],
            name="Inactivos",
        )
    )

    fig.update_layout(
        barmode="stack",
        xaxis=dict(
            title="Mes",
            dtick=1,
            tickangle=0,
        ),
        yaxis=dict(
            title="Usuarios",
        ),
        height=450,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

# ===================================================================
# PESTAÑA 3: TASAS MENSUALES (Subplots Alineados)
# ===================================================================

with tab3:
    st.subheader("Evolución de Tasas Porcentuales")

    fig_tasas = go.Figure()

    # Tasa de crecimiento
    fig_tasas.add_trace(
        go.Scatter(
            x=df["mes"],
            y=df["growth_rate_nuevos"],
            name="Crecimiento",
            mode="lines+markers",
            line=dict(dash="dash"),
            marker=dict(size=7),
            hovertemplate="Mes %{x}: %{y:.2f}%<extra></extra>",
        )
    )

    # Tasa de retención
    fig_tasas.add_trace(
        go.Scatter(
            x=df["mes"],
            y=df["retention_rate"],
            name="Retención",
            mode="lines+markers",
            line=dict(dash="dash"),
            marker=dict(size=7),
            hovertemplate="Mes %{x}: %{y:.2f}%<extra></extra>",
        )
    )

    fig_tasas.update_layout(
        xaxis=dict(
            title="Mes",
            dtick=1,
        ),
        yaxis=dict(
            title="Tasa (%)",
        ),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            title="Métrica",
        ),
        margin=dict(l=20, r=20, t=30, b=20),
    )

    st.plotly_chart(
        fig_tasas,
        use_container_width=True
    )

# with tab3:
#     st.subheader("Evolución de Tasas Porcentuales")

#     sns.set_theme(style="whitegrid")
#     fig_tasas, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 4))

#     # Subplot 1: Crecimiento
#     axes[0].plot(
#         df["mes"],
#         df["growth_rate_nuevos"],
#         "--g",
#         marker="o",
#         linewidth=2,
#     )
#     axes[0].set_title("Tasa de Crecimiento Mensual (%)", fontsize=11, pad=10)
#     axes[0].set_xlabel("Mes", fontsize=9)
#     axes[0].set_ylabel("Crecimiento (%)", fontsize=9)
#     axes[0].set_xticks(df["mes"])

#     # Subplot 2: Retención
#     axes[1].plot(
#         df["mes"],
#         df["retention_rate"],
#         "--b",
#         marker="o",
#         linewidth=2,
#     )
#     axes[1].set_title("Tasa de Retención (%)", fontsize=11, pad=10)
#     axes[1].set_xlabel("Mes", fontsize=9)
#     axes[1].set_ylabel("Retención (%)", fontsize=9)
#     axes[1].set_xticks(df["mes"])

#     plt.tight_layout()
#     st.pyplot(fig_tasas)

# -------------------------------------------------------------------
# 7. Footer
# -------------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6c757d; font-size: 0.85em;">
        📈 <b>Dashboard de Retención de Usuarios</b> | Modelo Scikit-Learn Integrado
    </div>
    """,
    unsafe_allow_html=True,
)

print(df)