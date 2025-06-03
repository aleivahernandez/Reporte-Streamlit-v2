import streamlit as st
import pandas as pd
from deep_translator import GoogleTranslator
import re

# Configuración de la página de Streamlit
st.set_page_config(page_title="Informe de Patentes Apícolas V2", layout="wide")

# ===== Estilos CSS personalizados =====
# Estos estilos controlan la apariencia de la página y las tarjetas.
# Se ha modificado para que las tarjetas de botón de Streamlit contengan una imagen y un título.
page_style = """
<style>
body {
    background-color: #f9f4ef;
}

/* Estilos para el contenedor principal de las tarjetas */
.container {
    display: flex;
    flex-wrap: wrap; /* Permite que las tarjetas se envuelvan a la siguiente línea */
    justify-content: center; /* Centra las tarjetas horizontalmente */
    gap: 20px; /* Espacio uniforme entre las tarjetas */
    padding: 10px; /* Pequeño padding alrededor del contenedor */
}

/* Estilo para la "tarjeta" visual que contendrá la imagen, título y botón */
.custom-card {
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 12px;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.2s ease;
    overflow: hidden; /* Asegura que el contenido no se desborde */
    width: 300px; /* Ancho fijo de la tarjeta */
    height: 280px; /* Alto fijo de la tarjeta (imagen + título + botón) */
    display: flex;
    flex-direction: column;
    justify-content: space-between; /* Espacio entre imagen/título y botón */
    align-items: center;
    padding-bottom: 10px; /* Espacio para el botón en la parte inferior */
}

.custom-card:hover {
    transform: scale(1.02);
}

/* Contenedor de la imagen dentro de la tarjeta */
.image-container-card {
    width: 100%;
    height: 180px; /* Alto fijo para la imagen */
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    background-color: #f0f0f0; /* Color de fondo si no hay imagen */
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
}

/* Estilos para la imagen dentro del contenedor */
.image-container-card img {
    width: 100%;
    height: 100%;
    object-fit: contain; /* Ajustar la imagen para que quepa sin recortarse */
}

/* Contenedor del título dentro de la tarjeta */
.title-container-card {
    padding: 8px 12px;
    text-align: center;
    font-weight: bold;
    font-size: 16px;
    flex-grow: 1; /* Permite que el título ocupe el espacio restante */
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: normal;
}

/* Estilos para el botón "Ver detalles" */
.stButton>button {
    background-color: #4CAF50; /* Un color verde para el botón */
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 15px;
    margin-top: 5px; /* Espacio entre el título y el botón */
    cursor: pointer;
    font-weight: bold;
    transition: background-color 0.2s ease;
}

.stButton>button:hover {
    background-color: #45a049;
}

/* Ajustes para las columnas de Streamlit para evitar márgenes duplicados */
.stColumns > div {
    padding: 0px !important;
    margin: 0px !important;
}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# ===== Funciones de utilidad =====
def limpiar_titulo(titulo):
    """Limpia el título eliminando texto entre paréntesis."""
    if pd.isna(titulo):
        return ""
    return re.sub(r'\s*\([^)]*\)\s*', '', titulo).strip()

def traducir_texto(texto, src="en", dest="es"):
    """Traduce un texto usando Google Translator."""
    if not isinstance(texto, str) or len(texto.strip()) < 5:
        return "Contenido no disponible o demasiado corto para traducir."
    try:
        return GoogleTranslator(source=src, target=dest).translate(texto)
    except Exception as e:
        # st.warning(f"Error de traducción para el texto: '{texto[:50]}...' - {e}") # Descomentar para depurar errores de traducción
        return "Error de traducción."

@st.cache_data(show_spinner=False)
def cargar_y_preparar_datos(filepath):
    """
    Carga los datos del archivo Excel y traduce títulos y resúmenes.
    Utiliza st.cache_data para cachear los resultados y evitar recargas innecesarias.
    """
    # Leer el archivo Excel, especificando que los encabezados están en la segunda fila (índice 1)
    df = pd.read_excel(filepath, header=1)

    # Usamos los nombres de columna originales directamente.
    required_columns = [
        "Title (Original language)",
        "Abstract (Original Language)",
        "Publication Number",
        "Publication Date",
        "Front Page Drawing",
        "Inventor - DWPI"
    ]

    # Verificar que todas las columnas requeridas existen en el DataFrame
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Error: Faltan las siguientes columnas en el archivo Excel: {missing_columns}")
        st.error(f"Por favor, verifica los nombres de las columnas en tu archivo '{filepath}'.")
        st.stop() # Detener la ejecución de la app

    # Limpiar títulos usando el nombre de columna original
    df["Titulo_limpio"] = df["Title (Original language)"].apply(limpiar_titulo)

    # Traducir títulos al español usando el nombre de columna original
    with st.spinner("Traduciendo títulos al español... Esto puede tomar un momento."):
        df["Titulo_es"] = [traducir_texto(t) for t in df["Titulo_limpio"]]

    # Traducir resúmenes al español usando el nombre de columna original
    with st.spinner("Traduciendo resúmenes al español... Esto puede tomar un momento."):
        df["Resumen_es"] = [traducir_texto(t) for t in df["Abstract (Original Language)"]]

    return df

# ===== Cargar y preparar datos =====
df = cargar_y_preparar_datos("prueba5docu.xlsx")


# ===== Lógica principal de la aplicación: Landing page o vista detallada =====
query_params = st.query_params

if "idx" in query_params:
    # Vista detallada de una patente
    try:
        idx = int(query_params["idx"][0])
        if 0 <= idx < len(df):
            patente = df.iloc[idx]
            st.title(patente["Titulo_es"])

            # --- SECCIÓN DE INFORMACIÓN CLAVE ---
            st.subheader("Información Clave")

            # Número de Publicación (usando el nombre de columna original)
            st.markdown(f"- **Número de Publicación:** {patente.get('Publication Number', 'No disponible')}")

            # País de Origen (primeros dos caracteres del número de publicación)
            pub_number_str = str(patente.get('Publication Number', ''))
            pais_origen = pub_number_str[:2] if len(pub_number_str) >= 2 else "No disponible"
            st.markdown(f"- **País de Origen:** {pais_origen}")

            # Fecha de Publicación (primer elemento si hay varios, separados por espacio o punto y coma)
            pub_dates_str = str(patente.get('Publication Date', ''))
            fecha_publicacion = re.split(r'[; ]+', pub_dates_str)[0].strip() if pub_dates_str else "No disponible"
            st.markdown(f"- **Fecha de Publicación:** {fecha_publicacion}")

            # Inventores (mostrados como lista) - Usando "Inventor - DWPI"
            inventors = patente.get('Inventor - DWPI', 'No disponible')
            if pd.isna(inventors) or inventors == 'No disponible':
                st.markdown(f"- **Inventores:** No disponible")
            else:
                inventors_list = [inv.strip() for inv in str(inventors).split(';') if inv.strip()]
                st.markdown(f"- **Inventores:**")
                for inv in inventors_list:
                    st.markdown(f"  - {inv}")
            st.markdown("---")
            # --- FIN SECCIÓN DE INFORMACIÓN CLAVE ---

            # Resumen de la patente (usando el nombre de columna original)
            st.markdown(f"**Resumen:** {patente.get('Resumen_es', 'Resumen no disponible.')}")
            st.markdown("---")

            # Botón para volver a la página principal
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
    # Landing page con la lista de tarjetas
    st.title("Informe de Patentes Apícolas V2 - Landing Page")
    st.markdown("Haz clic en una patente para ver más detalles.")

    # Contenedor HTML para las tarjetas (gestionado por CSS Flexbox)
    st.markdown('<div class="container">', unsafe_allow_html=True)

    # Iterar sobre las patentes para crear las tarjetas
    cols = st.columns(3) # Mantenemos 3 columnas
    for i, titulo in enumerate(df["Titulo_es"]):
        with cols[i % 3]: # Asigna cada tarjeta a una columna de 3
            # Usando el nombre de columna original para la imagen
            image_url = df.iloc[i].get('Front Page Drawing', '')
            # Si la URL de la imagen está vacía o no es válida, usa una imagen de placeholder
            if not image_url or not isinstance(image_url, str):
                image_url = "https://placehold.co/300x180/A0A0A0/FFFFFF?text=No+Image"

            # --- NUEVA ESTRUCTURA DE LA TARJETA ---
            # Creamos un contenedor HTML para la tarjeta visual
            st.markdown(f"""
            <div class="custom-card">
                <div class="image-container-card">
                    <img src="{image_url}" onerror="this.onerror=null;this.src='https://placehold.co/300x180/A0A0A0/FFFFFF?text=No+Image';" alt="Imagen de la patente"/>
                </div>
                <div class="title-container-card">
                    {titulo}
                </div>
                <!-- El botón real de Streamlit se colocará aquí abajo -->
            </div>
            """, unsafe_allow_html=True)

            # Colocamos el botón de Streamlit justo debajo de la tarjeta HTML.
            # Este botón es el que realmente manejará la interacción y la navegación.
            if st.button("Ver detalles", key=f"patent_card_button_{i}"):
                st.query_params["idx"] = str(i)
                st.rerun()
            # --- FIN NUEVA ESTRUCTURA DE LA TARJETA ---

    st.markdown('</div>', unsafe_allow_html=True)
