import anthropic
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

METRICS = {
    "completeness":       "Did the agent capture every required SOAP field?",
    "accuracy":           "Does the note correctly reflect what was said in the transcript?",
    "medication_capture": "Were all medications, doses and frequencies correctly extracted?",
    "clinical_reasoning": "Is the diagnosis and plan clinically justified by the findings?",
    "structure":          "Is the note properly formatted and organized for clinical use?"
}

def evaluate_note(transcript: str, soap_note: str) -> dict:
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[{
                "role": "user",
                "content": f"""You are a clinical documentation expert.
Evaluate this SOAP note against the original transcript.
Score each category strictly from 1 to 10.

TRANSCRIPT:
{transcript}

GENERATED SOAP NOTE:
{soap_note}

Return ONLY valid JSON, no extra text, no markdown:
{{
    "completeness":       {{"score": 0, "reason": "one sentence"}},
    "accuracy":           {{"score": 0, "reason": "one sentence"}},
    "medication_capture": {{"score": 0, "reason": "one sentence"}},
    "clinical_reasoning": {{"score": 0, "reason": "one sentence"}},
    "structure":          {{"score": 0, "reason": "one sentence"}},
    "overall_score": 0
}}"""
            }]
        )

        raw = response.content[0].text.strip()
        clean = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)

        for key in METRICS:
            if key in result:
                result[key]["description"] = METRICS[key]

        return result

    except Exception as e:
        return {
            "completeness":       {"score": 0, "reason": "Evaluation failed", "description": METRICS["completeness"]},
            "accuracy":           {"score": 0, "reason": "Evaluation failed", "description": METRICS["accuracy"]},
            "medication_capture": {"score": 0, "reason": "Evaluation failed", "description": METRICS["medication_capture"]},
            "clinical_reasoning": {"score": 0, "reason": "Evaluation failed", "description": METRICS["clinical_reasoning"]},
            "structure":          {"score": 0, "reason": "Evaluation failed", "description": METRICS["structure"]},
            "overall_score": 0
        }