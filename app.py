import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# Configuración de la interfaz de la app
st.set_page_config(page_title="Bitácora Agrícola Fitosanitaria", page_icon="🧅", layout="wide")

st.title("🚜 Cuaderno de Bitácora y Control Fitosanitario")
st.write("Registra tus cultivos, monitorea plagas y lleva el control permanente en la nube.")

# Gestión de la conexión con la base de datos mediante Streamlit GSheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. Lectura de los datos existentes en Google Sheets
try:
    # Lee la hoja de cálculo configurada en los Secrets
    df_bitacora = conn.read()
    if df_bitacora is not None:
        df_bitacora = df_bitacora.dropna(how="all")
except Exception as e:
    # Si la hoja está totalmente vacía o hay un error inicial, estructuramos las columnas vacías
    df_bitacora = pd.DataFrame(columns=[
        "Fecha Registro", "Nombre de Cultivo", "Lote / Parcela", 
        "Plagas Comunes / Observadas", "Control Fitosanitario (Dosis)", 
        "Control Nutricional (Etapa)", "Fertilizantes (Foliares/Granulados)", 
        "Estado del Cultivo", "Responsable"
    ])

# 2. Formulario de entrada en la barra lateral
st.sidebar.header("📝 Añadir Nuevo Registro")
with st.sidebar.form("formulario_campo"):
    fecha = st.date_input("Fecha de Registro/Inspección", datetime.date.today())
    cultivo = st.text_input("Nombre de Cultivo (ej. Cebolla)", placeholder="Cebolla")
    lote = st.text_input("Lote / Parcela / Sector", placeholder="Ej. Sector Bajo 2")
    plagas = st.text_input("Plagas Comunes / Observadas", placeholder="Ej. Trips, Mildiu")
    fitosanitario = st.text_area("Plan o Control Fitosanitario (Recomendaciones de Dosis)", placeholder="Ej. Delta Plus, Entrus, Etc.")
    nutricional = st.text_area("Plan o Control Nutricional (Recomendaciones por Etapa)", placeholder="Ej. Fósforo, aminoácidos, calcio boro potasio")
    fertilizantes = st.text_area("Fertilizantes (Foliares o Granulados)", placeholder="Ej. Urea, Sulfato, Potasio, Nitrato de Calcio ETC.")
    estado = st.selectbox("Estado Actual del Cultivo", ["Siembra", "Emergencia", "En Desarrollo", "Cosecha", "Post-cosecha"])
    responsable = st.text_input("Responsable de la Aplicación / Inspección")
    
    boton_guardar = st.form_submit_button("Guardar Permanentemente en Google Sheets")

# 3. Procesamiento y guardado permanente de los datos
if boton_guardar:
    if cultivo and plagas:
        # Formateamos los datos del formulario exactamente como una nueva fila
        nuevo_registro = pd.DataFrame([{
            "Fecha Registro": str(fecha),
            "Nombre de Cultivo": cultivo,
            "Lote / Parcela": lote if lote else "No asignado",
            "Plagas Comunes / Observadas": plagas,
            "Control Fitosanitario (Dosis)": fitosanitario,
            "Control Nutricional (Etapa)": nutritional if 'nutritional' in locals() else nutricional,
            "Fertilizantes (Foliares/Granulados)": fertilizantes,
            "Estado del Cultivo": estado,
            "Responsable": responsable if responsable else "General"
        }])
        
        # Combinamos los datos anteriores de Google Sheets con la nueva fila
        if df_bitacora.empty:
            df_actualizado = nuevo_registro
        else:
            df_actualizado = pd.concat([df_bitacora, nuevo_registro], ignore_index=True)
        
        # Actualizamos la hoja de Google Sheets de forma definitiva
        conn.update(data=df_actualizado)
        st.sidebar.success(f"¡Registro para '{cultivo}' guardado con éxito!")
        
        # Forzar recarga automática de la app para mostrar los nuevos cambios en la tabla
        st.rerun()
    else:
        st.sidebar.error("Por favor, ingresa al menos el Nombre del Cultivo y las Plagas.")

# 4. Mostrar la tabla actualizada en el centro de la pantalla
st.header("📊 Cuaderno de Campo Digitalizado (Nube)")

if df_bitacora is not None and not df_bitacora.empty:
    st.dataframe(df_bitacora, use_container_width=True)
else:
    st.info("La base de datos está vacía en Google Sheets o lista para recibir el primer registro.")
