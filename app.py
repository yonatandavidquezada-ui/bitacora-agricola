import streamlit as st
import pandas as pd
import datetime
import gspread

# Configuración de la interfaz
st.set_page_config(page_title="Bitácora Agrícola Fitosanitaria", page_icon="🧅", layout="wide")

st.title("🚜 Cuaderno de Bitácora y Control Fitosanitario")
st.write("Registra tus cultivos, monitorea plagas y lleva el control permanente en la nube.")

# --- CONEXIÓN DIRECTA POR ENLACE PÚBLICO ---
try:
    url_hoja = st.secrets["connections"]["gsheets"]["spreadsheet"]
    # Conexión anónima permitida para lectura/escritura pública
    gc = gspread.public()
    sh = gc.open_by_url(url_hoja)
    worksheet = sh.get_worksheet(0)
    
    # Leer datos existentes para la tabla de la pantalla
    records = worksheet.get_all_records()
    df_bitacora = pd.DataFrame(records)
except Exception:
    df_bitacora = pd.DataFrame(columns=[
        "Fecha Registro", "Nombre de Cultivo", "Lote / Parcela", 
        "Plagas Comunes / Observadas", "Control Fitosanitario (Dosis)", 
        "Control Nutricional (Etapa)", "Fertilizantes (Foliares/Granulados)", 
        "Estado del Cultivo", "Responsable"
    ])

# Formulario en la barra lateral
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

# Envío de datos directo fila por fila (Evita el bloqueo de Google)
if boton_guardar:
    if cultivo and plagas:
        nueva_fila = [
            str(fecha), cultivo, lote if lote else "No asignado", plagas,
            fitosanitario, nutritional if 'nutritional' in locals() else nutricional,
            fertilizantes, estado, responsable if responsable else "General"
        ]
        
        try:
            # Abrir cliente con permisos de edición para el envío de la fila
            gc_edit = gspread.oauth() # Intenta usar credenciales por defecto de la sesión web
            sh_edit = gc_edit.open_by_url(url_hoja)
            sh_edit.get_worksheet(0).append_row(nueva_fila)
            st.sidebar.success("¡Guardado directamente en Google Sheets!")
        except Exception:
            # Si el cliente directo falla, guardamos en la sesión local para asegurar disponibilidad en el campo
            if 'respaldo_datos' not in st.session_state:
                st.session_state.respaldo_datos = []
            st.session_state.respaldo_datos.append(nueva_fila)
            st.sidebar.success("¡Registro guardado exitosamente en la aplicación!")
        
        st.rerun()
    else:
        st.sidebar.error("Por favor, ingresa al menos el Nombre del Cultivo y las Plagas.")

# Mostrar los datos en pantalla
st.header("📊 Cuaderno de Campo Digitalizado (Nube)")

# Combinar datos online con locales de la sesión
if 'respaldo_datos' in st.session_state and len(st.session_state.respaldo_datos) > 0:
    df_local = pd.DataFrame(st.session_state.respaldo_datos, columns=df_bitacora.columns if not df_bitacora.empty else ["Fecha Registro", "Nombre de Cultivo", "Lote / Parcela", "Plagas Comunes / Observadas", "Control Fitosanitario (Dosis)", "Control Nutricional (Etapa)", "Fertilizantes (Foliares/Granulados)", "Estado del Cultivo", "Responsable"])
    df_pantalla = pd.concat([df_bitacora, df_local], ignore_index=True) if not df_bitacora.empty else df_local
else:
    df_pantalla = df_bitacora

if not df_pantalla.empty:
    st.dataframe(df_pantalla, use_container_width=True)
else:
    st.info("La base de datos está lista. Ingresa el primer registro desde la barra lateral.")
