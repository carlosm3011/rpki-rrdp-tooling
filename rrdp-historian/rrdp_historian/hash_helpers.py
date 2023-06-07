"""
Hashing
(c) Carlos M. Martinez
"""

import os
import hashlib
import fire
import logging
from rrdp_historian.git_helpers import *

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def hash_deltas(rir, session_id):
    rir_directory = rir

    session_ids = [name for name in os.listdir(rir_directory) if os.path.isdir(os.path.join(rir_directory, name))]

    # print(session_ids)

    if str(session_id) == "0":
        if session_ids:
            session_id = session_ids[0]
        else:
            raise ValueError("No session IDs found in the specified RIR directory.")
        
    if session_id not in session_ids:
        print(f"Invalid session ID {session_id}. Please provide a valid session ID.")
        raise ValueError(f"Invalid session ID {session_id}. Please provide a valid session ID.")

    session_directory = os.path.join(rir_directory, session_id)

    hashes = {}
    for root, _, files in os.walk(session_directory):
        for file in files:
            if file.endswith(".xml") and file.startswith("delta"):
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as f:
                    content = f.read()
                    file_hash = hashlib.sha256(content).hexdigest()
                    hashes[file_path] = file_hash
                    logger.info(f"File {file} has sha256 {file_hash}")

    output_file = f"{session_directory}/{session_id}-hashes.txt"
    with open(output_file, 'w') as f:
        sorted_hashes = sorted(hashes.items(), key=lambda x: x[0])
        for file_path, file_hash in sorted_hashes:
            f.write(f"{file_path}: {file_hash}\n")

    # output_file = f"{session_id}.txt"

    logger.info(f"Hashes have been written to {output_file}.")

    # commit el archivo de hashes

    # git(rir, session_id, "commit", "-a", "-m", "committing_file_hashes", f"{session_id}-hashes.txt")
    git(rir, session_id, "commit", "-a", "-m", "committing_file_hashes")
    logger.info(f"File with hashes has been committed to git repo.")

# end def

## main
if __name__ == '__main__':
    logging.error("This is a module and it is not not intended to be run directly.")
