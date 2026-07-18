"""
Streamlit UI for the Quiz Backend Management API.

Two modes, selectable from the sidebar:
  - Quiz Mode  : open to everyone, no login. Pick a category, answer, get scored.
  - Admin Mode : requires an admin login (JWT from the backend's /auth/login).
                 Only then can questions/choices be created, edited, or deleted.

This file talks to the FastAPI backend purely over HTTP (via `requests`),
so it can be deployed completely separately from the backend
(e.g. Streamlit Community Cloud) as long as API_BASE_URL points at your
live FastAPI deployment.

Run locally with:
    streamlit run ui/streamlit_app.py
"""

import requests
import streamlit as st

# ── Config ──────────────────────────────────────────────────────────────────

try:
    API_BASE_URL = st.secrets["API_BASE_URL"]
except Exception:
    API_BASE_URL = "http://localhost:8000"

API_BASE_URL = API_BASE_URL.rstrip("/")  # avoid accidental double-slash URLs like ".../com//questions"

st.set_page_config(page_title="DataQuiz", page_icon="◆", layout="wide")

CATEGORY_STYLE = {
    "Python": {"emoji": "🐍", "color": "#4B8BBE"},
    "SQL": {"emoji": "🗄️", "color": "#F29111"},
    "Statistics": {"emoji": "📊", "color": "#8E5CD9"},
    "Pandas/NumPy": {"emoji": "🐼", "color": "#2FA37C"},
    "Machine Learning": {"emoji": "🤖", "color": "#E0526A"},
}
DEFAULT_STYLE = {"emoji": "❖", "color": "#6C7A89"}


# ── Custom styling ────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, .app-title {
        font-family: 'Space Grotesk', sans-serif !important;
    }

    .stApp {
        background: radial-gradient(circle at 10% 0%, #171a2b 0%, #0e1018 55%, #0a0b12 100%);
    }

    .hero {
        padding: 1.4rem 1.8rem;
        border-radius: 16px;
        background: linear-gradient(135deg, #6C5CE7 0%, #341f97 100%);
        margin-bottom: 1.6rem;
        box-shadow: 0 8px 30px rgba(108, 92, 231, 0.25);
    }
    .hero h1 {
        color: white;
        margin: 0;
        font-size: 1.8rem;
        letter-spacing: -0.5px;
    }
    .hero p {
        color: rgba(255,255,255,0.85);
        margin: 0.2rem 0 0 0;
        font-size: 0.95rem;
    }

    .card {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 0.9rem;
    }

    .cat-badge {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        color: white;
        margin-bottom: 0.6rem;
    }

    .result-correct { border-left: 4px solid #2FA37C; padding-left: 0.9rem; }
    .result-wrong { border-left: 4px solid #E0526A; padding-left: 0.9rem; }

    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
    }

    section[data-testid="stSidebar"] {
        background: #10121c;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── API helper functions ─────────────────────────────────────────────────────

def _auth_headers():
    token = st.session_state.get("admin_token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def api_get(path, params=None):
    try:
        r = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return None


def _show_api_error(e, response=None):
    """Show the backend's actual detail message (e.g. the 4-choice-limit error) instead of a generic exception."""
    if response is not None:
        try:
            detail = response.json().get("detail")
            if detail:
                st.error(detail)
                return
        except Exception:
            pass
    st.error(f"Request failed: {e}")


def api_post(path, payload, auth=False):
    try:
        r = requests.post(
            f"{API_BASE_URL}{path}", json=payload, timeout=15,
            headers=_auth_headers() if auth else {},
        )
        if auth and r.status_code == 401:
            st.session_state.admin_token = None
            st.error("Session expired — please log in again.")
            st.rerun()
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        _show_api_error(e, response=getattr(e, "response", None))
        return None


def api_put(path, payload, auth=False):
    try:
        r = requests.put(
            f"{API_BASE_URL}{path}", json=payload, timeout=15,
            headers=_auth_headers() if auth else {},
        )
        if auth and r.status_code == 401:
            st.session_state.admin_token = None
            st.error("Session expired — please log in again.")
            st.rerun()
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return None


def api_delete(path, auth=False):
    try:
        r = requests.delete(
            f"{API_BASE_URL}{path}", timeout=15,
            headers=_auth_headers() if auth else {},
        )
        if auth and r.status_code == 401:
            st.session_state.admin_token = None
            st.error("Session expired — please log in again.")
            st.rerun()
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return None


def cat_style(category):
    return CATEGORY_STYLE.get(category, DEFAULT_STYLE)


# ── Sidebar navigation ───────────────────────────────────────────────────────

st.sidebar.markdown("### ◆ DataQuiz")
mode = st.sidebar.radio("Navigate", ["🎯 Take a Quiz", "🔐 Admin"], label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.caption(f"API: `{API_BASE_URL}`")

if st.session_state.get("admin_token"):
    st.sidebar.success(f"Logged in as **{st.session_state.get('admin_username')}**")
    if st.sidebar.button("Log out"):
        st.session_state.admin_token = None
        st.session_state.admin_username = None
        st.rerun()


# ── QUIZ MODE (public, no login) ─────────────────────────────────────────────

if mode == "🎯 Take a Quiz":
    st.markdown(
        """
        <div class="hero">
            <h1>Take a Data Science Quiz</h1>
            <p>No sign-in needed — pick a topic and test yourself.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False

    if not st.session_state.quiz_started:
        categories = api_get("/questions/categories/list") or []

        if not categories:
            st.warning("No categories found. Make sure the backend is seeded and reachable.")
        else:
            MIXED = "Mixed (All Categories)"
            category_options = [MIXED] + categories

            col1, col2 = st.columns(2)
            with col1:
                selected_category = st.selectbox(
                    "Category",
                    category_options,
                    format_func=lambda c: "🌐  Mixed (All Categories)" if c == MIXED else f"{cat_style(c)['emoji']}  {c}",
                )
            with col2:
                num_questions = st.slider("Number of questions", min_value=1, max_value=20, value=5)

            if selected_category == MIXED:
                st.markdown(
                    '<span class="cat-badge" style="background:#4A4E69">🌐 Mixed — all categories</span>',
                    unsafe_allow_html=True,
                )
            else:
                style = cat_style(selected_category)
                st.markdown(
                    f'<span class="cat-badge" style="background:{style["color"]}">'
                    f'{style["emoji"]} {selected_category}</span>',
                    unsafe_allow_html=True,
                )

            if st.button("Start Quiz ▶", type="primary"):
                params = {"limit": num_questions, "random_order": True}
                if selected_category != MIXED:
                    params["category"] = selected_category
                questions = api_get("/questions/", params=params)
                if questions:
                    st.session_state.quiz_started = True
                    st.session_state.quiz_questions = questions
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_category = selected_category
                    st.rerun()
                else:
                    st.warning("No questions found for this category.")

    else:
        questions = st.session_state.quiz_questions
        style = cat_style(st.session_state.get("quiz_category"))

        if not st.session_state.get("quiz_submitted", False):
            answered = sum(1 for q in questions if q["id"] in st.session_state.quiz_answers)
            st.progress(answered / len(questions) if questions else 0)
            st.caption(f"{answered} / {len(questions)} answered")

            for i, q in enumerate(questions, start=1):
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f"**Q{i}. {q['question_text']}**")
                choice_labels = [c["choice_text"] for c in q["choices"]]
                choice_ids = [c["id"] for c in q["choices"]]

                selected = st.radio(
                    "Your answer",
                    options=choice_ids,
                    format_func=lambda cid, labels=choice_labels, ids=choice_ids: labels[ids.index(cid)],
                    key=f"q_{q['id']}",
                    label_visibility="collapsed",
                    index=None,
                )
                if selected is not None:
                    st.session_state.quiz_answers[q["id"]] = selected
                st.markdown("</div>", unsafe_allow_html=True)

            if st.button("Submit Quiz ✔", type="primary"):
                st.session_state.quiz_submitted = True
                st.rerun()

        else:
            score = 0
            st.markdown("## Results")
            for i, q in enumerate(questions, start=1):
                correct_choice = next(c for c in q["choices"] if c["is_correct"])
                chosen_id = st.session_state.quiz_answers.get(q["id"])
                is_right = chosen_id == correct_choice["id"]
                score += int(is_right)

                css_class = "result-correct" if is_right else "result-wrong"
                icon = "✅" if is_right else "❌"
                st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                st.markdown(f"{icon} **Q{i}. {q['question_text']}**")
                if not is_right:
                    chosen_text = next(
                        (c["choice_text"] for c in q["choices"] if c["id"] == chosen_id), "No answer"
                    )
                    st.caption(f"Your answer: {chosen_text}  •  Correct: {correct_choice['choice_text']}")
                st.markdown("</div><br>", unsafe_allow_html=True)

            pct = round(100 * score / len(questions)) if questions else 0
            colA, colB = st.columns(2)
            with colA:
                st.metric("Score", f"{score} / {len(questions)}")
            with colB:
                st.metric("Percentage", f"{pct}%")

            if st.button("Try Another Quiz"):
                st.session_state.quiz_started = False
                st.session_state.quiz_submitted = False
                st.rerun()


# ── ADMIN MODE (requires login) ──────────────────────────────────────────────

else:
    if not st.session_state.get("admin_token"):
        st.markdown(
            """
            <div class="hero">
                <h1>Admin Login</h1>
                <p>Manage quiz content — questions and choices.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Log In", type="primary", use_container_width=True)
                if submitted:
                    try:
                        r = requests.post(
                            f"{API_BASE_URL}/auth/login",
                            json={"username": username, "password": password},
                            timeout=15,
                        )
                        if r.status_code == 200:
                            st.session_state.admin_token = r.json()["access_token"]
                            st.session_state.admin_username = username
                            st.rerun()
                        else:
                            st.error("Incorrect username or password.")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Could not reach backend: {e}")
            st.markdown("</div>", unsafe_allow_html=True)
            st.caption("Admin accounts are provisioned by the project owner only — there is no public sign-up.")

    else:
        st.markdown(
            """
            <div class="hero">
                <h1>Admin Panel</h1>
                <p>Create, edit, and remove quiz questions and choices.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        tab_questions, tab_choices = st.tabs(["📋 Questions", "🔘 Choices"])

        # ---- Questions tab ----
        with tab_questions:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Add a new question")
            with st.form("add_question_form", clear_on_submit=True):
                q_text = st.text_input("Question text")
                q_category = st.selectbox("Category", list(CATEGORY_STYLE.keys()) + ["Other"])
                submitted = st.form_submit_button("Create Question", type="primary")
                if submitted and q_text:
                    result = api_post(
                        "/questions/", {"question_text": q_text, "category": q_category}, auth=True
                    )
                    if result:
                        st.success(f"Created question #{result['id']}")
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            st.subheader("All questions")
            questions = api_get("/questions/", params={"limit": 500}) or []
            st.caption(f"{len(questions)} question(s) in the database")

            for q in questions:
                style = cat_style(q["category"])
                with st.expander(f"{style['emoji']} #{q['id']} — {q['question_text'][:70]}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        new_text = st.text_input("Text", value=q["question_text"], key=f"edit_text_{q['id']}")
                        new_category = st.text_input(
                            "Category", value=q["category"] or "", key=f"edit_cat_{q['id']}"
                        )
                    with col2:
                        st.write("")
                        st.write("")
                        if st.button("Update", key=f"update_{q['id']}"):
                            api_put(
                                f"/questions/{q['id']}",
                                {"question_text": new_text, "category": new_category},
                                auth=True,
                            )
                            st.success("Updated.")
                            st.rerun()
                        if st.button("Delete", key=f"delete_{q['id']}", type="secondary"):
                            api_delete(f"/questions/{q['id']}", auth=True)
                            st.warning("Deleted (choices cascade-deleted too).")
                            st.rerun()

                    st.markdown("**Choices:**")
                    for c in q["choices"]:
                        mark = "✅" if c["is_correct"] else "—"
                        st.write(f"{mark} {c['choice_text']}")

        # ---- Choices tab ----
        with tab_choices:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Add a new choice")
            questions_for_dropdown = api_get("/questions/", params={"limit": 500}) or []
            question_options = {
                f"#{q['id']} — {q['question_text'][:50]}": q["id"] for q in questions_for_dropdown
            }

            with st.form("add_choice_form", clear_on_submit=True):
                if question_options:
                    chosen_label = st.selectbox("Attach to question", list(question_options.keys()))
                    c_text = st.text_input("Choice text")
                    c_correct = st.checkbox("This is the correct answer")
                    submitted = st.form_submit_button("Create Choice", type="primary")
                    if submitted and c_text:
                        result = api_post(
                            "/choices/",
                            {
                                "choice_text": c_text,
                                "is_correct": c_correct,
                                "question_id": question_options[chosen_label],
                            },
                            auth=True,
                        )
                        if result:
                            st.success(f"Created choice #{result['id']}")
                            st.rerun()
                else:
                    st.info("Create a question first before adding choices.")
            st.markdown("</div>", unsafe_allow_html=True)

            st.subheader("All choices")
            choices = api_get("/choices/", params={"limit": 500}) or []
            st.caption(f"{len(choices)} choice(s) in the database")

            for c in choices:
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    mark = "✅" if c["is_correct"] else "—"
                    st.write(f"{mark} **#{c['id']}** (Q{c['question_id']}): {c['choice_text']}")
                with col2:
                    if st.button("Toggle", key=f"toggle_{c['id']}"):
                        api_put(f"/choices/{c['id']}", {"is_correct": not c["is_correct"]}, auth=True)
                        st.rerun()
                with col3:
                    if st.button("Delete", key=f"delchoice_{c['id']}"):
                        api_delete(f"/choices/{c['id']}", auth=True)
                        st.rerun()
