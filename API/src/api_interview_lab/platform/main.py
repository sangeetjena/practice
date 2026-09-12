"""SERVICE_NAME selects orders, customers or products in each process."""
import logging

from .app import create_app

logging.basicConfig(level=logging.INFO, format="%(message)s")
app = create_app()
