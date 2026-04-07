import streamlit as st
import pdfplumber
import docx
from PIL import Image
import json
import pandas as pd
from google import genai
from google.genai import types

# Initialize the AI Client
try:
    client = genai.Client()
except Exception as e:
    st.error("⚠️ Could not initialize the Gemini Client. Ensure your GEMINI_API_KEY environment variable is set.")
    st.stop()

# ==========================================
# 1. PAGE CONFIGURATION & STATE MANAGEMENT
# ==========================================
st.set_page_config(page_title="Smart Talent Engine", page_icon="🎯", layout="wide")

# Initialize Session State to "remember" data across different views
if 'candidates_db' not in st.session_state:
    st.session_state.candidates_db = []
if 'active_jd' not in st.session_state:
    st.session_state.active_jd = "Not Set"

# Custom CSS for Dark Mode & Styling
st.markdown("""
<style>
.stApp { background-color: #0f172a; }
.main-header { font-size: 38px; font-weight: 800; color: #f8fafc; margin-bottom: 5px; }
div[data-testid="metric-container"] { background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5); }
div[data-testid="metric-container"] label { color: #cbd5e1 !important; }
div[data-testid="metric-container"] div { color: #f8fafc !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("🎯 Smart Talent")
st.sidebar.markdown("---")
view_selection = st.sidebar.radio("Navigation", ["📊 Recruiter Dashboard", "☁️ Upload & Parsing", "🏆 Ranking View"])

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Clear Database"):
    st.session_state.candidates_db = []
    st.session_state.active_jd = "Not Set"
    st.rerun()

# ==========================================
# VIEW 1: RECRUITER DASHBOARD
# ==========================================
if view_selection == "📊 Recruiter Dashboard":
    st.markdown('<div class="main-header">📊 Recruiter Dashboard</div>', unsafe_allow_html=True)
    st.markdown("High-level overview of active hiring cycles and top talent.") # cite: 35
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active Roles", "1" if st.session_state.active_jd != "Not Set" else "0")
    with col2:
        st.metric("Resumes Processed", len(st.session_state.candidates_db)) # cite: 35
    with col3:
        # Calculate average score safely
        avg_score = sum([c['Score'] for c in st.session_state.candidates_db]) / len(st.session_state.candidates_db) if st.session_state.candidates_db else 0
        st.metric("Avg. Compatibility", f"{int(avg_score)}%")
        
    st.markdown("---")
    st.subheader("⭐ Top Talent Preview") # cite: 35
    
    if len(st.session_state.candidates_db) == 0:
        st.info("No candidates processed yet. Head to the Upload View to begin.")
    else:
        # Sort candidates by score descending and take the top 3
        top_candidates = sorted(st.session_state.candidates_db, key=lambda x: x['Score'], reverse=True)[:3]
        
        for idx, candidate in enumerate(top_candidates):
            with st.container(border=True):
                st.markdown(f"### #{idx+1}: {candidate['Name']} ({candidate['Score']}%)")
                st.markdown(f"**Top Skills:** {candidate['Top Skills']}")
                st.markdown(f"**AI Justification:** {candidate['AI Justification']}")

# ==========================================
# VIEW 2: UPLOAD & PARSING
# ==========================================
elif view_selection == "☁️ Upload & Parsing":
    st.markdown('<div class="main-header">☁️ Bulk Ingestion Portal</div>', unsafe_allow_html=True) # cite: 36
    
    job_desc = st.text_area("📝 Step 1: Define Job Description", value=st.session_state.active_jd if st.session_state.active_jd != "Not Set" else "", height=150)
    
    # BULK UPLOAD: Notice accept_multiple_files=True
    uploaded_files = st.file_uploader("📂 Step 2: Bulk Upload Resumes", type=["pdf", "docx", "png", "jpg", "jpeg"], accept_multiple_files=True) # cite: 36
    
    if st.button("🚀 Process Batch", type="primary"):
        if not uploaded_files or not job_desc:
            st.warning("⚠️ Please provide a Job Description and at least one resume.")
        else:
            st.session_state.active_jd = job_desc
            
            # Real-time status UI elements
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for index, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"⏳ Extracting and Parsing: {uploaded_file.name} ({index + 1}/{len(uploaded_files)})") # cite: 36
                
                try:
                    # --- Multi-Format Document Router ---
                    file_extension = uploaded_file.name.split('.')[-1].lower()
                    ai_contents = [] 
                    
                    if file_extension == 'pdf':
                        with pdfplumber.open(uploaded_file) as pdf:
                            resume_raw_text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
                        ai_contents.append(f"Resume Text: {resume_raw_text}")
                    elif file_extension == 'docx':
                        doc = docx.Document(uploaded_file)
                        resume_raw_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                        ai_contents.append(f"Resume Text: {resume_raw_text}")
                    elif file_extension in ['png', 'jpg', 'jpeg']:
                        image = Image.open(uploaded_file)
                        ai_contents.append(image)
                        ai_contents.append("Extract the candidate's profile from this image.")

                    # --- Upgraded Prompt for Table Data ---
                    prompt_instructions = f"""
                    You are an HR Selection Engine. Read the Candidate Resume and compare it to the Job Description.
                    Job Description: {job_desc}
                    
                    Format your response STRICTLY as a JSON object using the following structure:
                    {{
                        "candidate_name": "string",
                        "compatibility_score": integer,
                        "years_of_experience": integer,
                        "top_skills_summary": "string (comma separated list of top 5 skills)",
                        "summary_of_fit": "string",
                        "semantic_profile": {{
                            "professional_experience": ["role 1", "role 2"],
                            "certifications": ["cert 1"]
                        }}
                    }}
                    """
                    ai_contents.insert(0, prompt_instructions)

                    # --- Call Gemini ---
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=ai_contents,
                        config=types.GenerateContentConfig(response_mime_type="application/json")
                    )
                    
                    result = json.loads(response.text)

                    # Add the parsed data to our session state database
                    st.session_state.candidates_db.append({
                        "Name": result.get("candidate_name", "Unknown"),
                        "Score": result.get("compatibility_score", 0),
                        "Years Exp": result.get("years_of_experience", 0),
                        "Top Skills": result.get("top_skills_summary", ""),
                        "AI Justification": result.get("summary_of_fit", ""),
                        "Raw File": uploaded_file.name
                    })

                except Exception as e:
                    st.error(f"Failed processing {uploaded_file.name}: {e}")
                
                # Update progress bar
                progress_bar.progress((index + 1) / len(uploaded_files))
                
            status_text.success(f"✅ Successfully processed {len(uploaded_files)} resumes!")

# ==========================================
# VIEW 3: RANKING VIEW
# ==========================================
elif view_selection == "🏆 Ranking View":
    st.markdown('<div class="main-header">🏆 Candidate Leaderboard</div>', unsafe_allow_html=True) # cite: 37
    
    if len(st.session_state.candidates_db) == 0:
        st.info("No data available. Please upload resumes in the Upload View.")
    else:
        # Convert our list of dictionaries into a Pandas DataFrame
        df = pd.DataFrame(st.session_state.candidates_db)
        
        # Sort by Score descending
        df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)
        
        st.markdown("Interact with the table below to sort and filter candidates.")
        
        # Streamlit's native dataframe is automatically sortable and filterable
        st.dataframe(
            df,
            column_config={
                "Score": st.column_config.ProgressColumn(
                    "Match Score",
                    help="AI calculated compatibility",
                    format="%d%%",
                    min_value=0,
                    max_value=100,
                ),
                "Years Exp": st.column_config.NumberColumn("Years Exp"), # cite: 38
                "AI Justification": st.column_config.TextColumn("AI Justification", width="large") # cite: 38
            },
            hide_index=True,
            use_container_width=True,
            height=500
        )