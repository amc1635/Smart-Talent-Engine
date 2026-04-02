import os
from google import genai
from google.genai import types

# Initialize the client (ensure your GEMINI_API_KEY environment variable is still set)
client = genai.Client()

# This is the structured JSON data we pretended to get back from Phase 2
candidate_profile = """
{
  "name": "Jane Doe",
  "total_years_experience": 3,
  "skills": {
    "backend": ["Java", "Spring Boot", "MySQL"],
    "cloud": ["AWS"]
  },
  "professional_experience": ["Software Engineer at TechCorp (3 years)"]
}
"""

# A sample Job Description for testing
job_description = """
Looking for a Mid-Level Backend Developer. 
Must have 2+ years of experience with Java and Spring Boot. 
Experience deploying to AWS is highly preferred.
"""

# The Scoring Prompt
prompt = f"""
You are the logic engine for an HR Selection system. Compare the Candidate Profile to the Job Description.

Calculate a Compatibility Score (0-100) based on how well the skills and years of experience align. 
Provide a 2-sentence "Summary of Fit" explaining exactly why they received this score.

Job Description:
{job_description}

Candidate Profile:
{candidate_profile}

Format your response STRICTLY as a JSON object with the following keys:
- "score" (integer)
- "justification" (string)
"""

print("Analyzing candidate against Job Description...\n")

# Call the AI model
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json", 
    ),
)

print("--- SCORING RESULTS ---")
print(response.text)