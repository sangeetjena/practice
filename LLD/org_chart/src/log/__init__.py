import logging


def configure_logging() -> None:
    """Configure process logging for the command-line demonstration.

    Called by: src/main.py when executed as a script.
    Returns: None; configures logging handlers if not already configured.
    Example: configure_logging() enables the demo's informational operation logs.

    Additional contract:
    Configure console logging once, at application startup.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
