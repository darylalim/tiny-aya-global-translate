# Friendly UI Design

## Goal

Make the app simpler and more approachable for non-technical colleagues by reducing the overwhelming 43-language flat list and replacing developer-y copy with friendlier language throughout.

## Target Audience

Non-technical colleagues who want to translate or summarize text quickly with minimal friction.

## Constraint

Streamlit-native components only — no custom CSS or HTML.

## Changes

### New: Language groups data structure

Add a grouped dictionary alongside the existing `LANGUAGES` flat list:

```python
LANGUAGE_GROUPS: dict[str, list[str]] = {
    "European": [
        "English", "Dutch", "French", "Italian", "Portuguese", "Romanian",
        "Spanish", "Czech", "Polish", "Ukrainian", "Russian", "Greek",
        "German", "Danish", "Swedish", "Norwegian", "Catalan", "Galician",
        "Welsh", "Irish", "Basque", "Croatian", "Latvian", "Lithuanian",
        "Slovak", "Slovenian", "Estonian", "Finnish", "Hungarian", "Serbian",
        "Bulgarian",
    ],
    "Asia-Pacific": [
        "Chinese", "Japanese", "Korean", "Tagalog", "Malay", "Indonesian",
        "Javanese", "Khmer", "Thai", "Lao", "Vietnamese", "Burmese",
    ],
}
```

`LANGUAGES` remains unchanged (tests and pure functions reference it). `LANGUAGE_GROUPS` is used only by the UI for filtered selectboxes.

### Changed: Translate tab — language selection

The ① step gains a region radio filter above each language selectbox:

```
① Pick your languages

[Source]                          [Target]
(•) European  ( ) Asia-Pacific   (•) European  ( ) Asia-Pacific
[English          ▾]             [French           ▾]
```

- Each column gets its own independent `st.radio("Region", ["European", "Asia-Pacific"], horizontal=True)`
- The radio filters its column's `st.selectbox` to show only that region's languages
- Defaults: both radios on "European", source=English, target=French
- When a user switches region, the selectbox shows the first language in that group
- Selectbox labels remain unchanged: "Source Language" and "Target Language"

### Changed: Summarize tab — language selection

The ① step gains a region radio filter above the output language selectbox:

```
① Pick your options

Summary Length              Output Language
(•) Short (•) Medium ( ) Long    (•) European  ( ) Asia-Pacific
                            [English          ▾]
```

- Summary length radio stays as-is (left column)
- Right column adds a region radio above the output language selectbox
- Same filtering behavior as the translate tab
- Default: European, English

### Changed: Page header copy

- **Subtitle** changes from:
  `"Translate and summarize across 43 European and Asia-Pacific languages using CohereLabs/tiny-aya-water running locally."`
  to:
  `"Translate and summarize text across 43 languages — all running privately on your computer."`
- **Caption** changes from:
  `"Powered by tiny-aya-water · 43 languages"`
  to:
  `"Powered by tiny-aya-water · Supports 43 European and Asia-Pacific languages"`
  (markdown link on model name preserved)

### Changed: Step labels

**Translate tab:**
- "① Choose languages" → "① Pick your languages"
- "② Enter text" → "② Type or paste your text"
- "③ Result" → "③ Translation"

**Summarize tab:**
- "① Choose options" → "① Pick your options"
- "② Enter text" → "② Type or paste your text"
- "③ Result" → "③ Summary"

### Changed: Placeholder text

- Translate text area: unchanged (`"e.g. The weather is nice today"`)
- Summarize text area: `"Paste an article, paragraph, or any text to summarize..."` → `"e.g. Paste an article, email, or paragraph here"`

### Changed: Warning messages

- Translate empty text: `"Please enter some text to translate."` → `"Please enter some text first."`
- Translate same language: `"Source and target language are the same."` → `"Please pick two different languages."`
- Summarize empty text: `"Please enter some text to summarize."` → `"Please enter some text first."`

### Unchanged

- All pure functions: `translate_text`, `summarize_text`, `_generate`, `build_translation_prompt`, `build_summarization_prompt`, `clean_model_output`, `detect_device`, `select_dtype`, `get_summary_config`
- All config variables: `MODEL_ID`, `DEVICE`, `DEFAULT_TEMPERATURE`, `DEFAULT_MAX_TOKENS`, `TOP_P`
- `LANGUAGES` flat list
- `@st.cache_resource` model loading with spinner and error handling
- Tab structure: `st.tabs(["Translate", "Summarize"])`
- Guided ①②③ flow with `st.divider()` between steps
- `st.success(result)` for output display
- Button disabled state when model fails to load
- Spinners during inference (`"Translating..."`, `"Summarizing..."`)

## Widget Keys

The region radios need unique keys to avoid collisions since both tabs use the label "Region":
- Translate source: `key="source_region"`
- Translate target: `key="target_region"`
- Summarize output: `key="output_region"`

## Testing Impact

### Existing unit tests (`test_streamlit_app.py`)

No changes needed — these test pure functions only.

### Existing UI tests (`test_streamlit_ui.py`) — updates required

- **Step label assertions** update to match new copy (e.g., "① Pick your languages")
- **Widget indexing** changes in translate tab: two new radio widgets (region selectors) are added, so `tab.selectbox` and `tab.radio` indices shift
- **Widget indexing** changes in summarize tab: one new radio widget added
- **Warning message assertions** update to match new text
- **Placeholder assertion** for summarize tab updates to new text
- **Caption assertion** updates to match new caption text

### New tests needed

- Switching source region radio to "Asia-Pacific" filters source language selectbox to 12 Asia-Pacific languages
- Switching target region radio to "Asia-Pacific" filters target language selectbox to 12 Asia-Pacific languages
- Switching output region radio in summarize tab filters output language selectbox
- Default language after region switch is the first language in that group
