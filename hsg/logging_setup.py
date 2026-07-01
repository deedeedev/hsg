import logging

LOG_LEVELS: dict[str, int] = {
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
}


def configure_logging(level: str = 'warning') -> None:
    """Configure root logger with the given level name."""
    logging.basicConfig(
        level=LOG_LEVELS.get(level, logging.WARNING),
        format='%(levelname)s: %(message)s',
    )


def get_logger(name: str) -> logging.Logger:
    """Return a logger for the given module name."""
    return logging.getLogger(name)
