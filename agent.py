import anthropic
import os
import json
from dotenv import load_dotenv
from vector_store import retrieve_similar_notes

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── Tool Definitions ──────────────────────────────────────────
# These are the tools the agent can choose to call

TOOLS = [
    {
        "name": "retrieve_similar_cases",
        "description": "Search the clinical knowledge base for similar past cases. Use this when the transcript mentions specific symptoms, diagnoses, or conditions that would benefit from historical context.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A clinical query based on the patient's symptoms or condition"
                },
                "n_results": {
                    "type": "integer",
                    "description": "Number of similar cases to retrieve (1-5)",
                    "default": 3
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "check_medications",
        "description": "Extract all medications mentioned in the transcript and flag any that need attention, such as missing dosages or potential interactions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "transcript": {
                    "type": "string",
                    "description": "The full transcript to extract medications from"
                }
            },
            "required": ["transcript"]
        }
    },
    {
        "name": "assess_completeness",
        "description": "Assess what critical information is missing from the transcript before generating the SOAP note. Use this for vague or incomplete transcripts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "transcript": {
                    "type": "string",
                    "description": "The transcript to assess for completeness"
                }
            },
            "required": ["transcript"]
        }
    }
]

# ── Tool Execution Functions ──────────────────────────────────
# What actually runs when the agent calls each tool

def run_tool(tool_name: str, tool_input: dict) -> str:
    
    if tool_name == "retrieve_similar_cases":
        query = tool_input["query"]
        n = tool_input.get("n_results", 3)
        notes, metadatas = retrieve_similar_notes(query, n_results=n)
        result = f"Retrieved {len(notes)} similar cases:\n"
        for i, (note, meta) in enumerate(zip(notes, metadatas)):
            result += f"\n[Case {i+1}] Age: {meta['age']} | Visit: {meta['visit_motivation'][:100]}\n"
            result += f"Note: {note[:400]}\n"
        return result

    elif tool_name == "check_medications":
        transcript = tool_input["transcript"]
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=400,
            messages=[{
                "role": "user",
                "content": f"""Extract all medications from this transcript. For each one list:
                - Medication name
                - Dosage (or flag as MISSING if not mentioned)
                - Frequency (or flag as MISSING if not mentioned)
                - Any concerns
                
                Transcript: {transcript}
                
                Be concise. If no medications mentioned, say so."""
            }]
        )
        return response.content[0].text

    elif tool_name == "generate_soap_note":
        transcript = tool_input["transcript"]
        prior_context = tool_input.get("prior_context", "")

        context_block = ""
        if prior_context:
            context_block = f"\n\nCLINICAL CONTEXT FROM SIMILAR CASES:\n{prior_context}\n"

        system_prompt = """You are an expert medical scribe. Given a doctor-patient 
conversation transcript, extract and structure ALL information into a detailed SOAP note.

If prior case context is provided, use it to inform your clinical reasoning and 
reference relevant patterns in the Assessment section.

Return the note in EXACTLY this format — do not skip any section:

**SUBJECTIVE:**
- Chief Complaint:
- History of Present Illness:
- Onset:
- Duration:
- Quality/Character:
- Severity (1-10):
- Location/Radiation:
- Aggravating Factors:
- Relieving Factors:
- Associated Symptoms:
- Current Medications:
- Allergies:
- Past Medical History:
- Family History:
- Social History:
- Review of Symptoms:

**OBJECTIVE:**
- Vital Signs:
  - Blood Pressure:
  - Heart Rate:
  - Temperature:
  - Respiratory Rate:
  - O2 Saturation:
- General Appearance:
- Physical Exam Findings:
- Diagnostic Results (if mentioned):

**ASSESSMENT:**
- Primary Diagnosis:
- Differential Diagnoses:
- Clinical Reasoning:

**PLAN:**
- Medications/Orders:
- Diagnostics Ordered:
- Referrals:
- Patient Education:
- Follow-up:
- Precautions/Return to ED if:

Fill every field with information from the transcript.
For fields not mentioned, write [Not reported].
Flag critical missing information with [MISSING - REQUIRED].
Never leave a field blank."""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": f"{context_block}\nToday's transcript:\n{transcript}"
            }]
        )
        return response.content[0].text

    return f"Unknown tool: {tool_name}"


# ── The Agent Loop ────────────────────────────────────────────

def run_agent(transcript: str):

    steps = []
    collected_context = []

    system_prompt = """You are an expert AI clinical scribe agent.

Your job is to gather context before a SOAP note is generated.

You have access to 3 tools:
1. assess_completeness - check what info is missing from the transcript
2. retrieve_similar_cases - search for similar past clinical cases
3. check_medications - extract and validate medications mentioned

ALWAYS call all 3 tools in that order. Do not skip any.
After calling all 3 tools, stop. Do not write anything else."""

    messages = [
        {
            "role": "user",
            "content": f"Gather context for this transcript:\n\n{transcript}"
        }
    ]

    # ── Agent loop: only runs the 3 context tools ──────────
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=system_prompt,
            tools=[t for t in TOOLS if t["name"] != "generate_soap_note"],
            messages=messages
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    steps.append({
                        "type": "tool_call",
                        "tool": tool_name,
                        "input": tool_input
                    })

                    result = run_tool(tool_name, tool_input)
                    collected_context.append(f"[{tool_name}]:\n{result}")

                    steps.append({
                        "type": "tool_result",
                        "tool": tool_name,
                        "result": result
                    })

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({"role": "user", "content": tool_results})

        else:
            break

    # ── Directly call SOAP generator with all context ──────
    steps.append({
        "type": "tool_call",
        "tool": "generate_soap_note",
        "input": {}
    })

    prior_context = "\n\n".join(collected_context)
    soap_note = run_tool("generate_soap_note", {
        "transcript": transcript,
        "prior_context": prior_context
    })

    steps.append({
        "type": "tool_result",
        "tool": "generate_soap_note",
        "result": soap_note
    })

    steps.append({
        "type": "final",
        "content": soap_note
    })

    return steps