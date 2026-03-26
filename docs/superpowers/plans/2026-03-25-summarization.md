# Summarization Feature Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add cross-lingual summarization with controllable length to the existing translation app.

**Architecture:** Extend the single-file `streamlit_app.py` with three new pure functions (`get_summary_config`, `build_summarization_prompt`, `summarize_text`), rename `extract_translation` to `clean_model_output`, and add a task selector UI that switches between Translate and Summarize modes. All changes stay within the two existing files.

**Tech Stack:** Python 3.12+, Streamlit, Transformers, PyTorch, Pandas, pytest

**Spec:** `docs/superpowers/specs/2026-03-25-summarization-design.md`

---

### Task 1: Rename `extract_translation` to `clean_model_output`

**Files:**
- Modify: `streamlit_app.py:119-121` (function definition)
- Modify: `streamlit_app.py:161` (call site in `translate_text`)
- Modify: `test_streamlit_app.py:11` (import)
- Modify: `test_streamlit_app.py:131-144` (four test functions)

- [ ] **Step 1: Rename the function in `streamlit_app.py`**

In `streamlit_app.py`, rename the function definition and its call site:

```python
# Line 119-121: rename function
def clean_model_output(decoded_text: str) -> str:
    """Clean up decoded model output (skip_special_tokens=True already applied)."""
    return decoded_text.strip()
```

```python
# Line 161: update call site in translate_text
    return clean_model_output(decoded)
```

- [ ] **Step 2: Update tests to use new name**

In `test_streamlit_app.py`, update the import (line 11) from `extract_translation` to `clean_model_output`, and rename the four test functions:

```python
# Line 7-15: updated imports
from streamlit_app import (
    LANGUAGES,
    build_translation_prompt,
    clean_model_output,
    detect_device,
    parse_uploaded_file,
    select_dtype,
    translate_text,
)
```

```python
# Lines 131-144: rename four tests
def test_clean_model_output_strips_whitespace() -> None:
    assert clean_model_output("  Hello world  ") == "Hello world"


def test_clean_model_output_empty_string() -> None:
    assert clean_model_output("") == ""


def test_clean_model_output_newlines() -> None:
    assert clean_model_output("\n\nBonjour\n\n") == "Bonjour"


def test_clean_model_output_preserves_inner_whitespace() -> None:
    assert clean_model_output("  Hello   world  ") == "Hello   world"
```

- [ ] **Step 3: Run tests to verify rename doesn't break anything**

Run: `uv run pytest test_streamlit_app.py -v`
Expected: All 31 tests PASS (same count as before, just renamed)

- [ ] **Step 4: Run linter**

Run: `uv run ruff check --fix . && uv run ruff format .`
Expected: No errors

- [ ] **Step 5: Commit**

```bash
git add streamlit_app.py test_streamlit_app.py
git commit -m "refactor: rename extract_translation to clean_model_output"
```

---

### Task 2: Add `get_summary_config` with tests

**Files:**
- Modify: `streamlit_app.py:119-121` (add function after `clean_model_output`)
- Modify: `test_streamlit_app.py` (add 4 tests after `clean_model_output` tests)

- [ ] **Step 1: Write failing tests for `get_summary_config`**

Add these tests in `test_streamlit_app.py` after the `test_clean_model_output_*` tests. Also add `get_summary_config` to the imports from `streamlit_app`.

Add `import pytest` at the top of the test file (after the existing imports). Also add `get_summary_config` to the `from streamlit_app import (...)` block.

```python
import pytest

def test_get_summary_config_short() -> None:
    result = get_summary_config("Short")
    assert "brief summary" in result
    assert "1-2 sentences" in result


def test_get_summary_config_medium() -> None:
    result = get_summary_config("Medium")
    assert "short paragraph" in result


def test_get_summary_config_long() -> None:
    result = get_summary_config("Long")
    assert "detailed summary" in result


def test_get_summary_config_invalid_raises() -> None:
    with pytest.raises(ValueError):
        get_summary_config("Extra Long")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest test_streamlit_app.py::test_get_summary_config_short -v`
Expected: FAIL with `ImportError` (function not defined yet)

- [ ] **Step 3: Implement `get_summary_config`**

Add in `streamlit_app.py` after `clean_model_output` (around line 122), before `translate_text`:

```python
def get_summary_config(length: str) -> str:
    """Return the prompt instruction for the given summary length."""
    configs = {
        "Short": "Write a brief summary in 1-2 sentences",
        "Medium": "Write a summary in a short paragraph",
        "Long": "Write a detailed summary",
    }
    if length not in configs:
        raise ValueError(f"Unknown summary length: {length!r}")
    return configs[length]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest test_streamlit_app.py -k "get_summary_config" -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Run full test suite and linter**

Run: `uv run pytest test_streamlit_app.py -v && uv run ruff check --fix . && uv run ruff format .`
Expected: All tests PASS, no lint errors

- [ ] **Step 6: Commit**

```bash
git add streamlit_app.py test_streamlit_app.py
git commit -m "feat: add get_summary_config for summary length mapping"
```

---

### Task 3: Add `build_summarization_prompt` with tests

**Files:**
- Modify: `streamlit_app.py` (add function after `get_summary_config`)
- Modify: `test_streamlit_app.py` (add 5 tests)

- [ ] **Step 1: Write failing tests for `build_summarization_prompt`**

Add these tests in `test_streamlit_app.py`. Also add `build_summarization_prompt` to the imports from `streamlit_app`.

```python
def test_build_summarization_prompt_returns_single_message() -> None:
    result = build_summarization_prompt("Some long text here.", "Short", "English")
    assert len(result) == 1
    assert result[0]["role"] == "user"


def test_build_summarization_prompt_contains_target_language() -> None:
    result = build_summarization_prompt("Some text.", "Medium", "French")
    content = result[0]["content"]
    assert "French" in content


def test_build_summarization_prompt_contains_input_text() -> None:
    result = build_summarization_prompt("The quick brown fox.", "Short", "English")
    content = result[0]["content"]
    assert "The quick brown fox." in content


def test_build_summarization_prompt_includes_summarize_instruction() -> None:
    result = build_summarization_prompt("Some text.", "Short", "English")
    content = result[0]["content"]
    assert "summar" in content.lower()


def test_build_summarization_prompt_includes_length_wording() -> None:
    result = build_summarization_prompt("Some text.", "Short", "English")
    content = result[0]["content"]
    assert "brief summary" in content
    assert "1-2 sentences" in content
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest test_streamlit_app.py::test_build_summarization_prompt_returns_single_message -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement `build_summarization_prompt`**

Add in `streamlit_app.py` after `get_summary_config`:

```python
def build_summarization_prompt(
    text: str, summary_length: str, target_lang: str
) -> list[dict[str, str]]:
    """Build the chat messages list for a summarization request."""
    length_instruction = get_summary_config(summary_length)
    return [
        {
            "role": "user",
            "content": (
                f"{length_instruction} of the following text in {target_lang}. "
                f"Output only the summary, nothing else.\n\n{text}"
            ),
        }
    ]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest test_streamlit_app.py -k "build_summarization_prompt" -v`
Expected: All 5 tests PASS

- [ ] **Step 5: Run full test suite and linter**

Run: `uv run pytest test_streamlit_app.py -v && uv run ruff check --fix . && uv run ruff format .`
Expected: All tests PASS, no lint errors

- [ ] **Step 6: Commit**

```bash
git add streamlit_app.py test_streamlit_app.py
git commit -m "feat: add build_summarization_prompt for summary prompt construction"
```

---

### Task 4: Add `summarize_text` with tests

**Files:**
- Modify: `streamlit_app.py` (add function after `translate_text`)
- Modify: `test_streamlit_app.py` (add 4 tests)

- [ ] **Step 1: Write failing tests for `summarize_text`**

Add these tests in `test_streamlit_app.py`. Also add `summarize_text` to the imports from `streamlit_app`.

```python
def test_summarize_text_plain_tensor_path() -> None:
    """Plain tensor path: apply_chat_template returns a tensor directly."""
    mock_tokenizer = MagicMock()
    mock_model = MagicMock()
    mock_model.device = torch.device("cpu")

    prompt_ids = torch.tensor([[1, 2, 3]])
    mock_tokenizer.apply_chat_template.return_value = prompt_ids
    mock_model.generate.return_value = torch.tensor([[1, 2, 3, 4]])
    mock_tokenizer.decode.return_value = "A brief summary."

    summarize_text(
        text="Some long text to summarize.",
        target_lang="English",
        summary_length="Short",
        model=mock_model,
        tokenizer=mock_tokenizer,
        temperature=0.1,
        max_tokens=700,
    )

    input_ids = mock_model.generate.call_args[0][0]
    assert input_ids.device == torch.device("cpu")
    assert mock_model.generate.call_args[1]["attention_mask"] is None


def test_summarize_text_handles_batch_encoding() -> None:
    """BatchEncoding path: apply_chat_template returns a dict-like object."""
    mock_tokenizer = MagicMock()
    mock_model = MagicMock()
    mock_model.device = torch.device("cpu")

    prompt_ids = torch.tensor([[1, 2, 3]])
    attention = torch.tensor([[1, 1, 1]])
    batch_encoding = {"input_ids": prompt_ids, "attention_mask": attention}
    mock_tokenizer.apply_chat_template.return_value = batch_encoding

    mock_model.generate.return_value = torch.tensor([[1, 2, 3, 4, 5]])
    mock_tokenizer.decode.return_value = "A brief summary."

    result = summarize_text(
        text="Some long text to summarize.",
        target_lang="English",
        summary_length="Short",
        model=mock_model,
        tokenizer=mock_tokenizer,
        temperature=0.1,
        max_tokens=700,
    )

    assert result == "A brief summary."
    input_ids = mock_model.generate.call_args[0][0]
    assert input_ids.device == torch.device("cpu")
    mask = mock_model.generate.call_args[1]["attention_mask"]
    assert mask.device == torch.device("cpu")
    assert torch.equal(mask, attention)


def test_summarize_text_returns_cleaned_string() -> None:
    mock_tokenizer = MagicMock()
    mock_model = MagicMock()
    mock_model.device = torch.device("cpu")

    prompt_ids = torch.tensor([[1, 2, 3]])
    mock_tokenizer.apply_chat_template.return_value = prompt_ids
    mock_model.generate.return_value = torch.tensor([[1, 2, 3, 4, 5]])
    mock_tokenizer.decode.return_value = "  A brief summary.  "

    result = summarize_text(
        text="Some long text.",
        target_lang="English",
        summary_length="Short",
        model=mock_model,
        tokenizer=mock_tokenizer,
        temperature=0.1,
        max_tokens=700,
    )
    assert result == "A brief summary."


def test_summarize_text_calls_generate_with_correct_params() -> None:
    mock_tokenizer = MagicMock()
    mock_model = MagicMock()
    mock_model.device = torch.device("cpu")

    prompt_ids = torch.tensor([[1, 2, 3]])
    mock_tokenizer.apply_chat_template.return_value = prompt_ids
    mock_model.generate.return_value = torch.tensor([[1, 2, 3, 4, 5]])
    mock_tokenizer.decode.return_value = "Summary."

    summarize_text(
        text="Some text.",
        target_lang="French",
        summary_length="Medium",
        model=mock_model,
        tokenizer=mock_tokenizer,
        temperature=0.3,
        max_tokens=500,
    )

    mock_model.generate.assert_called_once()
    call_kwargs = mock_model.generate.call_args[1]
    assert call_kwargs["max_new_tokens"] == 500
    assert call_kwargs["temperature"] == 0.3
    assert call_kwargs["do_sample"] is True
    assert call_kwargs["top_p"] == streamlit_app.TOP_P
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest test_streamlit_app.py::test_summarize_text_plain_tensor_path -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement `summarize_text`**

Add in `streamlit_app.py` after `translate_text` (around line 175), before `parse_uploaded_file`:

```python
def summarize_text(
    text: str,
    target_lang: str,
    summary_length: str,
    model: Any,
    tokenizer: Any,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> str:
    """Summarize text using the model and return the cleaned result."""
    import torch

    messages = build_summarization_prompt(text, summary_length, target_lang)
    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt",
    )
    if hasattr(inputs, "keys"):
        input_ids = inputs["input_ids"].to(model.device)
        attention_mask = inputs["attention_mask"].to(model.device)
    else:
        input_ids = inputs.to(model.device)
        attention_mask = None
    with torch.inference_mode():
        gen_tokens = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=TOP_P,
        )
    output_tokens = gen_tokens[0][input_ids.shape[-1] :]
    decoded = tokenizer.decode(output_tokens, skip_special_tokens=True)
    return clean_model_output(decoded)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest test_streamlit_app.py -k "summarize_text" -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Run full test suite and linter**

Run: `uv run pytest test_streamlit_app.py -v && uv run ruff check --fix . && uv run ruff format .`
Expected: All tests PASS, no lint errors

- [ ] **Step 6: Commit**

```bash
git add streamlit_app.py test_streamlit_app.py
git commit -m "feat: add summarize_text for end-to-end summarization"
```

---

### Task 5: Add task selector UI and Summarize mode

**Files:**
- Modify: `streamlit_app.py:236-331` (UI section)

This task modifies only the Streamlit UI code below `import streamlit as st`. No pure function changes.

- [ ] **Step 1: Update page title and description**

In `streamlit_app.py`, replace the title and description (lines 236-241):

```python
st.title("Tiny Aya Water")
st.markdown(
    "Translate and summarize across 43 European and Asia-Pacific languages using "
    "[CohereLabs/tiny-aya-water](https://huggingface.co/CohereLabs/tiny-aya-water) "
    "running locally."
)
```

- [ ] **Step 2: Add task selector and wrap Translate mode in conditional**

Add the task selector radio right after the description, then wrap the existing translation UI (language selectors, text area, translate button, batch section) inside `if task == "Translate":`:

```python
task = st.radio("Task", ["Translate", "Summarize"], horizontal=True)

if task == "Translate":
    # Language selectors
    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox(
            "Source Language", LANGUAGES, index=LANGUAGES.index("English")
        )
    with col2:
        target_lang = st.selectbox(
            "Target Language", LANGUAGES, index=LANGUAGES.index("French")
        )

    # Single text translation
    input_text = st.text_area("Text to translate", height=150)

    if st.button("Translate", disabled=not model_loaded):
        if not input_text.strip():
            st.warning("Please enter some text to translate.")
        elif source_lang == target_lang:
            st.warning("Source and target language are the same.")
        else:
            with st.spinner("Translating..."):
                result = translate_text(
                    input_text,
                    source_lang,
                    target_lang,
                    model,
                    tokenizer,
                    temperature,
                    max_tokens,
                )
            st.text_area("Translation", value=result, height=150, disabled=True)

    # -- Batch Translation --------------------------------------------------------

    st.markdown("---")
    st.subheader("Batch Translation")

    uploaded_file = st.file_uploader(
        "Upload CSV or TXT file", type=["csv", "txt"], key="translate_file"
    )

    if uploaded_file is not None:
        column: str | None = None
        if uploaded_file.name.endswith(".csv"):
            preview_df = pd.read_csv(
                uploaded_file, encoding="utf-8", encoding_errors="replace"
            )
            uploaded_file.seek(0)
            column = st.selectbox("Column to translate", preview_df.columns.tolist())

        if st.button("Translate File", disabled=not model_loaded):
            if source_lang == target_lang:
                st.warning("Source and target language are the same.")
            else:
                texts = parse_uploaded_file(uploaded_file, column=column)
                if not texts:
                    st.warning("No text found in the uploaded file.")
                else:
                    if len(texts) >= MAX_BATCH_ROWS:
                        st.warning(
                            f"File exceeds {MAX_BATCH_ROWS} rows. "
                            f"Only the first {MAX_BATCH_ROWS} will be translated."
                        )
                    translations: list[str] = []
                    progress = st.progress(0)
                    for i, text in enumerate(texts):
                        translated = translate_text(
                            text,
                            source_lang,
                            target_lang,
                            model,
                            tokenizer,
                            temperature,
                            max_tokens,
                        )
                        translations.append(translated)
                        progress.progress((i + 1) / len(texts))

                    result_df = pd.DataFrame(
                        {"original": texts, "translated": translations}
                    )
                    st.dataframe(result_df)

                    csv_output = result_df.to_csv(index=False)
                    st.download_button(
                        "Download CSV",
                        csv_output,
                        file_name="translations.csv",
                        mime="text/csv",
                    )
```

Note: Add `key="translate_file"` to the file uploader so it doesn't conflict with the summarize file uploader.

- [ ] **Step 3: Add Summarize mode UI**

Add the `else:` branch (Summarize mode) immediately after the Translate block:

```python
else:
    # Summarize mode
    summary_length = st.radio(
        "Summary Length", ["Short", "Medium", "Long"], horizontal=True
    )
    output_lang = st.selectbox(
        "Output Language", LANGUAGES, index=LANGUAGES.index("English")
    )

    # Single text summarization
    input_text = st.text_area("Text to summarize", height=150)

    if st.button("Summarize", disabled=not model_loaded):
        if not input_text.strip():
            st.warning("Please enter some text to summarize.")
        else:
            with st.spinner("Summarizing..."):
                result = summarize_text(
                    input_text,
                    output_lang,
                    summary_length,
                    model,
                    tokenizer,
                    temperature,
                    max_tokens,
                )
            st.text_area("Summary", value=result, height=150, disabled=True)

    # -- Batch Summarization ------------------------------------------------------

    st.markdown("---")
    st.subheader("Batch Summarization")

    uploaded_file = st.file_uploader(
        "Upload CSV or TXT file", type=["csv", "txt"], key="summarize_file"
    )

    if uploaded_file is not None:
        column: str | None = None
        if uploaded_file.name.endswith(".csv"):
            preview_df = pd.read_csv(
                uploaded_file, encoding="utf-8", encoding_errors="replace"
            )
            uploaded_file.seek(0)
            column = st.selectbox(
                "Column to summarize", preview_df.columns.tolist()
            )

        if st.button("Summarize File", disabled=not model_loaded):
            texts = parse_uploaded_file(uploaded_file, column=column)
            if not texts:
                st.warning("No text found in the uploaded file.")
            else:
                if len(texts) >= MAX_BATCH_ROWS:
                    st.warning(
                        f"File exceeds {MAX_BATCH_ROWS} rows. "
                        f"Only the first {MAX_BATCH_ROWS} will be summarized."
                    )
                summaries: list[str] = []
                progress = st.progress(0)
                for i, text in enumerate(texts):
                    try:
                        summary = summarize_text(
                            text,
                            output_lang,
                            summary_length,
                            model,
                            tokenizer,
                            temperature,
                            max_tokens,
                        )
                    except Exception:
                        st.warning(f"Row {i + 1} failed to summarize.")
                        summary = "[Error: generation failed]"
                    summaries.append(summary)
                    progress.progress((i + 1) / len(texts))

                result_df = pd.DataFrame(
                    {"original": texts, "summary": summaries}
                )
                st.dataframe(result_df)

                csv_output = result_df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv_output,
                    file_name="summaries.csv",
                    mime="text/csv",
                )
```

- [ ] **Step 4: Run full test suite and linter**

Run: `uv run pytest test_streamlit_app.py -v && uv run ruff check --fix . && uv run ruff format .`
Expected: All tests PASS, no lint errors

- [ ] **Step 5: Commit**

```bash
git add streamlit_app.py
git commit -m "feat: add task selector UI with Summarize mode"
```

---

### Task 6: Update documentation

**Files:**
- Modify: `pyproject.toml:4`
- Modify: `README.md:1-11`
- Modify: `CLAUDE.md:1-3,32`

- [ ] **Step 1: Update `pyproject.toml` description**

Change line 4:

```toml
description = "Translation and summarization for European and Asia-Pacific languages with CohereLabs/tiny-aya-water"
```

- [ ] **Step 2: Update `README.md`**

Update the title, description, and features list:

```markdown
# Tiny Aya Water

Translate and summarize across 43 European and Asia-Pacific languages using [CohereLabs/tiny-aya-water](https://huggingface.co/CohereLabs/tiny-aya-water) running locally.

## Features

- Single text translation with language selection
- Cross-lingual summarization with controllable length (short/medium/long)
- Batch translation and summarization via CSV/TXT file upload with CSV download
- Configurable generation parameters (temperature, max tokens)
- Auto-detects CUDA, MPS, and CPU with optimal dtype per device
- Local inference — no API key required
```

- [ ] **Step 3: Update `CLAUDE.md`**

Update the project description (line 3) and the conventions section (line 32):

Line 3:
```
Streamlit translation and summarization app using CohereLabs/tiny-aya-water (3.35B parameter multilingual model) with local HuggingFace Transformers inference. Supports single text and batch file (CSV/TXT) translation and summarization across 43 European and Asia-Pacific languages.
```

Line 32 — update the `translate_text` convention to also mention `summarize_text`:
```
- `translate_text` and `summarize_text` handle both plain tensor and `BatchEncoding` returns from `apply_chat_template`
```

- [ ] **Step 4: Run linter**

Run: `uv run ruff check --fix . && uv run ruff format .`
Expected: No errors

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml README.md CLAUDE.md
git commit -m "docs: update project description and features for summarization"
```

---

### Task 7: Final verification

- [ ] **Step 1: Run full test suite**

Run: `uv run pytest test_streamlit_app.py -v`
Expected: All tests PASS (31 original + 13 new = 44 total)

- [ ] **Step 2: Run linter and formatter**

Run: `uv run ruff check --fix . && uv run ruff format .`
Expected: No errors

- [ ] **Step 3: Run type checker**

Run: `uv run ty check streamlit_app.py`
Expected: No errors (or only pre-existing warnings)

- [ ] **Step 4: Verify git status is clean**

Run: `git status`
Expected: Clean working tree, all changes committed
