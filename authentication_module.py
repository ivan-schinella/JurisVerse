import os
import time
import streamlit as st
import extra_streamlit_components as stx
import bcrypt
from supabase import Client, create_client


s_url = os.environ["SUPABASE_URL"]
s_key = os.environ["SUPABASE_KEY"]

# User Authentication
if "username" not in st.session_state:
    st.session_state["username"] = None

if "email" not in st.session_state:
    st.session_state["email"] = None

if "password" not in st.session_state:
    st.session_state["password"] = None

if "cookie_username" not in st.session_state:
    st.session_state["cookie_username"] = None

if "cookie_email" not in st.session_state:
    st.session_state["cookie_email"] = None

if "cookie_password" not in st.session_state:
    st.session_state["cookie_password"] = None


@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()


@st.cache_resource
def init_connection() -> Client:
    try:
        return create_client(supabase_url=s_url, supabase_key=s_key)
    except KeyError:
        return create_client(s_url, s_key)
    # try:
    #     return create_client(
    #         st.secrets["connections"]["supabase"]["SUPABASE_URL"],
    #         st.secrets["connections"]["supabase"]["SUPABASE_KEY"],
    #     )
    # except KeyError:
    #     return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def encrypt_pwd(password: str):
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    string_password = hashed_password.decode("utf8")
    return string_password


def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode("utf-8")
    hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_byte_enc, hashed_password)


def save_cookies(cookie_manager, username, email, password):
    cookie_manager.set("username", username, key="1")
    time.sleep(0.2)
    cookie_manager.set("email", email, key="2")
    time.sleep(0.2)
    cookie_manager.set("password", password, key="3")
    time.sleep(0.2)


def load_cookies(cookie_manager):
    st.session_state["cookie_username"] = cookie_manager.get(cookie="username")
    st.session_state["cookie_email"] = cookie_manager.get(cookie="email")
    st.session_state["cookie_password"] = cookie_manager.get(cookie="password")

    return (
        st.session_state["cookie_username"],
        st.session_state["cookie_email"],
        st.session_state["cookie_password"],
    )


def logout(cookie_manager):
    cookie_manager.delete("username")
    st.session_state["authenticated"] = False


def login_success(message: str, username: str, email: str, password: str) -> None:
    st.toast(message)
    st.session_state["authenticated"] = True
    st.session_state["username"] = username
    st.session_state["password"] = password
    st.session_state["email"] = email


# Create the python function that will be called
def login_form(
    cookie_manager,
    title: str = "Authentication",
    user_tablename: str = "users",
    username_col: str = "username",
    email_col: str = "email",
    password_col: str = "password",
    allow_create: bool = True,
    create_title: str = "Crea un nuovo account",
    login_title: str = "Login in un account esistente",
    allow_guest: bool = True,
    guest_title: str = "Guest login",
    create_username_label: str = "Creare uno username univoco",
    create_username_placeholder: str = None,
    create_username_help: str = None,
    create_email_label: str = "Immettere una email valida",
    create_email_placeholder: str = None,
    create_email_help: str = None,
    create_password_label: str = "Crea una password",
    create_password_placeholder: str = None,
    create_password_help: str = "⚠️ Password will be stored as plain text. Do not reuse from other websites. Password cannot be recovered.",
    create_submit_label: str = "Creazione account",
    create_success_message: str = "Account creato",
    login_username_label: str = "Immetti il tuo username",
    login_username_placeholder: str = None,
    login_username_help: str = None,
    login_password_label: str = "Immetti la tua password",
    login_password_placeholder: str = None,
    login_password_help: str = None,
    info_title: str = "Informazioni",
    login_submit_label: str = "Login",
    login_success_message: str = "Login effettuato!",
    login_user_error_message: str = "Username errato:x: ",
    login_password_error_message: str = "Password errata:x: ",
    guest_submit_label: str = "Guest login",
) -> Client:
    """Creates a user login form in Streamlit apps.

    Connects to a Supabase DB using `SUPABASE_URL` and `SUPABASE_KEY` Streamlit secrets.
    Sets `session_state["authenticated"]` to True if the login is successful.
    Sets `session_state["username"]` to provided username or new or existing user, and to `None` for guest login.

    Returns:
    Supabase client instance
    """

    # Initialize supabase connection
    client = init_connection()

    (
        st.session_state["cookie_username"],
        st.session_state["cookie_email"],
        st.session_state["cookie_password"],
    ) = load_cookies(cookie_manager)

    if (
        st.session_state["cookie_username"] is None
        or st.session_state["cookie_email"] is None
        or st.session_state["cookie_password"] is None
    ):

        credential = st.empty()

        with credential.container():
            st.write(title)

            if allow_guest and allow_create:
                login_tab, create_tab, guest_tab, info_tab = st.tabs(
                    [
                        login_title,
                        create_title,
                        guest_title,
                        info_title,
                    ]
                )
            elif not allow_guest and allow_create:
                login_tab, create_tab, info_tab = st.tabs(
                    [
                        login_title,
                        create_title,
                        info_title,
                    ]
                )
            else:
                login_tab, info_tab = st.tabs(
                    [
                        login_title,
                        info_title,
                    ]
                )

            # Create new account
            if allow_create:
                with create_tab:
                    with st.form(key="create"):
                        username = st.text_input(
                            label=create_username_label,
                            placeholder=create_username_placeholder,
                            help=create_username_help,
                            disabled=st.session_state["authenticated"],
                        )

                        email = st.text_input(
                            label=create_email_label,
                            placeholder=create_email_placeholder,
                            help=create_email_help,
                            disabled=st.session_state["authenticated"],
                        )

                        pwd = st.text_input(
                            label=create_password_label,
                            placeholder=create_password_placeholder,
                            help=create_password_help,
                            type="password",
                            disabled=st.session_state["authenticated"],
                        )

                        if st.form_submit_button(
                            label=create_submit_label,
                            type="primary",
                            disabled=st.session_state["authenticated"],
                        ):
                            password = encrypt_pwd(pwd)
                            try:
                                data, _ = (
                                    client.table(user_tablename)
                                    .insert(
                                        {
                                            username_col: username,
                                            email_col: email,
                                            password_col: password,
                                        }
                                    )
                                    .execute()
                                )
                            except Exception as e:
                                st.error(e.message)
                            else:
                                save_cookies(cookie_manager, username, email, password)
                                login_success(
                                    create_success_message, username, email, password
                                )

            # Login to existing account
            with login_tab:
                with st.form(key="login"):
                    username = st.text_input(
                        label=login_username_label,
                        placeholder=login_username_placeholder,
                        help=login_username_help,
                        # disabled=st.session_state["authenticated"],
                    )

                    pwd = st.text_input(
                        label=login_password_label,
                        placeholder=login_password_placeholder,
                        help=login_password_help,
                        type="password",
                        # disabled=st.session_state["authenticated"],
                    )

                    if st.form_submit_button(
                        label=login_submit_label,
                        # disabled=st.session_state["authenticated"],
                        type="primary",
                    ):
                        data, _ = (
                            client.table(user_tablename)
                            .select(f"{username_col}, {email_col}, {password_col}")
                            .eq(username_col, username)
                            # .eq(password_col, password)
                            .execute()
                        )

                        if len(data[-1]) > 0:
                            # ('data', [{'username': 'ivansc', 'email': 'ivan.schinella@gmail.com', 'password': 'abcd'}])
                            user_data = data[1]
                            user = user_data[0]
                            email = user["email"]
                            password = user["password"]

                            if verify_password(pwd, password):
                                save_cookies(cookie_manager, username, email, password)
                                login_success(
                                    login_success_message, username, email, password
                                )
                            else:
                                st.error(login_password_error_message)
                        else:
                            st.error(login_user_error_message)

            # Guest login
            if allow_guest:
                with guest_tab:
                    if st.button(
                        label=guest_submit_label,
                        type="primary",
                        disabled=st.session_state["authenticated"],
                    ):
                        st.session_state["authenticated"] = True

            # Information
            with info_tab:
                st.write("Work in progress...")

        if st.session_state["authenticated"]:
            credential.empty()

    else:

        login_success(
            login_success_message,
            st.session_state["cookie_username"],
            st.session_state["cookie_email"],
            st.session_state["cookie_password"],
        )

    return
