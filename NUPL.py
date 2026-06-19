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
    st.error("🚨 **ALERTA CRÍTICA DEL REACTOR:** Ninguno de los combustibles disponibles es seguro bajo la configuración actual. Todos los materiales se encuentran en estado de colapso o superan las restricciones.")
