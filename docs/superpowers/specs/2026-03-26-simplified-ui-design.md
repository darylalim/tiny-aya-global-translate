# Simplified UI Design

## Goal

Simplify the Streamlit app UI to reduce visual clutter, streamline the workflow, and make it approachable for both technical and non-technical users.

## Changes

### Removed

- **Sidebar** entirely — this includes:
  - Temperature slider
  - Max tokens slider
  - Model name/license caption (`CohereLabs/tiny-aya-water`, CC-BY-NC link)
  - Device/dtype info line
- **Batch translation UI** — file uploader, CSV column selector, progress bar, download button
- **Batch summarization UI** — same as above

### Changed

- **Task selector**: `st.radio("Task", ...)` replaced with `st.tabs(["Translate", "Summarize"])`
- **Execution order**: title and subtitle move above model loading (currently they appear after). See Execution Order section below
- **Model/device info**: `st.sidebar.info` (device/dtype) and sidebar model/license caption are consolidated into a single `st.caption` on the main page, placed after model loading. Shows `"Model: [CohereLabs/tiny-aya-water](https://huggingface.co/CohereLabs/tiny-aya-water) | Device: {device} | Dtype: {dtype} | License: CC-BY-NC"` (markdown link preserved). Uses destructured `device` and `dtype` from `load_model()`. Only displayed when model loading succeeds — on failure, the existing `st.error` is shown and the caption is omitted
- **Summarize tab layout**: summary length radio and output language selectbox are now placed in `st.columns` side by side (currently stacked vertically)
- **Temperature and max tokens**: remove the `temperature` and `max_tokens` keyword arguments from all `translate_text` and `summarize_text` call sites, allowing the function parameter defaults (`DEFAULT_TEMPERATURE`, `DEFAULT_MAX_TOKENS`) to take effect. These remain configurable via `.env`

### Unchanged

- **Page title and subtitle**: `st.title("Tiny Aya Water")` and the `st.markdown(...)` description paragraph are kept as-is (content unchanged, but repositioned above model loading — see Execution Order)
- **All pure functions** remain intact: `translate_text`, `summarize_text`, `_generate`, `build_translation_prompt`, `build_summarization_prompt`, `clean_model_output`, `detect_device`, `select_dtype`, `get_summary_config`, `parse_uploaded_file`
- **`parse_uploaded_file`** is intentionally retained as dead code (along with its `pandas` and `BytesIO` imports) to preserve the module's public API for potential future use
- **All config variables** remain: `MODEL_ID`, `DEVICE`, `DEFAULT_TEMPERATURE`, `DEFAULT_MAX_TOKENS`, `TOP_P`, `MAX_BATCH_ROWS` — `MAX_BATCH_ROWS` is still used as the default parameter in `parse_uploaded_file`
- **`@st.cache_resource` model loading** with spinner and error handling
- **`LANGUAGES` list**
- **Spinners**: `st.spinner("Translating...")` and `st.spinner("Summarizing...")` are kept around inference calls
- **All existing tests** pass without modification

## Translate Tab

1. Two `st.columns`: source language `st.selectbox("Source Language", default="English")` (left) + target language `st.selectbox("Target Language", default="French")` (right)
2. `st.text_area("Text to translate", height=150)`
3. `st.button("Translate")` — disabled when model not loaded
4. Validation: `st.warning` on empty text, `st.warning` when source equals target language
5. `st.text_area("Translation", height=150, disabled=True)`

## Summarize Tab

1. Two `st.columns`: summary length `st.radio("Summary Length", ["Short", "Medium", "Long"], horizontal=True)` in left column + output language `st.selectbox("Output Language", default="English")` in right column
2. `st.text_area("Text to summarize", height=150)`
3. `st.button("Summarize")` — disabled when model not loaded
4. Validation: `st.warning` on empty text
5. `st.text_area("Summary", height=150, disabled=True)`

## Execution Order

1. `st.title("Tiny Aya Water")`
2. `st.markdown(...)` — description paragraph
3. Model loading via `load_model()` inside `st.spinner`
4. On success: `st.caption(...)` with model/device/dtype/license info
5. On failure: `st.error(...)` (no caption)
6. `st.tabs(["Translate", "Summarize"])` — tab contents follow

## Widget Keys

With `st.tabs`, both tabs' widgets coexist in session state. No key collisions exist because each tab uses distinct widget labels: "Source Language"/"Target Language"/"Text to translate"/"Translate" vs "Summary Length"/"Output Language"/"Text to summarize"/"Summarize". No explicit `key` parameters are needed.

## Testing Impact

- Existing pure function tests remain unchanged — all tests exercise pure functions only (no UI/widget tests exist)
- `parse_uploaded_file` tests stay (function is retained in the module and imported by test file, so ruff will not flag it as unused)
- No new tests needed — changes are UI deletion and restructuring only
