import streamlit as st
import pandas as pd
from deep_translator import GoogleTranslator
import re

st.set_page_config(page_title="Informe de Patentes Apícolas", layout="wide")

# ===== Estilos CSS personalizados =====
page_style = """
<style>
body {
    background-color: #f9f4ef;
}
/* Revertimos los estilos de .card si los habías puesto antes */
.card {
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 12px;
    padding: 16px;
    margin: 12px;
    width: 300px; /* Tamaño original o similar */
    height: 120px; /* Tamaño original o similar */
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.2s ease;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    text-align: center;
}
.card:hover {
    transform: scale(1.02);
    background-color: #f0f0f0;
}
.container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
}
/* Estilos para el botón de Streamlit para que se parezca a una tarjeta */
.stButton>button {
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 12px;
    padding: 16px;
    margin: 12px; /* Margen para espacio entre botones */
    width: 300px; /* Tamaño original o similar */
    height: 120px; /* Tamaño original o similar */
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.2s ease;
    cursor: pointer;
    font-weight: bold;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    color: inherit;
    font-size: 16px; /* Ajustado para el tamaño de botón */
    line-height: 1.3;
}
.stButton>button:hover {
    transform: scale(1.02);
    background-color: #f0f0f0;
}
/* Aseguramos que las columnas de Streamlit no tengan márgenes internos inesperados */
.stColumns > div {
    padding: 0px !important; /* Elimina padding interno de las columnas de Streamlit */
    margin: 0px !important;  /* Elimina margen interno de las columnas de Streamlit */
}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# ===== Funciones =====
def limpiar_titulo(titulo):
    if pd.isna(titulo):
        return ""
    return re.sub(r'\s*\([^)]*\)\s*', '', titulo).strip()

def traducir_texto(texto, src="en", dest="es"):
    if not isinstance(texto, str) or len(texto.strip()) < 5:
        return "Contenido no disponible o demasiado corto para traducir."
    try:
        return GoogleTranslator(source=src, target=dest).translate(texto)
    except Exception as e:
        # st.warning(f"Error de traducción para el texto: '{texto[:50]}...' - {e}") # Descomentar para depurar
        return "Error de traducción."

@st.cache_data(show_spinner=False)
def cargar_y_preparar_datos(filepath):
    df = pd.read_csv(filepath)
    df["Titulo_limpio"] = df["Title"].apply(limpiar_titulo)

    with st.spinner("Traduciendo títulos al español... Esto puede tomar un momento."):
        df["Titulo_es"] = [traducir_texto(t) for t in df["Titulo_limpio"]]

    with st.spinner("Traduciendo resúmenes al español... Esto puede tomar un momento."):
        df["Resumen_es"] = [traducir_texto(t) for t in df["Abstract"]]

    return df

# ===== Cargar y preparar datos =====
df = cargar_y_preparar_datos("ORBIT_REGISTRO_QUERY.csv")


# ===== Landing page o vista detallada =====
query_params = st.query_params

if "idx" in query_params:
    try:
        idx = int(query_params["idx"][0])
        if 0 <= idx < len(df):
            patente = df.iloc[idx]
            st.title(patente["Titulo_es"])

            # --- SECCIÓN DE DETALLES ---
            st.subheader("Información Clave")
            st.markdown(f"- **Número de Publicación:** {patente.get('Publication numbers', 'No disponible')}")

            # Extraer País de Origen
            pub_numbers = str(patente.get('Publication numbers', ''))
            pais_origen = pub_numbers[:2] if len(pub_numbers) >= 2 else "No disponible"
            st.markdown(f"- **País de Origen:** {pais_origen}")

            # Extraer Fecha de Publicación (primer elemento si hay varios)
            pub_dates = str(patente.get('Publication dates', ''))
            fecha_publicacion = pub_dates.split(';')[0].strip() if pub_dates else "No disponible"
            st.markdown(f"- **Fecha de Publicación:** {fecha_publicacion}")

            # Mostrar Inventores como lista
            inventors = patente.get('Inventors', 'No disponible')
            if pd.isna(inventors) or inventors == 'No disponible':
                st.markdown(f"- **Inventores:** No disponible")
            else:
                inventors_list = [inv.strip() for inv in str(inventors).split(';') if inv.strip()]
                st.markdown(f"- **Inventores:**")
                for inv in inventors_list:
                    st.markdown(f"  - {inv}")
            st.markdown("---")
            # --- FIN SECCIÓN DE DETALLES ---

            st.markdown(f"**Resumen:** {patente.get('Resumen_es', 'Resumen no disponible.')}")
            st.markdown("---")
            if st.button("🔙 Volver"):
                query_params.clear()
                st.rerun()
        else:
            st.error("Índice de patente no válido.")
            if st.button("🔙 Volver a la página principal"):
                query_params.clear()
                st.rerun()
    except ValueError:
        st.error("El índice proporcionado no es un número válido.")
        if st.button("🔙 Volver a la página principal"):
            query_params.clear()
            st.rerun()
    except Exception as e:
        st.error(f"Error al cargar la patente seleccionada: {e}")
        st.exception(e)
        if st.button("🔙 Volver a la página principal"):
            query_params.clear()
            st.rerun()
else:
    st.title("Informe de Patentes Apícolas - Landing Page")
    st.markdown("Haz clic en una patente para ver más detalles.")
    
    # Volvemos a usar st.columns para la disposición en 3 columnas
    # Esto manejará la responsividad básica (cambiará a 1 columna en móviles)
    # pero mantendrá el control de 3 columnas en pantallas más grandes.
    cols = st.columns(3) 
    
    for i, titulo in enumerate(df["Titulo_es"]):
        with cols[i % 3]: # Asigna cada tarjeta a una columna de 3
            if st.button(titulo, key=f"patent_card_{i}"):
                st.query_params["idx"] = str(i)
                st.rerun()
