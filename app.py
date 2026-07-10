import os
import tempfile

import plotly.graph_objects as go
import streamlit as st
from streamlit_mic_recorder import mic_recorder

from services import interview
from services import resume as resume_service
from services.llm import LLMOverride, PERSONAS, SESSION_TYPES
from services.models import InterviewSession, Question

st.set_page_config(page_title="Pocket Interview Coach", page_icon="🎤", layout="centered")

ACCENT = "#9b6bff"
ACCENT_2 = "#2dd4ee"

PRESET_ROLES = ["Software Engineer", "Product Manager", "Data Analyst"]
EXPERIENCE_LEVELS = ["Entry-level (0-1 yrs)", "Mid-level (2-5 yrs)", "Senior (5+ yrs)", "Staff/Lead (8+ yrs)"]
SAMPLE_ANSWER_MODES = {"After each answer": "after", "At the end": "end", "Don't show": "off"}

st.markdown(
    f"""
    <style>
    h1, h2, h3 {{ font-weight: 700; }}
    .gradient-text {{
        background: linear-gradient(90deg, {ACCENT_2}, {ACCENT});
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }}
    .persona-badge {{
        display: inline-block;
        border: 1px solid #292942;
        border-radius: 999px;
        padding: 2px 12px;
        font-size: 0.75rem;
        color: #cfcfe6;
        background: rgba(255,255,255,0.04);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def init_state():
    defaults = {
        "page": "setup",
        "session": None,
        "current_index": 0,
        "current_feedback": None,
        "sample_answer_mode": "end",
        "byok_api_key": "",
        "byok_base_url": "",
        "byok_model": "",
        "drill_prefill": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_override() -> LLMOverride:
    return LLMOverride(
        api_key=st.session_state.byok_api_key or None,
        base_url=st.session_state.byok_base_url or None,
        model=st.session_state.byok_model or None,
    )


def render_sidebar():
    with st.sidebar:
        st.markdown("### 🎤 Pocket Interview Coach")
        if st.session_state.page != "setup":
            if st.button("🏠 Start new interview", use_container_width=True):
                st.session_state.page = "setup"
                st.session_state.session = None
                st.session_state.current_index = 0
                st.session_state.current_feedback = None
                st.rerun()
        with st.expander("⚙️ Bring your own API key"):
            st.caption("Leave blank to use the app's default key/model.")
            st.session_state.byok_api_key = st.text_input(
                "API key", value=st.session_state.byok_api_key, type="password"
            )
            st.session_state.byok_base_url = st.text_input(
                "Base URL", value=st.session_state.byok_base_url, placeholder="https://openrouter.ai/api/v1"
            )
            st.session_state.byok_model = st.text_input(
                "Model", value=st.session_state.byok_model, placeholder="google/gemma-4-26b-a4b-it"
            )


def speak_button(text: str, key: str):
    safe_text = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
    st.components.v1.html(
        f"""
        <button id="speak-{key}" style="
            background: rgba(255,255,255,0.06); border: 1px solid #292942; color: #cfcfe6;
            border-radius: 999px; padding: 6px 14px; font-size: 0.8rem; cursor: pointer;">
            🔊 Play question
        </button>
        <script>
        document.getElementById("speak-{key}").onclick = function() {{
            const u = new SpeechSynthesisUtterance("{safe_text}");
            u.rate = 0.95;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(u);
        }};
        </script>
        """,
        height=40,
    )


def score_gauge(value: int, title: str, color: str):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": title, "font": {"size": 14, "color": "#cfcfe6"}},
            number={"font": {"size": 28, "color": "#f7f7fb"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#292942"},
                "bar": {"color": color},
                "bgcolor": "#12121f",
                "borderwidth": 1,
                "bordercolor": "#292942",
            },
        )
    )
    fig.update_layout(height=180, margin=dict(l=20, r=20, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def setup_page():
    st.markdown('<h1 class="gradient-text">Pocket Interview Coach</h1>', unsafe_allow_html=True)
    st.write(
        "Practice out loud. Get coached on what you said **and** how you said it — "
        "pace, tone, filler words, and confidence."
    )

    prefill = st.session_state.drill_prefill or {}

    with st.form("setup_form"):
        role = st.text_input("Target role", value=prefill.get("role", ""), placeholder="e.g. Senior Backend Engineer")
        st.caption("Presets: " + " · ".join(PRESET_ROLES))

        company = st.text_input("Company (optional)", value=prefill.get("company", ""), placeholder="e.g. Acme Corp")

        session_type = st.selectbox("Session type", list(SESSION_TYPES.keys()), format_func=lambda k: SESSION_TYPES[k]["label"])

        col1, col2 = st.columns(2)
        with col1:
            persona_key = st.selectbox(
                "Interviewer persona",
                [""] + list(PERSONAS.keys()),
                format_func=lambda k: "Default" if k == "" else k.replace("_", " ").title(),
            )
        with col2:
            panel_mode = st.checkbox("Panel mode (rotate personas)")

        job_description = st.text_area("Job description (optional)", height=100)

        num_questions = st.slider("Number of questions", 1, 10, 5)
        experience_level = st.select_slider("Experience level", options=EXPERIENCE_LEVELS, value=prefill.get("experience_level") or EXPERIENCE_LEVELS[1])

        resume_file = st.file_uploader("Resume (optional, PDF or text)", type=["pdf", "txt", "md"])

        sample_mode_label = st.radio("Sample answers", list(SAMPLE_ANSWER_MODES.keys()), horizontal=True, index=1)

        drill_focus = prefill.get("drill_focus", "")
        if drill_focus:
            st.info(f"🎯 Weakness drill: focused practice on **{drill_focus}**")

        submitted = st.form_submit_button("Start Mock Interview", use_container_width=True, type="primary")

    if submitted:
        if not role.strip():
            st.error("Enter a target role to generate your interview.")
            return

        st.session_state.sample_answer_mode = SAMPLE_ANSWER_MODES[sample_mode_label]

        resume_text = ""
        if resume_file is not None:
            suffix = os.path.splitext(resume_file.name)[1] or ".txt"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(resume_file.getvalue())
                tmp_path = tmp.name
            try:
                resume_text = resume_service.extract_text(tmp_path, resume_file.name)
            finally:
                os.unlink(tmp_path)

        with st.spinner("Generating your interview with Gemma 4..."):
            try:
                session = interview.create_session(
                    role=role.strip(),
                    job_description=job_description.strip(),
                    num_questions=num_questions,
                    company=company.strip(),
                    experience_level=experience_level,
                    resume_text=resume_text,
                    session_type=session_type,
                    persona=persona_key,
                    panel_mode=panel_mode,
                    drill_focus=drill_focus,
                    override=get_override(),
                )
            except Exception as exc:
                st.error(f"Couldn't start the session: {exc}")
                return

        st.session_state.session = session
        st.session_state.current_index = 0
        st.session_state.current_feedback = None
        st.session_state.drill_prefill = None
        st.session_state.page = "session"
        st.rerun()


def session_page():
    session: InterviewSession = st.session_state.session
    idx = st.session_state.current_index
    question: Question = session.questions[idx]

    top_cols = st.columns([2, 3, 1])
    with top_cols[0]:
        label = f"{session.role} @ {session.company}" if session.company else session.role
        st.markdown(f'<span class="persona-badge">{label}</span>', unsafe_allow_html=True)
    with top_cols[2]:
        st.markdown(f"**{idx + 1} / {len(session.questions)}**")
    st.progress((idx) / max(len(session.questions), 1))

    with st.container(border=True):
        header_cols = st.columns([4, 1])
        with header_cols[0]:
            st.caption(("FOLLOW-UP" if question.is_dynamic else "QUESTION"))
            if question.persona:
                st.markdown(f'<span class="persona-badge">{question.persona.replace("_", " ").title()}</span>', unsafe_allow_html=True)
        with header_cols[1]:
            speak_button(question.text, key=question.id)
        st.markdown(f"### {question.text}")

        if question.answer is None:
            st.write("")
            audio = mic_recorder(start_prompt="🎙️ Record Answer", stop_prompt="⏹️ Stop", format="wav", key=f"rec_{question.id}")
            if audio and audio.get("bytes"):
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio["bytes"])
                    tmp_path = tmp.name
                try:
                    with st.spinner("Transcribing and scoring your answer..."):
                        answer, follow_up = interview.process_answer(session, question, tmp_path, get_override())
                    st.session_state.current_feedback = answer
                    if follow_up:
                        st.toast("Your interviewer added a follow-up question!", icon="🔍")
                except Exception as exc:
                    st.error(f"Couldn't analyze that answer: {exc}")
                finally:
                    os.unlink(tmp_path)
                st.rerun()
        else:
            answer = question.answer
            gcols = st.columns(2)
            with gcols[0]:
                score_gauge(answer.content_score, "Content", ACCENT)
            with gcols[1]:
                score_gauge(answer.delivery_score, "Delivery", ACCENT_2)

            mcols = st.columns(4)
            mcols[0].metric("Pace", f"{answer.words_per_minute:.0f} wpm")
            mcols[1].metric("Fillers", answer.filler_word_count)
            mcols[2].metric("Pauses", f"{answer.pause_ratio * 100:.0f}%")
            mcols[3].metric("Tone variation", f"{answer.pitch_variation * 100:.0f}%")

            if len(answer.delivery_timeline) > 1:
                fig = go.Figure()
                ts = [p["t"] for p in answer.delivery_timeline]
                fig.add_trace(go.Scatter(x=ts, y=[p["words_per_minute"] for p in answer.delivery_timeline], name="Pace (wpm)", line=dict(color=ACCENT_2)))
                fig.add_trace(go.Scatter(x=ts, y=[p["pitch_variation"] * 100 for p in answer.delivery_timeline], name="Tone %", line=dict(color=ACCENT)))
                fig.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend=dict(font=dict(color="#cfcfe6")))
                fig.update_xaxes(color="#8888a0")
                fig.update_yaxes(color="#8888a0")
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            st.info(f"**Content feedback:** {answer.content_feedback}")
            st.info(f"**Voice & tone feedback:** {answer.delivery_feedback}")

            if st.session_state.sample_answer_mode == "after" and question.sample_answer:
                with st.expander("Sample answer"):
                    st.write(question.sample_answer)

            is_last = idx + 1 == len(session.questions)
            if st.button("View Report" if is_last else "Next Question →", type="primary", use_container_width=True):
                st.session_state.current_feedback = None
                if is_last:
                    st.session_state.page = "report"
                else:
                    st.session_state.current_index += 1
                st.rerun()


def compute_weakest_area(session: InterviewSession) -> str:
    answered = session.answered_questions
    n = len(answered)
    scores = {
        "filler words": max(0.0, 1 - sum(a.answer.filler_word_count for a in answered) / n / 5),
        "pausing and hesitation": max(0.0, 1 - sum(a.answer.pause_ratio for a in answered) / n / 0.3),
        "vocal tone and expressiveness": sum(a.answer.pitch_variation for a in answered) / n,
        "voice steadiness": sum(a.answer.volume_consistency for a in answered) / n,
        "answer structure and specificity": sum(a.answer.content_score for a in answered) / n / 100,
    }
    return min(scores, key=scores.get)


def report_page():
    session: InterviewSession = st.session_state.session

    if not session.summary:
        with st.spinner("Building your report..."):
            try:
                interview.build_report(session, get_override())
            except Exception as exc:
                st.error(f"Couldn't build the report: {exc}")
                return

    st.markdown('<h1 class="gradient-text">Session Report</h1>', unsafe_allow_html=True)

    gcols = st.columns(2)
    with gcols[0]:
        score_gauge(session.avg_content_score, "Avg Content", ACCENT)
    with gcols[1]:
        score_gauge(session.avg_delivery_score, "Avg Delivery", ACCENT_2)

    st.write(session.summary)

    answered = session.answered_questions
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[f"Q{i+1}" for i in range(len(answered))], y=[q.answer.content_score for q in answered], name="Content", line=dict(color=ACCENT)))
    fig.add_trace(go.Scatter(x=[f"Q{i+1}" for i in range(len(answered))], y=[q.answer.delivery_score for q in answered], name="Delivery", line=dict(color=ACCENT_2)))
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend=dict(font=dict(color="#cfcfe6")), yaxis=dict(range=[0, 100]))
    fig.update_xaxes(color="#8888a0")
    fig.update_yaxes(color="#8888a0")
    st.subheader("Score trend")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.subheader("Top actions")
    for action in session.top_actions:
        st.markdown(f"- {action}")

    if len(answered) >= 2:
        weakest = compute_weakest_area(session)
        with st.container(border=True):
            st.markdown(f"🎯 **Your biggest opportunity:** {weakest}")
            if st.button("Drill this weak area"):
                st.session_state.drill_prefill = {
                    "role": session.role,
                    "company": session.company,
                    "experience_level": session.experience_level,
                    "drill_focus": weakest,
                }
                st.session_state.page = "setup"
                st.session_state.session = None
                st.rerun()

    with st.container(border=True):
        st.subheader("Personalized cheat sheet")
        if not session.cheat_sheet:
            if st.button("✨ Generate my cheat sheet"):
                with st.spinner("Generating..."):
                    try:
                        interview.build_cheat_sheet(session, get_override())
                    except Exception as exc:
                        st.error(f"Couldn't generate a cheat sheet: {exc}")
                st.rerun()
        else:
            st.markdown(session.cheat_sheet)

    st.subheader("Per-question detail")
    for i, q in enumerate(answered):
        with st.expander(f"Q{i + 1}: {q.text}"):
            st.caption(f"{q.answer.content_score}/100 content · {q.answer.delivery_score}/100 delivery")
            st.write(f"*\"{q.answer.transcript}\"*")
            st.write(q.answer.content_feedback)
            st.write(q.answer.delivery_feedback)
            if st.session_state.sample_answer_mode == "end" and q.sample_answer:
                st.markdown("**Sample answer:**")
                st.write(q.sample_answer)

    if st.button("Start New Interview", use_container_width=True):
        st.session_state.page = "setup"
        st.session_state.session = None
        st.rerun()


init_state()
render_sidebar()

if st.session_state.page == "setup":
    setup_page()
elif st.session_state.page == "session":
    session_page()
elif st.session_state.page == "report":
    report_page()
