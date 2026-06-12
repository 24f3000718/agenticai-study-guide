"""
Track A2: Comprehensive Exam Preparation Assistant.
Specialises in exam-oriented workflows: topic-wise practice, weak-area
identification, study plan generation, and progress analytics drawn from
all uploaded academic materials.
"""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime

from tracks.base_track import BaseTrack, TrackFeatures
from config.settings import TrackType, ContentType
from core.rag_chain import ChainMode
from prompts.base_prompts import EXAM_MODE_PROMPT, STUDY_MODE_PROMPT, QUICK_REVISION_PROMPT


# ---------------------------------------------------------------------------
# Prompt templates specific to the Exam Prep track
# ---------------------------------------------------------------------------

EXAM_PRACTICE_PROMPT = """You are an expert exam preparation coach for Indian university students.

You have access to the student's uploaded study materials (lecture notes, textbooks,
past papers, lab manuals).  Use them as the primary source of truth.

Context from uploaded materials:
{context}

Student's request: {question}

Respond with:
1. **Direct Answer** — a clear, exam-ready answer
2. **Key Points to Remember** — 3-5 bullet points the examiner expects
3. **Common Mistakes** — typical errors students make on this topic
4. **Sample Answer** — a model answer in the style of a university exam response
5. **Source** — mention which uploaded material supports this answer

Keep the tone encouraging and exam-focused."""

WEAK_AREA_PROMPT = """You are analysing a student's question history to identify knowledge gaps.

Question history:
{context}

Current query: {question}

Based on the topics covered and difficulty signals in the questions, provide:
1. **Identified Weak Areas** — topics that need more attention
2. **Strength Areas** — topics the student seems confident in
3. **Recommended Focus** — prioritised list of topics to review before the exam
4. **Study Strategy** — practical 3-step plan to address the weak areas

Be specific and actionable."""

STUDY_PLAN_PROMPT = """You are an academic advisor helping a student plan their exam preparation.

Available study materials and topics:
{context}

Student's request: {question}

Create a structured study plan including:
1. **Topic Priority List** — ranked by importance and difficulty
2. **Daily Schedule** — realistic time allocation per topic
3. **Practice Strategy** — how to use past papers effectively
4. **Revision Checkpoints** — mini-milestones to track progress
5. **Last-Day Tips** — quick revision strategy for the day before the exam

Tailor the plan to Indian university semester exam patterns."""


class TrackA2Exam(BaseTrack):
    """
    Track A2: Comprehensive Exam Preparation Assistant.
    Provides exam-focused workflows built on multi-document RAG.
    """

    def __init__(self):
        """Initialise the Exam Prep track."""
        super().__init__()
        self.track_type = TrackType.TRACK_A2_EXAM
        self.features = self.get_features()

        # Session-level analytics
        self.topics_queried: Dict[str, int] = {}          # topic → query count
        self.weak_areas: List[str] = []                   # topics flagged as weak
        self.questions_answered: int = 0
        self.study_plan_generated: bool = False

    # ------------------------------------------------------------------
    # BaseTrack interface
    # ------------------------------------------------------------------

    def get_features(self) -> TrackFeatures:
        return TrackFeatures(
            name="Exam Preparation Assistant",
            description="""
Exam-focused academic assistant with:
- Topic-wise question practice with solutions from uploaded materials
- Weak-area identification and targeted recommendations
- Custom study plan generation based on your syllabus
- Exam-ready answer formatting for university submissions
- Progress tracking across topics and practice sessions
""",
            supported_content_types=[
                ContentType.LECTURE_NOTES.value,
                ContentType.TEXTBOOK.value,
                ContentType.PAST_PAPER.value,
                ContentType.LAB_MANUAL.value,
                ContentType.REFERENCE.value,
            ],
            special_prompts={
                "exam_practice": EXAM_PRACTICE_PROMPT,
                "weak_area":     WEAK_AREA_PROMPT,
                "study_plan":    STUDY_PLAN_PROMPT,
            },
            analytics_enabled=True,
            progress_tracking=True,
            export_formats=["markdown", "study_plan", "weak_area_report"],
        )

    def get_specialized_prompt(self, prompt_type: str) -> str:
        return self.features.special_prompts.get(prompt_type, EXAM_MODE_PROMPT)

    def process_query(
        self,
        query: str,
        query_type: str = "exam",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Route the query to the appropriate exam-prep handler.

        Args:
            query:      The student's question or request.
            query_type: One of 'exam', 'study', 'quick', 'study_plan',
                        'weak_area', or 'practice'.
        Returns:
            Dict with 'answer', 'track_type', 'sources', and metadata.
        """
        category = self._detect_query_category(query, query_type)
        self._record_topic(query)

        handlers = {
            "study_plan":   self._handle_study_plan_query,
            "weak_area":    self._handle_weak_area_query,
            "practice":     self._handle_practice_query,
            "exam":         self._handle_exam_query,
            "quick":        self._handle_quick_query,
            "study":        self._handle_study_query,
        }

        handler = handlers.get(category, self._handle_exam_query)
        result = handler(query, **kwargs)
        self.questions_answered += 1
        return result

    # ------------------------------------------------------------------
    # Category detection
    # ------------------------------------------------------------------

    def _detect_query_category(self, query: str, hint: str = "exam") -> str:
        """Infer the best handler from the query text."""
        q_lower = query.lower()

        study_plan_keywords = [
            "study plan", "schedule", "prepare", "how to study",
            "plan for exam", "exam schedule", "revision plan",
        ]
        weak_area_keywords = [
            "weak area", "what should i focus", "where am i weak",
            "improve", "struggling", "difficult topics", "gap",
        ]
        practice_keywords = [
            "practice", "previous year", "past paper", "question bank",
            "solve this question", "model question", "sample question",
        ]
        quick_keywords = ["brief", "short", "quick revision", "summarize", "in brief", "quickly summarize"]

        if any(k in q_lower for k in study_plan_keywords):
            return "study_plan"
        if any(k in q_lower for k in weak_area_keywords):
            return "weak_area"
        if any(k in q_lower for k in practice_keywords):
            return "practice"
        if any(k in q_lower for k in quick_keywords):
            return "quick"
        if hint in ("study", "quick"):
            return hint
        return "exam"

    # ------------------------------------------------------------------
    # Query handlers
    # ------------------------------------------------------------------

    def _handle_exam_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """Standard exam-mode answer: structured, mark-scheme aware."""
        try:
            chain = self.rag_manager.create_chain(mode=ChainMode.EXAM)
            answer = chain.invoke(query)
            return self.format_response(
                answer,
                metadata={"mode": "exam", "track": "A2"},
            )
        except Exception as exc:
            return self.format_response(
                f"Unable to generate exam answer: {exc}",
                metadata={"error": True},
            )

    def _handle_study_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """Deep study-mode answer with theory and examples."""
        try:
            chain = self.rag_manager.create_chain(mode=ChainMode.STUDY)
            answer = chain.invoke(query)
            return self.format_response(
                answer,
                metadata={"mode": "study", "track": "A2"},
            )
        except Exception as exc:
            return self.format_response(
                f"Unable to generate study answer: {exc}",
                metadata={"error": True},
            )

    def _handle_quick_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """Concise bullet-point revision answer."""
        try:
            chain = self.rag_manager.create_chain(mode=ChainMode.QUICK)
            answer = chain.invoke(query)
            return self.format_response(
                answer,
                metadata={"mode": "quick", "track": "A2"},
            )
        except Exception as exc:
            return self.format_response(
                f"Unable to generate quick answer: {exc}",
                metadata={"error": True},
            )

    def _handle_practice_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Answers a past-paper / practice question with exam-ready formatting.
        Uses the EXAM_PRACTICE_PROMPT for richer structure.
        """
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.runnables import RunnableParallel, RunnablePassthrough

            retriever = self.rag_manager.vector_store_manager.get_retriever()

            def fmt_docs(docs):
                return "\n\n".join(
                    f"[{d.metadata.get('content_type','?')}] {d.page_content}"
                    for d in docs
                )

            prompt = ChatPromptTemplate.from_template(EXAM_PRACTICE_PROMPT)
            chain = (
                RunnableParallel(
                    context=retriever | fmt_docs,
                    question=RunnablePassthrough(),
                )
                | prompt
                | self.rag_manager.llm
                | StrOutputParser()
            )
            answer = chain.invoke(query)
            return self.format_response(
                answer,
                metadata={"mode": "practice", "track": "A2"},
            )
        except Exception as exc:
            # Fallback to standard exam chain
            return self._handle_exam_query(query, **kwargs)

    def _handle_study_plan_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Generates a personalised study plan using uploaded syllabus/notes.
        """
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.runnables import RunnableParallel, RunnablePassthrough

            retriever = self.rag_manager.vector_store_manager.get_retriever(k=8)

            def fmt_docs(docs):
                return "\n\n".join(
                    f"[{d.metadata.get('source','?')}] {d.page_content[:400]}"
                    for d in docs
                )

            prompt = ChatPromptTemplate.from_template(STUDY_PLAN_PROMPT)
            chain = (
                RunnableParallel(
                    context=retriever | fmt_docs,
                    question=RunnablePassthrough(),
                )
                | prompt
                | self.rag_manager.llm
                | StrOutputParser()
            )
            answer = chain.invoke(query)
            self.study_plan_generated = True
            return self.format_response(
                answer,
                metadata={"mode": "study_plan", "track": "A2"},
            )
        except Exception as exc:
            return self.format_response(
                f"Unable to generate study plan: {exc}",
                metadata={"error": True},
            )

    def _handle_weak_area_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Analyses the session's query history to surface weak areas.
        """
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.runnables import RunnableParallel, RunnablePassthrough

            # Build a synthetic context from topic query counts
            topic_summary = "\n".join(
                f"- {topic}: queried {count} time(s)"
                for topic, count in sorted(
                    self.topics_queried.items(), key=lambda x: x[1], reverse=True
                )
            ) or "No topic history yet."

            retriever = self.rag_manager.vector_store_manager.get_retriever(k=6)

            def fmt_docs(docs):
                return topic_summary + "\n\nUploaded material topics:\n" + "\n\n".join(
                    f"[{d.metadata.get('content_type','?')}] {d.page_content[:300]}"
                    for d in docs
                )

            prompt = ChatPromptTemplate.from_template(WEAK_AREA_PROMPT)
            chain = (
                RunnableParallel(
                    context=retriever | fmt_docs,
                    question=RunnablePassthrough(),
                )
                | prompt
                | self.rag_manager.llm
                | StrOutputParser()
            )
            answer = chain.invoke(query)
            return self.format_response(
                answer,
                metadata={"mode": "weak_area", "track": "A2"},
            )
        except Exception as exc:
            return self.format_response(
                f"Unable to analyse weak areas: {exc}",
                metadata={"error": True},
            )

    # ------------------------------------------------------------------
    # Analytics helpers
    # ------------------------------------------------------------------

    def _record_topic(self, query: str) -> None:
        """
        Heuristically extract topic keywords from the query and increment
        counters for session-level analytics.
        """
        # Simple keyword extraction — find capitalised phrases or known keywords
        words = re.findall(r'\b[A-Z][a-z]{2,}\b|\b(?:algorithm|data structure|sorting|'
                           r'database|network|os|memory|process|tree|graph|sql|'
                           r'normalization|recursion|complexity|array|pointer)\b',
                           query, re.IGNORECASE)
        for word in set(words):
            key = word.strip().title()
            self.topics_queried[key] = self.topics_queried.get(key, 0) + 1

    def get_exam_summary(self) -> Dict[str, Any]:
        """Return session-level analytics for the dashboard."""
        return {
            "questions_answered":    self.questions_answered,
            "topics_queried":        self.topics_queried,
            "study_plan_generated":  self.study_plan_generated,
            "total_topics":          len(self.topics_queried),
            "most_queried_topic":    max(
                self.topics_queried, key=self.topics_queried.get
            ) if self.topics_queried else None,
        }

    def get_welcome_message(self) -> str:
        return (
            "Welcome to the Exam Preparation Assistant! "
            "Upload your lecture notes, past papers, and textbooks, "
            "then ask me to explain topics, solve exam questions, "
            "or generate a personalised study plan."
        )
