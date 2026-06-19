import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Simulador de Combustible Nuclear", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILO Y ENCABEZADO ---
st.title("⚛️ Centro de Evaluación de Combustibles Nucleares")
st.markdown(
    "Bienvenido al sistema de simulación core. Ajusta las tolerancias globales en el panel izquierdo "
    "y personaliza los materiales en las tarjetas de abajo para calcular la eficiencia óptima del reactor."
)
st.write("")

# --- PANEL LATERAL (RESTRICCIONES GLOBALES) ---
st.sidebar.header("⚙️ Restricciones del Sistema")
umbral_fallo = st.sidebar.number_input(
    "Umbral de Fallo Crítico (MWh)", 
    value=410000, 
    step=10000,
    help="La generación que supere este límite provocará un fallo por sobrecarga."
)
limite_residuos = st.sidebar.slider(
    "Límite de Residuos Total (kg)", 
    min_value=100, 
    max_value=2000, 
    value=500, 
    step=50,
    help="Capacidad máxima de almacenamiento de residuos del reactor."
)

# --- CUERPO PRINCIPAL: CONFIGURACIÓN EN TARJETAS ---
st.subheader("⚡ 1. Parámetros de los Materiales")

combustibles = ["Uranio Enriquecido", "MOX", "Torio"]
energia_por_kg = []
residuos_por_kg = []
limite_fisico = []

# Distribución en 3 columnas simétricas con contenedores independientes
cols_input = st.columns(3)

for i, fuel in enumerate(combustibles):
    with cols_input[i]:
        with st.container(border=True):
            st.markdown(f"### **{fuel}**")
            
            # Valores por defecto optimizados
            def_e = 8000 if i == 0 else (11000 if i == 1 else 12000)
            def_r = 12 if i == 0 else (13 if i == 1 else 18)
            def_l = 30 if i == 0 else (40 if i == 1 else 50)
            
            e = st.number_input("Energía (MWh/kg)", value=def_e, key=f"e_{fuel}", step=500)
            r = st.number_input("Residuos (kg/kg)", value=def_r, key=f"r_{fuel}", step=1)
            l = st.slider("Límite Físico (Masa Máx kg)", min_value=5, max_value=150, value=def_l, key=f"l_{fuel}")
            
            energia_por_kg.append(e)
            residuos_por_kg.append(r)
            limite_fisico.append(l)

# --- LÓGICA DE EVALUACIÓN ---
resultados_evaluacion = []

for i in range(3):
    if residuos_por_kg[i] > 0:
        max_por_residuos = limite_residuos // residuos_por_kg[i]
    else:
        max_por_residuos = limite_fisico[i]
        
    kg_usados = min(limite_fisico[i], max_por_residuos)
    energia_generada = kg_usados * energia_por_kg[i]
    residuos_generados = kg_usados * residuos_por_kg[i]

    es_fiable = energia_generada <= umbral_fallo
    estado = "🟢 OPERATIVO" if es_fiable else "🔴 FALLO CRÍTICO"

    resultados_evaluacion.append({
        "Combustible": combustibles[i],
        "Masa Utilizada": f"{kg_usados} / {limite_fisico[i]} kg",
        "Residuos Puros": residuos_generados,       # Para la barra de progreso
        "Energía Pura": energia_generada,           # Para el gráfico y formato numérico
        "Estado": estado,
        "_fiable": es_fiable,
        "_kg_usados": kg_usados,
        "_capacidad": limite_fisico[i]
    })

# --- VISUALIZACIÓN DE RESULTADOS Y GRÁFICOS ---
st.write("")
st.subheader("📊 2. Análisis de Rendimiento y Seguridad")

# Creamos dos columnas: izquierda para datos, derecha para gráfica
col_tabla, col_grafico = st.columns([5, 4], gap="large")

with col_tabla:
    df_resultados = pd.DataFrame(resultados_evaluacion)
    
    # Renderizado estético de la tabla usando column_config
    st.dataframe(
        df_resultados[["Combustible", "Masa Utilizada", "Residuos Puros", "Energía Pura", "Estado"]],
        column_config={
            "Combustible": st.column_config.TextColumn("Material"),
            "Masa Utilizada": st.column_config.TextColumn("Carga (Usado/Máx)"),
            "Residuos Puros": st.column_config.ProgressColumn(
                "Residuos Generados",
                help="Progreso estimado hacia el límite crítico de residuos",
                format="%d kg",
                min_value=0,
                max_value=limite_residuos
            ),
            "Energía Pura": st.column_config.NumberColumn(
                "Energía Neta",
                format="%d MWh"
            ),
            "Estado": st.column_config.TextColumn("Diagnóstico")
        },
        use_container_width=True,
        hide_index=True
    )

with col_grafico:
    # Preparación de datos rápida para el gráfico nativo
    df_chart = pd.DataFrame({
        "Combustible": combustibles,
        "Energía (MWh)": [r["Energía Pura"] for r in resultados_evaluacion]
    }).set_index("Combustible")
    
    st.bar_chart(df_chart, y="Energía (MWh)", color="#4A90E2", use_container_width=True)

# --- PANEL DE CONCLUSIÓN ---
st.write("")
st.subheader("🏆 3. Conclusión Estratégica")

candidatos_fiables = [r for r in resultados_evaluacion if r["_fiable"]]

if candidatos_fiables:
    mejor = max(candidatos_
