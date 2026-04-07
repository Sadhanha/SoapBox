import streamlit as st
from agent import run_agent

st.set_page_config(
    page_title="SoapBox",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,400&family=Instrument+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"], .stApp {
    background-color: #F2EDE4 !important;
    font-family: 'Instrument Sans', sans-serif;
    color: #1A1A18;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    max-width: 600px !important;
    padding: 5rem 1.5rem !important;
}

/* Title */
h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 2.2rem !important;
    font-weight: 600 !important;
    color: #1B4332 !important;
    text-align: center !important;
    margin-bottom: 0.2rem !important;
}
.subtitle {
    text-align: center;
    font-size: 0.7rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #8a8a7a;
    margin-bottom: 3rem;
}

/* Paste card */
.paste-card {
    background: white;
    border-radius: 20px;
    padding: 2rem 2rem 1.5rem 2rem;
    box-shadow: 0 4px 32px rgba(0,0,0,0.06);
}
.paste-card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    color: #1A1A18;
    text-align: center;
    margin-bottom: 0.2rem;
}
.paste-card-sub {
    font-size: 0.68rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #8a8a7a;
    text-align: center;
    margin-bottom: 1.2rem;
}

/* Textarea */
textarea {
    background: #F8F5F0 !important;
    border: 1.5px solid #E2DDD4 !important;
    border-radius: 12px !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.85rem !important;
    color: #1A1A18 !important;
    line-height: 1.7 !important;
    padding: 1rem !important;
}
textarea:focus {
    border-color: #1B4332 !important;
    box-shadow: 0 0 0 2px rgba(27,67,50,0.1) !important;
}
textarea::placeholder {
    color: #C4BFB6 !important;
}

/* Hide the default label */
[data-testid="stFileUploader"] label {
    display: none !important;
}

/* The dropzone area */
[data-testid="stFileUploaderDropzone"] {
    background: #F8F5F0 !important;
    border: 1.5px dashed #D4CFC6 !important;
    border-radius: 12px !important;
    padding: 2rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #1B4332 !important;
    background: #F0EDE6 !important;
}

/* Upload button inside dropzone */
[data-testid="stFileUploaderDropzone"] button {
    background: #1B4332 !important;
    color: white !important;
    border: none !important;
    border-radius: 100px !important;
    padding: 0.6rem 2rem !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.8rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    cursor: pointer !important;
    transition: background 0.2s !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    background: #2D6A4F !important;
}

/* Dropzone instruction text */
[data-testid="stFileUploaderDropzoneInstructions"] > div > span {
    font-size: 0.85rem !important;
    color: #8a8a7a !important;
}

/* Begin scribing button */
.stButton > button {
    background: #1B4332 !important;
    color: white !important;
    border: none !important;
    border-radius: 100px !important;
    padding: 0.7rem 2.5rem !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    width: 100% !important;
    margin-top: 1rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 16px rgba(27,67,50,0.2) !important;
}
.stButton > button:hover {
    background: #2D6A4F !important;
    box-shadow: 0 6px 20px rgba(27,67,50,0.3) !important;
}

/* Processing card */
.processing-card {
    background: white;
    border-radius: 20px;
    padding: 3rem 2rem;
    text-align: center;
    box-shadow: 0 4px 32px rgba(0,0,0,0.06);
}
.orb {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: #1B4332;
    margin: 0 auto 1.5rem auto;
    animation: breathe 2.2s ease-in-out infinite;
}
@keyframes breathe {
    0%, 100% { transform: scale(1);   opacity: 1; }
    50%       { transform: scale(1.1); opacity: 0.7; }
}
.processing-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    color: #1A1A18;
    margin-bottom: 0.3rem;
}
.processing-sub {
    font-size: 0.7rem;
    color: #8a8a7a;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}
.step-pill {
    display: inline-block;
    background: #EAF3E6;
    color: #1B4332;
    border-radius: 100px;
    padding: 0.35rem 0.9rem;
    font-size: 0.72rem;
    margin: 0.2rem;
    letter-spacing: 0.5px;
}

/* Result card */
.result-card {
    background: white;
    border-radius: 20px;
    padding: 2.5rem;
    box-shadow: 0 4px 32px rgba(0,0,0,0.06);
}
.result-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem;
    color: #1B4332;
    margin-bottom: 0.2rem;
}
.result-meta {
    font-size: 0.68rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #8a8a7a;
    margin-bottom: 1.5rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid #EDE9E0;
}
.result-body {
    font-size: 0.85rem;
    line-height: 1.85;
    color: #2a2a28;
    white-space: pre-wrap;
}

/* Download button */
.stDownloadButton > button {
    background: transparent !important;
    color: #1B4332 !important;
    border: 1.5px solid #1B4332 !important;
    border-radius: 100px !important;
    padding: 0.65rem 2rem !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.75rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    width: 100% !important;
    margin-top: 1.2rem !important;
}
.stDownloadButton > button:hover {
    background: #EAF3E6 !important;
}

/* Tab styling */
[data-testid="stTabs"] {
    background: white;
    border-radius: 20px;
    padding: 1rem 1.5rem 0 1.5rem;
    box-shadow: 0 4px 32px rgba(0,0,0,0.06);
}
button[data-baseweb="tab"] {
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: #8a8a7a !important;
    padding: 0.6rem 1.5rem !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #1B4332 !important;
    border-bottom: 2px solid #1B4332 !important;
    font-weight: 600 !important;
}
button[data-baseweb="tab"]:hover {
    color: #2D6A4F !important;
}
[data-testid="stTabsContent"] {
    padding: 1.5rem 0 0 0 !important;
}        
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────
if "stage" not in st.session_state:
    st.session_state.stage = "upload"
if "uploaded_text" not in st.session_state:
    st.session_state.uploaded_text = None
if "agent_steps" not in st.session_state:
    st.session_state.agent_steps = []
if "final_note" not in st.session_state:
    st.session_state.final_note = None
if "evaluation" not in st.session_state:
    st.session_state.evaluation = None

TOOL_LABELS = {
    "assess_completeness":    "Assessed completeness",
    "retrieve_similar_cases": "Searched knowledge base",
    "check_medications":      "Checked medications",
    "generate_soap_note":     "Generated SOAP note",
}

# ── Wordmark ──────────────────────────────────────────────────
st.markdown("# SoapBox")
st.markdown('<div class="subtitle">Your AI medical scribe</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# STAGE 1 — UPLOAD
# ══════════════════════════════════════════════════════════════
if st.session_state.stage == "upload":

    st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 4px 32px rgba(0,0,0,0.06);
    }
    textarea {
        background: #F8F5F0 !important;
        border: 1.5px solid #E2DDD4 !important;
        border-radius: 12px !important;
        font-family: 'Instrument Sans', sans-serif !important;
        font-size: 0.85rem !important;
        color: #1A1A18 !important;
        line-height: 1.7 !important;
    }
    textarea:focus {
        border-color: #1B4332 !important;
        box-shadow: 0 0 0 2px rgba(27,67,50,0.1) !important;
    }
    textarea::placeholder { color: #C4BFB6 !important; }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("""
        <div style="text-align:center; padding-bottom:1.2rem;
                    border-bottom:1px solid #EDE9E0;
                    margin-bottom:1.2rem;">
            <div style="font-family:'Playfair Display',serif;
                        font-size:1.2rem; color:#1A1A18;
                        margin-bottom:0.2rem;">
                Paste your visit transcripts
            </div>
            <div style="font-size:0.7rem; color:#8a8a7a;
                        letter-spacing:1px; text-transform:uppercase;">
                Type or paste the provider — patient conversation below
            </div>
        </div>
        """, unsafe_allow_html=True)

        pasted_text = st.text_area(
            "transcript",
            height=220,
            placeholder="Dr: Good morning, what brings you in today?\nPatient: I've been having neck pain for the past two weeks...",
            label_visibility="collapsed"
        )

        # Button always visible
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            clicked = st.button("Begin Scribing", 
                disabled=not pasted_text.strip()
            )

    if clicked and pasted_text.strip():
        st.session_state.uploaded_text = pasted_text
        st.session_state.stage = "processing"
        st.rerun()

# ══════════════════════════════════════════════════════════════
# STAGE 2 — PROCESSING
# ══════════════════════════════════════════════════════════════
elif st.session_state.stage == "processing":

    tools_done = [
        s["tool"] for s in st.session_state.agent_steps
        if s["type"] == "tool_call"
    ]
    pills = "".join([
        f'<span class="step-pill">✓ {TOOL_LABELS.get(t, t)}</span>'
        for t in tools_done
    ])

    st.markdown(f"""
    <div class="processing-card">
        <div class="orb"></div>
        <div class="processing-title">Scribing in progress</div>
        <div class="processing-sub">Processing transcript...</div>
        {pills}
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.final_note:
        steps = run_agent(st.session_state.uploaded_text)
        st.session_state.agent_steps = steps
        for step in steps:
            if step["type"] == "final":
                st.session_state.final_note = step["content"]
            if step["type"] == "evaluation":
                st.session_state.evaluation = step["content"]
        st.session_state.stage = "complete"
        st.rerun()

# ══════════════════════════════════════════════════════════════
# STAGE 3 — COMPLETE
# ══════════════════════════════════════════════════════════════
elif st.session_state.stage == "complete":

    tools_used = len({
        s["tool"] for s in st.session_state.agent_steps
        if s["type"] == "tool_call"
    })

    ev = st.session_state.evaluation

    tab1, tab2 = st.tabs(["SOAP Note", "Note Quality"])

    # ══════════════════════════════════════════════════
    # TAB 1 — SOAP Note
    # ══════════════════════════════════════════════════
    with tab1:

        st.markdown(st.session_state.final_note)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="↓  Download Note",
                data=st.session_state.final_note,
                file_name="soap_note.txt",
                mime="text/plain"
            )
            if st.button("↩  Scribe another"):
                for key in ["uploaded_text", "agent_steps",
                             "final_note", "evaluation"]:
                    st.session_state[key] = None
                st.session_state.stage = "upload"
                st.rerun()

    # ══════════════════════════════════════════════════
    # TAB 2 — Note Quality (dynamic per session)
    # ══════════════════════════════════════════════════
    with tab2:
        if not ev:
            st.info("Evaluation not available for this note.")
        else:
            overall = ev.get("overall_score", 0)

            if overall >= 9:
                badge_color = "#1B4332"
                badge_label = "Excellent"
            elif overall >= 7:
                badge_color = "#2D6A4F"
                badge_label = "Good"
            elif overall >= 5:
                badge_color = "#B5924C"
                badge_label = "Moderate"
            else:
                badge_color = "#9B1C1C"
                badge_label = "Needs Review"

            st.markdown(f"""
            <div style="background:white; border-radius:20px;
                        padding:2rem 2.5rem;
                        box-shadow:0 4px 32px rgba(0,0,0,0.06);
                        margin-bottom:1.5rem;">
                <div style="display:flex; align-items:center;
                            justify-content:space-between;
                            border-bottom:1px solid #EDE9E0;
                            padding-bottom:1rem; margin-bottom:1.5rem;">
                    <div>
                        <div style="font-family:'Playfair Display',serif;
                                    font-size:1.1rem; font-weight:600;
                                    color:#1B4332;">Note Quality Report</div>
                        <div style="font-size:0.68rem; letter-spacing:2px;
                                    text-transform:uppercase; color:#8a8a7a;">
                            Evaluated against this transcript
                        </div>
                    </div>
                    <div style="background:{badge_color}; color:white;
                                border-radius:100px; padding:0.4rem 1.2rem;
                                font-size:0.75rem; font-weight:500;
                                letter-spacing:1px;">
                        {badge_label} · {overall}/10
                    </div>
                </div>
                <div style="font-size:0.72rem; color:#8a8a7a;
                            text-align:center; margin-bottom:0.5rem;
                            letter-spacing:1px; text-transform:uppercase;">
                    Overall note quality
                </div>
                <div style="font-size:2.5rem; font-weight:600;
                            color:#1B4332; text-align:center;
                            font-family:'Playfair Display',serif;">
                    {overall}<span style="font-size:1rem;
                                         color:#8a8a7a;">/10</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            metrics_order = [
                "completeness",
                "accuracy",
                "medication_capture",
                "clinical_reasoning",
                "structure"
            ]
            metric_labels = {
                "completeness":       "Completeness",
                "accuracy":           "Accuracy",
                "medication_capture": "Medication Capture",
                "clinical_reasoning": "Clinical Reasoning",
                "structure":          "Structure"
            }

            for key in metrics_order:
                if key not in ev:
                    continue
                m = ev[key]
                score = m.get("score", 0)
                reason = m.get("reason", "")
                description = m.get("description", "")
                pct = int((score / 10) * 100)

                if score >= 9:
                    bar_color = "#1B4332"
                elif score >= 7:
                    bar_color = "#2D6A4F"
                elif score >= 5:
                    bar_color = "#B5924C"
                else:
                    bar_color = "#9B1C1C"

                st.markdown(f"""
                <div style="background:white; border-radius:16px;
                            padding:1.25rem 1.75rem;
                            box-shadow:0 2px 16px rgba(0,0,0,0.05);
                            margin-bottom:0.75rem;">
                    <div style="display:flex; justify-content:space-between;
                                align-items:flex-start; margin-bottom:0.6rem;">
                        <div>
                            <div style="font-weight:600; font-size:0.88rem;
                                        color:#1A1A18;">
                                {metric_labels[key]}
                            </div>
                            <div style="font-size:0.72rem; color:#8a8a7a;
                                        margin-top:0.1rem;">
                                {description}
                            </div>
                        </div>
                        <div style="font-size:1.3rem; font-weight:600;
                                    color:{bar_color}; min-width:48px;
                                    text-align:right;">
                            {score}/10
                        </div>
                    </div>
                    <div style="background:#F2EDE4; border-radius:100px;
                                height:6px; width:100%;">
                        <div style="background:{bar_color};
                                    border-radius:100px; height:6px;
                                    width:{pct}%;">
                        </div>
                    </div>
                    <div style="font-size:0.72rem; color:#5C5C52;
                                margin-top:0.5rem; font-style:italic;">
                        {reason}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
            <div style="text-align:center; font-size:0.68rem; color:#8a8a7a;
                        margin-top:1rem; letter-spacing:1px;
                        text-transform:uppercase;">
                For clinical oversight only
            </div>
            """, unsafe_allow_html=True)