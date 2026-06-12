"""
Academic Assistant — Main Streamlit Application
================================================
AI-powered academic assistant for CS students.
Supports:
  Track A1 — Computer Science Subject Guide
  Track A2 — Exam Preparation Assistant

Students upload lecture notes, textbooks, lab manuals, and past papers
and get comprehensive, source-attributed answers in three response modes.
"""

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

from config.settings import (
    TrackType,
    TRACK_DISPLAY_NAMES,
    TRACK_DESCRIPTIONS,
)
from core.rag_chain import get_rag_chain_manager, ChainMode
from tracks.track_a1_cs import TrackA1CS
from tracks.track_a2_exam import TrackA2Exam
from components.sidebar import render_sidebar
from components.chat_interface import render_chat_interface
from components.progress_tracker import render_cs_dashboard, render_exam_dashboard


# ---------------------------------------------------------------------------
# API key check
# ---------------------------------------------------------------------------

def check_api_keys() -> bool:
    for key, value in os.environ.items():
        if key.startswith("GROQ_API_KEY") and value and value != "":
            return True
    keys_string = os.getenv("GROQ_API_KEYS", "")
    if keys_string:
        valid_keys = [k.strip() for k in keys_string.split(",") if k.strip()]
        if valid_keys:
            return True
    return False


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

def initialize_session_state():
    """Set up all Streamlit session-state variables on first load."""
    if "track_selected" not in st.session_state:
        st.session_state.track_selected = False

    if "current_track" not in st.session_state:
        st.session_state.current_track = None

    if "track_type" not in st.session_state:
        st.session_state.track_type = None

    if "vector_store_manager" not in st.session_state:
        from core.vector_store import get_vector_store_manager
        st.session_state.vector_store_manager = get_vector_store_manager()

    if "documents_processed" not in st.session_state:
        st.session_state.documents_processed = False

    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = set()

    if "document_stats" not in st.session_state:
        st.session_state.document_stats = {}

    if "rag_manager" not in st.session_state:
        st.session_state.rag_manager = get_rag_chain_manager()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "current_mode" not in st.session_state:
        st.session_state.current_mode = "Study Mode"

    if "progress_data" not in st.session_state:
        st.session_state.progress_data = {}

    if "processing_in_progress" not in st.session_state:
        st.session_state.processing_in_progress = False


# ---------------------------------------------------------------------------
# Track selection UI
# ---------------------------------------------------------------------------

def render_track_selection():
    """Let the user pick which learning track to use."""
    st.title("🎓 Academic Assistant")
    st.markdown("### Choose Your Learning Track")
    st.markdown(
        "Select the track that best fits your current goal. "
        "You can switch tracks at any time from the sidebar (your documents will be cleared)."
    )
    st.markdown("---")

    col_a1, col_a2 = st.columns(2)

    with col_a1:
        st.subheader("📚 Track A1")
        st.markdown("**Computer Science Subject Guide**")
        st.markdown(TRACK_DESCRIPTIONS[TrackType.TRACK_A1_CS])
        if st.button("Select Track A1", use_container_width=True, type="primary"):
            _activate_track(TrackType.TRACK_A1_CS)

    with col_a2:
        st.subheader("📝 Track A2")
        st.markdown("**Exam Preparation Assistant**")
        st.markdown(TRACK_DESCRIPTIONS[TrackType.TRACK_A2_EXAM])
        if st.button("Select Track A2", use_container_width=True, type="primary"):
            _activate_track(TrackType.TRACK_A2_EXAM)


def _activate_track(track_type: TrackType):
    """Initialise the chosen track and move to the main UI."""
    st.session_state.track_type = track_type
    if track_type == TrackType.TRACK_A1_CS:
        st.session_state.current_track = TrackA1CS()
    else:
        st.session_state.current_track = TrackA2Exam()
    st.session_state.track_selected = True
    st.session_state.chat_history = []
    st.session_state.documents_processed = False
    st.session_state.uploaded_files = set()
    st.rerun()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(
        page_title="Academic Assistant",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if not check_api_keys():
        st.error("No GROQ API key found. Please check your .env file.")
        st.info("""
**How to fix:**
1. Create a `.env` file in the project root.
2. Add:  `GROQ_API_KEY_1=gsk_your_key_here`
3. Get free keys at https://console.groq.com
        """)
        st.stop()

    initialize_session_state()

    if not st.session_state.track_selected:
        render_track_selection()
    else:
        render_sidebar()
        render_chat_interface()

        if st.session_state.documents_processed:
            if st.session_state.track_type == TrackType.TRACK_A1_CS:
                render_cs_dashboard()
            elif st.session_state.track_type == TrackType.TRACK_A2_EXAM:
                render_exam_dashboard()


if __name__ == "__main__":
    main()
