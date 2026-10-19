"""Centralized ReportLab styles and palettes for BioRobust PDFs."""

from __future__ import annotations

import html
from dataclasses import dataclass
from typing import Any

from .report_options import RenderOptions


STATUS_LABELS = {
    "pass": "PASS",
    "fail": "FAIL",
    "unknown": "UNKNOWN",
    "manual_review": "MANUAL REVIEW",
    "not_applicable": "NOT APPLICABLE",
}


@dataclass(frozen=True, slots=True)
class ThemePalette:
    name: str
    page_background: str
    heading: str
    body: str
    muted: str
    accent: str
    border: str
    panel: str
    status_backgrounds: tuple[tuple[str, str], ...]
    status_foregrounds: tuple[tuple[str, str], ...]

    def status_background(self, status: str) -> str:
        return dict(self.status_backgrounds).get(status, self.panel)

    def status_foreground(self, status: str) -> str:
        return dict(self.status_foregrounds).get(status, self.body)


THEME_PALETTES = {
    "scientific": ThemePalette(
        name="scientific",
        page_background="#FFFFFF",
        heading="#143642",
        body="#17202A",
        muted="#53636D",
        accent="#2A7F8E",
        border="#C9D4DA",
        panel="#F5F8F9",
        status_backgrounds=(
            ("pass", "#D1E7DD"),
            ("fail", "#F8D7DA"),
            ("unknown", "#FFF3CD"),
            ("manual_review", "#FFF3CD"),
            ("not_applicable", "#E2E3E5"),
        ),
        status_foregrounds=(
            ("pass", "#0F5132"),
            ("fail", "#842029"),
            ("unknown", "#664D03"),
            ("manual_review", "#664D03"),
            ("not_applicable", "#41464B"),
        ),
    ),
    "minimal": ThemePalette(
        name="minimal",
        page_background="#FFFFFF",
        heading="#111111",
        body="#202020",
        muted="#555555",
        accent="#222222",
        border="#777777",
        panel="#F7F7F7",
        status_backgrounds=tuple((status, "#FFFFFF") for status in STATUS_LABELS),
        status_foregrounds=tuple((status, "#111111") for status in STATUS_LABELS),
    ),
    "high-contrast": ThemePalette(
        name="high-contrast",
        page_background="#FFFFFF",
        heading="#000000",
        body="#000000",
        muted="#222222",
        accent="#000000",
        border="#000000",
        panel="#FFFFFF",
        status_backgrounds=tuple((status, "#FFFFFF") for status in STATUS_LABELS),
        status_foregrounds=tuple((status, "#000000") for status in STATUS_LABELS),
    ),
}


@dataclass(frozen=True, slots=True)
class PDFStyles:
    palette: ThemePalette
    title: Any
    meta: Any
    section: Any
    finding_header: Any
    body: Any
    secondary: Any
    footer: Any


def palette_for(theme: str) -> ThemePalette:
    """Return the validated palette for a requested theme."""
    RenderOptions(theme=theme)  # validates values at this boundary
    return THEME_PALETTES[theme]


def status_label(status: str) -> str:
    return STATUS_LABELS.get(status, status.replace("_", " ").upper())


def _pdf_escape(value: object) -> str:
    """Escape ReportLab paragraph text while keeping built-in fonts portable."""
    text = str(value).replace("—", "-").replace("–", "-")
    return html.escape(text)


def make_pdf_styles(options: RenderOptions) -> PDFStyles:
    """Create readable styles for the selected presentation theme."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

    palette = palette_for(options.theme)
    base = getSampleStyleSheet()
    return PDFStyles(
        palette=palette,
        title=ParagraphStyle(
            "BioRobustTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=25,
            textColor=colors.HexColor(palette.heading),
            alignment=TA_LEFT,
            spaceAfter=6,
        ),
        meta=ParagraphStyle(
            "BioRobustMeta",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.7,
            leading=11,
            textColor=colors.HexColor(palette.muted),
            spaceAfter=2,
        ),
        section=ParagraphStyle(
            "BioRobustSection",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=17,
            textColor=colors.HexColor(palette.heading),
            spaceBefore=9,
            spaceAfter=6,
        ),
        finding_header=ParagraphStyle(
            "BioRobustFindingHeader",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=14,
            textColor=colors.HexColor(palette.heading),
            spaceAfter=2,
        ),
        body=ParagraphStyle(
            "BioRobustBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.7,
            leading=12.2,
            textColor=colors.HexColor(palette.body),
            spaceAfter=3,
        ),
        secondary=ParagraphStyle(
            "BioRobustSecondary",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.6,
            leading=10.7,
            textColor=colors.HexColor(palette.muted),
            spaceAfter=3,
        ),
        footer=ParagraphStyle(
            "BioRobustFooter",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=9.5,
            textColor=colors.HexColor(palette.muted),
        ),
    )
