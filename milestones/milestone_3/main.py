import streamlit as st
import ast
import os
import re
import zipfile
import tempfile
import json
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Code Reviewer", layout="wide")

# ─────────────────────────── CSS ─────────────────────────── #
st.markdown("""
<style>
  .stApp {
      background: linear-gradient(160deg, #0a1628, #0d2137, #0a1f35);
  }
  .stApp, .stApp p, .stApp span, .stApp label,
  .stApp div, .stApp li, .stApp a { color: #e0f7fa !important; }

  h1, h2, h3 { color: #00e5ff !important; text-shadow: 0 0 12px #00e5ff88; }

  section[data-testid="stSidebar"] {
      background: linear-gradient(180deg, #071525, #0d2137) !important;
      border-right: 2px solid #00e5ff;
  }
  section[data-testid="stSidebar"] * { color: #00e5ff !important; }

  [data-testid="stMetricValue"] {
      color: #00e5ff !important; font-size:2rem !important; font-weight:bold !important;
  }
  [data-testid="stMetricLabel"] { color: #80deea !important; }

  .stSelectbox label { color: #00e5ff !important; }
  .stSelectbox > div > div {
      background-color: #0d2137 !important; color: #e0f7fa !important;
      border: 1px solid #00e5ff !important; border-radius: 8px !important;
  }
  [data-baseweb="select"] * { color: #e0f7fa !important; background-color: #0d2137 !important; }

  /* ALL buttons bold — fixed height, no vertical stretch */
  .stButton > button {
      background: linear-gradient(90deg,#00e5ff,#0077b6) !important;
      color: #071525 !important; border: none !important;
      border-radius: 8px !important; font-weight: 900 !important;
      font-size: 1rem !important; letter-spacing: 0.5px !important;
      padding: 10px 16px !important;
      height: 48px !important;
      min-height: 48px !important;
      max-height: 48px !important;
      white-space: nowrap !important;
      overflow: hidden !important;
      line-height: 1.2 !important;
      transition: 0.3s;
  }
  .stButton > button:hover { transform:scale(1.04); box-shadow:0 0 15px #00e5ff; }

  .stDownloadButton > button {
      background: linear-gradient(90deg,#2ecc71,#1abc9c) !important;
      color: #071525 !important; border: none !important;
      border-radius: 8px !important; font-weight: 900 !important; font-size: 1rem !important;
  }

  pre { background-color:#071525 !important; color:#a8ff78 !important; }
  .stCodeBlock, [data-testid="stCode"] {
      background-color:#071525 !important;
      border:1px solid #00e5ff !important; border-radius:8px !important;
  }
  .stCodeBlock pre, [data-testid="stCode"] pre,
  .stCodeBlock code, [data-testid="stCode"] code {
      background-color:#071525 !important; color:#a8ff78 !important;
  }

  [data-testid="stFileUploader"] {
      background-color:#0d2137 !important; border:2px dashed #00e5ff !important;
      border-radius:12px !important; padding:10px !important;
  }
  [data-testid="stFileUploader"] * { color:#e0f7fa !important; background-color:transparent !important; }
  [data-testid="stFileUploaderDropzone"] { background-color:#0d2137 !important; border:none !important; }
  [data-testid="stFileUploaderDropzone"] button {
      background: linear-gradient(90deg,#00e5ff,#0077b6) !important;
      color: #071525 !important; font-weight: 900 !important;
      border: none !important; border-radius: 8px !important;
  }

  .stAlert { border-radius:10px !important; }
  .stAlert p { color:white !important; }
  [data-testid="stInfo"] { background-color:#0d3349 !important; border-left:4px solid #00e5ff !important; }
  hr { border-color:#00e5ff55 !important; }

  .stRadio label { color: #e0f7fa !important; font-weight: bold !important; }
  .stRadio > div { background: #0d2137 !important; border-radius: 8px !important; padding: 6px !important; }

  .stTextInput > div > div > input {
      background-color: #0d2137 !important; color: #e0f7fa !important;
      border: 1px solid #00e5ff !important; border-radius: 8px !important;
  }

  /* Accept button - green */
  div[data-testid="column"]:nth-child(1) .stButton > button {
      background: linear-gradient(90deg,#27ae60,#2ecc71) !important;
      color: #071525 !important;
  }
  /* Reject button - red */
  div[data-testid="column"]:nth-child(2) .stButton > button {
      background: linear-gradient(90deg,#c0392b,#e74c3c) !important;
      color: white !important;
  }
  /* Skip button - orange */
  div[data-testid="column"]:nth-child(3) .stButton > button {
      background: linear-gradient(90deg,#d35400,#e67e22) !important;
      color: white !important;
  }
  /* No Style button - gray */
  div[data-testid="column"]:nth-child(4) .stButton > button {
      background: linear-gradient(90deg,#555,#777) !important;
      color: white !important;
  }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────── HELPERS ─────────────────────────── #

def get_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_functions(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            existing_doc = ast.get_docstring(node) or ""
            functions.append({
                "name": node.name,
                "lineno": node.lineno,
                "end_lineno": node.end_lineno,
                "existing_doc": existing_doc,
                "has_doc": bool(existing_doc)
            })
    return functions

def get_func_source(code, func_name):
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                return "\n".join(code.splitlines()[node.lineno - 1: node.end_lineno])
    except Exception:
        pass
    return ""

def generate_docstring(func_name, code_snippet, style, model):
    style_instructions = {
        "Google": "Use Google style docstrings with Args:, Returns:, Raises: sections.",
        "NumPy":  "Use NumPy style docstrings with Parameters, Returns, Examples sections using dashed underlines.",
        "reST":   "Use reStructuredText (reST) style with :param:, :type:, :returns:, :rtype: tags."
    }
    prompt = f"""You are a Python documentation expert.
Generate ONLY a docstring for the function below.
{style_instructions.get(style, style_instructions['Google'])}
Return ONLY the docstring between triple quotes. No explanation.

Function:
{code_snippet}
"""
    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"```(?:python)?\n?", "", raw).replace("```", "").strip()
        if not raw.startswith('"""'): raw = '"""' + raw
        if not raw.endswith('"""'):   raw = raw + '"""'
        return raw
    except Exception as e:
        return f'"""Error: {e}"""'

def inject_docstring_into_code(code, func_name, new_docstring):
    try:
        tree  = ast.parse(code)
        lines = code.splitlines()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                def_line = node.lineno - 1
                if (isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, ast.Constant) and
                        isinstance(node.body[0].value.value, str)):
                    ds = node.body[0]
                    lines[ds.lineno - 1: ds.end_lineno] = []
                indent = "    "
                if def_line + 1 < len(lines):
                    detected = ""
                    for ch in lines[def_line + 1]:
                        if ch in (" ", "\t"): detected += ch
                        else: break
                    if detected: indent = detected
                doc_lines    = new_docstring.splitlines()
                indented_doc = "\n".join(indent + l if l.strip() else l for l in doc_lines)
                lines.insert(def_line + 1, indented_doc)
                return "\n".join(lines)
    except Exception:
        pass
    return code

def save_to_disk(filepath, content):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        # Touch file timestamp so VS Code file watcher triggers reload
        import time
        os.utime(filepath, (time.time(), time.time()))
        return True, None
    except Exception as e:
        return False, str(e)

def setup_vscode_autoreload(project_dir):
    """Create .vscode/settings.json to enable auto-reload in VS Code."""
    try:
        vscode_dir = os.path.join(project_dir, ".vscode")
        os.makedirs(vscode_dir, exist_ok=True)
        settings_path = os.path.join(vscode_dir, "settings.json")

        # Read existing settings if any
        existing = {}
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                import json as _json
                try:
                    existing = _json.load(f)
                except Exception:
                    existing = {}

        # Apply auto-reload settings
        existing["files.autoSave"]              = "onFocusChange"
        existing["files.watcherExclude"]        = {}
        existing["editor.formatOnSave"]         = False
        existing["workbench.editor.autoLockGroups"] = {}

        with open(settings_path, "w") as f:
            import json as _json
            _json.dump(existing, f, indent=4)
        return True
    except Exception:
        return False

def try_save_vscode(active_file, updated_code, project_dir, fdata):
    disk_path = fdata.get("path")
    if disk_path and os.path.exists(disk_path):
        ok, err = save_to_disk(disk_path, updated_code)
        return ok, disk_path, err
    if project_dir and os.path.isdir(project_dir):
        candidate = os.path.join(project_dir, active_file)
        ok, err   = save_to_disk(candidate, updated_code)
        return ok, candidate, err
    return False, None, "No disk path"

def scan_folder(folder_path):
    found = {}
    if not os.path.isdir(folder_path):
        return found, f"Folder not found: {folder_path}"
    for root, _, files in os.walk(folder_path):
        for fname in files:
            if fname.endswith(".py") and not fname.startswith("__"):
                full = os.path.join(root, fname)
                try:
                    with open(full, "r", encoding="utf-8") as f:
                        found[fname] = {"code": f.read(), "path": full}
                except Exception:
                    pass
    return found, None

def read_zip_files(zip_file):
    files = {}
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "upload.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_file.read())
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(tmpdir)
            for root, _, filenames in os.walk(tmpdir):
                for name in filenames:
                    if name.endswith(".py") and not name.startswith("__"):
                        full = os.path.join(root, name)
                        with open(full, "r", encoding="utf-8") as pf:
                            files[name] = {"code": pf.read(), "path": full}
    return files


# ─────────────────────────── SESSION STATE ─────────────────────────── #

for key, default in [
    ("files_data",    {}),
    ("selected_style","Google"),
    ("generated_docs",{}),
    ("accepted_funcs",set()),
    ("skipped_funcs", set()),
    ("modified_codes",{}),
    ("selected_file", None),
    ("page",          "📋 Docstring Review"),
    ("project_dir",   ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────── SIDEBAR ─────────────────────────── #

st.sidebar.markdown(
    "<h2 style='color:#00e5ff; font-weight:900;'>🤖 AI Code Reviewer</h2>",
    unsafe_allow_html=True
)
st.sidebar.divider()

# ── NAVIGATION ──
st.sidebar.markdown(
    "<p style='font-weight:900; font-size:1rem; color:#00e5ff;'>🧭 NAVIGATION</p>",
    unsafe_allow_html=True
)

if st.sidebar.button("📋 Docstring Review", use_container_width=True):
    st.session_state.page = "📋 Docstring Review"

if st.sidebar.button("📊 Coverage Report", use_container_width=True):
    st.session_state.page = "📊 Coverage Report"

# Show active page indicator
st.sidebar.markdown(
    f"<div style='background:#00e5ff22; border:1px solid #00e5ff; border-radius:8px;"
    f"padding:6px 12px; text-align:center; font-weight:900; color:#00e5ff; margin-top:4px;'>"
    f"▶ {st.session_state.page}</div>",
    unsafe_allow_html=True
)

st.sidebar.divider()

# ── CONFIGURATION ──
st.sidebar.markdown(
    "<p style='font-weight:900; font-size:1rem; color:#00e5ff;'>⚙️ CONFIGURATION</p>",
    unsafe_allow_html=True
)
st.sidebar.markdown(
    "<small style='color:#80deea;'>Click BROWSE to pick your project folder directly. "
    "Accepted docstrings will auto-save there for VS Code sync.</small>",
    unsafe_allow_html=True
)

# ── FOLDER PICKER via tkinter ──
def pick_folder():
    """Open native OS folder browser dialog."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', True)
        folder = filedialog.askdirectory(title="Select Your Project Folder")
        root.destroy()
        return folder if folder else ""
    except Exception:
        return ""

if "project_dir" not in st.session_state:
    st.session_state.project_dir = ""

# Show selected folder or placeholder
if st.session_state.project_dir:
    st.sidebar.markdown(
        f"<div style='background:#0d2137; border:1px solid #2ecc71; border-radius:8px;"
        f"padding:8px 10px; font-size:0.8rem; color:#2ecc71; font-weight:bold;"
        f"word-break:break-all; margin-bottom:6px;'>"
        f"📁 {st.session_state.project_dir}</div>",
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        "<div style='background:#0d2137; border:1px dashed #555; border-radius:8px;"
        "padding:8px 10px; font-size:0.8rem; color:#7f8c8d; margin-bottom:6px;'>"
        "📁 No folder selected yet</div>",
        unsafe_allow_html=True
    )

# BROWSE button — opens native OS folder picker popup
if st.sidebar.button("📂 BROWSE & SELECT FOLDER", use_container_width=True):
    selected = pick_folder()
    if selected:
        st.session_state.project_dir = selected
        # Auto-setup VS Code settings for instant reload
        setup_vscode_autoreload(selected)
        st.rerun()
    else:
        st.sidebar.warning("⚠️ No folder was selected.")

# Clear folder button
if st.session_state.project_dir:
    if st.sidebar.button("✖ Clear Selected Folder", use_container_width=True):
        st.session_state.project_dir = ""
        st.rerun()

project_dir = st.session_state.project_dir
log_file = st.sidebar.text_input("📝 Log File Path", value="storage/review_logs.json")

GROQ_MODELS = {
    "🧠 LLaMA 3.3 70B (Smart)":     "llama-3.3-70b-versatile",
    "⚡ LLaMA 3.1 8B (Fast)":       "llama-3.1-8b-instant",
    "🚀 OPEN AI 120B ":              "openai/gpt-oss-120b",
    "💡 OPEN AI 20B ":              "openai/gpt-oss-20b",
}
model_label    = st.sidebar.selectbox("🤖 Groq Model", list(GROQ_MODELS.keys()))
selected_model = GROQ_MODELS[model_label]

st.sidebar.divider()

# ── SCAN PROJECT ──
st.sidebar.markdown(
    "<p style='font-weight:900; font-size:1rem; color:#f39c12;'>🔍 SCAN PROJECT</p>",
    unsafe_allow_html=True
)
if st.sidebar.button("▶ SCAN NOW", use_container_width=True):
    if project_dir and os.path.isdir(project_dir):
        found, err = scan_folder(project_dir)
        if err:
            st.sidebar.error(err)
        else:
            st.session_state.files_data.update(found)
            st.sidebar.success(f"✅ Found {len(found)} .py files!")
    else:
        st.sidebar.warning("⚠️ Enter a valid folder path above.")

st.sidebar.divider()

# ── DEPLOY / RUN — BOLD & VISIBLE ──
st.sidebar.markdown(
    "<p style='font-weight:900; font-size:1.1rem; color:#2ecc71; "
    "text-shadow: 0 0 8px #2ecc71; letter-spacing:1px;'>🚀 DEPLOY / RUN</p>",
    unsafe_allow_html=True
)
st.sidebar.markdown(
    "<div style='background: linear-gradient(90deg,#27ae60,#2ecc71); "
    "border-radius:10px; padding:10px 14px; text-align:center; "
    "font-weight:900; font-size:1rem; color:#071525; "
    "box-shadow: 0 0 12px #2ecc71; letter-spacing:1px;'>"
    "streamlit run milestone3_app.py"
    "</div>",
    unsafe_allow_html=True
)

st.sidebar.divider()
st.sidebar.markdown(
    "<p style='color:#80deea; font-size:0.8rem;'>Milestone 3 · Docstring Generation</p>",
    unsafe_allow_html=True
)


# ─────────────────────────── HEADER ─────────────────────────── #

st.markdown(
    "<h1 style='text-align:center;'>🛠️ AI Powered Code Reviewer</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center; color:#80deea; font-size:1.1rem;'>"
    "Milestone 3 — Docstring Generation Dashboard</p>",
    unsafe_allow_html=True
)
st.divider()

page = st.session_state.page


# ════════════════════════════════════════════════════
#  PAGE: DOCSTRING REVIEW
# ════════════════════════════════════════════════════

if page == "📋 Docstring Review":

    st.markdown("## 📋 Docstring Review")

    # ── Style Buttons ──
    st.markdown(
        "<p style='font-weight:900; font-size:1.1rem; color:#00e5ff;'>📌 SELECT DOCSTRING STYLE</p>",
        unsafe_allow_html=True
    )

    cg, cn, cr, cnone = st.columns(4)
    with cg:
        if st.button("🟢  Google Style", key="style_google"):
            st.session_state.selected_style = "Google"
            st.rerun()
    with cn:
        if st.button("🔵  NumPy Style", key="style_numpy"):
            st.session_state.selected_style = "NumPy"
            st.rerun()
    with cr:
        if st.button("🟠  reST Style", key="style_rest"):
            st.session_state.selected_style = "reST"
            st.rerun()
    with cnone:
        if st.button("⚫  No Style", key="style_none"):
            st.session_state.selected_style = "None"
            st.rerun()

    style = st.session_state.selected_style
    style_colors = {
        "Google": "#2ecc71", "NumPy": "#3498db",
        "reST": "#e67e22",   "None":  "#7f8c8d"
    }
    sc = style_colors.get(style, "#00e5ff")
    st.markdown(
        f"<div style='background:{sc}22; border:2px solid {sc}; border-radius:10px;"
        f"padding:10px 20px; font-weight:900; color:{sc}; font-size:1rem; margin-top:8px;'>"
        f"{'⚫ No Style — Code kept as-is, no docstrings will be added' if style == 'None' else f'✅ Active Style: {style}'}"
        f"</div>",
        unsafe_allow_html=True
    )

    st.divider()

    # ── Upload ──
    st.markdown(
        "<p style='font-weight:900; font-size:1.1rem; color:#00e5ff;'>📂 UPLOAD PYTHON FILES OR ZIP FOLDER</p>",
        unsafe_allow_html=True
    )
    upload_mode = st.radio("Upload Mode", ["📄 Individual .py Files", "📦 ZIP Folder"], horizontal=True)

    if upload_mode == "📄 Individual .py Files":
        uploaded = st.file_uploader("Upload one or more .py files", type=["py"], accept_multiple_files=True)
        if uploaded:
            for f in uploaded:
                fname     = f.name
                code      = f.read().decode("utf-8")
                disk_path = None
                if project_dir and os.path.isdir(project_dir):
                    candidate = os.path.join(project_dir, fname)
                    if os.path.exists(candidate):
                        disk_path = candidate
                st.session_state.files_data[fname] = {"code": code, "path": disk_path}
            st.success(f"✅ {len(uploaded)} file(s) loaded!")
    else:
        zip_upload = st.file_uploader("Upload a ZIP of your project folder", type=["zip"])
        if zip_upload:
            extracted = read_zip_files(zip_upload)
            st.session_state.files_data.update(extracted)
            st.success(f"✅ Extracted {len(extracted)} .py file(s) from ZIP!")

    st.divider()

    if st.session_state.files_data:

        left, right = st.columns([1, 2])

        # ── LEFT: Project Files ──
        with left:
            st.markdown(
                "<h3 style='background:linear-gradient(90deg,#4e54c8,#8f94fb);"
                "padding:10px 16px; border-radius:10px; font-weight:900;'>📁 Project Files</h3>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<p style='color:#80deea;'>Total: <b>{len(st.session_state.files_data)}</b> "
                f"files | Style: <b style='color:{sc};'>{style}</b></p>",
                unsafe_allow_html=True
            )

            for fname, fdata in st.session_state.files_data.items():
                code   = st.session_state.modified_codes.get(fname, fdata["code"])
                funcs  = extract_functions(code)
                needed = sum(1 for f in funcs if not f["has_doc"])

                is_active = (st.session_state.selected_file == fname)
                border    = "2px solid #00e5ff" if is_active else "1px solid #00e5ff33"
                fc1, fc2  = st.columns([3, 1])
                with fc1:
                    if st.button(f"📄 {fname}", key=f"file_{fname}", use_container_width=True):
                        st.session_state.selected_file = fname
                        st.rerun()
                with fc2:
                    if needed > 0:
                        st.markdown(
                            f"<div style='background:#e74c3c; color:white; border-radius:8px;"
                            f"padding:4px 6px; text-align:center; font-size:0.75rem; font-weight:900;'>"
                            f"{needed} needed</div>", unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            "<div style='background:#2ecc71; color:#071525; border-radius:8px;"
                            "padding:4px 6px; text-align:center; font-size:0.75rem; font-weight:900;'>"
                            "✅ Done</div>", unsafe_allow_html=True
                        )

        # ── RIGHT: Function Review ──
        with right:
            st.markdown(
                "<h3 style='background:linear-gradient(90deg,#6c3483,#a569bd);"
                "padding:10px 16px; border-radius:10px; font-weight:900;'>⚙️ Function Review</h3>",
                unsafe_allow_html=True
            )

            active_file = st.session_state.selected_file
            if not active_file and st.session_state.files_data:
                active_file = list(st.session_state.files_data.keys())[0]
                st.session_state.selected_file = active_file

            if active_file:
                fdata     = st.session_state.files_data[active_file]
                code      = st.session_state.modified_codes.get(active_file, fdata["code"])
                funcs     = extract_functions(code)

                if not funcs:
                    st.warning("⚠️ No functions found in this file.")
                else:
                    func_names    = [f["name"] for f in funcs]
                    selected_func = st.selectbox("🔧 **Select Function**", func_names, key="func_select")
                    func_info     = next(f for f in funcs if f["name"] == selected_func)
                    func_src      = get_func_source(code, selected_func)
                    gen_key       = f"{active_file}::{selected_func}::{style}"

                    # ── GENERATE BUTTON ──
                    if style != "None":
                        if st.button(
                            f"✨ GENERATE {style.upper()} DOCSTRING",
                            key=f"gen_{gen_key}",
                            use_container_width=True
                        ):
                            with st.spinner(f"⏳ Generating {style} docstring via Groq AI..."):
                                doc = generate_docstring(selected_func, func_src, style, selected_model)
                                st.session_state.generated_docs[gen_key] = doc
                            st.success("✅ Docstring generated! Click an action below.")
                    else:
                        st.markdown(
                            "<div style='background:#1a1a1a; border:1px solid #555; border-radius:8px;"
                            "padding:10px; color:#bdc3c7; text-align:center; font-weight:bold;'>"
                            "⚫ No Style selected — switch to Google / NumPy / reST to generate.</div>",
                            unsafe_allow_html=True
                        )

                    # ── DIFF VIEW ──
                    st.markdown("---")
                    cur_col, gen_col = st.columns(2)
                    with cur_col:
                        st.markdown(
                            "<p style='font-weight:900; color:#80deea;'>📄 Current Docstring</p>",
                            unsafe_allow_html=True
                        )
                        st.code(
                            f'"""{func_info["existing_doc"] or "No docstring."}"""',
                            language="python"
                        )
                    with gen_col:
                        st.markdown(
                            f"<p style='font-weight:900; color:#00e5ff;'>✨ Generated ({style})</p>",
                            unsafe_allow_html=True
                        )
                        generated = st.session_state.generated_docs.get(gen_key, "")
                        if generated:
                            st.code(generated, language="python")
                        else:
                            st.info("👆 Click GENERATE to preview the docstring here.")

                    # ── REJECTED VERSIONS HISTORY ──
                    history_key = f"history_{gen_key}"
                    history = st.session_state.get(history_key, [])
                    if history:
                        with st.expander(f"🗂️ View {len(history)} Rejected Version(s)", expanded=False):
                            for i, old_doc in enumerate(history, 1):
                                st.markdown(
                                    f"<p style='color:#e74c3c; font-weight:900;'>❌ Rejected Version {i}</p>",
                                    unsafe_allow_html=True
                                )
                                st.code(old_doc, language="python")
                                st.markdown("---")

                    # ══════════════════════════════════════
                    #  4 ACTION BUTTONS (inline, click to perform)
                    # ══════════════════════════════════════
                    st.markdown("---")
                    st.markdown(
                        "<p style='font-weight:900; font-size:1.1rem; color:#f39c12;'>"
                        "🎯 CHOOSE ACTION — Click to apply instantly</p>",
                        unsafe_allow_html=True
                    )

                    a1, a2, a3, a4 = st.columns(4)

                    # ── ACCEPT & APPLY ──
                    with a1:
                        if st.button("✅ Accept & Apply", key=f"accept_{gen_key}", use_container_width=True):
                            if not generated:
                                st.error("❌ Generate a docstring first.")
                            else:
                                updated = inject_docstring_into_code(code, selected_func, generated)
                                st.session_state.modified_codes[active_file] = updated
                                st.session_state.accepted_funcs.add(gen_key)
                                saved, path, err = try_save_vscode(
                                    active_file, updated, project_dir, fdata
                                )
                                if saved:
                                    st.success(
                                        f"✅ **SAVED TO DISK & VS CODE WILL AUTO-RELOAD!**\n\n"
                                        f"📁 `{path}`\n\n"
                                        f"🖥️ Just **click on the file in VS Code** — "
                                        f"it will show the updated docstring automatically."
                                    )
                                else:
                                    st.success("✅ Accepted in app!")
                                    st.info(
                                        "💡 Click **📂 BROWSE & SELECT FOLDER** in the sidebar "
                                        "to enable auto-save directly to VS Code."
                                    )
                                st.rerun()

                    # ── REJECT & REGENERATE ──
                    with a2:
                        if st.button("🔄 Reject & Regenerate", key=f"reject_{gen_key}", use_container_width=True):
                            if not generated:
                                st.warning("⚠️ Nothing to reject — generate a docstring first.")
                            else:
                                # Track previous versions
                                history_key = f"history_{gen_key}"
                                if history_key not in st.session_state:
                                    st.session_state[history_key] = []
                                # Save rejected version to history
                                st.session_state[history_key].append(generated)

                                with st.spinner("🔄 Regenerating a new docstring..."):
                                    new_doc = generate_docstring(selected_func, func_src, style, selected_model)
                                    st.session_state.generated_docs[gen_key] = new_doc
                                st.session_state.accepted_funcs.discard(gen_key)
                                rejected_count = len(st.session_state[history_key])
                                st.warning(f"🔄 Rejected version {rejected_count}. New docstring generated — review it above!")
                                st.rerun()

                    # ── SKIP THIS STYLE ──
                    with a3:
                        if st.button("⏭️ Skip Style", key=f"skip_{gen_key}", use_container_width=True):
                            st.session_state.skipped_funcs.add(gen_key)
                            st.info(
                                f"⏭️ Skipped `{selected_func}` for **{style}**.\n\n"
                                f"Switch to a different style and generate again."
                            )
                            st.rerun()

                    # ── NO STYLE ──
                    with a4:
                        if st.button("⚫ No Style", key=f"nostyle_{gen_key}", use_container_width=True):
                            st.info(
                                f"⚫ No style applied — `{selected_func}` kept as original.\n\n"
                                f"No changes made to the file."
                            )

                    # ── Status Badges ──
                    st.markdown("")
                    b1, b2, _, _ = st.columns(4)
                    with b1:
                        if gen_key in st.session_state.accepted_funcs:
                            st.markdown(
                                "<div style='background:#2ecc71; color:#071525; border-radius:8px;"
                                "padding:6px; text-align:center; font-weight:900;'>"
                                "✅ ACCEPTED</div>", unsafe_allow_html=True
                            )
                    with b2:
                        if gen_key in st.session_state.skipped_funcs:
                            st.markdown(
                                "<div style='background:#e67e22; color:#071525; border-radius:8px;"
                                "padding:6px; text-align:center; font-weight:900;'>"
                                "⏭️ SKIPPED</div>", unsafe_allow_html=True
                            )

        # ── Download Updated Files ──
        st.divider()
        st.markdown(
            "<p style='font-weight:900; font-size:1.1rem; color:#2ecc71;'>💾 DOWNLOAD UPDATED FILES</p>",
            unsafe_allow_html=True
        )
        if st.session_state.modified_codes:
            dl_cols = st.columns(min(len(st.session_state.modified_codes), 4))
            for i, (fname, updated_code) in enumerate(st.session_state.modified_codes.items()):
                with dl_cols[i % 4]:
                    st.download_button(
                        f"⬇️ {fname}",
                        data=updated_code,
                        file_name=fname,
                        mime="text/x-python",
                        key=f"dl_{fname}"
                    )
        else:
            st.info("💡 Accept docstrings above to enable file download.")

        # ── Bulk Generate ──
        st.divider()
        st.markdown(
            "<p style='font-weight:900; font-size:1.1rem; color:#f39c12;'>"
            "⚡ BULK: GENERATE ALL MISSING DOCSTRINGS AT ONCE</p>",
            unsafe_allow_html=True
        )
        if style == "None":
            st.warning("⚫ Switch to Google / NumPy / reST to use bulk generate.")
        else:
            if st.button("⚡ GENERATE ALL & AUTO-SAVE TO VSCODE", use_container_width=True):
                all_funcs = [
                    (fname, fn["name"])
                    for fname, fdata in st.session_state.files_data.items()
                    for fn in extract_functions(fdata["code"])
                    if not fn["has_doc"]
                ]
                if not all_funcs:
                    st.info("✅ All functions already have docstrings!")
                else:
                    progress    = st.progress(0)
                    status_text = st.empty()
                    saved_count = 0
                    for idx, (fname, func_name) in enumerate(all_funcs):
                        status_text.markdown(
                            f"<p style='color:#00e5ff; font-weight:bold;'>"
                            f"⏳ Processing `{func_name}` in `{fname}`...</p>",
                            unsafe_allow_html=True
                        )
                        fdata   = st.session_state.files_data[fname]
                        code    = st.session_state.modified_codes.get(fname, fdata["code"])
                        src     = get_func_source(code, func_name)
                        doc     = generate_docstring(func_name, src, style, selected_model)
                        gk      = f"{fname}::{func_name}::{style}"
                        st.session_state.generated_docs[gk] = doc
                        updated = inject_docstring_into_code(code, func_name, doc)
                        st.session_state.modified_codes[fname] = updated
                        ok, path, _ = try_save_vscode(fname, updated, project_dir, fdata)
                        if ok: saved_count += 1
                        progress.progress((idx + 1) / len(all_funcs))

                    status_text.empty()
                    st.success(
                        f"🎉 **Done! Processed {len(all_funcs)} function(s).**\n\n"
                        f"💾 Auto-saved {saved_count} file(s) to disk.\n\n"
                        f"🖥️ Just **click on any file in VS Code** — "
                        f"it will auto-reload with the new docstrings instantly!"
                    )
                    st.rerun()

    else:
        st.markdown(
            "<div style='background:#0d2137; border:2px dashed #00e5ff; border-radius:12px;"
            "padding:40px; text-align:center;'>"
            "<p style='font-size:1.2rem; color:#80deea; font-weight:900;'>"
            "👆 Upload .py files above<br>— OR —<br>"
            "Enter project folder path in sidebar and click <b>▶ SCAN NOW</b></p>"
            "</div>",
            unsafe_allow_html=True
        )


# ════════════════════════════════════════════════════
#  PAGE: COVERAGE REPORT
# ════════════════════════════════════════════════════

elif page == "📊 Coverage Report":

    st.markdown("## 📊 Coverage Report")
    st.divider()

    if not st.session_state.files_data:
        st.info("📂 Upload files in **Docstring Review** first.")
    else:
        total_funcs = 0
        documented  = 0
        report_rows = []

        for fname, fdata in st.session_state.files_data.items():
            modified = st.session_state.modified_codes.get(fname, fdata["code"])
            funcs    = extract_functions(modified)
            tf = len(funcs)
            td = sum(1 for f in funcs if f["has_doc"])
            total_funcs += tf
            documented  += td
            cov = round((td / tf * 100) if tf else 0, 1)
            report_rows.append({
                "File": fname,
                "Total Functions": tf,
                "Documented": td,
                "Missing": tf - td,
                "Coverage %": cov,
                "Status": "✅ Rich" if cov >= 80 else ("⚠️ Moderate" if cov >= 50 else "❌ Poor")
            })

        overall = round((documented / total_funcs * 100) if total_funcs else 0, 1)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📁 Total Files",      len(st.session_state.files_data))
        c2.metric("🔧 Total Functions",  total_funcs)
        c3.metric("📝 Documented",       documented)
        c4.metric("📊 Overall Coverage", f"{overall}%")

        st.divider()
        if overall >= 90:
            st.success(f"🎉 **Coverage {overall}%** — Meets the 90% threshold! ✅")
        elif overall >= 50:
            st.warning(f"⚠️ **Coverage {overall}%** — Below 90% threshold.")
        else:
            st.error(f"❌ **Coverage {overall}%** — Poor. Generate docstrings first.")

        st.divider()
        st.markdown(
            "<p style='font-weight:900; font-size:1.1rem; color:#00e5ff;'>📋 PER-FILE BREAKDOWN</p>",
            unsafe_allow_html=True
        )
        st.dataframe(pd.DataFrame(report_rows), use_container_width=True)

        st.divider()
        report_json = json.dumps(report_rows, indent=4)
        st.download_button(
            "⬇️ DOWNLOAD COVERAGE REPORT (JSON)",
            report_json,
            file_name="coverage_report.json",
            mime="application/json"
        )