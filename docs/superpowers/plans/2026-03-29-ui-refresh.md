# UI Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Light UI refresh — updated title, cleaner chrome, copy-friendly output, prominent translate button.

**Architecture:** Six targeted edits to the UI section of `streamlit_app.py` (lines 190–283) plus corresponding test updates in `test_streamlit_ui.py`. No changes to pure functions, config, or model loading.

**Tech Stack:** Streamlit (st.title, st.selectbox, st.code, st.button)

---

## File Structure

- **Modify:** `streamlit_app.py:190-283` — UI section (title, subtitle, language bar, output panel, translate button)
- **Modify:** `test_streamlit_ui.py` — update tests that reference `app.text_area[1]` (output) since it becomes `st.code`

---

### Task 1: Update title and remove subtitle

**Files:**
- Modify: `streamlit_app.py:190-191`

- [ ] **Step 1: Update the title**

Change line 190:

```python
st.title("Tiny Aya Water Translate")
```

- [ ] **Step 2: Remove the subtitle**

Delete line 191:

```python
st.markdown("Translate text — running privately on your computer.")
```

- [ ] **Step 3: Run tests to verify nothing broke**

Run: `uv run pytest test_streamlit_app.py test_streamlit_ui.py -v`
Expected: All tests PASS (no tests reference the title or subtitle)

- [ ] **Step 4: Commit**

```bash
git add streamlit_app.py
git commit -m "feat: update title to Tiny Aya Water Translate and remove subtitle"
```

---

### Task 2: Remove language selectbox labels and swap button padding

**Files:**
- Modify: `streamlit_app.py:228-243`

- [ ] **Step 1: Collapse the "From" label**

Change the source language selectbox (line 230-234):

```python
    source_lang = st.selectbox(
        "From",
        LANGUAGES,
        key="source_lang",
        label_visibility="collapsed",
    )
```

- [ ] **Step 2: Remove the padding hack and collapse the swap button label**

Remove line 236 (`st.html("<div style='padding-top:1.8rem'></div>")`). The swap button stays as-is.

- [ ] **Step 3: Collapse the "To" label**

Change the target language selectbox (line 239-243):

```python
    target_lang = st.selectbox(
        "To",
        LANGUAGES,
        key="target_lang",
        label_visibility="collapsed",
    )
```

- [ ] **Step 4: Run tests to verify nothing broke**

Run: `uv run pytest test_streamlit_app.py test_streamlit_ui.py -v`
Expected: All tests PASS (tests reference selectboxes by index, not by label text)

- [ ] **Step 5: Commit**

```bash
git add streamlit_app.py
git commit -m "feat: remove language selectbox labels and swap button padding"
```

---

### Task 3: Replace output text area with st.code()

**Files:**
- Modify: `streamlit_app.py:256-263`
- Modify: `test_streamlit_ui.py`

- [ ] **Step 1: Update the failing test — output disabled check**

In `test_streamlit_ui.py`, the test `test_output_text_area_is_disabled` (line 155) checks `app.text_area[1].disabled`. With `st.code()` there is no second text area and no `disabled` property. Replace the test:

```python
def test_output_uses_code_block(app: AppTest) -> None:
    assert len(app.code) > 0
```

- [ ] **Step 2: Run tests to verify the new test fails**

Run: `uv run pytest test_streamlit_ui.py::test_output_uses_code_block -v`
Expected: FAIL — `app.code` has no elements because the output is still a text area

- [ ] **Step 3: Replace the output text area with st.code()**

Change `streamlit_app.py` lines 256-263. Replace:

```python
with col_output:
    st.text_area(
        "Output",
        value=st.session_state.translate_output,
        height=200,
        disabled=True,
        label_visibility="collapsed",
    )
```

With:

```python
with col_output:
    st.code(st.session_state.translate_output, language=None)
```

- [ ] **Step 4: Run all tests to check what else broke**

Run: `uv run pytest test_streamlit_app.py test_streamlit_ui.py -v`
Expected: `test_output_uses_code_block` PASSES. Check for failures in:
- `test_translate_success_shows_result` — references `at.text_area[1].value`
- `test_swap_moves_output_to_input` — references `at.text_area[1].value`

- [ ] **Step 5: Fix test_translate_success_shows_result**

In `test_streamlit_ui.py`, update `test_translate_success_shows_result` (line 166). Replace:

```python
def test_translate_success_shows_result() -> None:
    at = _run_inference_test(input_text="Hello", decode_result="Bonjour")
    assert at.text_area[1].value == "Bonjour"
```

With:

```python
def test_translate_success_shows_result() -> None:
    at = _run_inference_test(input_text="Hello", decode_result="Bonjour")
    assert at.code[0].value == "Bonjour"
```

- [ ] **Step 6: Fix test_swap_moves_output_to_input**

In `test_streamlit_ui.py`, update `test_swap_moves_output_to_input` (line 117). Replace the assertions at lines 143-145:

```python
    # Input should now contain the previous output
    assert at.text_area[0].value == "Bonjour"
    # Output should be cleared
    assert at.code[0].value == ""
```

- [ ] **Step 7: Run all tests**

Run: `uv run pytest test_streamlit_app.py test_streamlit_ui.py -v`
Expected: All tests PASS

- [ ] **Step 8: Commit**

```bash
git add streamlit_app.py test_streamlit_ui.py
git commit -m "feat: replace output text area with st.code for built-in copy button"
```

---

### Task 4: Make Translate button primary type

**Files:**
- Modify: `streamlit_app.py:267`

- [ ] **Step 1: Add type="primary" to the Translate button**

Change line 267:

```python
if st.button("Translate", key="Translate", disabled=not model_loaded, type="primary"):
```

- [ ] **Step 2: Run all tests**

Run: `uv run pytest test_streamlit_app.py test_streamlit_ui.py -v`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add streamlit_app.py
git commit -m "feat: make Translate button primary type for visual prominence"
```

---

### Task 5: Final verification

- [ ] **Step 1: Run the full test suite**

Run: `uv run pytest test_streamlit_app.py test_streamlit_ui.py -v`
Expected: All tests PASS

- [ ] **Step 2: Run linter and formatter**

Run: `uv run ruff check --fix . && uv run ruff format .`
Expected: No errors

- [ ] **Step 3: Run type checker**

Run: `uv run ty check streamlit_app.py`
Expected: No errors (or only pre-existing ones)
