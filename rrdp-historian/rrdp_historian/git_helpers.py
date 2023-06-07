"""
Git helpers for the RRDP Historian
"""
import logging
import os
import subprocess
import fire

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def git(rir, session_id, *args):
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

    subprocess.run(["git"] + list(args), cwd=session_directory, check=True)

## main
if __name__ == '__main__':
    logger.error("This is a module and it is not not intended to be run directly.")
