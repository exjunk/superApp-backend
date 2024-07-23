import os
import requests
from datetime import datetime
from logger import logger

def is_today(file_path):
    """Check if the file was modified today."""
    if not os.path.exists(file_path):
        return False
    file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
    today = datetime.now().date()
    return file_mod_time.date() == today

def download_file(url, dest_path):
    """Download a file from the given URL to the specified path."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        return True
    except requests.RequestException as e:
        logger.info(f"Failed to download file: {e}")
        return False

def manage_file_download(url, file_path):
    """Manage the download of a file with consideration for existing file from today."""
    temp_file_path = file_path + '.temp'

    if not is_today(file_path):
        # Rename the existing file to a temporary name if it's not from today
        if os.path.exists(file_path):
            os.rename(file_path, temp_file_path)
            logger.info(f"Renamed {file_path} to {temp_file_path}")

        # Attempt to download the new file
        if download_file(url, file_path):
            logger.info(f"Downloaded new file to {file_path}")
            # If download is successful, delete the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.info(f"Deleted temporary file {temp_file_path}")
        else:
            # If download fails, rename the temp file back to original
            if os.path.exists(temp_file_path):
                os.rename(temp_file_path, file_path)
                logger.info(f"Restored original file from {temp_file_path} to {file_path}")
    else:
        logger.info(f"File {file_path} was already downloaded today. No action taken.")

