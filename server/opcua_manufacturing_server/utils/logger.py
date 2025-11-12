import logging
import sys


COLORS = {
    "DEBUG": "\033[37m",   # White
    "INFO": "\033[36m",    # Cyan
    "WARNING": "\033[33m", # Yellow
    "ERROR": "\033[31m",   # Red
    "CRITICAL": "\033[41m",# Red background
    "RESET": "\033[0m",    # Reset to default
}


class ColorFormatter(logging.Formatter):
    """Custom formatter to add colors based on log level."""
    def format(self, record):
        log_color = COLORS.get(record.levelname, COLORS["RESET"])
        message = super().format(record)
        return f"{log_color}{message}{COLORS['RESET']}"


handler = logging.StreamHandler(sys.stdout)
formatter = ColorFormatter(
    "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
)
handler.setFormatter(formatter)


logging.basicConfig(level=logging.INFO, handlers=[handler])
_logger = logging.getLogger(__name__)
