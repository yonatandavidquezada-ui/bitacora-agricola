import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# Configuración de la interfaz
st.set_page_config(page_title="Bitácora Agrícola Fitosanitaria", page_icon="🧅", layout="wide")

st.title("🚜 Cuaderno de Bitácora y Control Fitosanitario")
st.write("Registra tus cultivos, monitorea plagas y lleva el control permanente en la nube.")

# --- CONEXIÓN DIRECTA A GOOGLE SHEETS ---
# Configura la conexión usando las credenciales secretas de Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

# Función para leer los datos actuales de Google Sheets de forma segura
try:
    df_bitacora = conn.read(ttl="5s") # ttl=5s hace que la app se actualice cada 5 segundos con el campo
except Exception:
    # Si la hoja está totalmente vacía al inicio, creamos una estructura base
    df_bitacora = pd.DataFrame(columns=[
        "Fecha Registro", "Nombre de Cultivo", "Lote / Parcela", 
        "Plagas Comunes / Observadas", "Control Fitosanitario (Dosis)", 
        "Control Nutricional (Etapa)", "Fertilizantes (Foliares/Granulados)", 
        "Estado del Cultivo", "Responsable"
    ])

# Formulario para añadir nuevos registros en la barra lateral
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

# Lógica para guardar directamente en Google Sheets al presionar el botón
if boton_guardar:
    if cultivo and plagas:
        # Formatear el nuevo registro como una fila de datos
        nuevo_registro = pd.DataFrame([{
            "Fecha Registro": str(fecha),
            "Nombre de Cultivo": cultivo,
            "Lote / Parcela": lote if lote else "No asignado",
            "Plagas Comunes / Observadas": plagas,
            "Control Fitosanitario (Dosis)": fitosanitario,
            "Control Nutricional (Etapa)": nutricional,
            "Fertilizantes (Foliares/Granulados)": fertilizantes,
            "Estado del Cultivo": estado,
            "Responsable": responsable if responsable else "General"
        }])
        
        # Unir el registro nuevo con los datos que ya existían en la nube
        df_actualizado = pd.concat([df_bitacora, nuevo_registro], ignore_index=True)
        
        # Enviar los datos combinados de regreso a Google Sheets de forma permanente
        conn.update(data=df_actualizado)
        st.success(f"¡Registro para el cultivo '{cultivo}' guardado en la nube con éxito!")
        
        # Forzar la recarga de datos para mostrar los cambios en pantalla inmediatamente
        st.rerun()
    else:
        st.error("Por favor, ingresa al menos el Nombre del Cultivo y las Plagas para guardar.")

# --- MOSTRAR LA TABLA EN PANTALLA ---
st.header("📊 Cuaderno de Campo Digitalizado (Nube)")

if not df_bitacora.empty:
    # Filtro rápido por cultivo
    cultivos_disponibles = ["Todos"] + list(df_bitacora["Nombre de Cultivo"].dropna().unique())
    filtro_cultivo = st.selectbox("Filtrar visualización por cultivo:", cultivos_disponibles)

    if filtro_cultivo != "Todos":
        df_filtrado = df_bitacora[df_bitacora["Nombre de Cultivo"] == filtro_cultivo]
    else:
        df_filtrado = df_bitacora

    # Mostrar tabla interactiva en tiempo real
    st.dataframe(df_filtrado, use_container_width=True)

    # Opción de respaldo rápido local en formato CSV
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar copia de respaldo local (Excel)",
        data=csv,
        file_name=f"bitacora_agricola_nube_{datetime.date.today()}.csv",
        mime="text/csv",
    )
else:
    st.info("Aún no hay registros en la base de datos de Google Sheets. ¡Ingresa el primero usando el formulario!")
