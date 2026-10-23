import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# Configuración de la interfaz
st.set_page_config(page_title="Bitácora Agrícola Fitosanitaria", page_icon="🧅", layout="wide")

st.title("🚜 Cuaderno de Bitácora y Control Fitosanitario")
st.write("Registra tus cultivos, monitorea plagas y lleva el control permanente en la nube.")

# Conexión directa y simple
conn = st.connection("gsheets", type=GSheetsConnection)

# Lectura de datos existentes
try:
    df_bitacora = conn.read()
    # Si la hoja tiene filas completamente vacías o nulas, las limpiamos
    df_bitacora = df_bitacora.dropna(how="all")
except Exception:
    df_bitacora = pd.DataFrame(columns=[
        "Fecha Registro", "Nombre de Cultivo", "Lote / Parcela", 
        "Plagas Comunes / Observadas", "Control Fitosanitario (Dosis)", 
        "Control Nutricional (Etapa)", "Fertilizantes (Foliares/Granulados)", 
        "Estado del Cultivo", "Responsable"
    ])

# Formulario lateral
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
    
    boton_guardar = st.form_submit_button("Guardar Permanentemente")

if boton_guardar:
    if cultivo and plagas:
        # Formateamos los datos del formulario de manera exacta
        nuevo_registro = pd.DataFrame([{
            "Fecha Registro": str(fecha),
            "Nombre de Cultivo": cultivo,
            "Lote / Parcela": lote if lote else "No asignado",
            "Plagas Comunes / Observadas": plagas,
            "Control Fitosanitario (Dosis)": fitosanitario,
            "Control Nutricional (Etapa)": nutritional,
            "Fertilizantes (Foliares/Granulados)": fertilizantes,
            "Estado del Cultivo": estado,
            "Responsable": responsable if responsable else "General"
        }])
        
        # Combinamos los datos viejos con la nueva fila
        if df_bitacora.empty:
            df_actualizado = nuevo_registro
        else:
            df_actualizado = pd.concat([df_bitacora, nuevo_registro], ignore_index=True)
        
        # Guardamos la tabla completa actualizada en Google Sheets
        conn.update(data=df_actualizado)
        st.success(f"¡Registro para '{cultivo}' guardado con éxito!")
        st.rerun()
    else:
        st.error("Por favor, ingresa al menos el Nombre del Cultivo y las Plagas.")

# Mostrar los datos en el centro de la pantalla
st.header("📊 Cuaderno de Campo Digitalizado (Nube)")
if not df_bitacora.empty:
    st.dataframe(df_bitacora, use_container_width=True)
else:
    st.info("La base de datos está vacía o lista para recibir el primer registro desde la barra lateral.")
