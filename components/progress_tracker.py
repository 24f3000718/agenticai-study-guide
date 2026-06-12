"""
Progress tracker component for the Academic Assistant.
Displays exam preparation analytics and the A2 dashboard.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, List

from config.settings import TrackType

# ---------------------------------------------------------------------------
# Track A2 — Exam Preparation Dashboard
# ---------------------------------------------------------------------------

def render_exam_dashboard():
    """
    Dashboard for Track A2.  Shows query history, topic coverage, and
    study-plan generation status.
    Called from main app when Track A2 is active and documents are loaded.
    """
    from config.settings import TrackType

    if st.session_state.get("track_type") != TrackType.TRACK_A2_EXAM:
        return

    track = st.session_state.get("current_track")
    if not track or not hasattr(track, "get_exam_summary"):
        return

    col_header, col_action = st.columns([8, 1])
    with col_action:
        if st.button("Switch Track"):
            st.session_state.track_selected = False
            st.session_state.current_track = None
            st.session_state.documents_processed = False
            st.rerun()

    st.markdown("---")
    st.header("Exam Prep Analytics")

    summary = track.get_exam_summary()

    # Metrics row
    c1, c2, c3 = st.columns(3)
    c1.metric("Questions Answered", summary.get("questions_answered", 0))
    c2.metric("Topics Covered",     summary.get("total_topics", 0))
    c3.metric(
        "Study Plan",
        "✅ Generated" if summary.get("study_plan_generated") else "Not yet",
    )

    # Topic frequency bar
    topics = summary.get("topics_queried", {})
    if topics:
        st.subheader("Topic Query Frequency")
        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]
        max_count = sorted_topics[0][1] if sorted_topics else 1
        for topic, count in sorted_topics:
            st.progress(count / max_count, text=f"{topic}  ({count} query{'s' if count > 1 else ''})")
    else:
        st.info("Ask questions to build your topic analytics.")

    # Most-queried topic
    top = summary.get("most_queried_topic")
    if top:
        st.success(f"📌 Most-studied topic this session: **{top}**")

    # Quick-access buttons for exam prep workflows
    st.subheader("Quick Actions")
    qcol1, qcol2 = st.columns(2)
    with qcol1:
        if st.button("📋 Generate Study Plan", use_container_width=True):
            st.session_state.chat_history.append({
                "role": "user",
                "content": "Please generate a comprehensive study plan for my upcoming exam based on my uploaded materials.",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
            st.rerun()
    with qcol2:
        if st.button("🔍 Identify Weak Areas", use_container_width=True):
            st.session_state.chat_history.append({
                "role": "user",
                "content": "Based on the topics I have studied, what are my weak areas and how should I improve?",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
            st.rerun()
