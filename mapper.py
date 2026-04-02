import os
from google import genai
from google.genai import types

# Initialize the client. 
# Note: You must set your API key as an environment variable named GEMINI_API_KEY
client = genai.Client()

# This is a placeholder for the text you extracted using pdfplumber in Phase 1
raw_resume_text = """
Jane Doe
Software Engineer
Experience: 3 years at TechCorp building backend systems using Java and Spring Boot.
Skills: Java, Python, Spring Boot, MySQL, AWS.
Projects: Built a personal weather app using React and Node.js.
"""

# The Prompt is the secret sauce of your logic engine
prompt = f"""
You are an expert HR Selection Engine. Read the following resume text and extract the candidate's profile. 
You must recognize skill synonyms and hierarchies.

Format your response STRICTLY as a JSON object with the following keys:
- "name"
- "total_years_experience" (integer)
- "skills" (categorized into "frontend", "backend", "cloud", "machine_learning")
- "professional_experience" (list of roles)
- "academic_projects" (list of projects)

Resume Text:
{raw_resume_text}
"""

print("Sending data to the AI logic engine...\n")

# Call the AI model
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json", # This forces the AI to output valid JSON
    ),
)

print("--- STANDARDIZED CANDIDATE JSON ---")
print(response.text)