import os
import re
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from google.cloud import storage
from google.cloud.storage import Client, transfer_manager

load_dotenv()

BUCKET_NAME = "wedding-venues-001"


def list_files(filter=None):
    if filter is not None:
        filter = re.compile(filter, re.IGNORECASE)

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blobs = bucket.list_blobs()
    return [blob.name for blob in blobs if filter is None or filter.search(blob.name)]


def download_file(source_blob_name: str, destination_file_name: str):
    source_blob_name = Path(source_blob_name).as_posix()
    destination_file_name = Path(destination_file_name).as_posix()
    os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)
    # source_blob_name.replace("//", "/")
    source_blob_name = source_blob_name.strip("/").replace("//", "/")
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)
    return destination_file_name


def download_files(
    files: list[str], destination_files: list[str] | None = None, verbose=False
):
    client = Client()
    bucket = client.bucket(BUCKET_NAME)

    if destination_files is None:
        destination_files = files

    downloads = [
        (bucket.blob(file_name), destination_file_name)
        for file_name, destination_file_name in zip(files, destination_files)
    ]

    for _, dest_path in downloads:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    results = transfer_manager.download_many(
        downloads,
        max_workers=10,
    )
    if verbose:
        for blob_name, dest_name in zip(files, destination_files):
            print(f"downloaded {blob_name} to {dest_name}")
    return results


def upload_file(source_file_path: str, destination_blob_name: str | None = None) -> str:
    """
    Upload a single file to Google Cloud Storage.

    Parameters
    ----------
    source_file_path : str
        Local path to the file to upload
    destination_blob_name : str, optional
        Destination path in the bucket. If None, uses the source filename

    Returns
    -------
    str
        The public URL of the uploaded file
    """
    if destination_blob_name is None:
        destination_blob_name = Path(source_file_path).name

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_path)

    return blob.public_url


def upload_files(file_pairs: list[tuple[str, str]]) -> list[str]:
    """
    Upload multiple files to Google Cloud Storage in parallel.

    Parameters
    ----------
    file_pairs : list[tuple[str, str]]
        List of (source_path, destination_path) tuples

    Returns
    -------
    list[str]
        List of public URLs for the uploaded files
    """
    client = Client()
    bucket = client.bucket(BUCKET_NAME)

    # Create list of (source_file, destination_blob) tuples
    uploads = [
        (file_path, bucket.blob(dest_path)) for file_path, dest_path in file_pairs
    ]

    # Upload files in parallel
    results = transfer_manager.upload_many(
        uploads,
        max_workers=10,
    )

    # Return public URLs of uploaded files
    return [blob.public_url for _, blob in uploads]


# def upload_directory(local_directory: str, bucket_prefix: str = "") -> list[str]:
#     """
#     Upload an entire directory and its contents recursively.

#     Parameters
#     ----------
#     local_directory : str
#         Path to local directory to upload
#     bucket_prefix : str, optional
#         Prefix to add to all files in the bucket

#     Returns
#     -------
#     list[str]
#         List of public URLs for all uploaded files
#     """
#     local_dir = Path(local_directory)

#     # Get all files in directory and subdirectories
#     all_files = [
#         (str(path), os.path.join(bucket_prefix, path.relative_to(local_dir).as_posix()))
#         for path in local_dir.rglob("*")
#         if path.is_file()
#     ]

#     return upload_files(all_files)


def upload_directory(local_directory: str, bucket_prefix: str = "") -> list[str]:
    """
    Upload an entire directory and its contents recursively, skipping files that already exist.

    Parameters
    ----------
    local_directory : str
        Path to local directory to upload
    bucket_prefix : str, optional
        Prefix to add to all files in the bucket

    Returns
    -------
    list[str]
        List of public URLs for all uploaded files
    """
    local_dir = Path(local_directory)
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)

    # Get all local files
    all_files = [
        (str(path), os.path.join(bucket_prefix, path.relative_to(local_dir).as_posix()))
        for path in local_dir.rglob("*")
        if path.is_file()
    ]

    # Filter out files that already exist in the bucket
    files_to_upload = []
    for local_path, bucket_path in all_files:
        blob = bucket.blob(bucket_path.lstrip("/"))
        if not blob.exists():
            files_to_upload.append((local_path, bucket_path))
        else:
            print(f"Skipping existing file: {bucket_path}")

    if not files_to_upload:
        print("All files already exist in the bucket. Nothing to upload.")
        return []

    return upload_files(files_to_upload)


def delete_file(blob_name: str) -> bool:
    """
    Delete a file from Google Cloud Storage.

    Parameters
    ----------
    blob_name : str
        Path to the file in the bucket to delete

    Returns
    -------
    bool
        True if deletion was successful, False otherwise
    """
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(blob_name)
        blob.delete()
        return True
    except Exception as e:
        print(f"Error deleting file {blob_name}: {str(e)}")
        return False


# def download_directory(venue: str, local_path: str) -> None:
#     """
#     Downloads the adobe-extracted directory for a specific venue from Google Cloud Storage.
#     """
#     storage_client = storage.Client()
#     bucket = storage_client.bucket(BUCKET_NAME)

#     # List all files in the venue's directory
#     files = list_files(f"processed/adobe-extracted/{venue}/")

#     if not files:
#         print(f"No files found for venue {venue}")
#         return

#     downloads = [
#         (
#             bucket.blob(file_name),
#             os.path.join(
#                 local_path, file_name.split(f"processed/adobe-extracted/{venue}/")[1]
#             ),
#         )
#         for file_name in files
#     ]

#     for _, dest_path in downloads:
#         os.makedirs(os.path.dirname(dest_path), exist_ok=True)

#     results = transfer_manager.download_many(downloads, max_workers=10)
#     print(f"Downloaded {len(files)} files for {venue}")

#     return results


def download_directory(venue: str, target_dir: str, verbose: bool = False) -> List[str]:
    """
    Downloads the adobe_extracted directory for a specific venue from Google Cloud Storage
    to the current working directory.

    Parameters
    ----------
    venue : str
        Name of the venue folder to download
    target_dir : str
        ...

    Returns
    -------
    List[str]
        List of downloaded file paths
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket("wedding-venues-001")
    prefix = f"processed/adobe_extracted/{venue}/"

    print(f"Using prefix: {prefix}")
    blobs = list(bucket.list_blobs(prefix=prefix))
    # Debug
    # print(f"Retrieved blobs: {[blob.name for blob in blobs]}")

    if not blobs:
        print(f"No files found for venue: {prefix}")
        return []

    blob_names = [blob.name for blob in blobs]
    if target_dir is None:
        target_dir = "."
    target_blob_names = [
        os.path.join(target_dir, blob_name.replace(prefix, ""))
        for blob_name in blob_names
    ]
    downloaded_files = []
    download_files(blob_names, target_blob_names, verbose=verbose)
    # for blob in blobs:
    #     try:
    #         # Construct local file path
    #         local_path = os.path.join(os.getcwd(), blob.name)
    #         # print(f"Processing blob: {blob.name}")
    #         # print(f"Saving to: {local_path}")

    #         # Create necessary directories
    #         os.makedirs(os.path.dirname(local_path), exist_ok=True)

    #         # Download the file
    #         blob.download_to_filename(local_path)
    #         downloaded_files.append(local_path)

    #     except Exception as e:
    #         print(f"Error downloading {blob.name}: {str(e)}")

    print(f"Successfully downloaded {len(downloaded_files)} files for venue {venue}")
    return downloaded_files
