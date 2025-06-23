"""Simple logger implementation for connectchain."""


class Logger:
    """Simple logger that prints messages."""

    def debug(self, message: str) -> None:
        """Log debug message."""
        print(f"DEBUG: {message}")

    def info(self, message: str) -> None:
        """Log info message."""
        print(f"INFO: {message}")

    def warning(self, message: str) -> None:
        """Log warning message."""
        print(f"WARNING: {message}")

    def error(self, message: str) -> None:
        """Log error message."""
        print(f"ERROR: {message}")
