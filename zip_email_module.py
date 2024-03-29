from utils_module import get_files, get_parent_directory
import os
import pathlib
import zipfile
import smtplib
from email.message import EmailMessage
import streamlit as st

current_dir = get_parent_directory()
path_docs = os.path.join(current_dir, "docs")
path_abstracts = os.path.join(current_dir, "abstracts")

# zip_file_name = "abstract.zip"
zip_file_name = os.path.join(current_dir, "abstract.zip")


def send_msg():

    # files = get_files(path_docs)

    directory = pathlib.Path(path_docs)

    with zipfile.ZipFile(zip_file_name, mode="w") as archive:
        for file_path in directory.iterdir():
            archive.write(file_path, arcname=file_path.name)

    # # Create a ZipFile Object
    # zip_object = zipfile.ZipFile(zip_file_name, "w")

    # # Add multiple files to the zip file
    # for file_name in files:
    #     zip_object.write(path_docs + file_name, compress_type=zipfile.ZIP_DEFLATED)

    # # Close the Zip File
    # zip_object.close()

    # # Set up email account information (gmail)
    # email_address = "ischinella.dev@gmail.com"
    # email_password = "monp xsfs oote sqmz"
    # smtp_server = "smtps.gmail.com"
    # smtp_port = 587

    # Set up email account information (aruba)
    email_address = "yoia@ac-tech.it"
    email_password = "JurisVerse@24"
    smtp_server = "smtp.ac-tech.it"
    smtp_port = 587

    # Create email message
    msg = EmailMessage()
    msg["Subject"] = "Decisioni e pareri"
    msg["From"] = email_address
    msg["To"] = st.session_state.email

    msg.set_content(
        f"Ciao {st.session_state.username},\nin allegato troverai il file compresso contenente tutte le sentenze trovate e il file word degli abstract elaborati.\n\nCordiali saluti\nJurisVerse"
    )

    abstracts_file = os.path.join(path_abstracts, "Abstracts.docx")
    with open(abstracts_file, "rb") as f:
        file_data = f.read()
    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="Abstracts.docx",
    )

    with open(zip_file_name, "rb") as f:
        file_data = f.read()
    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="x-zip-compressed",
        filename=zip_file_name,
    )
    # Send email message
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_address, email_password)

        status = server.send_message(msg)

    return status
