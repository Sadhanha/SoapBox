# ClinScribe — AI Clinical Scribe Agent

> Converts doctor-patient transcripts into structured SOAP notes using an agentic RAG pipeline.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0-red)
![Claude](https://img.shields.io/badge/Claude-Sonnet_4-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## What it does

Physicians spend nearly **2 hours on documentation for every 1 hour of patient care.**
ClinScribe automates the most time-consuming part — turning raw visit transcripts into
structured, billable SOAP notes in seconds.

The agent doesn't just summarize. It reasons about the transcript, retrieves similar
clinical cases, validates medications, and then generates a note informed by all of that
context.

---

## Demo

[🔗 Live Demo on Hugging Face Spaces](#) ← add your link here

---

## Evaluation Results

Evaluated across 3 clinical test cases using LLM-as-judge, ROUGE,
semantic similarity, and field coverage:

| Metric | Score |
|---|---|
| LLM Quality Score | 9.67 / 10 |
| Semantic Similarity | 0.81 |
| Field Coverage | 100% |
| Cases Evaluated | 3 / 3 |

> ROUGE scores intentionally low (avg 0.43) — the agent paraphrases
> and restructures clinical information rather than copying transcript verbatim.
> This is the expected behavior of a good clinical scribe.

---

## Architecture
Doctor-Patient Transcript
    ↓
┌───────────────────────────────────┐
│           AI AGENT                │
│                                   │
│  1. assess_completeness           │
│     └── flags missing info        │
│                                   │
│  2. retrieve_similar_cases        │
│     └── RAG over 143 clinical     │
│         notes (ChromaDB)          │
│                                   │
│  3. check_medications             │
│     └── extracts & validates meds │
│                                   │
│  4. generate_soap_note            │
│     └── structured SOAP output    │
└───────────────────────────────────┘
   ↓
Structured SOAP Note

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Anthropic Claude Sonnet 4 |
| Agent Framework | Claude Tool Calling |
| Vector Database | ChromaDB |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| Clinical Dataset | AGBonnet/augmented-clinical-notes (HuggingFace) |
| Frontend | Streamlit |
| Evaluation | LLM-as-judge + ROUGE + Cosine Similarity |

---

## Agent Tools

### 1. `assess_completeness`
Reviews the transcript before anything else. Identifies visit type,
flags missing critical information, and scores overall completeness.

### 2. `retrieve_similar_cases`
Performs semantic search over 143 indexed clinical notes using
ChromaDB and Sentence Transformers. Returns the most clinically
similar past cases to inform the note generation.

### 3. `check_medications`
Extracts every medication mentioned in the transcript. Validates
dosages and frequencies. Flags anything missing or concerning.

### 4. `generate_soap_note`
Called directly outside the agent loop to guarantee clean,
structured output. Uses a strict system prompt to enforce the
exact SOAP format across all 4 sections and 20+ subfields.

---

## SOAP Note Format

Every generated note follows this exact structure:
SUBJECTIVE:

Chief Complaint
History of Present Illness
Onset, Duration, Quality, Severity, Location
Aggravating/Relieving Factors
Associated Symptoms
Current Medications
Allergies
Past Medical / Family / Social History
Review of Systems

OBJECTIVE:

Vital Signs (BP, HR, Temp, RR, O2 Sat)
General Appearance
Physical Exam Findings
Diagnostic Results

ASSESSMENT:

Primary Diagnosis
Differential Diagnoses
Clinical Reasoning

PLAN:

Medications/Orders
Diagnostics Ordered
Referrals
Patient Education
Follow-up
Precautions/Return to ED