#!/usr/bin/env python3
"""
RRDP HISTORIAN CLI
"""

import fire
from rrdp_historian.rrdp_historian import *
from rrdp_historian.git_helpers import *
from rrdp_historian.hash_helpers import *

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def download(baseurl, rir):
    retrieve_rrdp_repository(baseurl, rir)

if __name__ == '__main__':
    fire.Fire({
        'download': download,
        'git': git,
        'hash': hash_deltas
    })