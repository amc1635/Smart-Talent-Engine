# 🎯 Smart Talent Selection Engine

## The Problem
Talent Acquisition teams are often bottlenecked by "Volume Hiring" cycles where a single job posting attracts thousands of applicants. Recruiters currently rely on primitive, keyword-based ATS systems that accidentally reject high-potential talent due to missing exact keywords, leading to "manual fatigue" and missed opportunities.

## The Solution
The Smart Talent Engine is an AI-powered HR platform that moves beyond "dumb" keyword matching. It utilizes Large Language Models to read resumes across multiple chaotic formats (PDF, Word, and Images) and transforms unstructured text into a standardized semantic profile. It grades candidates based on the actual *intent* of their experience against a specific Job Description and generates an interactive, ranked leaderboard with AI-backed justifications for recruiters.

## Tech Stack
* **Programming Language:** Python
* **Frontend Framework:** Streamlit (Multi-view dashboard)
* **AI/Logic Engine:** Google Gemini 2.5 Flash API (via `google-genai` SDK)
* **Data Handling:** Pandas
* **Document Parsing:** `pdfplumber` (PDF), `python-docx` (Word), `Pillow` (Images/OCR)

## Setup Instructions
Follow these steps to run the project locally:

1.  **Clone the repository:**
    `git clone https://github.com/amc1635/smart-talent-engine.git`
    `cd smart-talent-engine`

2.  **Install dependencies:**
    `pip install -r requirements.txt`

3.  **Set up your environment variables:**
    You must have a Google Gemini API Key to run the logic engine. 
    * Mac/Linux: `export GEMINI_API_KEY="your_api_key_here"`
    * Windows (CMD): `set GEMINI_API_KEY="your_api_key_here"`
    * Windows (PowerShell): `$env:GEMINI_API_KEY="your_api_key_here"`

4.  **Run the application locally:**
    `streamlit run app.py`