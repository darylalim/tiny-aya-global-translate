# Compact UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Simplify the Streamlit UI by removing region radios, step labels, dividers, and the summary length selector to create a compact, clutter-free experience.

**Architecture:** Replace the guided three-step flow with a minimal layout — inline language pickers for Translate, single dropdown for Summarize, auto-determined summary length. All pure functions stay intact; only UI code and tests change.

**Tech Stack:** Python 3.12+, Streamlit, pytest

---

### Task 1: Add `select_summary_length` pure function

**Files:**
- Modify: `streamlit_app.py:171-180` (insert after `get_summary_config`)
- Modify: `test_streamlit_app.py:209` (insert after `get_summary_config` tests)

- [ ] **Step 1: Write failing tests**

Add to `test_streamlit_app.py` after the `test_get_summary_config_invalid_raises` test (line 208), and add `select_summary_length` to the import block:

```python
# In the import block at top, add select_summary_length:
from streamlit_app import (
    LANGUAGE_GROUPS,
    LANGUAGES,
    build_summarization_prompt,
    build_translation_prompt,
    clean_model_output,
    detect_device,
    get_summary_config,
    select_dtype,
    select_summary_length,
    summarize_text,
    translate_text,
)


# -- select_summary_length -----------------------------------------------------


def test_select_summary_length_short() -> None:
    assert select_summary_length("Hello") == "Short"


def test_select_summary_length_short_boundary() -> None:
    assert select_summary_length("x" * 499) == "Short"


def test_select_summary_length_medium_boundary() -> None:
    assert select_summary_length("x" * 500) == "Medium"


def test_select_summary_length_medium() -> None:
    assert select_summary_length("x" * 1000) == "Medium"


def test_select_summary_length_medium_upper_boundary() -> None:
    assert select_summary_length("x" * 2000) == "Medium"


def test_select_summary_length_long_boundary() -> None:
    assert select_summary_length("x" * 2001) == "Long"


def test_select_summary_length_long() -> None:
    assert select_summary_length("x" * 5000) == "Long"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest test_streamlit_app.py -k "select_summary_length" -v`
Expected: FAIL with `ImportError: cannot import name 'select_summary_length'`

- [ ] **Step 3: Write implementation**

Add to `streamlit_app.py` after `get_summary_config` (after line 180):

```python
def select_summary_length(text: str) -> str:
    """Select summary length based on input text size."""
    if len(text) > 2000:
        return "Long"
    if len(text) >= 500:
        return "Medium"
    return "Short"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest test_streamlit_app.py -k "select_summary_length" -v`
Expected: 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add streamlit_app.py test_streamlit_app.py
git commit -m "feat: add select_summary_length pure function"
```

---

### Task 2: Simplify page header

**Files:**
- Modify: `streamlit_app.py:282-297` (page header section)
- Modify: `test_streamlit_ui.py:106-116` (caption tests)

- [ ] **Step 1: Remove caption tests from `test_streamlit_ui.py`**

Delete the entire `# -- Caption` section (lines 106-116):

```python
# -- Caption ------------------------------------------------------------------


def test_caption_contains_powered_by(app: AppTest) -> None:
    captions = [c.value for c in app.caption]
    assert any("Powered by" in c for c in captions)


def test_caption_contains_language_count(app: AppTest) -> None:
    captions = [c.value for c in app.caption]
    assert any("43 European and Asia-Pacific languages" in c for c in captions)
```

- [ ] **Step 2: Remove caption from `streamlit_app.py`**

In `streamlit_app.py`, remove lines 293-297 (the `model_url` and `st.caption` inside the try block):

```python
    model_url = "https://huggingface.co/CohereLabs/tiny-aya-water"
    st.caption(
        f"Powered by [tiny-aya-water]({model_url}) · Supports 43 European and "
        f"Asia-Pacific languages"
    )
```

Keep `model_loaded = True` — just delete the two lines above it.

- [ ] **Step 3: Run tests to verify they pass**

Run: `uv run pytest test_streamlit_ui.py -v`
Expected: All remaining UI tests PASS

- [ ] **Step 4: Commit**

```bash
git add streamlit_app.py test_streamlit_ui.py
git commit -m "feat: remove caption from page header"
```

---

### Task 3: Simplify translate tab

**Files:**
- Modify: `streamlit_app.py:306-361` (translate tab)
- Modify: `test_streamlit_ui.py` (translate tab tests)

- [ ] **Step 1: Remove stale translate tab tests**

Delete these tests from `test_streamlit_ui.py`:

```python
# Remove: test_translate_tab_has_choose_languages_label (lines 122-125)
def test_translate_tab_has_choose_languages_label(app: AppTest) -> None:
    tab = app.tabs[0]
    markdown_values = [m.value for m in tab.markdown]
    assert any("① Pick your languages" in v for v in markdown_values)


# Remove: test_translate_tab_has_enter_text_label (lines 128-131)
def test_translate_tab_has_enter_text_label(app: AppTest) -> None:
    tab = app.tabs[0]
    markdown_values = [m.value for m in tab.markdown]
    assert any("② Type or paste your text" in v for v in markdown_values)


# Remove: test_translate_tab_has_divider (lines 134-136)
def test_translate_tab_has_divider(app: AppTest) -> None:
    tab = app.tabs[0]
    assert len(tab.divider) >= 1


# Remove: test_translate_tab_source_region_default (lines 162-164)
def test_translate_tab_source_region_default(app: AppTest) -> None:
    tab = app.tabs[0]
    assert tab.radio[0].value == "European"


# Remove: test_translate_tab_target_region_default (lines 167-169)
def test_translate_tab_target_region_default(app: AppTest) -> None:
    tab = app.tabs[0]
    assert tab.radio[1].value == "European"


# Remove: test_translate_source_region_filters_languages (lines 172-178)
def test_translate_source_region_filters_languages(app: AppTest) -> None:
    """Switching source region to Asia-Pacific shows Asia-Pacific languages."""
    app.tabs[0].radio[0].set_value("Asia-Pacific")
    _rerun_with_mocks(app)

    assert app.tabs[0].selectbox[0].value == "Chinese"


# Remove: test_translate_target_region_filters_languages (lines 181-186)
def test_translate_target_region_filters_languages(app: AppTest) -> None:
    """Switching target region to Asia-Pacific shows Asia-Pacific languages."""
    app.tabs[0].radio[1].set_value("Asia-Pacific")
    _rerun_with_mocks(app)

    assert app.tabs[0].selectbox[1].value == "Chinese"


# Remove: test_translate_success_shows_result_label (lines 198-202)
def test_translate_success_shows_result_label() -> None:
    """After a successful translation the '③ Translation' label is shown."""
    at = _run_inference_test(tab_index=0, input_text="Hello", decode_result="Bonjour")
    markdown_values = [m.value for m in at.tabs[0].markdown]
    assert any("③ Translation" in v for v in markdown_values)
```

Also remove the section comment `# -- Translate tab: structure` since the remaining tests are a mix of structure and interaction.

- [ ] **Step 2: Update translate tab placeholder test**

Change `test_translate_tab_text_area_placeholder` from:

```python
def test_translate_tab_text_area_placeholder(app: AppTest) -> None:
    tab = app.tabs[0]
    text_area = tab.text_area[0]
    assert text_area.placeholder == "e.g. The weather is nice today"
```

To:

```python
def test_translate_tab_text_area_placeholder(app: AppTest) -> None:
    tab = app.tabs[0]
    text_area = tab.text_area[0]
    assert text_area.placeholder == "Type or paste your text here..."
```

- [ ] **Step 3: Run translate UI tests to see failures**

Run: `uv run pytest test_streamlit_ui.py -k "translate" -v`
Expected: `test_translate_tab_text_area_placeholder` FAILS (old placeholder in code)

- [ ] **Step 4: Rewrite translate tab in `streamlit_app.py`**

Replace the entire `with translate_tab:` block (lines 308-361) with:

```python
with translate_tab:
    col1, col2, col3 = st.columns([5, 1, 5])
    with col1:
        source_lang = st.selectbox("From", LANGUAGES)
    with col2:
        st.markdown(
            "<p style='text-align:center;padding-top:2rem;font-size:1.2rem'>"
            "&rarr;</p>",
            unsafe_allow_html=True,
        )
    with col3:
        target_lang = st.selectbox(
            "To", LANGUAGES, index=LANGUAGES.index("French")
        )

    translate_input = st.text_area(
        "Text to translate",
        placeholder="Type or paste your text here...",
        height=150,
    )

    if st.button("Translate", disabled=not model_loaded):
        if not translate_input.strip():
            st.warning("Please enter some text first.")
        elif source_lang == target_lang:
            st.warning("Please pick two different languages.")
        else:
            with st.spinner("Translating..."):
                result = translate_text(
                    translate_input,
                    source_lang,
                    target_lang,
                    model,
                    tokenizer,
                )
            st.success(result)
```

- [ ] **Step 5: Run translate UI tests to verify they pass**

Run: `uv run pytest test_streamlit_ui.py -k "translate" -v`
Expected: All remaining translate tests PASS

- [ ] **Step 6: Commit**

```bash
git add streamlit_app.py test_streamlit_ui.py
git commit -m "feat: simplify translate tab to compact inline layout"
```

---

### Task 4: Simplify summarize tab

**Files:**
- Modify: `streamlit_app.py:362-401` (summarize tab)
- Modify: `test_streamlit_ui.py` (summarize tab tests)

- [ ] **Step 1: Remove stale summarize tab tests**

Delete these tests from `test_streamlit_ui.py`:

```python
# Remove: test_summarize_tab_has_choose_options_label (lines 247-250)
def test_summarize_tab_has_choose_options_label(app: AppTest) -> None:
    tab = app.tabs[1]
    markdown_values = [m.value for m in tab.markdown]
    assert any("① Pick your options" in v for v in markdown_values)


# Remove: test_summarize_tab_has_enter_text_label (lines 253-256)
def test_summarize_tab_has_enter_text_label(app: AppTest) -> None:
    tab = app.tabs[1]
    markdown_values = [m.value for m in tab.markdown]
    assert any("② Type or paste your text" in v for v in markdown_values)


# Remove: test_summarize_tab_has_divider (lines 259-261)
def test_summarize_tab_has_divider(app: AppTest) -> None:
    tab = app.tabs[1]
    assert len(tab.divider) >= 1


# Remove: test_summarize_tab_radio_default (lines 264-266)
def test_summarize_tab_radio_default(app: AppTest) -> None:
    tab = app.tabs[1]
    assert tab.radio[0].value == "Short"


# Remove: test_summarize_tab_output_region_default (lines 285-287)
def test_summarize_tab_output_region_default(app: AppTest) -> None:
    tab = app.tabs[1]
    assert tab.radio[1].value == "European"


# Remove: test_summarize_output_region_filters_languages (lines 290-295)
def test_summarize_output_region_filters_languages(app: AppTest) -> None:
    """Switching output region to Asia-Pacific shows Asia-Pacific languages."""
    app.tabs[1].radio[1].set_value("Asia-Pacific")
    _rerun_with_mocks(app)

    assert app.tabs[1].selectbox[0].value == "Chinese"


# Remove: test_summarize_success_shows_result_label (lines 310-315)
def test_summarize_success_shows_result_label() -> None:
    """After a successful summarize the '③ Summary' label is shown."""
    at = _run_inference_test(
        tab_index=1, input_text="Some long text.", decode_result="A brief summary."
    )
    markdown_values = [m.value for m in at.tabs[1].markdown]
    assert any("③ Summary" in v for v in markdown_values)


# Remove: test_summarize_change_radio_to_long (lines 329-334)
def test_summarize_change_radio_to_long(app: AppTest) -> None:
    """Changing the summary length radio to 'Long' updates its value."""
    app.tabs[1].radio[0].set_value("Long")
    _rerun_with_mocks(app)

    assert app.tabs[1].radio[0].value == "Long"
```

- [ ] **Step 2: Update summarize tab placeholder test**

Change `test_summarize_tab_text_area_placeholder` from:

```python
def test_summarize_tab_text_area_placeholder(app: AppTest) -> None:
    tab = app.tabs[1]
    text_area = tab.text_area[0]
    assert text_area.placeholder == "e.g. Paste an article, email, or paragraph here"
```

To:

```python
def test_summarize_tab_text_area_placeholder(app: AppTest) -> None:
    tab = app.tabs[1]
    text_area = tab.text_area[0]
    assert text_area.placeholder == "Paste an article, email, or paragraph here..."
```

- [ ] **Step 3: Run summarize UI tests to see failures**

Run: `uv run pytest test_streamlit_ui.py -k "summarize" -v`
Expected: `test_summarize_tab_text_area_placeholder` FAILS (old placeholder in code)

- [ ] **Step 4: Rewrite summarize tab in `streamlit_app.py`**

Replace the entire `with summarize_tab:` block (lines 362-401) with:

```python
with summarize_tab:
    output_lang = st.selectbox("Output Language", LANGUAGES)

    summarize_input = st.text_area(
        "Text to summarize",
        placeholder="Paste an article, email, or paragraph here...",
        height=150,
    )

    if st.button("Summarize", disabled=not model_loaded):
        if not summarize_input.strip():
            st.warning("Please enter some text first.")
        else:
            summary_length = select_summary_length(summarize_input)
            with st.spinner("Summarizing..."):
                result = summarize_text(
                    summarize_input,
                    output_lang,
                    summary_length,
                    model,
                    tokenizer,
                )
            st.success(result)
```

- [ ] **Step 5: Run summarize UI tests to verify they pass**

Run: `uv run pytest test_streamlit_ui.py -k "summarize" -v`
Expected: All remaining summarize tests PASS

- [ ] **Step 6: Commit**

```bash
git add streamlit_app.py test_streamlit_ui.py
git commit -m "feat: simplify summarize tab with auto summary length"
```

---

### Task 5: Remove result divider tests

**Files:**
- Modify: `test_streamlit_ui.py:403-418` (result divider tests)

- [ ] **Step 1: Delete result divider tests**

Remove the entire `# -- Result divider` section from `test_streamlit_ui.py`:

```python
# -- Result divider -----------------------------------------------------------


def test_translate_success_shows_result_divider() -> None:
    """After a successful translation, a divider appears before the result."""
    at = _run_inference_test(tab_index=0, input_text="Hello", decode_result="Bonjour")
    # Initial load has 1 divider (between steps 1 and 2); after result there are 2
    assert len(at.tabs[0].divider) >= 2


def test_summarize_success_shows_result_divider() -> None:
    """After a successful summarization, a divider appears before the result."""
    at = _run_inference_test(
        tab_index=1, input_text="Some long text.", decode_result="A brief summary."
    )
    assert len(at.tabs[1].divider) >= 2
```

- [ ] **Step 2: Run full test suite**

Run: `uv run pytest test_streamlit_app.py test_streamlit_ui.py -v`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add test_streamlit_ui.py
git commit -m "test: remove result divider tests for compact UI"
```

---

### Task 6: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update conventions**

In CLAUDE.md, make these changes:

Replace:
```
- `LANGUAGE_GROUPS` groups the 43 languages by region (European, Asia-Pacific) for filtered selectboxes
```
With:
```
- `LANGUAGE_GROUPS` groups the 43 languages by region (European, Asia-Pacific); not used by UI but kept for potential future use
```

Replace:
```
- UI uses `st.tabs` with a guided three-step flow (① Pick languages/options, ② Type or paste text, ③ Translation/Summary) in each tab
```
With:
```
- UI uses `st.tabs` with a compact layout — inline language pickers for Translate, single dropdown for Summarize
```

Replace:
```
- Each language selectbox has a region radio filter above it (`key="source_region"`, `key="target_region"`, `key="output_region"`)
```
With:
```
- Language selectboxes use the flat `LANGUAGES` list (43 items) with Streamlit's built-in type-to-search
- `select_summary_length` auto-determines summary length from input text size (Short < 500 chars, Medium 500-2000, Long > 2000)
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for compact UI changes"
```

---

### Task 7: Final verification

- [ ] **Step 1: Run full test suite**

Run: `uv run pytest test_streamlit_app.py test_streamlit_ui.py -v`
Expected: All tests PASS

- [ ] **Step 2: Run linter**

Run: `uv run ruff check --fix .`
Expected: No errors

- [ ] **Step 3: Run formatter**

Run: `uv run ruff format .`
Expected: No changes (or minor formatting applied)

- [ ] **Step 4: Run type checker**

Run: `uv run ty check streamlit_app.py`
Expected: No errors
