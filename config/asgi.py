import os
import sys

from src.common.utils import get_logger

logger = get_logger(__name__)

logger.info("Loading ASGI application...")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(os.path.join(BASE_DIR, "src"))

logger.info(f"Adding {os.path.join(BASE_DIR, 'src')} to sys.path")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

logger.info("Setting DJANGO_SETTINGS_MODULE to config.settings")

from django.core.asgi import get_asgi_application  # noqa: E402

application = get_asgi_application()

logger.info("ASGI application loaded successfully.")
