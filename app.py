import streamlit as st
import pdfplumber
from google import genai
from google.genai import types

# Initialize the AI Client
client = genai.Client()

# -- UI Setup --
st.set_page_config(page_title="Smart Talent Engine", layout="wide")
st.title("⚙️ Smart Talent Selection Engine")
st.markdown("Upload a resume and compare it against a Job Description.")

# -- Interface Layout --
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Job Description")
    job_desc = st.text_area("Paste the JD here:", height=300)

with col2:
    st.subheader("2. Candidate Resume")
    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])

# -- Processing Logic --
if st.button("Run Analysis", type="primary"):
    if not uploaded_file or not job_desc:
        st.warning("Please provide both a Job Description and a Resume.")
    else:
        with st.spinner("Extracting text and analyzing candidate..."):
            try:
                # Phase 1: Extract Text
                with pdfplumber.open(uploaded_file) as pdf:
                    resume_text = pdf.pages[0].extract_text()
                
                # Phase 2 & 3 Combined: Analyze and Score
                prompt = f"""
                You are an expert HR Selection Engine. 
                1. Read the Candidate Resume and extract their skills and experience.
                2. Compare this to the Job Description.
                3. Calculate a Compatibility Score (0-100).
                4. Provide a 2-sentence "Summary of Fit" explaining the score.
                
                Job Description: {job_desc}
                Resume Text: {resume_text}
                
                Format your response STRICTLY as JSON with these keys:
                - "candidate_name" (string)
                - "compatibility_score" (integer)
                - "summary_of_fit" (string)
                """

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                
                # Parse the JSON response
                import json
                result = json.loads(response.text)

                # -- Display Results --
                st.success("Analysis Complete!")
                
                st.metric(label=f"Score for {result.get('candidate_name', 'Candidate')}", 
                          value=f"{result.get('compatibility_score', 0)}%")
                
                st.info(f"**AI Justification:** {result.get('summary_of_fit', '')}")

            except Exception as e:
                st.error(f"An error occurred: {e}")