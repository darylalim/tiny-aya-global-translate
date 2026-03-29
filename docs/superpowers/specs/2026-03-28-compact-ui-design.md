# Compact UI Design

Simplify the Streamlit interface by removing visual clutter — region radios, step labels, dividers, and the summary length selector — to create a compact, Google Translate-like experience.

## Goals

- Reduce visual noise so the page is easy to scan at a glance
- Serve both technical and non-technical users
- Keep the existing two-tab structure (Translate / Summarize)

## Page Header

- Keep `st.title("Tiny Aya Water")`
- Remove the `st.caption` (model name, language count) entirely

## Language Selection

- Remove all region radio buttons (`source_region`, `target_region`, `output_region`)
- Use the flat `LANGUAGES` list (43 items) directly in `st.selectbox`
- Streamlit's built-in type-to-search handles discoverability
- `LANGUAGE_GROUPS` stays in code but is no longer used by the UI

## Translate Tab

- Three `st.columns` — source language selectbox, a narrow center column with "→" text, target language selectbox
- Defaults: English (source), French (target)
- Text area below with placeholder "Type or paste your text here..."
- "Translate" button below the text area
- Result appears in `st.success` directly below the button
- No step labels, no dividers, no bold markdown headers

## Summarize Tab

- Output language selectbox at the top (full width)
- Default: English
- Text area below with placeholder "Paste an article, email, or paragraph here..."
- "Summarize" button below the text area
- Result appears in `st.success` directly below the button
- No step labels, no dividers, no summary length radio

## Auto Summary Length

A new pure function `select_summary_length(text: str) -> str` determines summary length from input size:

- Under 500 characters: "Short" (1-2 sentences)
- 500-2000 characters: "Medium" (short paragraph)
- Over 2000 characters: "Long" (detailed summary)

This reuses the existing `get_summary_config` and `build_summarization_prompt` functions — only the selection is automated instead of user-chosen.

## Removed Elements

| Element | Where | Why |
|---|---|---|
| Region radio buttons | Both tabs | Replaced by flat searchable dropdown |
| Step labels (bold ①②③) | Both tabs | Unnecessary with compact layout |
| Dividers | Both tabs | Whitespace provides enough separation |
| Summary length radio | Summarize tab | Auto-determined from input length |
| `st.caption` | Page header | Technical detail that adds noise |

## Validation

Existing validation stays unchanged:

- Empty text: `st.warning("Please enter some text first.")`
- Same source/target language (Translate only): `st.warning("Please pick two different languages.")`

## Testing

- Update existing UI tests to reflect removed elements (no region radios, no step labels, no summary length radio)
- Add unit tests for `select_summary_length` function
- Update existing tests that reference removed UI components
