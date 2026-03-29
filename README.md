# AI-Powered-Code-Reviewer-and-Quality-Assistant-

# 🤖 AI-Powered Code Reviewer & Quality Assistant

> An intelligent, end-to-end code quality analysis platform built with Python and Streamlit — designed to help developers write cleaner, better-documented, and more maintainable code through AI-driven insights.

---

## 📌 Purpose of the Project

Modern software development demands not just working code, but **readable, documented, and maintainable** code. The AI-Powered Code Reviewer & Quality Assistant bridges the gap between writing code and writing *good* code — by automating code metrics analysis, validating and generating docstrings, and presenting everything through an intuitive dashboard interface.

This project was developed as part of the **Infosys Springboard Virtual Internship Program**, structured across 4 progressive milestones to incrementally build a production-ready AI tool.

---

## 🚀 Project Features

- 📊 **Automated Code Metrics Analysis** — Instantly analyze complexity, maintainability, and quality scores of any Python file
- ✅ **Docstring Validation** — Detect missing, incomplete, or incorrectly formatted docstrings across functions and classes
- ✨ **AI Docstring Generation** — Automatically generate meaningful, professional docstrings for undocumented code using AI
- 🖥️ **Interactive Dashboard Interface** — A clean, user-friendly Streamlit dashboard to visualize all analysis results in one place
- 📁 **Multi-file Support** — Analyze individual files or entire project folders
- 📈 **Visual Reports** — Charts and metrics displayed with clear visual indicators for quick decision-making

---

## 🏗️ Project Milestones

### ✅ Milestone 1 — Code Metrics Analysis
The foundation of the project. This milestone focused on building the core engine to analyze Python source code and extract meaningful quality metrics.

- Implemented static code analysis using industry-standard libraries
- Extracted metrics such as cyclomatic complexity, lines of code, maintainability index, and Halstead metrics
- Established a modular pipeline for processing Python files
- Output structured metric reports for further processing in later milestones

---

### ✅ Milestone 2 — Docstring Validation
Built on top of Milestone 1 to introduce intelligent documentation quality checks.

- Developed a docstring parser to scan all functions, methods, and classes in a Python file
- Validated the presence, completeness, and format of docstrings (Google style / NumPy style)
- Generated detailed reports highlighting undocumented or poorly documented code sections
- Integrated validation results into the existing metrics pipeline for unified reporting

---

### ✅ Milestone 3 — Docstring Generation
Introduced AI capabilities to the project by automating docstring creation for undocumented code.

- Integrated an AI/LLM-based backend to intelligently generate context-aware docstrings
- Automatically detected functions and classes lacking proper documentation
- Generated professional, accurate docstrings based on function signatures and logic
- Allowed developers to review and accept generated docstrings with minimal effort

---

### ✅ Milestone 4 — Dashboard Interface
The final milestone brought everything together into a polished, production-ready application.

- Designed and developed a full Streamlit-based interactive dashboard
- Integrated all previous milestone features (metrics, validation, generation) into a single unified UI
- Added dynamic visualizations including charts, progress indicators, and summary cards
- Implemented sidebar navigation, file upload support, and real-time analysis feedback
- Focused on UI/UX polish, performance optimization, and final project packaging

---

## 🛠️ Tech Stack & Tools

| Category | Technology / Libraries |
|---|---|
| **Language** | Python 3.8+ |
| **Web Framework** | Streamlit |
| **AI / LLM Models** | LLaMA 3.3 70B, LLaMA 3.1 8B, GPT-OSS 120B, GPT-OSS 20B |
| **API Provider** | Groq API, OpenAI-compatible API |
| **Code Analysis** | Radon, Pylint, AST |
| **Data Visualization** | Plotly, Matplotlib |
| **Utilities** | python-dotenv, os, re, json |
| **Version Control** | Git & GitHub |
| **Environment** | Python Virtual Environment (venv) |
| **IDE** | Visual Studio Code |

---

## 📁 Project Files

```
ai_powered/
│
|Documentation
|
|examples
|
├── milestones/
│   ├── milestone_1/          # Code metrics analysis module
│   ├── milestone_2/          # Docstring validation module
│   ├── milestone_3/          # Docstring generation module
│   └── milestone_4/          # Dashboard interface & main app
│       ├── main_app.py       # Main Streamlit application
│
├── python_basics.py          # Utility and helper functions
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

---

## 📂 Documentation & Demo

| Type | Link |
|---|---|
| 📊 **Presentation (PPT)** | [Download PPT](Documentation/AI_Powered_Code_Reviewer%20%5BTharun%20Kumar%20S%5D.pptx) |
| 🎥 **Demo Video** | [Download Video](Documentation/demo_video.mp4) |

---

## ⚙️ How to Run the Project

### Prerequisites
- Python 3.8 or above
- pip package manager
- API key (OpenAI / Gemini) if using AI generation features

### Step 1 — Clone the Repository
```bash
git clone https://github.com/tharunkumars-workspace/AI-Powered-Code-Reviewer-and-Quality-Assistant-.git
cd AI-Powered-Code-Reviewer-and-Quality-Assistant-
```

### Step 2 — Create a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# or
source venv/bin/activate     # macOS/Linux
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Configure Environment Variables
Create a `.env` file in the `milestone_4` folder and add your API key:
```
OPENAI_API_KEY=your_api_key_here
```

### Step 5 — Run the Application
```bash
cd milestones/milestone_4
streamlit run main_app.py
```

The app will launch in your browser at `http://localhost:8501`

------------------

## 👨‍💻 Author

**Tharun Kumar S**
- 🎓 Infosys Springboard Virtual Internship Program
- 💼 Project: AI-Powered Code Reviewer & Quality Assistant
- 🔗 GitHub: [@tharunkumars-workspace](https://github.com/tharunkumars-workspace)

------------------