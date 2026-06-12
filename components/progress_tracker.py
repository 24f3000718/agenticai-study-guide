"""
Progress tracker component for the Academic Assistant.
Displays learning progress, weak areas, and the CS dashboard.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, List

from config.settings import TrackType

def _render_cs_dashboard_content():
    """
    Internal function to render CS dashboard content for Track A1.
    shows detected code blocks, algorithms, and subject analysis.
    """
    track = st.session_state.get("current_track")
    if not track:
        return
    
    st.markdown("---")
    st.header("CS Subject Analysis")
    
    summary = track.get_cs_subject_summary()
    subjects = summary.get("identified_subjects", {})
    
    if subjects:
        st.subheader("Detected CS Subjects")
        sorted_subjects = sorted(subjects.items(), key=lambda x: x[1], reverse=True)
        for subject, confidence in sorted_subjects:
            st.progress(
                confidence,
                text=f"{subject} (Confidence: {confidence:.1%})"
            )
    else:
        st.info("No CS subjects detected yet. Upload more CS-related documents.")
    
    primary_subject = summary.get("primary_subject")
    if primary_subject:
        st.success(f"📌 Primary Subject: **{primary_subject}**")
    
    st.subheader("Content Analysis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Code Blocks",
            summary.get("code_blocks_found", 0),
            help="Number of code snippets detected in documents"
        )
    
    with col2:
        st.metric(
            "Algorithms",
            summary.get("algorithms_detected", 0),
            help="Number of algorithms identified"
        )
    
    with col3:
        st.metric(
            "Total Subjects",
            summary.get("total_subjects", 0),
            help="Number of distinct CS subjects identified"
        )
    
    if hasattr(track, 'detected_algorithms') and track.detected_algorithms:
        st.subheader("Detected Algorithms")
        for algo in track.detected_algorithms[:5]:
            with st.expander(f"🔍 {algo.name}"):
                st.caption(f"**Type:** {algo.algorithm_type.value}")
                st.caption(f"**Time Complexity:** {algo.complexity_time}")
                st.caption(f"**Space Complexity:** {algo.complexity_space}")
                if algo.steps:
                    st.caption("**Steps:**")
                    for i, step in enumerate(algo.steps[:5], 1):
                        st.caption(f" {i}. {step}")
    
    if hasattr(track, 'detected_code_blocks') and track.detected_code_blocks:
        st.subheader("Code Language Distribution")
        lang_counts = {}
        for block in track.detected_code_blocks:
            lang = block.language
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
        for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True):
            st.caption(f"• {lang}: {count} block(s)")

def render_cs_dashboard():
    """
    Wrapper for CS dashboard that checks track type before rendering.
    called from the main app for Track A1.
    """
    if st.session_state.get("track_type") == TrackType.TRACK_A1_CS:
        track = st.session_state.get("current_track")
        # provide quick switch track action on CS dashboard
        col_header, col_action = st.columns([8, 1])
        with col_header:
            st.write("")
        with col_action:
            if st.button("Switch Track"):
                st.session_state.track_selected = False
                st.session_state.current_track = None
                st.session_state.documents_processed = False
                st.rerun()

        if track and hasattr(track, 'get_cs_subject_summary'):
            _render_cs_dashboard_content()

def render_progress_dashboard():
    """
    Main progress dashboard router.
    renders the appropriate dashboard based on active track type.
    this is the entry point called from the main app.
    """
    track_type = st.session_state.get("track_type")

    # Only CS track supported; render CS dashboard when available
    if track_type == TrackType.TRACK_A1_CS:
        render_cs_dashboard()

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
