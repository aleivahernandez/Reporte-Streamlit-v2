import streamlit as st
import pandas as pd
from deep_translator import GoogleTranslator
import re
# Ya no necesitamos 'time' para el retardo en la traducción en esta versión

# Configuración de la página de Streamlit
st.set_page_config(page_title="Informe de Patentes Apícolas V1", layout="wide")

# ===== Estilos CSS personalizados =====
# Estos estilos controlan la apariencia de la página y las tarjetas.
page_style = """
<style>
body {
    background-color: #f9f4ef;
}
/* Estilo para el contenedor principal de la aplicación */
.stApp {
    max-width: 90%; /* Limita el ancho máximo al 80% de la pantalla */
    margin: auto; /* Centra la aplicación en la pantalla */
}
.card {
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 12px;
    padding: 16px;
    margin: 12px;
    width: 300px; /* Ancho fijo de la tarjeta */
    height: 120px; /* Alto fijo de la tarjeta */
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
    margin: 12px;
    width: 300px; /* Ancho fijo para simular la tarjeta */
    height: 120px; /* Alto fijo para simular la tarjeta */
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.2s ease;
    cursor: pointer;
    font-weight: bold;
    text-align: center;
    display: flex; /* Para centrar el texto del botón */
    align-items: center;
    justify-content: center;
    color: inherit; /* Heredar color de texto para que no sea el azul por defecto */
    font-size: 16px; /* Ajustado para el tamaño de botón */
    line-height: 1.3;
}
.stButton>button:hover {
    transform: scale(1.02);
    background-color: #f0f0f0;
}
/* Aseguramos que las columnas de Streamlit no tengan márgenes internos inesperados */
.stColumns > div {
    padding: 0px !important;
    margin: 0px !important;
}
/* Estilos para el iframe de YouTube */
.youtube-container {
    position: relative;
    max-width: 30vw; /* Limita el ancho máximo del video al 30% del ancho del viewport */
    padding-bottom: calc(30vw * 9 / 16); /* Calcula el padding-bottom para mantener 16:9 basado en 30vw */
    height: 0;
    overflow: hidden;
    margin: 0 auto 20px auto; /* Centra el contenedor y añade margen inferior */
}
.youtube-container iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# Inicializar el estado de la vista
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'home'
if 'vigilancia_report_type' not in st.session_state:
    st.session_state.vigilancia_report_type = None


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
    Carga los datos del archivo CSV y traduce títulos y resúmenes.
    Utiliza st.cache_data para cachear los resultados y evitar recargas innecesarias.
    """
    # Leer el archivo CSV
    df = pd.read_csv(filepath)

    # Usamos los nombres de columna originales del CSV
    required_columns = [
        "Title",
        "Abstract",
        "Publication numbers",
        "Publication dates",
        "Inventors"
    ]

    # Verificar que todas las columnas requeridas existen en el DataFrame
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Error: Faltan las siguientes columnas en el archivo CSV: {missing_columns}")
        st.error(f"Por favor, verifica los nombres de las columnas en tu archivo '{filepath}'.")
        st.stop() # Detener la ejecución de la app

    # Limpiar títulos usando el nombre de columna original
    df["Titulo_limpio"] = df["Title"].apply(limpiar_titulo)

    # Traducir títulos al español
    with st.spinner("Traduciendo títulos al español... Esto puede tomar un momento."):
        df["Titulo_es"] = [traducir_texto(t) for t in df["Titulo_limpio"]]

    # Traducir resúmenes al español
    with st.spinner("Traduciendo resúmenes al español... Esto puede tomar un momento."):
        df["Resumen_es"] = [traducir_texto(t) for t in df["Abstract"]]

    return df

# ===== Lógica principal de la aplicación: Control de vistas =====
if st.session_state.current_view == 'home':
    st.title("Bienvenido a nuestra Plataforma de Soluciones")

    # Contenedor para el video de YouTube para hacerlo responsivo
    st.markdown(
        """
        <div class="youtube-container">
            <iframe src="https://www.youtube.com/embed/2UjdalNj7Qw?si=IoTVBxYvOy_-XOAm" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
        </div>
        """,
        unsafe_allow_html=True
    )
    # Nota: La URL del iframe proporcionada (https://www.youtube.com/embed/2UjdalNj7Qw?si=IoTVBxYvOy_-XOAm)
    # parece ser un placeholder y podría no mostrar un video real de YouTube.
    # Para un video real, necesitarías una URL de embed de YouTube válida.

    st.write("Selecciona una solución para explorar:")
    solution_choice = st.selectbox(
        "Busca tu solución",
        ("Selecciona una opción", "Solución Apícola", "Solución Cárnica"),
        index=0 # Opción por defecto
    )

    if solution_choice == "Solución Apícola":
        st.session_state.current_view = 'apicola'
        st.rerun() # Recarga la aplicación para mostrar la vista apícola
    elif solution_choice == "Solución Cárnica":
        st.info("La solución Cárnica aún no está disponible. ¡Pronto tendremos más información!")
        # No se redirige a ninguna parte, se queda en la página principal

    st.markdown("---") # Separador visual

    # ===== Sección de Informes de Vigilancia =====
    st.subheader("Informes de Vigilancia")
    report_type_choice = st.selectbox(
        "Selecciona el tipo de informe de vigilancia",
        ("Selecciona una opción", "Patentes Abiertas", "Patentes Protegidas"),
        index=0
    )

    if report_type_choice == "Patentes Abiertas":
        st.session_state.current_view = 'vigilancia_patentes'
        st.session_state.vigilancia_report_type = 'abiertas'
        st.rerun()
    elif report_type_choice == "Patentes Protegidas":
        st.session_state.current_view = 'vigilancia_patentes'
        st.session_state.vigilancia_report_type = 'protegidas'
        st.rerun()
    # ===== Fin Sección de Informes de Vigilancia =====

    st.markdown("---") # Separador visual

    # ===== Sección de Newsletter (existente) =====
    st.subheader("Suscríbete a nuestro Newsletter")
    st.write("Mantente al día con nuestras últimas soluciones e innovaciones.")

    email_input = st.text_input("Ingresa tu correo electrónico", placeholder="tu.email@ejemplo.com")

    newsletter_topic = st.selectbox(
        "Selecciona los temas de tu interés",
        ("Solución Apícola", "Solución Cárnica")
    )

    if st.button("Solicitar Suscripción"):
        if email_input and "@" in email_input and "." in email_input:
            st.success(f"¡Gracias por suscribirte, {email_input}! Te enviaremos información sobre {newsletter_topic}.")
            # Aquí iría la lógica para guardar el correo y el tema en una base de datos,
            # pero por ahora solo mostramos un mensaje de éxito.
        else:
            st.error("Por favor, ingresa un correo electrónico válido.")
    # ===== Fin Sección de Newsletter =====


elif st.session_state.current_view == 'apicola':
    # ===== Cargar y preparar datos (solo se carga cuando se necesita la vista apícola) =====
    # Asegúrate de que el nombre del archivo CSV sea correcto
    df = cargar_y_preparar_datos("ORBIT_REGISTRO_QUERY.csv")


    # ===== Lógica de la vista detallada o landing de patentes apícolas =====
    query_params = st.query_params

    # Botón para volver a la página principal desde la lista de patentes o detalle de patente apícola
    if st.button("🔙 Volver a la página principal", key="back_to_home_from_apicola_list"):
        st.session_state.current_view = 'home'
        st.query_params.clear() # <--- Limpiar el parámetro 'idx' al volver a la página principal
        st.rerun()

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
                st.markdown(f"- **Número de Publicación:** {patente.get('Publication numbers', 'No disponible')}")

                # País de Origen (primeros dos caracteres del número de publicación)
                pub_number_str = str(patente.get('Publication numbers', ''))
                pais_origen = pub_number_str[:2] if len(pub_number_str) >= 2 else "No disponible"
                st.markdown(f"- **País de Origen:** {pais_origen}")

                # Fecha de Publicación (primer elemento si hay varios, separados por espacio o punto y coma)
                pub_dates_str = str(patente.get('Publication dates', ''))
                fecha_publicacion = re.split(r'[; ]+', pub_dates_str)[0].strip() if pub_dates_str else "No disponible"
                st.markdown(f"- **Fecha de Publicación:** {fecha_publicacion}")

                # Inventores (mostrados como lista) - Usando "Inventors"
                inventors = patente.get('Inventors', 'No disponible')
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

                # Botón para volver a la página principal (desde la vista detallada)
                if st.button("🔙 Volver a la lista de patentes", key="back_to_apicola_list"): # Cambiado el texto
                    query_params.clear() # Limpia los parámetros de la URL
                    st.rerun() # Fuerza una nueva ejecución de la app
            else:
                st.error("Índice de patente no válido.")
                if st.button("🔙 Volver a la página principal"):
                    st.session_state.current_view = 'home'
                    query_params.clear()
                    st.rerun()
        except ValueError:
            st.error("El índice proporcionado no es un número válido.")
            if st.button("🔙 Volver a la página principal"):
                st.session_state.current_view = 'home'
                query_params.clear()
                st.rerun()
        except Exception as e:
            st.error(f"Error al cargar la patente seleccionada: {e}")
            st.exception(e)
            if st.button("🔙 Volver a la página principal"):
                st.session_state.current_view = 'home'
                query_params.clear()
                st.rerun()
    else:
        # Landing page con la lista de tarjetas de patentes apícolas
        st.title("Informe de Patentes Apícolas") # Título actualizado
        st.markdown("Haz clic en una patente para ver más detalles.")

        # Contenedor HTML para las tarjetas (gestionado por CSS Flexbox)
        st.markdown('<div class="container">', unsafe_allow_html=True)

        # Iterar sobre las patentes para crear las tarjetas
        cols = st.columns(3) # Volvemos a 3 columnas
        for i, titulo in enumerate(df["Titulo_es"]):
            with cols[i % 3]: # Asigna cada tarjeta a una columna de 3
                # Creamos el botón con el título como etiqueta
                if st.button(titulo, key=f"patent_card_{i}"):
                    st.query_params["idx"] = str(i)
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_view == 'vigilancia_patentes':
    st.title("Informes de Vigilancia de Patentes")

    # Botón para volver a la página principal desde la lista de informes
    if st.button("🔙 Volver a la página principal", key="back_to_home_from_vigilancia_list"):
        st.session_state.current_view = 'home'
        st.session_state.vigilancia_report_type = None # Limpiar el tipo de informe
        st.rerun()

    # URL de los informes de INAPI
    reports_url = "https://www.inapi.cl/centro-de-documentacion/informes"

    with st.spinner(f"Scrapeando informes de {st.session_state.vigilancia_report_type}... Esto puede tomar un momento."):
        all_reports = scrape_reports_page(reports_url)

    if not all_reports:
        st.warning("No se encontraron informes o hubo un error al scrapear la página. Por favor, verifica la URL y la estructura de la página.")
    else:
        # Filtrar informes según la selección
        filtered_reports = []
        if st.session_state.vigilancia_report_type == 'abiertas':
            st.subheader("Patentes Abiertas (Caducadas)")
            for report in all_reports:
                # Filtrar por "Patentes Caducadas" en el título
                if "patentes caducadas" in report['title'].lower():
                    filtered_reports.append(report)
        elif st.session_state.vigilancia_report_type == 'protegidas':
            st.subheader("Patentes Protegidas")
            for report in all_reports:
                # Filtrar por NO "Patentes Caducadas" en el título
                if "patentes caducadas" not in report['title'].lower():
                    filtered_reports.append(report)

        if not filtered_reports:
            st.info(f"No se encontraron informes de tipo '{st.session_state.vigilancia_report_type}'.")
        else:
            st.markdown('<div class="container">', unsafe_allow_html=True)
            cols = st.columns(3)
            for i, report in enumerate(filtered_reports):
                with cols[i % 3]:
                    # Usamos st.markdown con un enlace <a> para que la tarjeta sea clicable al PDF
                    # target="_blank" abre el PDF en una nueva pestaña
                    card_html = f"""
                    <div class="card" style="cursor: pointer;">
                        <a href="{report['pdf_link']}" target="_blank" style="text-decoration: none; color: inherit; display: flex; align-items: center; justify-content: center; width: 100%; height: 100%;">
                            {report['title']}
                        </a>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
