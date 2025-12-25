import logging
import os
from datetime import datetime

#Creating logs directory
LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

#Log file name (one per day)
LOG_FILE = f"rag_app_{datetime.now().strftime('%Y_%m_%d')}.log"
LOG_FILEPATH = os.path.join(LOG_DIR, LOG_FILE)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILEPATH),
        logging.StreamHandler()
    ]
)

#Creating logger instance
logger = logging.getLogger("PolicyRAG")
