import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """
You are an expert medical scribe. Given a raw doctor-patient conversation transcript,
extract and structure the information into a proper SOAP note.

If prior visit context is provided, use it to:
- Reference relevant patient history
- Flag any changes in symptoms, medications, or diagnoses compared to prior visits
- Note any patterns or progressions across visits

Return the note in this exact format:

**SUBJECTIVE:**
- Chief Complaint:
- History of Present Illness:
- Current Medications:
- Allergies:
- Review of Symptoms:

**OBJECTIVE:**
- Vital Signs (if mentioned):
- Physical Exam Findings:
- Diagnostic Results (if mentioned):

**ASSESSMENT:**
- Primary Diagnosis:
- Differential Diagnoses:

**PLAN:**
- Medications/Orders:
- Follow-up:
- Patient Education:

**CLINICAL CONTEXT (from prior similar cases):**
- Relevant patterns from similar cases:

Only include fields where information is available.
Flag any critical missing information with [MISSING - REQUIRED].
"""

def generate_soap_note(transcript: str, prior_notes: list = []) -> str:

    # Build prior context string if notes were retrieved
    prior_context = ""
    if prior_notes:
        prior_context = "\n\nRELEVANT CLINICAL CONTEXT FROM SIMILAR CASES:\n"
        for i, note in enumerate(prior_notes):
            prior_context += f"\n[Similar Case {i+1}]:\n{note[:600]}\n"
        prior_context += "\nUse the above context to inform your clinical reasoning.\n"

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"{prior_context}\nToday's transcript:\n{transcript}"
        }]
    )
    return message.content[0].text