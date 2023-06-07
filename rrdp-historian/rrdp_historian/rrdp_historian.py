"""
# RRDP Historian
(c) CarlosM and chatgpt, 20230606

"""

import os
import logging
import requests
import xml.etree.ElementTree as ET
import subprocess
import fire
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_file(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        file_content = response.content
        logger.info("Downloaded %s", url)
        return file_content
    except requests.exceptions.RequestException as e:
        logger.error("Failed to download %s: %s", url, str(e))
        return None

def save_file(content, filepath):
    try:
        with open(filepath, 'wb') as file:
            file.write(content)
        logger.info("Saved %s", filepath)
    except IOError as e:
        logger.error("Failed to save %s: %s", filepath, str(e))

def create_directory(directory):
    os.makedirs(directory, exist_ok=True)
    logger.info("Created directory %s", directory)

def process_notification(notification_xml):
    try:
        root = ET.fromstring(notification_xml)
        session_id = root.attrib.get('session_id')
        serial = int(root.attrib.get('serial'))
        logger.info("Session ID: %s", session_id)
        return session_id, serial, root.findall('.//{http://www.ripe.net/rpki/rrdp}delta')
    except ET.ParseError as e:
        logger.error("Failed to parse notification.xml: %s", str(e))
        return None, None, []

def initialize_git_repository(directory):
    subprocess.run(["git", "init"], cwd=directory, check=True)
    logger.info("Initialized Git repository at %s", directory)

def git_add_commit(directory, highest_serial, num_changed_files):
    commit_message = f"Automatic commit\n\nHighest Serial: {highest_serial}\nNumber of Changed Files: {num_changed_files}"
    subprocess.run(["git", "add", "."], cwd=directory, check=True)
    try:
        subprocess.run(["git", "diff", "--cached", "--exit-code"], cwd=directory, check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["git", "commit", "-a", "-m", commit_message], cwd=directory, check=True)
        logger.info("Committed changes to Git repository at %s", directory)
    else:
        logger.info("No changes to commit in Git repository at %s", directory)

def store_highest_serial(session_directory, highest_serial):
    serial_file_path = os.path.join(session_directory, 'highest_serial.txt')
    timestamp = datetime.now().isoformat()
    with open(serial_file_path, 'a') as serial_file:
        serial_file.write(f"{highest_serial} {timestamp}\n")
    logger.info("Stored highest serial in %s", serial_file_path)

def delta_content_changed(delta_content, delta_file_path):
    if os.path.exists(delta_file_path):
        with open(delta_file_path, 'rb') as file:
            previous_content = file.read()
        if delta_content != previous_content:
            logger.info("File %s has changed", delta_file_path)
            return True
        else:
            logger.info("File %s is the same", delta_file_path)
            return False
    else:
        # si el archivo no existe entonces efectivamente "cambió"
        logger.info("File %s is not on disk", delta_file_path)
        return True
    


def retrieve_rrdp_repository(baseurl, rir):
    # Download notification.xml file
    notification_url = baseurl
    notification_content = download_file(notification_url)
    if not notification_content:
        return

    # Parse notification.xml
    session_id, serial, delta_elements = process_notification(notification_content)
    if not session_id or serial is None:
        return

    # Create session directory
    session_directory = os.path.join(rir, session_id)
    create_directory(session_directory)

    # Save notification.xml
    notification_file_path = os.path.join(session_directory, 'notification.xml')
    save_file(notification_content, notification_file_path)

    # Initialize Git repository if not already initialized
    git_directory = os.path.join(session_directory, '.git')
    if not os.path.exists(git_directory):
        initialize_git_repository(session_directory)

    # Keep track of the highest serial and the number of changed files
    highest_serial_seen = 0
    num_changed_files = 0

    # Iterate through delta elements
    for delta in delta_elements:
        delta_serial = int(delta.attrib.get('serial'))
        delta_uri = delta.attrib.get('uri')
        delta_filename = f"delta_{delta_serial}.xml"
        delta_file_path = os.path.join(session_directory, delta_filename)

        logger.info("Downloading delta XML from: %s", delta_uri)

        # Download delta.xml file
        delta_content = download_file(delta_uri)
        if not delta_content:
            continue

        # Check if delta content has changed
        if delta_content_changed(delta_content, delta_file_path):
            # Save delta.xml file
            save_file(delta_content, delta_file_path)
            num_changed_files += 1

        # Update the highest serial seen
        if delta_serial > highest_serial_seen:
            highest_serial_seen = delta_serial

    # Add and commit changes to Git repository
    git_add_commit(session_directory, highest_serial_seen, num_changed_files)

    # Store the highest serial
    store_highest_serial(session_directory, highest_serial_seen)

    logger.info("Repository retrieval completed.")

if __name__ == '__main__':
    logger.error("This is a module and it is not not intended to be run directly.")
