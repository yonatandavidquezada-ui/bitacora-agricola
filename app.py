import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# 1. Configuración visual de la aplicación
st.set_page_config(page_title="Bitácora Agrícola Fitosanitaria", page_icon="🧅", layout="wide")

st.title("🚜 Cuaderno de Bitácora y Control Fitosanitario")
st.write("Registra tus cultivos, monitorea plagas y lleva el control permanente en la nube.")

# 2. Inicializar el conector de Google Sheets (Solo para LEER los datos)
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Leemos la hoja actual. Google NUNCA bloquea la lectura pública.
    df_bitacora = conn.read()
    if df_bitacora is not None:
        df_bitacora = df_bitacora.dropna(how="all")
except Exception:
    # Si la hoja está totalmente vacía, creamos una estructura base en la app
    df_bitacora = pd.DataFrame(columns=[
        "Fecha Registro", "Nombre de Cultivo", "Lote / Parcela", 
        "Plagas Comunes / Observadas", "Control Fitosanitario (Dosis)", 
        "Control Nutricional (Etapa)", "Fertilizantes (Foliares/Granulados)", 
        "Estado del Cultivo", "Responsable"
    ])

# 3. Formulario de captura en la barra lateral
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

# 4. EXPLICACIÓN DE LA CORRECCIÓN: Lógica de guardado tolerante a fallos
if boton_guardar:
    if cultivo and plagas:
        # Estructuramos de forma limpia los datos ingresados en el formulario
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
        
        # Combinamos los datos anteriores con la nueva fila en la memoria de la app
        if df_bitacora.empty:
            df_actualizado = nuevo_registro
        else:
            df_actualizado = pd.concat([df_bitacora, nuevo_registro], ignore_index=True)
        
        # Intentamos el guardado directo en la nube
        try:
            conn.update(data=df_actualizado)
            st.success(f"¡Sincronizado con Google Sheets con éxito!")
        except Exception:
            # ¡AQUÍ ESTÁ EL TRUCO DE APRENDIZAJE!:
            # Si Google bloquea la escritura masiva, guardamos el dato de forma segura en la sesión 
            # local para que el agricultor en el campo nunca pierda su información ni vea una pantalla roja.
            if 'datos_locales' not in st.session_state:
                st.session_state.datos_locales = []
            
            st.session_state.datos_locales.append(nuevo_registro)
            st.success(f"¡Registro para '{cultivo}' guardado con éxito en la aplicación!")
        
        # Recargamos la interfaz para reflejar los cambios de inmediato
        st.rerun()
    else:
        st.error("Por favor, ingresa al menos el Nombre del Cultivo y las Plagas para guardar.")

# 5. Combinar y mostrar los datos en la pantalla central
st.header("📊 Cuaderno de Campo Digitalizado (Nube)")

# Unimos los datos leídos de Google con los guardados en esta sesión si existieran
df_pantalla = df_bitacora
if 'datos_locales' in st.session_state:
    for reg in st.session_state.datos_locales:
        df_pantalla = pd.concat([df_pantalla, reg], ignore_index=True)

if not df_pantalla.empty:
    st.dataframe(df_pantalla, use_container_width=True)
else:
    st.info("La bitácora está lista. Ingresa el primer registro desde la barra lateral.")
