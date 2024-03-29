import os
import streamlit as st


# Gestione path relativi e assoluti necessaria per il deploy:
# @st.cache_resource
def get_current_path():
    return os.path.abspath(__file__)


def get_parent_directory():
    return str(os.path.dirname(get_current_path()))


def create_directory():

    current_dir = get_parent_directory()
    DOCS = os.path.join(current_dir, "docs\\")
    ABSTRACTS = os.path.join(current_dir, "abstracts\\")
    directories = [DOCS, ABSTRACTS]

    for directory in directories:
        # Verifica se la directory esiste già
        if not os.path.exists(directory):
            # Se non esiste, crea la directory
            os.makedirs(directory)
            print(f"La directory '{directory}' è stata creata.")
        else:
            print(
                f"La directory '{directory}' esiste già. Non è stata necessaria alcuna azione."
            )


def verifica_file(directory, nome_file):
    """
    Verifica se un file è presente nella directory specificata.

    Argomenti:
    directory (str): Il percorso della directory in cui cercare il file.
    nome_file (str): Il nome del file da cercare.

    Ritorna:
    bool: True se il file è presente nella directory, False altrimenti.
    """
    # Unione del percorso della directory con il nome del file
    percorso_file = os.path.join(directory, nome_file)

    # Verifica se il file esiste nella directory specificata
    if os.path.exists(percorso_file):
        return True
    else:
        return False


def get_files(directory: str) -> list:
    files = []
    if os.path.exists(directory) and os.path.isdir(directory):
        # Recupera l'elenco delle entrate (file e directory)
        entries = os.scandir(directory)
        for entry in entries:
            if entry.is_file():
                # Aggiungi il suo nome alla nostra lista
                files.append(entry.name)
    else:
        print("Error: directory doesn't exist!")

    return files


def map_value(value, from_min, from_max, to_min, to_max):
    return (value - from_min) / (from_max - from_min) * (to_max - to_min) + to_min


def filename_retrieve(url: str, htlmType: bool) -> str:
    """
    Nel'url che punta al documento si può individuare il parametro 'nomefile':
    [...]nrg=199702691&nomeFile=201506368_07.html&subDir=Provvedimenti[...] -> in caso di un documento .html
                                ^^^^^^^^^ -> len_data_numProvv
    [...]nrg=199900577&nomeFile=fi_200305087_SE.DOC&subDir=Provvedimenti...] -> in caso di un documento .doc
            len_tag -> ^^^^^^^^^=== <- 3 caratteri
    """
    tag = "nomeFile="
    len_tag = len(tag)
    len_data_numProvv = 9
    pos_nomefile = url.find(tag)
    offset = len_tag if htlmType else len_tag + 3
    start = pos_nomefile + offset
    stop = pos_nomefile + offset + len_data_numProvv
    data_num_provv = url[start:stop]

    return data_num_provv
