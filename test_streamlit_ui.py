from unittest.mock import MagicMock, patch

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def app() -> AppTest:
    """Create a patched AppTest instance with mocked model loading.

    AppTest runs the script via exec() in the same process, so patches must
    target the upstream source of the objects the script imports.  load_model()
    does ``from transformers import AutoModelForCausalLM, AutoTokenizer``
    inside its body, so patching those names on the real ``transformers``
    module (approach 3) intercepts the call before any file I/O or network
    access occurs.
    """
    mock_tokenizer = MagicMock()
    mock_model = MagicMock()
    mock_model.device = "cpu"

    with (
        patch(
            "transformers.AutoTokenizer.from_pretrained",
            return_value=mock_tokenizer,
        ),
        patch(
            "transformers.AutoModelForCausalLM.from_pretrained",
            return_value=mock_model,
        ),
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


# -- Translate tab: structure -------------------------------------------------


def test_translate_tab_has_choose_languages_label(app: AppTest) -> None:
    tab = app.tabs[0]
    markdown_values = [m.value for m in tab.markdown]
    assert any("① Choose languages" in v for v in markdown_values)


def test_translate_tab_has_enter_text_label(app: AppTest) -> None:
    tab = app.tabs[0]
    markdown_values = [m.value for m in tab.markdown]
    assert any("② Enter text" in v for v in markdown_values)


def test_translate_tab_has_divider(app: AppTest) -> None:
    tab = app.tabs[0]
    assert len(tab.divider) >= 1


def test_translate_tab_source_language_default(app: AppTest) -> None:
    tab = app.tabs[0]
    source_select = tab.selectbox[0]
    assert source_select.value == "English"


def test_translate_tab_target_language_default(app: AppTest) -> None:
    tab = app.tabs[0]
    target_select = tab.selectbox[1]
    assert target_select.value == "French"


def test_translate_tab_text_area_placeholder(app: AppTest) -> None:
    tab = app.tabs[0]
    text_area = tab.text_area[0]
    assert text_area.placeholder == "e.g. The weather is nice today"


def test_translate_tab_button_exists(app: AppTest) -> None:
    tab = app.tabs[0]
    assert tab.button[0].label == "Translate"
