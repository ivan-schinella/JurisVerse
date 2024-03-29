from authentication_module import login_form, logout, get_manager
from utils_module import create_directory
from form_module import query_dcsnprr
from query_module import interroga
from zip_email_module import send_msg
import streamlit as st

cookie_manager = get_manager()


if "directories_exist" not in st.session_state:
    st.session_state.directories_exist = False

if not st.session_state.directories_exist:
    create_directory()
    st.session_state.directories_exist = True

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    # il parametro "allow_create" attiva il tab necessario a creare un nuovo account
    login_dcsnprr = login_form(cookie_manager, allow_guest=False, allow_create=False)

if "sentenze_trovate" not in st.session_state:
    st.session_state.sentenze_trovate = False

if "total_docs" not in st.session_state:
    st.session_state.total_docs = 0

if "abstract_creati" not in st.session_state:
    st.session_state.abstract_creati = False

if "query_button" not in st.session_state:
    st.session_state.query_button = None

if "auto_send_email" not in st.session_state:
    st.session_state.auto_send_email = True

if "email_sent" not in st.session_state:
    st.session_state.email_sent = False


if st.session_state["authenticated"]:
    with st.sidebar:
        st.header("Giustizia Amministrativa")
        st.subheader("Decisioni e Pareri", divider="grey")
        st.text("Utente: " + st.session_state["username"])
        if st.button(
            "Logout",
            type="primary",
            use_container_width=False,
        ):
            logout(cookie_manager)

        st.session_state.auto_send_email = st.toggle(
            "Invio automatico email abstract",
            value=True,
        )

        if st.session_state.sentenze_trovate:
            st.divider()
            st.subheader("Interroga i documenti trovati")
            st.session_state.query_button = st.button(
                label=f"Query su **{st.session_state.total_docs} sentenze**",
                type="secondary",
                use_container_width=True,
            )

        if st.session_state.abstract_creati:
            st.divider()
            st.subheader("Invia gli abstract creati")
            send_mail_button = st.button(
                "Invia",
                type="primary",
                use_container_width=False,
            )
            if send_mail_button:
                with st.spinner("Preparazione ed invio email..."):
                    send_msg()
                st.info("Email inviata!")

    if st.session_state.query_button:
        st.session_state.ricerca.empty()
        st.session_state.email_sent = False
        interroga()

    if not st.session_state.query_button:
        query_dcsnprr()
