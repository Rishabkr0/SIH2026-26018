import logging
import sys
from .config import settings

def setup_logging():
    level = logging.DEBUG if settings.DEBUG else logging.INFO
    logging.basicConfig(
        stream=sys.stdout,
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Silence third-party logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    return logging.getLogger(settings.APP_NAME)

logger = setup_logging()
