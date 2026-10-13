"""Refresh worker entry point (FR-039, FR-040).

POST /api/refresh starts this file as a subprocess after taking the refresh lock. It runs one
refresh and always clears the running flag at the end. Run from modules/api:
    python refresh_worker.py
"""

import sys

from app.services.refresh import worker_main

if __name__ == "__main__":
    sys.exit(worker_main())
