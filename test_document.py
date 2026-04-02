from __future__ import annotations

import io

from docx import Document
from pptx import Presentation
from pptx.util import Inches

from document import (
    extract_segments_docx,
    extract_segments_pptx,
    rebuild_document_docx,
    rebuild_document_pptx,
)


def _make_docx(paragraphs: list[str]) -> bytes:
    """Create a minimal DOCX with the given paragraph texts."""
    doc = Document()
    for text in paragraphs:
        doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _make_docx_with_table(paragraphs: list[str], table_rows: list[list[str]]) -> bytes:
    """Create a DOCX with body paragraphs and a table."""
    doc = Document()
    for text in paragraphs:
        doc.add_paragraph(text)
    table = doc.add_table(rows=len(table_rows), cols=len(table_rows[0]))
    for i, row_data in enumerate(table_rows):
        for j, cell_text in enumerate(row_data):
            table.rows[i].cells[j].text = cell_text
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _make_pptx(texts: list[str]) -> bytes:
    """Create a minimal PPTX with one slide and one textbox per text."""
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank layout
    for i, text in enumerate(texts):
        txBox = slide.shapes.add_textbox(
            Inches(1), Inches(0.5 + i * 1.5), Inches(5), Inches(1)
        )
        txBox.text_frame.paragraphs[0].text = text
    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue()


# -- extract_segments_docx -----------------------------------------------------


def test_extract_docx_returns_paragraph_texts() -> None:
    file_bytes = _make_docx(["Hello", "World"])
    segments = extract_segments_docx(file_bytes)
    assert segments == ["Hello", "World"]


def test_extract_docx_includes_empty_paragraphs() -> None:
    file_bytes = _make_docx(["Hello", "", "World"])
    segments = extract_segments_docx(file_bytes)
    assert segments == ["Hello", "", "World"]


def test_extract_docx_includes_table_text() -> None:
    file_bytes = _make_docx_with_table(["Intro"], [["Cell A", "Cell B"]])
    segments = extract_segments_docx(file_bytes)
    assert "Intro" in segments
    assert "Cell A" in segments
    assert "Cell B" in segments


# -- rebuild_document_docx -----------------------------------------------------


def test_rebuild_docx_replaces_text() -> None:
    file_bytes = _make_docx(["Hello", "World"])
    rebuilt = rebuild_document_docx(file_bytes, ["Bonjour", "Monde"])
    segments = extract_segments_docx(rebuilt)
    assert segments == ["Bonjour", "Monde"]


def test_rebuild_docx_round_trip() -> None:
    original = ["Hello", "World"]
    file_bytes = _make_docx(original)
    segments = extract_segments_docx(file_bytes)
    rebuilt = rebuild_document_docx(file_bytes, segments)
    result = extract_segments_docx(rebuilt)
    assert result == original


# -- extract_segments_pptx -----------------------------------------------------


def test_extract_pptx_returns_paragraph_texts() -> None:
    file_bytes = _make_pptx(["Hello", "World"])
    segments = extract_segments_pptx(file_bytes)
    assert segments == ["Hello", "World"]


def test_extract_pptx_includes_empty_paragraphs() -> None:
    file_bytes = _make_pptx(["Hello", "", "World"])
    segments = extract_segments_pptx(file_bytes)
    assert segments == ["Hello", "", "World"]


# -- rebuild_document_pptx -----------------------------------------------------


def test_rebuild_pptx_replaces_text() -> None:
    file_bytes = _make_pptx(["Hello", "World"])
    rebuilt = rebuild_document_pptx(file_bytes, ["Bonjour", "Monde"])
    segments = extract_segments_pptx(rebuilt)
    assert segments == ["Bonjour", "Monde"]


def test_rebuild_pptx_round_trip() -> None:
    original = ["Hello", "World"]
    file_bytes = _make_pptx(original)
    segments = extract_segments_pptx(file_bytes)
    rebuilt = rebuild_document_pptx(file_bytes, segments)
    result = extract_segments_pptx(rebuilt)
    assert result == original
