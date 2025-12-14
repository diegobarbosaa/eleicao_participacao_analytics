from datetime import datetime
from typing import Any

from rich.console import Console
from rich.text import Text


class ModernLogger:
    """Logger minimalista inspirado em CLIs modernas"""

    LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "SUCCESS": 20,
    "ERROR": 40,
    "CRITICAL": 50,
    }


    ICONS = {
        "DEBUG": " 🔍 ",
        "INFO": " ℹ️ ",
        "SUCCESS": " ✓ ",
        "PROGRESS": " → ",
        "WARNING": " ⚠ ",
        "ERROR": " ✗ ",
        "CRITICAL": " 🔥 ",
    }

    COLORS = {
        "DEBUG": "dim cyan",
        "INFO": "blue",
        "SUCCESS": "green",
        "PROGRESS": "cyan",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold red",
    }

    def __init__(
        self,
        level: str = "INFO",
        show_timestamp: bool = False,
        context: dict[str, Any] | None = None,
    ):
        self.level = level.upper()
        self.show_timestamp = show_timestamp
        self.context = context or {}
        self.console = Console(stderr=False, highlight=False)

    # ===== Context handling =====
    def bind(self, **context: Any) -> "ModernLogger":
        return ModernLogger(
            level=self.level,
            show_timestamp=self.show_timestamp,
            context={**self.context, **context},
        )

    # ===== Internals =====
    def _should_log(self, level: str) -> bool:
        return self.LEVELS.get(level, self.LEVELS["INFO"]) >= self.LEVELS[self.level]

    def _format_value(self, key: str, value: Any) -> str:
        if "ano" in key.lower() and isinstance(value, int):
            return str(value)
        if isinstance(value, int) and value > 999:
            return f"{value:,}"
        if isinstance(value, float):
            return f"{value:.2f}"
        if isinstance(value, bool):
            return "✓" if value else "✗"
        return str(value)

    def _format_context(self, **context: Any) -> str:
        if not context:
            return ""
        parts = []
        for k, v in context.items():
            parts.append(f"{k}={self._format_value(k, v)}")
        return " | " + " ".join(parts)

    def _log(self, level: str, message: str, **context: Any) -> None:
        if not self._should_log(level):
            return

        text = Text()

        if self.show_timestamp:
            text.append(datetime.now().strftime("%H:%M:%S "), style="dim")

        text.append(self.ICONS[level], style=self.COLORS[level])
        text.append(message, style=self.COLORS[level] if level in {"ERROR", "CRITICAL"} else "")

        merged_context = {**self.context, **context}
        if merged_context:
            text.append(self._format_context(**merged_context), style="dim")

        self.console.print(text)

    # ===== Public API =====
    def debug(self, message: str, **context: Any) -> None:
        self._log("DEBUG", message, **context)

    def info(self, message: str, **context: Any) -> None:
        self._log("INFO", message, **context)

    def success(self, message: str, **context: Any) -> None:
        self._log("SUCCESS", message, **context)

    def progress(self, message: str, **context: Any) -> None:
        self._log("PROGRESS", message, **context)

    def warning(self, message: str, **context: Any) -> None:
        self._log("WARNING", message, **context)

    def error(self, message: str, **context: Any) -> None:
        self._log("ERROR", message, **context)

    def critical(self, message: str, **context: Any) -> None:
        self._log("CRITICAL", message, **context)