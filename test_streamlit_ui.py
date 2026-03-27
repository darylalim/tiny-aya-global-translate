from unittest.mock import MagicMock, patch

import pytest
import torch
from streamlit.testing.v1 import AppTest


@pytest.fixture
def app() -> AppTest:
    """Create a patched AppTest instance with mocked model loading."""
    mock_tokenizer = MagicMock()
    mock_model = MagicMock()

    with (
        patch(
            "streamlit_app.load_model",
            return_value=(mock_tokenizer, mock_model, "cpu", torch.float32),
        ),
        patch("streamlit_app.translate_text", return_value="Bonjour"),
        patch("streamlit_app.summarize_text", return_value="A brief summary."),
    ):
        at = AppTest.from_file("streamlit_app.py")
        at.run(timeout=60)
    return at


# -- Caption ------------------------------------------------------------------


def test_caption_contains_powered_by(app: AppTest) -> None:
    captions = [c.value for c in app.caption]
    assert any("Powered by" in c for c in captions)


def test_caption_contains_language_count(app: AppTest) -> None:
    captions = [c.value for c in app.caption]
    assert any("43 languages" in c for c in captions)
