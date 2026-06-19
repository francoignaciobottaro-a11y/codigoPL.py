import streamlit as st
import pandas as pd

# Configuración básica de la página
st.set_page_config(page_title="Simulador de Combustible", layout="wide")

st.title("⚛️ Evaluador de Combustibles Nucleares")
st.markdown("Ajusta los parámetros en el panel lateral para simular diferentes escenarios de rendimiento y seguridad.")

# --- PANEL LATERAL (INPUTS DEL USUARIO) ---
st.sidebar.header("⚙️ Parámetros Globales")
umbral_fallo = st.sidebar.number_input("Umbral de Fallo Crítico (MWh)", value=410000, step=10000)
limite_residuos = st.sidebar.number_input("Límite de Residuos Total (kg)", value=500, step=50)

st.sidebar.header("🧪 Parámetros por Material")
combustibles = ["Uranio Enriquecido", "MOX", "Torio"]
energia_por_kg = []
residuos_por_kg = []
limite_fisico = []

# Crear controles dinámicos para cada combustible
for i, fuel in enumerate(combustibles):
    with st.sidebar.expander(f"Ajustes de {fuel}", expanded=(i==0)):
        # Valores por defecto basados en tu código original
        def_e = 8000 if i == 0 else (11000 if i == 1 else 12000)
        def_r = 12 if i == 0 else (13 if i == 1 else 18)
        def_l = 30 if i == 0 else (40 if i == 1 else 50)
        
        e = st.number_input("Energía (MWh/kg)", value=def_e, key=f"e_{fuel}")
        r = st.number_input("Residuos (kg/kg)", value=def_r, key=f"r_{fuel}")
        l = st.number_input("Límite Físico (kg)", value=def_l, key=f"l_{fuel}")
        
        energia_por_kg.append(e)
        residuos_por_kg.append(r)
        limite_fisico.append(l)

# --- LÓGICA DE EVALUACIÓN ---
resultados_evaluacion = []

for i in range(3):
    # Evitar división por cero si el usuario pone 0 residuos
    if residuos_por_kg[i] > 0:
        max_por_residuos = limite_residuos // residuos_por_kg[i]
    else:
        max_por_residuos = limite_fisico[i]
        
    kg_usados = min(limite_fisico[i], max_por_residuos)

    energia_generada = kg_usados * energia_por_kg[i]
    residuos_generados = kg_usados * residuos_por_kg[i]

    # Verificación de fallo crítico
    es_fiable = energia_generada <= umbral_fallo
    estado = "🟢 OPERATIVO" if es_fiable else "🔴 FALLO CRÍTICO"

    # Guardamos los datos para la tabla y para la conclusión
    resultados_evaluacion.append({
        "Combustible": combustibles[i],
        "KG Usados": f"{kg_usados} / {limite_fisico[i]}",
        "Residuos": f"{residuos_generados} / {limite_residuos} kg",
        "Energía (MWh)": f"{energia_generada:,.0f}",
        "Estado": estado,
        # Variables ocultas para procesar la lógica final
        "_energia": energia_generada,
        "_kg_usados": kg_usados,
        "_capacidad": limite_fisico[i],
        "_fiable": es_fiable
    })

# --- VISUALIZACIÓN DE RESULTADOS ---
st.subheader("📊 Resultados de la Simulación")

# Usamos Pandas para mostrar una tabla limpia (excluyendo las columnas de lógica)
df_resultados = pd.DataFrame(resultados_evaluacion)
df_mostrar = df_resultados[["Combustible", "KG Usados", "Residuos", "Energía (MWh)", "Estado"]]
st.dataframe(df_mostrar, use_container_width=True)

# --- CONCLUSIÓN ---
st.divider()
st.subheader("🏆 Conclusión del Sistema")

candidatos_fiables = [r for r in resultados_evaluacion if r["_fiable"]]

if candidatos_fiables:
    mejor = max(candidatos_fiables, key=lambda x: x["_energia"])
    st.success(f"El combustible más óptimo y seguro es: **{mejor['Combustible']}**")
    st.write(f"- **Uso de material:** Utilizando {mejor['_kg_usados']} kg de una capacidad máxima de {mejor['_capacidad']} kg.")
    st.write(f"- **Energía Final:** {mejor['_energia']:,.0f} MWh.")
else:
    st.error("ALERTA: Ningún combustible es seguro bajo los parámetros actuales.")
