# UI Refresh Design

## Goal

Light UI refresh to the Tiny Aya Water Streamlit app: cleaner chrome, copy-friendly output, and a more prominent translate action.

## Changes

### 1. Change title

- **Current:** `st.title("Tiny Aya Water")`
- **New:** `st.title("Tiny Aya Water Translate")`

### 2. Remove subtitle

- **Remove:** `st.markdown("Translate text — running privately on your computer.")`

### 3. Remove language selectbox labels

- **Current:** `st.selectbox("From", ...)` and `st.selectbox("To", ...)`
- **New:** Set `label_visibility="collapsed"` on both selectboxes to hide the "From" and "To" labels

### 4. Remove swap button padding hack

- **Current:** `st.html("<div style='padding-top:1.8rem'></div>")` adds vertical spacing to align the swap button below the "From"/"To" labels
- **New:** Remove this spacer. Without labels, the swap button aligns naturally with the selectboxes.

### 5. Replace output text area with st.code()

- **Current:** `st.text_area("Output", value=..., disabled=True, label_visibility="collapsed")`
- **New:** `st.code(st.session_state.translate_output, language=None)` — provides a built-in copy button with no custom code
- `language=None` disables syntax highlighting since the output is natural language, not code
- Trade-off: monospace font and gray background on the output panel

### 6. Make Translate button primary type

- **Current:** `st.button("Translate", ...)`
- **New:** `st.button("Translate", ..., type="primary")` for visual prominence

## Files affected

- `streamlit_app.py` — all 6 changes are in the UI section (lines 190–283)
- `test_streamlit_ui.py` — update tests that reference the output text area (`app.text_area[1]`) since it becomes `st.code()`

## Out of scope

- No CSS injection or custom styling
- No layout/structural changes (columns, containers)
- No changes to pure functions, model loading, or session state logic
