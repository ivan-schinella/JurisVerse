from utils_module import (
    map_value,
    filename_retrieve,
    get_parent_directory,
)

import os
import requests
import streamlit as st
from streamlit_extras.row import row
from bs4 import BeautifulSoup
from docx import Document
from htmldocx import HtmlToDocx
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

site = "https://www.giustizia-amministrativa.it/web/guest/dcsnprr"

# Form query Decisioni e Pareri
select_sedi = [
    "",
    "Consiglio Di Stato",
    "C.G.A.R.S",
    "Ancona",
    "Aosta",
    "Bari",
    "Bologna",
    "Bolzano",
    "Brescia",
    "Cagliari",
    "Campobasso",
    "Catania",
    "Catanzaro",
    "Firenze",
    "Genova",
    "L'Aquila",
    "Latina",
    "Lecce",
    "Milano",
    "Napoli",
    "Palermo",
    "Parma",
    "Perugia",
    "Pescara",
    "Potenza",
    "ReggioCalabria",
    "Roma",
    "Salerno",
    "Torino",
    "Trento",
    "Trieste",
    "Venezia",
]

tipologie_provvedimenti = [
    "",
    "Decreto",
    "Ordinanza",
    "Parere",
    "Sentenza",
    "Adunanza Plenaria",
    "Adunanza Generale",
]

select_anni = list(range(2024, 1908, -1))
select_anni.insert(0, "")


def query_dcsnprr():
    st.session_state.ricerca = st.empty()
    with st.session_state.ricerca.container():
        with st.form("dcsnprr", border=True):
            # riga 1
            row1 = row(2, vertical_align="center")
            row1.subheader(":blue[Ricerca avanzata]")

            # riga 2
            row2 = row(2, vertical_align="center")
            row2.text_input(
                label="Che contenga tutte le seguenti parole:", key="searchAllWords"
            )
            row2.text_input(
                "Che contenga una qualunque delle seguenti parole:",
                key="searchAnyWords",
            )
            # riga 3
            row3 = row(2, vertical_align="center")
            row3.text_input(
                "Che non contenga le seguenti parole:", key="searchNotWords"
            )
            row3.text_input(
                "Che contenga la seguente frase:",
                key="searchPhrase",
                value="proprietà confinante",
            )
            # row 4
            row4 = row(2, vertical_align="center")
            row4.selectbox(
                "Tipo Provvedimento:",
                tipologie_provvedimenti,
                key="tipo_provvedimento",
                index=4,
            )
            row4.selectbox(
                "Sede:",
                select_sedi,
                key="sede",
                index=26,
            )
            # riga 5
            row5 = row(2, vertical_align="center")
            row5.selectbox(
                "dall'Anno:",
                select_anni,
                key="from_year",
                index=1,
            )
            row5.selectbox(
                "all'Anno:",
                select_anni,
                key="to_year",
                index=1,
            )
            # riga 6
            row6 = row(2, vertical_align="center")
            row6.text_input("Numero Provvedimento:", key="numero_provvedimento")
            row6.selectbox(
                "Risultati per pagina:", ["20", "40", "60"], key="risultati_per_pagina"
            )

            st.form_submit_button(
                label="Cerca :mag_right:",
                type="primary",
                use_container_width=True,
                on_click=my_query,
            )


def my_query():
    # funzione interna di web scraping richiamata dalla query
    def scraping(anno):

        options = webdriver.ChromeOptions()
        # Il parametro "--headless=new" non apre Chrome: commentare in fase di debug
        # options.add_argument("--headless=new")
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=options)
        driver.get(site)

        with st.spinner(text="Ricerca documenti in corso..."):
            # Analisi del DOM tramite i DevTools di Chrome.
            # Utilizzo a scopo didattico di XPATH, NAME, ID e CSS_SELECTOR

            # Localizzazione (find_element) ed esecuzione comando (click) sull'elemento html "Ricerca Avanzata".
            driver.find_element(By.CSS_SELECTOR, "div.col-sm-3.clickable").click()

            # Localizzazione (find_element) e valorizzazione (send_keys) dei campi di ricerca.
            driver.find_element(
                By.ID, "_GaSearch_INSTANCE_2NDgCF3zWBwk_searchAllWords"
            ).send_keys(st.session_state["searchAllWords"])
            driver.find_element(
                By.ID, "_GaSearch_INSTANCE_2NDgCF3zWBwk_searchAnyWords"
            ).send_keys(st.session_state["searchAnyWords"])
            driver.find_element(
                By.ID, "_GaSearch_INSTANCE_2NDgCF3zWBwk_searchNotWords"
            ).send_keys(st.session_state["searchNotWords"])
            driver.find_element(
                By.ID, "_GaSearch_INSTANCE_2NDgCF3zWBwk_searchPhrase"
            ).send_keys(st.session_state["searchPhrase"])
            driver.find_element(
                By.XPATH,
                "//*[@id='_GaSearch_INSTANCE_2NDgCF3zWBwk_pageResultsProvvedimenti']",
            ).send_keys(st.session_state["risultati_per_pagina"])
            driver.find_element(
                By.XPATH,
                "//*[@id='_GaSearch_INSTANCE_2NDgCF3zWBwk_TipoProvvedimentoItem']",
            ).send_keys(st.session_state["tipo_provvedimento"])
            driver.find_element(
                By.NAME, "_GaSearch_INSTANCE_2NDgCF3zWBwk_sedeProvvedimenti"
            ).send_keys(st.session_state["sede"])
            driver.find_element(
                By.XPATH, "//*[@id='_GaSearch_INSTANCE_2NDgCF3zWBwk_DataYearItem2']"
            ).send_keys(anno)
            driver.find_element(
                By.XPATH,
                "//*[@id='_GaSearch_INSTANCE_2NDgCF3zWBwk_numeroProvvedimenti']",
            ).send_keys(st.session_state["numero_provvedimento"])

            # Localizzazione (find_element) ed esecuzione comando (click) sul pulsante "Cerca".
            driver.find_element(
                By.ID, "_GaSearch_INSTANCE_2NDgCF3zWBwk_submitButton"
            ).click()

            # Adozione della Waiting Strategy di Selenium. L'esecuzione dello script si arresta in attesa del risultato della query.
            # L'analisi del DOM ha portato a individuare la sezione "ricerca--item" che viene creata solo se la ricerca ha esito positivo.
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ricerca--item"))
                )
            except TimeoutException:
                print("Nessun record trovato")

            # Analisi del DOM: i link href presentano un testo tipo "202310140 (CONSIGLIO DI STATO, SEZIONE 5) html" dove è costante la stringa 'html'
            # Gli elementi/items trovati vengono individuati e salvati nella lista "decisioni".
            # '.find.element' trova la prima ricorrenza mentre '.find.elements' trova tutte le ricorrenze.
            decisioni = driver.find_elements(By.PARTIAL_LINK_TEXT, "html")
            num_decisioni = len(decisioni)

            # sono presenti anche dei link href dove è presente la stringa "DOC". Questi link sono dei doc da scaricare direttamente
            ricorsi = driver.find_elements(By.PARTIAL_LINK_TEXT, "DOC")
            num_ricorsi = len(ricorsi)

            st.session_state.total_docs = num_decisioni + num_ricorsi

        if st.session_state.total_docs == 0:
            st.success(f"Nell'anno {anno} non è stato trovato nessun ricorso")
        elif st.session_state.total_docs == 1:
            st.success(
                f"Trovato {st.session_state.total_docs} ricorso nell'anno {anno}"
            )
        else:
            st.success(
                f"Trovati {st.session_state.total_docs} ricorsi nell'anno {anno}"
            )

        if st.session_state.total_docs > 0:
            # with st.sidebar:
            st.session_state.sentenze_trovate = True

        query_parameters = {"downloadformat": "html"}
        my_index = 0

        current_dir = get_parent_directory()
        path_docs = os.path.join(current_dir, "docs\\")

        my_bar = st.progress(0)

        # iterazione sulla lista degli items trovati per l'estrapolazione del link href e relativo download del documento
        for decisione in decisioni:
            my_index += 1

            mapped_value = int(
                map_value(
                    my_index,
                    from_min=0,
                    from_max=st.session_state.total_docs,
                    to_min=0,
                    to_max=100,
                )
            )
            my_bar.progress(
                mapped_value,
                text=(
                    f"Download {my_index} di {st.session_state.total_docs} in corso..."
                ),
            )

            # creazione del documento vuoto Word e del parser di conversione
            document = Document()
            new_parser = HtmlToDocx()

            # Recupero (fetch) del valore a run time dell'attributo del DOM. In questo caso il valore dell'"href"
            url = decisione.get_attribute("href")

            # Creazione del nome del file da salvare tramite find e slice sulla stringa "url"
            nomefile = filename_retrieve(url, True)

            # In response si scarica il documento html
            response = requests.get(url, params=query_parameters)

            if response.status_code == 200:
                # Parsing dell'HTML utilizzando BeautifulSoup
                soup = BeautifulSoup(response.content, "html.parser")

                # Conversione del documento html e aggiunta al documento Word vuoto creato precedentemente
                new_parser.add_html_to_document(str(soup), document)

                file_name = f"{nomefile}_{my_index:02d}.docx"
                file_path = os.path.join(path_docs, file_name)
                # print(f"{file_name} salvato!")

                # Salvataggio del documento in formato .docx tramite la libreria 'docx'
                document.save(file_path)

        # iterazione sulla lista degli items trovati per l'estrapolazione del link href e relativo download del documento
        for ricorso in ricorsi:
            my_index += 1

            mapped_value = int(
                map_value(
                    my_index,
                    from_min=0,
                    from_max=st.session_state.total_docs,
                    to_min=0,
                    to_max=100,
                )
            )
            my_bar.progress(
                mapped_value,
                text=(
                    f"Download {my_index} di {st.session_state.total_docs} in corso..."
                ),
            )
            # Recupero (fetch) del valore a run time dell'attributo del DOM. In questo caso il valore dell'"href"
            url = ricorso.get_attribute("href")

            # Creazione del nome del file da salvare tramite find e slice sull'url
            nomefile = filename_retrieve(url, False)

            # In response si scarica il documento doc
            response = requests.get(url, params=query_parameters)

            if response.status_code == 200:
                file_name = f"{nomefile}_{my_index:02d}.doc"
                file_path = os.path.join(path_docs, file_name)

                with open(file_path, "wb") as file:
                    file.write(response.content)

        my_bar.empty()
        driver.quit()

    # chiude la form della query ed avvia lo scraping sull'intervallo anni impostato
    st.session_state.ricerca.empty()

    if st.session_state.from_year == st.session_state.to_year:
        anno = st.session_state.from_year
        scraping(anno)
    elif st.session_state.from_year > st.session_state.to_year:
        st.toast("Errore intervallo anni", icon="🚨")
    else:
        intervallo_custom = list(
            range(st.session_state.from_year, st.session_state.to_year + 1, 1)
        )
        for anno in intervallo_custom:
            scraping(anno)
