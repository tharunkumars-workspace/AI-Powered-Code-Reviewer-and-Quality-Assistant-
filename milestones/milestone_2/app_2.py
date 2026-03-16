import streamlit as st
import ast
import json
import os
import re
import matplotlib.pyplot as plt
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Powered Code Reviewer", layout="wide")

# ---------------- CUSTOM CSS ---------------- #

st.markdown("""
<style>

    /* ── Main background ── */
    .stApp {
        background: linear-gradient(160deg, #0a1628, #0d2137, #0a1f35);
    }

    /* ── Force ALL text white ── */
    .stApp, .stApp p, .stApp span, .stApp label,
    .stApp div, .stApp li, .stApp a {
        color: #e0f7fa !important;
    }

    h1, h2, h3 {
        color: #00e5ff !important;
        text-shadow: 0 0 12px #00e5ff88;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #071525, #0d2137) !important;
        border-right: 2px solid #00e5ff;
    }
    section[data-testid="stSidebar"] * {
        color: #00e5ff !important;
    }

    /* ── Metric cards ── */
    [data-testid="stMetricValue"] {
        color: #00e5ff !important;
        font-size: 2rem !important;
        font-weight: bold !important;
    }
    [data-testid="stMetricLabel"] {
        color: #80deea !important;
    }

    /* ── Selectbox ── */
    .stSelectbox label { color: #00e5ff !important; }
    .stSelectbox > div > div {
        background-color: #0d2137 !important;
        color: #e0f7fa !important;
        border: 1px solid #00e5ff !important;
        border-radius: 8px !important;
    }
    [data-baseweb="select"] * {
        color: #e0f7fa !important;
        background-color: #0d2137 !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
        background-color: #071525;
        padding: 8px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"]:nth-child(1) { background: #c0392b; border-radius: 8px; }
    .stTabs [data-baseweb="tab"]:nth-child(2) { background: #d35400; border-radius: 8px; }
    .stTabs [data-baseweb="tab"]:nth-child(3) { background: #b7950b; border-radius: 8px; }
    .stTabs [data-baseweb="tab"]:nth-child(4) { background: #1e8449; border-radius: 8px; }
    .stTabs [data-baseweb="tab"]:nth-child(5) { background: #117a65; border-radius: 8px; }
    .stTabs [data-baseweb="tab"]:nth-child(6) { background: #1a5276; border-radius: 8px; }
    .stTabs [data-baseweb="tab"]:nth-child(7) { background: #6c3483; border-radius: 8px; }
    .stTabs [data-baseweb="tab"]:nth-child(8) { background: #922b21; border-radius: 8px; }

    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] span,
    .stTabs [data-baseweb="tab"] div {
        color: white !important;
        font-weight: bold !important;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #00e5ff !important;
        transform: scale(1.05);
        box-shadow: 0 0 10px #00e5ff;
    }

    /* ── CODE BLOCKS — fix white background ── */
    .stCodeBlock, [data-testid="stCode"] {
        background-color: #071525 !important;
        border: 1px solid #00e5ff !important;
        border-radius: 8px !important;
    }
    .stCodeBlock pre, [data-testid="stCode"] pre,
    .stCodeBlock code, [data-testid="stCode"] code {
        background-color: #071525 !important;
        color: #a8ff78 !important;
    }
    /* Streamlit uses highlight.js container */
    .stCodeBlock > div {
        background-color: #071525 !important;
    }
    pre {
        background-color: #071525 !important;
        color: #a8ff78 !important;
    }

    /* ── FILE UPLOADER — fix white box ── */
    [data-testid="stFileUploader"] {
        background-color: #0d2137 !important;
        border: 2px dashed #00e5ff !important;
        border-radius: 12px !important;
        padding: 10px !important;
        color: #e0f7fa !important;
    }
    [data-testid="stFileUploader"] * {
        color: #e0f7fa !important;
        background-color: transparent !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        background-color: #0d2137 !important;
        border: none !important;
    }
    /* Browse files button */
    [data-testid="stFileUploaderDropzone"] button {
        background: linear-gradient(90deg, #00e5ff, #0077b6) !important;
        color: #071525 !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 8px !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(90deg, #00e5ff, #0077b6) !important;
        color: #071525 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        transition: 0.3s;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px #00e5ff;
    }

    /* ── Download button ── */
    .stDownloadButton > button {
        background: linear-gradient(90deg, #2ecc71, #1abc9c) !important;
        color: #071525 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background-color: #0d2137 !important;
        color: #00e5ff !important;
        border: 1px solid #00e5ff !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] {
        background-color: #0d2137 !important;
        border: 1px solid #00e5ff33 !important;
        border-radius: 8px !important;
    }

    /* ── Alert boxes ── */
    .stAlert { border-radius: 10px !important; }
    .stAlert p { color: white !important; }

    /* ── Info box ── */
    [data-testid="stInfo"] {
        background-color: #0d3349 !important;
        border-left: 4px solid #00e5ff !important;
    }

    /* ── Divider ── */
    hr { border-color: #00e5ff55 !important; }

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ---------------- #

st.title("🤖 AI Powered Code Reviewer")
st.markdown("<p style='text-align:center; color:#80deea; font-size:1.1rem;'>Groq LLM Based | Docstring Coverage + AI Fix</p>", unsafe_allow_html=True)

# ---------------- SIDEBAR ---------------- #

st.sidebar.title("🎛️ Project Dashboard")

GROQ_MODELS = {
    "🧠 LLaMA 3.3 70B (Smart)":     "llama-3.3-70b-versatile",
    "⚡ LLaMA 3.1 8B (Fast)":       "llama-3.1-8b-instant",
    "🚀 OPEN AI 120B ":              "openai/gpt-oss-120b",
    "💡 OPEN AI 20B ":              "openai/gpt-oss-20b",
}

st.sidebar.markdown("### 🤖 Select Groq Model")
selected_model_label = st.sidebar.selectbox(
    "Model",
    list(GROQ_MODELS.keys()),
    index=0
)
selected_model = GROQ_MODELS[selected_model_label]
st.sidebar.success(f"Active: `{selected_model}`")
st.sidebar.divider()

# ---------------- COMPLEXITY ---------------- #

def calculate_complexity(node):
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (
            ast.If, ast.For, ast.While,
            ast.And, ast.Or,
            ast.ExceptHandler
        )):
            complexity += 1
    return complexity

# ---------------- ANALYSIS ---------------- #

def analyze_code(code):
    tree = ast.parse(code)

    total_functions = 0
    documented_functions = 0
    function_details = []
    issues = []

    lines = code.split("\n")
    start_line = 1
    end_line = len(lines)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            total_functions += 1
            docstring = ast.get_docstring(node)
            complexity = calculate_complexity(node)

            if docstring:
                documented_functions += 1
            else:
                issues.append(f"{node.name} missing docstring (PEP 257)")

            function_details.append({
                "name": node.name,
                "start_line": node.lineno,
                "end_line": node.end_lineno,
                "complexity": complexity,
                "docstring": docstring if docstring else "Missing"
            })

    coverage = 0
    if total_functions > 0:
        coverage = (documented_functions / total_functions) * 100

    if coverage >= 80:
        status = "Rich"
    elif coverage >= 50:
        status = "Moderate"
    else:
        status = "Poor"

    return {
        "start_line": start_line,
        "end_line": end_line,
        "total_functions": total_functions,
        "documented_functions": documented_functions,
        "coverage": coverage,
        "docstring_report": f"{documented_functions}/{total_functions}",
        "function_details": function_details,
        "issues": issues,
        "status": status
    }

# ---------------- AI FIX ---------------- #

def ai_fix_code(code, issues, model):
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        prompt = f"""
You are a professional Python code reviewer.

Fix the following Python code:
- Follow PEP 257
- Add missing docstrings
- Improve formatting

Issues:
{issues}

Return ONLY corrected full Python code.

Code:
{code}
"""

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Groq API Error: {e}"

# ---------------- CLEAN AI CODE ---------------- #

def clean_ai_code(raw_code):
    """Strip markdown code fences from AI response."""
    cleaned = re.sub(r"```(?:python)?\n?", "", raw_code)
    cleaned = cleaned.replace("```", "").strip()
    return cleaned

# ---------------- FILE UPLOAD ---------------- #

st.markdown("### 📂 Upload Python Files")
uploaded_files = st.file_uploader(
    "Drop your .py files here",
    type=["py"],
    accept_multiple_files=True
)

if uploaded_files:

    for file in uploaded_files:

        st.divider()
        st.markdown(f"<h2 style='color:#00e5ff;'>📄 {file.name}</h2>", unsafe_allow_html=True)

        code = file.read().decode("utf-8")
        original_result = analyze_code(code)

        final_result = st.session_state.get(
            f"new_result_{file.name}",
            original_result
        )

        # Sidebar
        st.sidebar.markdown(f"**📄 {file.name}**")
        st.sidebar.markdown(f"<span style='color:#e0f7fa;'>Functions: <b style='color:#00e5ff;'>{final_result['total_functions']}</b></span>", unsafe_allow_html=True)
        st.sidebar.markdown(f"<span style='color:#e0f7fa;'>Coverage: <b style='color:#00e5ff;'>{round(final_result['coverage'], 2)}%</b></span>", unsafe_allow_html=True)
        st.sidebar.markdown(f"<span style='color:#e0f7fa;'>Status: <b style='color:#2ecc71;'>{final_result['status']}</b></span>", unsafe_allow_html=True)
        st.sidebar.divider()

        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "📊 Coverage",
            "🔍 Functions",
            "📝 Source Code",
            "🗂️ JSON Report",
            "🛠️ AI Fix",
            "👁️ Code View",
            "✏️ Modified",
            "📈 Graphs"
        ])

        # -------- TAB 1 -------- #
        with tab1:
            st.markdown("## 📊 Coverage Report")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Functions", final_result["total_functions"])
            col2.metric("Documented", final_result["documented_functions"])
            col3.metric("Coverage %", f"{round(final_result['coverage'], 2)}%")

            st.markdown(f"<p style='color:#e0f7fa;'>▶ <b>Start Line:</b> {final_result['start_line']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#e0f7fa;'>▶ <b>End Line:</b> {final_result['end_line']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#e0f7fa;'>▶ <b>Docstring Report:</b> {final_result['docstring_report']}</p>", unsafe_allow_html=True)

            if final_result["status"] == "Rich":
                st.success("✅ Rich Documentation Quality")
            elif final_result["status"] == "Moderate":
                st.warning("⚠️ Moderate Documentation")
            else:
                st.error("❌ Poor Documentation")

        # -------- TAB 2 -------- #
        with tab2:
            st.markdown("## 🔍 Function Details")
            for func in final_result["function_details"]:
                with st.expander(f"🔧 {func['name']}"):
                    st.markdown(f"<p style='color:#e0f7fa;'>📍 <b>Start Line:</b> {func['start_line']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color:#e0f7fa;'>📍 <b>End Line:</b> {func['end_line']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color:#e0f7fa;'>🔁 <b>Complexity:</b> {func['complexity']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color:#e0f7fa;'>📝 <b>Docstring:</b> {func['docstring']}</p>", unsafe_allow_html=True)

        # -------- TAB 3 -------- #
        with tab3:
            st.markdown("## 📝 Source Code")
            st.code(code, language="python")

        # -------- TAB 4 -------- #
        with tab4:
            st.markdown("## 🗂️ JSON Output")
            json_output = json.dumps(final_result, indent=4)
            st.code(json_output, language="json")
            st.download_button(
                "⬇️ Download Coverage Report",
                json_output,
                file_name=f"{file.name}_report.json"
            )

        # -------- TAB 5 -------- #
        with tab5:
            st.markdown("## 🛠️ AI Fix + Validation")
            st.info(f"🤖 Using Model: `{selected_model}`")

            if original_result["issues"]:
                for issue in original_result["issues"]:
                    col1, col2 = st.columns([4, 1])
                    col1.error(f"⚠️ {issue}")

                    if col2.button("🔧 Fix", key=f"{file.name}-{issue}"):
                        with st.spinner("🤖 AI is fixing the issue..."):
                            fixed_code = ai_fix_code(code, issue, selected_model)
                            fixed_code = clean_ai_code(fixed_code)
                            st.session_state[f"modified_{file.name}"] = fixed_code
                            try:
                                new_result = analyze_code(fixed_code)
                                st.session_state[f"new_result_{file.name}"] = new_result
                                st.session_state[f"fix_msg_{file.name}"] = "success"
                            except SyntaxError as e:
                                st.session_state[f"fix_msg_{file.name}"] = f"error: {e}"

                if st.button("⚡ Fix All Issues", key=f"all_{file.name}"):
                    with st.spinner("🤖 AI is fixing all issues..."):
                        fixed_code = ai_fix_code(code, original_result["issues"], selected_model)
                        fixed_code = clean_ai_code(fixed_code)
                        st.session_state[f"modified_{file.name}"] = fixed_code
                        try:
                            new_result = analyze_code(fixed_code)
                            st.session_state[f"new_result_{file.name}"] = new_result
                            st.session_state[f"fix_msg_{file.name}"] = "all_success"
                        except SyntaxError as e:
                            st.session_state[f"fix_msg_{file.name}"] = f"error: {e}"

                msg = st.session_state.get(f"fix_msg_{file.name}", "")
                if msg == "success":
                    st.success("✅ Issue Fixed Successfully!")
                elif msg == "all_success":
                    st.success("✅ All Issues Fixed Successfully!")
                elif msg.startswith("error"):
                    st.error(f"❌ AI returned unparseable code: {msg}")

            else:
                st.success("✅ No PEP 257 Violations Found!")

        # -------- TAB 6 -------- #
        with tab6:
            st.markdown("## 👁️ Uploaded Code View")
            st.code(code, language="python")
            st.download_button("⬇️ Download Uploaded Code", code, file.name)

        # -------- TAB 7 -------- #
        with tab7:
            st.markdown("## ✏️ Modified Code View")
            modified_code = st.session_state.get(
                f"modified_{file.name}",
                "No modifications yet."
            )
            st.code(modified_code, language="python")
            st.download_button(
                "⬇️ Download Modified Code",
                modified_code,
                f"modified_{file.name}"
            )

        # -------- TAB 8 -------- #
        with tab8:
            st.markdown("## 📈 Graphical Visualization")

            labels = ["Documented", "Missing"]
            values = [
                final_result["documented_functions"],
                final_result["total_functions"] - final_result["documented_functions"]
            ]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🥧 Pie Chart")
                fig1, ax1 = plt.subplots()
                fig1.patch.set_facecolor("#071525")
                ax1.set_facecolor("#071525")
                ax1.pie(values, labels=labels,
                        autopct="%1.1f%%",
                        colors=["#2ecc71", "#e74c3c"],
                        textprops={"color": "white"})
                st.pyplot(fig1)

            with col2:
                st.markdown("### 📊 Bar Chart")
                fig2, ax2 = plt.subplots()
                fig2.patch.set_facecolor("#071525")
                ax2.set_facecolor("#071525")
                ax2.bar(labels, values, color=["#00e5ff", "#e74c3c"])
                ax2.tick_params(colors="white")
                ax2.xaxis.label.set_color("white")
                ax2.yaxis.label.set_color("white")
                for spine in ax2.spines.values():
                    spine.set_color("#00e5ff")
                st.pyplot(fig2)