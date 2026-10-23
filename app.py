import streamlit as st
import pandas as pd
import datetime

# Configuración de la interfaz
st.set_page_config(page_title="Bitácora Agrícola Fitosanitaria", page_icon="🧅", layout="wide")

st.title("🚜 Cuaderno de Bitácora y Control Fitosanitario")
st.write("Registra tus cultivos, monitorea plagas y lleva el control nutricional de tus lotes.")

# Base de datos simulada en la memoria del navegador
if 'bitacora' not in st.session_state:
    st.session_state.bitacora = [
        {
            "Fecha Registro": "2026-10-23",
            "Nombre de Cultivo": "Cebolla",
            "Lote / Parcela": "Lote Norte A1",
            "Plagas Comunes / Observadas": "Trips",
            "Control Fitosanitario (Dosis)": "Delta Plus, Entrus, Etc.",
            "Control Nutricional (Etapa)": "Fósforo, aminoácidos, calcio boro potasio",
            "Fertilizantes (Foliares/Granulados)": "Urea, Sulfato, Potasio, Nitrato de Calcio ETC.",
            "Estado del Cultivo": "En Desarrollo",
            "Responsable": "Juan Pérez"
        }
    ]

# Formulario para añadir nuevos registros con campos expandidos
st.sidebar.header("📝 Añadir Nuevo Registro")
with st.sidebar.form("formulario_campo"):
    fecha = st.date_input("Fecha de Registro/Inspección", datetime.date.today())
    cultivo = st.text_input("Nombre de Cultivo (ej. Cebolla)", placeholder="Cebolla")
    lote = st.text_input("Lote / Parcela / Sector", placeholder="Ej. Sector Bajo 2")
    plagas = st.text_input("Plagas Comunes / Observadas", placeholder="Ej. Trips, Mildiu")
    fitosanitario = st.text_area("Plan o Control Fitosanitario (Recomendaciones de Dosis)", placeholder="Ej. Delta Plus, Entrus, Etc.")
    nutricional = st.text_area("Plan o Control Nutricional (Recomendaciones por Etapa)", placeholder="Ej. Fósforo, aminoácidos, calcio boro potasio")
    fertilizantes = st.text_area("Fertilizantes (Foliares o Granulados)", placeholder="Ej. Urea, Sulfato, Potasio, Nitrato de Calcio ETC.")
    
    # --- NUEVOS CAMPOS AÑADIDOS ---
    estado = st.selectbox("Estado Actual del Cultivo", ["Siembra", "Emergencia", "En Desarrollo", "Cosecha", "Post-cosecha"])
    responsable = st.text_input("Responsable de la Aplicación / Inspección")
    
    boton_guardar = st.form_submit_button("Guardar en la Bitácora")

# Lógica para insertar los datos ingresados a la tabla
if boton_guardar:
    if cultivo and plagas:
        nuevo_registro = {
            "Fecha Registro": str(fecha),
            "Nombre de Cultivo": cultivo,
            "Lote / Parcela": lote if lote else "No asignado",
            "Plagas Comunes / Observadas": plagas,
            "Control Fitosanitario (Dosis)": fitosanitario,
            "Control Nutricional (Etapa)": nutricional,
            "Fertilizantes (Foliares/Granulados)": fertilizantes,
            "Estado del Cultivo": estado,
            "Responsable": responsable if responsable else "General"
        }
        st.session_state.bitacora.append(nuevo_registro)
        st.success(f"¡Registro para el cultivo '{cultivo}' añadido correctamente!")
    else:
        st.error("Por favor, ingresa al menos el Nombre del Cultivo y las Plagas para guardar.")

# Convertir la lista de datos a un formato de tabla interactiva (DataFrame)
df_bitacora = pd.DataFrame(st.session_state.bitacora)

# Mostrar la tabla en pantalla completa con opciones de filtrado y descarga
st.header("📊 Cuaderno de Campo Digitalizado")

# Filtro rápido por cultivo
cultivos_disponibles = ["Todos"] + list(df_bitacora["Nombre de Cultivo"].unique())
filtro_cultivo = st.selectbox("Filtrar visualización por cultivo:", cultivos_disponibles)

if filtro_cultivo != "Todos":
    df_filtrado = df_bitacora[df_bitacora["Nombre de Cultivo"] == filtro_cultivo]
else:
    df_filtrado = df_bitacora

# Mostrar tabla interactiva (permite ordenar columnas haciendo clic en los títulos)
st.dataframe(df_filtrado, use_container_width=True)

# Opción para exportar y descargar los datos directamente a Excel o CSV
csv = df_filtrado.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Descargar esta tabla en formato CSV (Excel)",
    data=csv,
    file_name=f"bitacora_agricola_{datetime.date.today()}.csv",
    mime="text/csv",
)
