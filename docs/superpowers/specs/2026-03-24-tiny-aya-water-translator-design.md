# Tiny Aya Water Translator — Design Spec

## Overview

A single-page Streamlit application that provides translation between 40+ European and Asia-Pacific languages using the CohereLabs/tiny-aya-water model via local HuggingFace Transformers inference. Supports both single text translation and batch file translation (CSV/TXT) with download.

## Architecture

Single-file Streamlit app (`streamlit_app.py`) with three logical sections:

1. **Model loading** — load `CohereLabs/tiny-aya-water` tokenizer + model once via `@st.cache_resource`, BF16 precision
2. **Translation function** — takes source text, source language, target language; constructs a chat-template prompt; runs `model.generate()` and decodes the output
3. **UI layer** — language selectors, text input, file upload, translate button, results display, download

Config (model ID, default generation params) loaded from `.env` via `python-dotenv`.

## UI Layout

Top-down single-page flow:

- **Title:** "Tiny Aya Water Translator" with subtitle describing the model
- **Language selectors:** Two columns — source language (default: English) and target language (default: French). Both contain the full list of Water's supported languages as human-readable names
- **Text input:** `st.text_area` for entering text to translate
- **Translate button:** Triggers single-text translation
- **Translation output:** `st.text_area`, read-only, displays the result
- **Batch Translation section:**
  - File upload accepting CSV and TXT
  - Column selector (if CSV) to pick which column to translate
  - Translate File button
  - Results table (`st.dataframe`) showing original + translated columns side by side
  - Download CSV button
- **Sidebar:**
  - Temperature slider (0.0–1.0, default 0.1)
  - Max tokens slider (100–2000, default 700)

## Translation Logic

### Prompt Construction

```python
messages = [
    {
        "role": "system",
        "content": "You are a translator. Translate the user's text from {source_language} to {target_language}. Output only the translation, nothing else."
    },
    {
        "role": "user",
        "content": "{text_to_translate}"
    }
]
```

Applied via `tokenizer.apply_chat_template()`, then `model.generate()`.

### Generation Parameters

- `temperature`: 0.1 (default, configurable via sidebar)
- `max_new_tokens`: 700 (default, configurable via sidebar)
- `do_sample`: True
- `top_p`: 0.95

### Single Text Flow

1. Build messages, tokenize with chat template, generate, decode
2. Strip prompt/template artifacts from the output

### Batch Flow

1. Read uploaded file — CSV via `pd.read_csv()`, TXT as one line per entry
2. For each row, run the same translation function
3. Show `st.progress()` bar during batch processing
4. Collect results into a DataFrame with columns: `original`, `translated`
5. Display with `st.dataframe()`, offer `st.download_button()` for CSV export

### No Streaming

`model.generate()` returns the full output at once. Streaming with local Transformers adds complexity (TextIteratorStreamer + threading) for minimal benefit on a translation tool where outputs are short.

## Supported Languages

Full list of Tiny Aya Water's supported languages (European + Asia-Pacific):

**European:** English, Dutch, French, Italian, Portuguese, Romanian, Spanish, Czech, Polish, Ukrainian, Russian, Greek, German, Danish, Swedish, Norwegian, Catalan, Galician, Welsh, Irish, Basque, Croatian, Latvian, Lithuanian, Slovak, Slovenian, Estonian, Finnish, Hungarian, Serbian, Bulgarian

**Asia-Pacific:** Chinese, Japanese, Korean, Tagalog, Malay, Indonesian, Javanese, Khmer, Thai, Lao, Vietnamese, Burmese

## File Structure

| File | Purpose |
|------|---------|
| `streamlit_app.py` | Single-file app with all logic |
| `test_streamlit_app.py` | Pytest tests for translation and file processing functions |
| `pyproject.toml` | uv-managed project with all dependencies |
| `.env.example` | Documents configurable environment variables |

## Dependencies

- `streamlit` — UI framework
- `transformers` — model loading and inference
- `torch` — PyTorch backend
- `pandas` — CSV handling for batch mode
- `python-dotenv` — env config loading
- Dev: `ruff`, `ty`, `pytest`

## `.env.example`

```
MODEL_ID=CohereLabs/tiny-aya-water
DEFAULT_TEMPERATURE=0.1
DEFAULT_MAX_TOKENS=700
```

## Testable Functions

Functions extracted from the Streamlit UI for independent testing:

- `build_translation_prompt(text, source_lang, target_lang)` — returns the messages list
- `extract_translation(decoded_text)` — strips prompt/template artifacts from model output
- `parse_uploaded_file(file, column)` — returns a list of strings from CSV or TXT
- `translate_text(text, source_lang, target_lang, model, tokenizer, temperature, max_tokens)` — end-to-end translation
