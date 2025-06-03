import requests
from bs4 import BeautifulSoup
import time
import streamlit as st # Importar st para usar st.warning/st.error en la función de utilidad
import re # Importar re para expresiones regulares

@st.cache_data(show_spinner=False)
def scrape_reports_page(url: str) -> list[dict]:
    """
    Scrapes a webpage for report titles and PDF links based on the provided HTML structure.

    Args:
        url (str): La URL de la página web a scrapear.

    Returns:
        list[dict]: Una lista de diccionarios, donde cada diccionario contiene
                    'title' (título del informe) y 'pdf_link' (enlace al PDF).
    """
    if not isinstance(url, str) or not url.startswith('http'):
        st.warning(f"URL de scraping no válida: {url}")
        return []

    reports_data = []
    try:
        # Añade un pequeño retardo para evitar sobrecargar el servidor de origen
        time.sleep(0.5)
        # Realiza la petición HTTP con un tiempo de espera
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Lanza un error para códigos de estado HTTP erróneos

        soup = BeautifulSoup(response.text, 'html.parser')

        # Buscar todos los contenedores de informes
        # Los informes están en <div> con clase class="item-archivo archivo2 archivo2b"
        report_containers = soup.find_all('div', class_=re.compile(r'item-archivo\s+archivo2\s+archivo2b'))

        if not report_containers:
            st.warning(f"No se encontraron contenedores de informes con la clase esperada en {url}.")
            return []

        for container in report_containers:
            title = "Título no encontrado"
            pdf_link = None

            # Extraer el título
            # Los titulos están en un <div> con clase der-archivo que contiene otro <div> con clase texto-archivo, en un <h4>
            title_h4_tag = container.find('div', class_='der-archivo').find('div', class_='texto-archivo').find('h4')
            if title_h4_tag:
                title = title_h4_tag.get_text(strip=True)

            # Extraer el link al PDF
            # Los informes (links a los pdfs) están contenidos en un <div class="izq-archivo">, dentro de ese div hay un objeto a (un link)
            pdf_link_tag = container.find('div', class_='izq-archivo').find('a', href=True)
            if pdf_link_tag:
                href = pdf_link_tag['href']
                if href.lower().endswith('.pdf'):
                    # Asegurarse de que el link sea absoluto
                    if not href.startswith('http'):
                        pdf_link = requests.compat.urljoin(url, href)
                    else:
                        pdf_link = href

            if title and pdf_link:
                reports_data.append({'title': title, 'pdf_link': pdf_link})

    except requests.exceptions.Timeout:
        st.error(f"Tiempo de espera agotado al intentar scrapear: {url}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error de red/HTTP al scrapear {url}: {e}")
    except Exception as e:
        st.error(f"Error inesperado al scrapear {url}: {e}")
        st.exception(e) # Mostrar la excepción completa para depuración

    return reports_data
