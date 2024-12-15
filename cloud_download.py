import os

import streamlit as st
from dotenv import load_dotenv
from google.cloud import storage

load_dotenv()


def list_files(bucket_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    return [blob.name for blob in blobs]


def download_file(bucket_name, source_blob_name, destination_file_name):
    os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)
    return destination_file_name


bucket_name = "wedding-venues-001"

st.title("File Downloader")

files = list_files(bucket_name)
st.write("Available Files:")
selected_file = st.selectbox("Choose a file to download:", files)

if st.button("Download"):
    download_path = f"./{selected_file}"
    download_file(bucket_name, selected_file, download_path)
    st.success(f"Downloaded {selected_file}")
    with open(download_path, "rb") as f:
        st.download_button(label="Download File", data=f, file_name=selected_file)
