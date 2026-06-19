import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Simulador de Combustible Nuclear", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INICIALIZACIÓN DEL ESTADO DEL REACTOR ---
if "reactor_scram" not in st.session_state:
    st.session_state.reactor_scram = False
if "scram_requested" not in st.session_state:
    st.session_state.scram_requested = False

# --- ESTILO Y ENCABEZADO ---
st.title("⚛️ Centro de Evaluación de Combustibles Nucleares")
st.markdown(
    "Bienvenido al sistema de simulación core. Ajusta las tolerancias globales en el panel izquierdo "
    "y personaliza los materiales en las tarjetas de abajo para calcular la eficiencia óptima del reactor."
)
st.write("")

# --- DOCUMENTACIÓN DEL SISTEMA ---
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

# --- SECCIÓN DE CONTROL DE EMERGENCIA (SCRAM Y CONFIRMACIÓN) ---
st.error("🚨 **SISTEMA DE CONTENCIÓN DE EMERGENCIA**")

# Caso 1: El reactor ya fue apagado
if st.session_state.reactor_scram:
    st.markdown("⚠️ **EL REACTOR SE ENCUENTRA APAGADO FORZOSAMENTE.** Las barras de control de neutrones se insertaron por completo.")
    if st.button("🔄 REINICIAR Y REENFOCAR NÚCLEO", use_container_width=True):
        st.session_state.reactor_scram = False
        st.rerun()

# Caso 2: El usuario inició el protocolo pero debe confirmar leyendo los peligros primero
elif st.session_state.scram_requested:
    with st.container(border=True):
        st.markdown("### ☢️⚠️ Peligros Críticos de Detener el Reactor (SCRAM)")
        st.markdown("""
        Apagar un reactor nuclear de forma abrupta mediante un protocolo SCRAM introduce **riesgos térmicos y químicos extremos** que el equipo de ingeniería debe gestionar bajo estricto control:
        
        * **1. Calor de Decaimiento (Decay Heat):** Aunque la fisión en cadena se detenga al 0%, los materiales radiactivos acumulados dentro del combustible siguen descomponiéndose y **generando un calor masivo residual**. Si las bombas de refrigeración de emergencia fallan tras el apagado, el núcleo se derretirá por completo (el escenario exacto que causó el desastre de **Fukushima**).
        * **2. Envenenamiento por Xenón (Poison Pit):** Al detenerse el flujo de neutrones, el reactor comienza a acumular cantidades críticas de **Xenón-135**, un isótopo que devora neutrones. Esto 'envenena' el reactor de tal forma que vuelve **matemáticamente imposible reiniciar el sistema** durante las siguientes 48 a 72 horas, dejando a la red eléctrica sin suministro.
        * **3. Choque y Estrés Térmico Estructural:** Pasar de miles de grados Celsius a temperaturas frías de contención en pocos segundos contrae violentamente el acero de la vasija de presión. Este choque térmico severo puede inducir **microfisuras y fracturas estructurales catastróficas** en las tuberías primarias del refrigerante.
        """)
        
        st.warning("🖥️ **PANTALLA DE CONTROL:** ¿Está completamente seguro de proceder con la parada forzada del núcleo?")
        
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("🛑 SÍ, ENCLAVAR BARRAS (PROCEDER)", type="primary", use_container_width=True):
                st.session_state.reactor_scram = True
                st.session_state.scram_requested = False
                st.rerun()
        with col_no:
            if st.button("🟢 NO, ABORTAR Y MANTENER REACCIÓN", use_container_width=True):
                st.session_state.scram_requested = False
                st.rerun()

# Caso 3: Estado operativo normal (reactor encendido)
else:
    st.markdown("🟢 **EL REACTOR OPERA NORMALMENTE.** El botón SCRAM cortará la fisión inmediatamente en caso de anomalía irreversible.")
    if st.button("🔴 INICIAR PROTOCOLO DE PARADA DE EMERGENCIA (SCRAM)", use_container_width=True, type="primary"):
        st.session_state.scram_requested = True
        st.rerun()


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
st.write("")
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
            e = st.number_input("Energía (MWh/kg)", value=def_e, key=f"e_{fuel}", step=500, disabled=st.session_state.reactor_scram)
            r = st.number_input("Residuos (kg/kg)", value=def_r, key=f"r_{fuel}", step=1, disabled=st.session_state.reactor_scram)
            l = st.slider("Límite Físico (Masa Máx kg)", min_value=5, max_value=150, value=def_l, key=f"l_{fuel}", disabled=st.session_state.reactor_scram)
            
            # --- LÓGICA DE EVALUACIÓN INMEDIATA ---
            if st.session_state.reactor_scram:
                kg_usados = 0
                energia_generada = 0
                residuos_generados = 0
                es_fiable = True
                estado = "🛑 APAGADO (SCRAM)"
                st.info("🛑 Combustible inerte por parada técnica.")
            else:
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
                    st.error(f"☢️ **FALLO CRÍTICO: PELIGRO NUCLEAR**\n\nGenerando **{energia_generada:,} MWh** (Excede el umbral por {exceso:,} MWh). Reduzca la masa o la energía por kg.")
                    estado = "☢️ FALLO CRÍTICO"
                else:
                    st.success(f"🟢 **SISTEMA ESTABLE**\n\nGeneración segura a {energia_generada:,} MWh.")
                    estado = "🟢 OPERATIVO"

            # Guardamos los datos para los gráficos y tablas posteriores
            resultados_evaluacion.append({
                "Combustible": fuel,
                "Masa Utilizada": f"{kg_usados} / {l} kg" if not st.session_state.reactor_scram else "0 kg",
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
    df_chart = pd.DataFrame({
        "Combustible": combustibles,
        "Energía (MWh)": [r["Energía Pura"] for r in resultados_evaluacion]
    }).set_index("Combustible")
    
    st.bar_chart(df_chart, y="Energía (MWh)", color="#4A90E2", use_container_width=True)

# --- PANEL DE CONCLUSIÓN ---
st.write("")
st.subheader("🏆 3. Conclusión Estratégica")

if st.session_state.reactor_scram:
    st.info("🛑 **MONITOR INACTIVO:** El reactor está completamente apagado. No se pueden calcular eficiencias hasta reestablecer la reacción nuclear.")
else:
    candidatos_fiables = [r for r in resultados_evaluacion if r["_fiable"]]
    candidatos_fallo = [r for r in resultados_evaluacion if not r["_fiable"]]

    if candidatos_fiables:
        mejor = max(candidatos_fiables, key=lambda x: x["Energía Pura"])
        
        with st.container(border=True):
            st.success(f"### El combustible más eficiente y seguro es el **{mejor['Combustible']}**")
            
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Energía Desplegada", f"{mejor['Energía Pura']:,} MWh")
            m_col2.metric("Masa Requerida", f"{mejor['_kg_usados']} kg", f"Límite: {mejor['_capacidad']} kg", delta_color="inverse")
            m_col3.metric("Residuos Generados", f"{mejor['Residuos Puros']} kg", f"Máx: {limite_residuos} kg", delta_color="inverse")
    else:
        st.error("☢️🚨 **ALERTA CRÍTICA DEL REACTOR:** Ninguno de los combustibles disponibles es seguro bajo la configuración actual. Todos los materiales se encuentran en estado de peligro nuclear crítico.")

    # --- SECCIÓN: REPORTE DETALLADO DE FALLOS ---
    if candidatos_fallo:
        st.write("")
        st.markdown("### ⚠️ Reporte de Inestabilidad y Riesgo Nuclear")
        
        for material in candidatos_fallo:
            exceso_energia = material["Energía Pura"] - umbral_fallo
            st.warning(
                f"☢️ **{material['Combustible']}** ha provocado un **Fallo Crítico por Sobrecarga Térmica**.\n\n"
                f"* **Causa técnica:** La energía proyectada de **{material['Energía Pura']:,} MWh** excede el umbral de seguridad configurado (**{umbral_fallo:,} MWh**).\n"
                f"* **Gravedad del exceso:** Requiere una disipación de emergencia de **+{exceso_energia:,} MWh** para estabilizar el núcleo y evitar una fusión nuclear masiva."
            )
