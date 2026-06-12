"""
Export manager component for the Academic Assistant.
Allows students to download chat history, topic summaries, and study notes.
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Any


def _chat_to_markdown(chat_history: List[Dict[str, Any]]) -> str:
    """Convert chat history to a clean markdown document."""
    lines = [
        "# Academic Assistant — Chat Export",
        f"*Exported on {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
        "---",
        "",
    ]
    for msg in chat_history:
        role = "You" if msg["role"] == "user" else "Assistant"
        ts = msg.get("timestamp", "")
        lines.append(f"### {role}  ")
        if ts:
            lines.append(f"*{ts}*  ")
        lines.append("")
        lines.append(msg.get("content", ""))
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def _chat_to_txt(chat_history: List[Dict[str, Any]]) -> str:
    """Convert chat history to plain text."""
    lines = [
        "ACADEMIC ASSISTANT — CHAT EXPORT",
        f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 60,
        "",
    ]
    for msg in chat_history:
        role = "YOU" if msg["role"] == "user" else "ASSISTANT"
        ts = msg.get("timestamp", "")
        lines.append(f"[{role}]  {ts}")
        lines.append(msg.get("content", ""))
        lines.append("-" * 40)
        lines.append("")
    return "\n".join(lines)


def _build_study_summary(chat_history: List[Dict[str, Any]], document_stats: Dict) -> str:
    """Build a condensed study-notes summary from assistant answers."""
    answers = [
        msg["content"]
        for msg in chat_history
        if msg["role"] == "assistant"
    ]
    sources = list(document_stats.get("sources", {}).keys())

    lines = [
        "# Study Notes Summary",
        f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
        "## Sources Used",
    ]
    for src in sources:
        lines.append(f"- {src}")
    lines += ["", "---", "", "## Key Answers & Explanations", ""]

    for i, ans in enumerate(answers, 1):
        lines.append(f"### Answer {i}")
        lines.append(ans.strip())
        lines.append("")

    return "\n".join(lines)


def render_export_section():
    """
    Render the export panel in the sidebar.
    Shows download buttons for chat history and study notes.
    Only visible after at least one question has been answered.
    """
    chat_history = st.session_state.get("chat_history", [])
    if not chat_history:
        return

    st.markdown("---")
    st.subheader("Export")

    # Markdown export
    md_content = _chat_to_markdown(chat_history)
    st.download_button(
        label="Download chat (Markdown)",
        data=md_content.encode("utf-8"),
        file_name=f"academic_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
        mime="text/markdown",
        use_container_width=True,
    )

    # Plain text export
    txt_content = _chat_to_txt(chat_history)
    st.download_button(
        label="Download chat (Text)",
        data=txt_content.encode("utf-8"),
        file_name=f"academic_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain",
        use_container_width=True,
    )

    # Study notes export (only when docs are loaded)
    if st.session_state.get("documents_processed"):
        doc_stats = st.session_state.get("document_stats", {})
        summary = _build_study_summary(chat_history, doc_stats)
        st.download_button(
            label="Download study notes (Markdown)",
            data=summary.encode("utf-8"),
            file_name=f"study_notes_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
