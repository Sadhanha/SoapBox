import anthropic
import os
import json
from dotenv import load_dotenv
from agent import run_agent
from sentence_transformers import SentenceTransformer, util
from rouge_score import rouge_scorer

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── Semantic similarity model ─────────────────────────────────
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ── Test transcripts ──────────────────────────────────────────
TEST_CASES = [
    {
        "name": "Chest Pain / Pericarditis",
        "transcript": """
Dr: Good morning, how are you feeling today?
Patient: Not great, doctor. I've been having really bad chest pain for the past 3 days. It gets worse when I breathe deeply or lie down.
Dr: Can you describe the pain? Is it sharp or dull?
Patient: It's sharp. Like a stabbing feeling on the left side of my chest.
Dr: Does it radiate anywhere — like your arm, jaw, or back?
Patient: No, it stays in my chest mostly.
Dr: Any shortness of breath, dizziness, or sweating?
Patient: Some shortness of breath yes, especially when I climb stairs. No dizziness or sweating though.
Dr: How about coughing or fever?
Patient: I had a mild fever two days ago, about 99.8. No cough.
Dr: Any recent illness?
Patient: Yes, I had an upper respiratory infection about two weeks ago.
Dr: Are you on any medications currently?
Patient: I take lisinopril 10mg daily and aspirin 81mg daily. I also took ibuprofen 400mg a couple times for the chest pain but it didn't help much.
Dr: Any allergies?
Patient: Penicillin. I get a rash.
Dr: Any history of heart disease?
Patient: My father had a heart attack at 62. I've never had any heart issues myself.
Dr: Blood pressure is 138 over 88. Heart rate 92. Temperature 98.9. O2 sat 96% on room air. I can hear a friction rub on auscultation.
Dr: Based on your symptoms I believe you have pericarditis. I'm stopping the ibuprofen and starting colchicine 0.5mg twice daily and aspirin 650mg three times a day. I'm ordering an EKG, chest X-ray, CBC, CRP, and troponin.
Patient: Should I avoid exercise?
Dr: Yes, avoid strenuous activity. Follow up in one week or sooner if pain worsens or fever exceeds 101.
Patient: Thank you doctor.
"""
    },
    {
        "name": "Diabetic Follow-up",
        "transcript": """
Dr: Good afternoon. How have you been since your last visit?
Patient: Honestly not great. I've been feeling really tired and urinating a lot more, especially at night.
Dr: How long has this been going on?
Patient: About three weeks now.
Dr: Are you checking your blood sugars at home?
Patient: Yes, they've been running high. Usually between 250 and 310 in the mornings. Sometimes over 350 after meals.
Dr: Any blurry vision, numbness or tingling?
Patient: Yes, my feet have been tingling a lot at night. And my vision has been a little blurry on and off.
Dr: Any chest pain or swelling?
Patient: No chest pain. My ankles swell a little by end of day.
Dr: Are you taking your medications?
Patient: I take metformin 1000mg twice a day. But I ran out of glipizide about two weeks ago and haven't refilled it.
Dr: Any other medications?
Patient: Lisinopril 10mg daily, atorvastatin 40mg at night, aspirin 81mg daily.
Dr: Any allergies?
Patient: No known drug allergies.
Dr: Family history?
Patient: My mother had diabetes and eventually went on dialysis.
Dr: Blood pressure 148 over 92, heart rate 84, temperature 98.6, weight 218 pounds which is up 6 pounds. O2 sat 97%. Feet show decreased sensation bilaterally. Mild pitting edema in both ankles.
Dr: We need better control urgently. I'm refilling your glipizide 10mg daily and increasing lisinopril to 20mg. Check blood sugar four times daily. I'm ordering A1C, metabolic panel, urine microalbumin, and lipid panel. Referrals to ophthalmology and podiatry. Follow up in 4 weeks.
Patient: Should I change my diet?
Dr: Yes. Meet with our diabetes educator. Reduce refined carbs, increase fiber, walk 20 to 30 minutes daily.
Patient: Thank you doctor.
"""
    },
    {
        "name": "Neck Pain",
        "transcript": """
Dr: Good morning, what brings you in today?
Patient: I've been having neck pain for the past two weeks. It started after I slept in a bad position. The pain is about a 6 out of 10, radiates to my left shoulder.
Dr: Any headaches or numbness?
Patient: Some headaches yes, but no numbness.
Dr: Are you on any medications?
Patient: I take ibuprofen 400mg when the pain gets bad, and lisinopril 10mg daily for blood pressure.
Dr: Any allergies?
Patient: Penicillin. I get a rash.
Dr: Range of motion is limited on the left side. No neurological deficits. I think this is muscle strain. I'm prescribing cyclobenzaprine 5mg at night. Follow up in 2 weeks if no improvement.
Patient: Thank you doctor.
"""
    }
]


# ── LLM Judge ─────────────────────────────────────────────────
def llm_judge(transcript: str, soap_note: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""You are a clinical documentation expert.
Evaluate this SOAP note against the original transcript.
Score each category from 1-10.

TRANSCRIPT:
{transcript}

GENERATED SOAP NOTE:
{soap_note}

Return ONLY valid JSON in this exact format with no extra text:
{{
    "completeness": {{"score": 0, "reason": ""}},
    "accuracy": {{"score": 0, "reason": ""}},
    "structure": {{"score": 0, "reason": ""}},
    "medication_capture": {{"score": 0, "reason": ""}},
    "clinical_reasoning": {{"score": 0, "reason": ""}},
    "overall_score": 0,
    "summary": ""
}}"""
        }]
    )
    raw = response.content[0].text.strip()
    clean = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


# ── ROUGE Score ────────────────────────────────────────────────
def compute_rouge(reference: str, generated: str) -> dict:
    scorer = rouge_scorer.RougeScorer(
        ["rouge1", "rouge2", "rougeL"],
        use_stemmer=True
    )
    scores = scorer.score(reference, generated)
    return {
        "rouge1": round(scores["rouge1"].fmeasure, 3),
        "rouge2": round(scores["rouge2"].fmeasure, 3),
        "rougeL": round(scores["rougeL"].fmeasure, 3),
    }


# ── Semantic Similarity ────────────────────────────────────────
def compute_similarity(transcript: str, soap_note: str) -> float:
    emb1 = embedder.encode(transcript, convert_to_tensor=True)
    emb2 = embedder.encode(soap_note, convert_to_tensor=True)
    score = util.cos_sim(emb1, emb2).item()
    return round(score, 3)


# ── Field Coverage ─────────────────────────────────────────────
def compute_field_coverage(soap_note: str) -> dict:
    required_fields = [
        "Chief Complaint",
        "History of Present Illness",
        "Current Medications",
        "Allergies",
        "Vital Signs",
        "Physical Exam",
        "Primary Diagnosis",
        "Plan",
        "Follow-up"
    ]
    covered = [f for f in required_fields if f.lower() in soap_note.lower()]
    coverage = round(len(covered) / len(required_fields), 2)
    return {
        "covered": len(covered),
        "total": len(required_fields),
        "coverage": coverage,
        "missing": [f for f in required_fields if f not in covered]
    }


# ── Print helpers ──────────────────────────────────────────────
def print_bar(score: float, out_of: float = 10) -> str:
    filled = int((score / out_of) * 10)
    return "█" * filled + "░" * (10 - filled)


def print_section(title: str):
    print(f"\n{'─' * 55}")
    print(f"  {title}")
    print(f"{'─' * 55}")


# ── Main evaluation runner ─────────────────────────────────────
def run_evaluation():

    all_overall = []
    all_rouge1  = []
    all_sim     = []
    all_coverage = []

    print("\n" + "═" * 55)
    print("   CLINSCRIBE — EVALUATION REPORT")
    print("═" * 55)

    for i, case in enumerate(TEST_CASES):
        print(f"\n\n{'═' * 55}")
        print(f"  CASE {i+1}: {case['name']}")
        print(f"{'═' * 55}")

        # ── Run agent ──────────────────────────────────────
        print("\n  ⏳ Running agent...")
        steps = run_agent(case["transcript"])
        soap_note = next(
            (s["content"] for s in steps if s["type"] == "final"),
            None
        )

        if not soap_note:
            print("  ⚠️  Agent returned no note — skipping")
            continue

        print("  ✅ Note generated\n")

        # ── LLM Judge ──────────────────────────────────────
        print("  ⏳ Running LLM judge...")
        judge = llm_judge(case["transcript"], soap_note)
        all_overall.append(judge["overall_score"])

        print_section("LLM JUDGE SCORES")
        categories = [
            ("completeness",      "Completeness"),
            ("accuracy",          "Accuracy"),
            ("structure",         "Structure"),
            ("medication_capture","Medication Capture"),
            ("clinical_reasoning","Clinical Reasoning"),
        ]
        for key, label in categories:
            s = judge[key]["score"]
            r = judge[key]["reason"]
            print(f"\n  {label}")
            print(f"  [{print_bar(s)}] {s}/10")
            print(f"  ↳ {r}")

        print(f"\n  OVERALL:  [{print_bar(judge['overall_score'])}] {judge['overall_score']}/10")
        print(f"  SUMMARY:  {judge['summary']}")

        # ── ROUGE ──────────────────────────────────────────
        rouge = compute_rouge(case["transcript"], soap_note)
        all_rouge1.append(rouge["rouge1"])

        print_section("ROUGE SCORES (overlap with transcript)")
        print(f"  ROUGE-1:  [{print_bar(rouge['rouge1'], 1)}] {rouge['rouge1']}")
        print(f"  ROUGE-2:  [{print_bar(rouge['rouge2'], 1)}] {rouge['rouge2']}")
        print(f"  ROUGE-L:  [{print_bar(rouge['rougeL'], 1)}] {rouge['rougeL']}")

        # ── Semantic Similarity ────────────────────────────
        sim = compute_similarity(case["transcript"], soap_note)
        all_sim.append(sim)

        print_section("SEMANTIC SIMILARITY")
        print(f"  Score:    [{print_bar(sim, 1)}] {sim}")
        print(f"  ↳ How well the note captures the meaning of the transcript")

        # ── Field Coverage ─────────────────────────────────
        cov = compute_field_coverage(soap_note)
        all_coverage.append(cov["coverage"])

        print_section("FIELD COVERAGE")
        print(f"  Covered:  {cov['covered']}/{cov['total']} required fields")
        print(f"  Score:    [{print_bar(cov['coverage'], 1)}] {cov['coverage']}")
        if cov["missing"]:
            print(f"  Missing:  {', '.join(cov['missing'])}")
        else:
            print(f"  Missing:  None ✅")

    # ── Aggregate Results ──────────────────────────────────
    print("\n\n" + "═" * 55)
    print("   AGGREGATE RESULTS ACROSS ALL CASES")
    print("═" * 55)

    def avg(lst):
        return round(sum(lst) / len(lst), 2) if lst else 0

    print(f"\n  LLM Overall Score:      {avg(all_overall)}/10")
    print(f"  Avg ROUGE-1:            {avg(all_rouge1)}")
    print(f"  Avg Semantic Similarity:{avg(all_sim)}")
    print(f"  Avg Field Coverage:     {avg(all_coverage)}")
    print(f"\n  Cases evaluated:        {len(all_overall)}/{len(TEST_CASES)}")
    print("\n" + "═" * 55)
    print("  Evaluation complete")
    print("═" * 55 + "\n")


if __name__ == "__main__":
    run_evaluation()