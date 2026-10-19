"""Presentation-only options shared by human-readable report writers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ThemeName = Literal["scientific", "minimal", "high-contrast"]
DetailLevel = Literal["minimal", "standard", "verbose"]

THEME_NAMES = ("scientific", "minimal", "high-contrast")
DETAIL_LEVELS = ("minimal", "standard", "verbose")


@dataclass(frozen=True, slots=True)
class RenderOptions:
    """Control report presentation without changing the underlying evidence."""

    theme: ThemeName = "scientific"
    detail: DetailLevel = "standard"

    def __post_init__(self) -> None:
        if self.theme not in THEME_NAMES:
            raise ValueError(f"Unsupported report theme: {self.theme}")
        if self.detail not in DETAIL_LEVELS:
            raise ValueError(f"Unsupported report detail level: {self.detail}")

    @property
    def evidence_limit(self) -> int | None:
        """Return the maximum evidence observations to show in a human report."""
        return {"minimal": 2, "standard": 5, "verbose": None}[self.detail]
