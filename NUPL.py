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

# --- DOCUMENTACIÓN DEL SISTEMA (¿PARA QUÉ SERVE Y QUÉ RESUELVE?) ---
with st.expander("📖 Información del Sistema: ¿Para qué sirve y qué problema resuelve?", expanded=False):
    st.markdown("""
    ### 🎯 ¿Para qué sirve este software?
    Este simulador interactivo sirve como una **herramienta de soporte para la toma de decisiones estratégicas y mitigación de riesgos** en entornos de ingeniería nuclear. 
    Permite a ingenieros, operadores y estudiantes modelar de forma 100% segura el comportamiento del núcleo de un reactor antes de cualquier ejecución física. Su utilidad principal es evaluar escenarios hipotéticos (*"What-if"*), analizar la viabilidad de combustibles alternativos y prevenir catástrofes operativas mediante la detección matemática temprana de sobrecargas térmicas o saturación de depósitos radiactivos.

    ### 🧠 El problema que resuelve
    En la gestión de plantas de energía, la selección del combustible óptimo representa un problema de **optimización multiobjetivo bajo restricciones críticas**. Los operadores deben maximizar la producción energética sin comprometer la seguridad. 
    
    Este sistema resuelve el desafío de evaluar simultáneamente tres variables limitantes:
    1. **Capacidad del Reactor (Límite Físico):** La masa máxima en kilogramos que tolera el diseño de cada núcleo.
    2. **Restricción Ambiental (Límite de Residuos):** El tope estricto de subproductos radiactivos que la planta puede procesar por ciclo.
    3. **Seguridad Térmica (Umbral de Fallo):** La energía máxima que el sistema de refrigeración puede contener antes de sufrir un colapso o fallo crítico.
    """)

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
resultados_evaluacion = []

# Distribución en 3 columnas simétricas
cols_input = st.columns(3)

for i, fuel in enumerate(combustibles):
    with cols_input[i]:
        with st.container(border=True):
            st.markdown(f"### **{fuel}**")
            
            # Valores por defecto optimizados
            def_e = 8000 if i == 0 else (11000 if i == 1 else 12000)
            def_r = 12 if i == 0 else (13 if i == 1 else 18)
            def_l = 30 if i == 0 else (40 if i == 1 else 50)
            
            # Inputs interactivos
            e = st.number_input("Energía (MWh/kg)", value=def_e, key=f"e_{fuel}", step=500)
            r = st.number_input("Residuos (kg/kg)", value=def_r, key=f"r_{fuel}", step=1)
            l = st.slider("Límite Físico (Masa Máx kg)", min_value=5, max_value=150, value=def_l, key=f"l_{fuel}")
            
            # --- LÓGICA DE EVALUACIÓN INMEDIATA ---
            if r > 0:
                max_por_residuos = limite_residuos // r
            else:
                max_por_residuos = l
                
            kg_usados = min(l, max_por_residuos)
            energia_generada = kg_usados * e
            residuos_generados = kg_usados * r
            es_fiable = energia_generada <= umbral_fallo
            
            # --- FEEDBACK ESTÉTICO INSTANTÁNEO ---
            if not es_fiable:
                exceso = energia_generada - umbral_fallo
                st.error(f"💥 **FALLO CRÍTICO: SOBRECARGA**\n\nGenerando **{energia_generada:,} MWh** (Excede el umbral por {exceso:,} MWh). Reduzca la masa o la energía por kg.")
                estado = "💥 FALLO CRÍTICO"
            else:
                st.success(f"🟢 **SISTEMA ESTABLE**\n\nGeneración segura a {energia_generada:,} MWh.")
                estado = "🟢 OPERATIVO"

            # Guardamos los datos para los gráficos y tablas posteriores
            resultados_evaluacion.append({
                "Combustible": fuel,
                "Masa Utilizada": f"{kg_usados} / {l} kg",
                "Residuos Puros": residuos_generados,
                "Energía Pura": energia_generada,
                "Estado": estado,
                "_fiable": es_fiable,
                "_kg_usados": kg_usados,
                "_capacidad": l
            })

# --- VISUALIZACIÓN DE RESULTADOS Y GRÁFICOS ---
st.write("")
st.subheader("📊 2. Análisis de Rendimiento y Seguridad")

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
    mejor = max(candidatos_fiables, key=lambda x: x["Energía Pura"])
    
    with st.container(border=True):
        st.success(f"### El combustible más eficiente y seguro es el **{mejor['Combustible']}**")
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Energía Desplegada", f"{mejor['Energía Pura']:,} MWh")
        m_col2.metric("Masa Requerida", f"{mejor['_kg_usados']} kg", f"Límite: {mejor['_capacidad']} kg", delta_color="inverse")
        m_col3.metric("Residuos Generados", f"{mejor['Residuos Puros']} kg", f"Máx: {limite_residuos} kg", delta_color="inverse")
else:
    st.error("🚨 **ALERTA CRÍTICA DEL REACTOR:** Ninguno de los combustibles disponibles es seguro bajo la configuración actual. Todos los materiales se encuentran en estado de colapso o superan las restricciones.")
