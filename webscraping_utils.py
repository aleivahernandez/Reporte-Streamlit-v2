import requests
from bs4 import BeautifulSoup
import time
import streamlit as st # Importar st para usar st.warning/st.info en la función de utilidad

@st.cache_data(show_spinner=False)
def get_direct_image_url_from_page(page_url: str) -> str:
    """
    Intenta extraer una URL de imagen directa de una página web.
    Busca meta tags Open Graph (og:image) y las etiquetas <img>.
    """
    if not isinstance(page_url, str) or not page_url.startswith('http'):
        return "" # Retorna vacío si no es una URL válida

    try:
        # Añade un pequeño retardo para evitar sobrecargar el servidor de origen
        time.sleep(0.1)
        # Realiza la petición HTTP con un tiempo de espera
        response = requests.get(page_url, timeout=5)
        response.raise_for_status() # Lanza un error para códigos de estado HTTP erróneos

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Buscar meta tags Open Graph (usado por redes sociales para previsualizaciones)
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']

        # 2. Buscar la primera imagen grande en el cuerpo del documento
        # Esto es un enfoque heurístico y podría no ser la imagen correcta en todos los casos
        for img_tag in soup.find_all('img'):
            img_src = img_tag.get('src')
            if img_src and img_src.startswith('http'): # Asegúrate de que sea una URL absoluta
                # Puedes añadir lógica para filtrar por tamaño o atributos específicos si es necesario
                return img_src

        # Si no se encuentra ninguna URL directa, retorna vacío
        return ""

    except requests.exceptions.Timeout:
        st.warning(f"Tiempo de espera agotado al intentar obtener imagen de: {page_url}")
        return ""
    except requests.exceptions.RequestException as e:
        st.warning(f"Error al acceder a la página {page_url}: {e}")
        return ""
    except Exception as e:
        st.warning(f"Error inesperado al procesar la página {page_url}: {e}")
        return ""

