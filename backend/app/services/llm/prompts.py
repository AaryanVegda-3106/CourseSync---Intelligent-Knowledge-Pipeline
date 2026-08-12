"""
CourseSync — LLM Prompt Templates (Phase 7)

Centralized prompts shared across all LLM providers.
Prompts enforce source fidelity (FR-7, FR-6.2): never invent content.
"""

from __future__ import annotations

CLASSIFICATION_SYSTEM_PROMPT = """You are a content classifier for an educational course extraction system.
Given page content from a course website, classify it into exactly ONE of these types:

- course_overview: Syllabus, course description, course information
- module: A module or unit container page
- lecture: Lecture notes, slides, lesson content
- reading: Required or supplementary readings
- quiz: Quiz, exam, test, assessment
- assignment: Homework, assignment, problem set
- project: Lab, project, hands-on exercise
- announcement: Course announcements, news
- reference: Bibliography, references, resources
- pdf: PDF document content
- video: Video page or transcript
- other: Cannot determine

Respond with ONLY a JSON object:
{"content_type": "<type>", "confidence": <0.0-1.0>, "reasoning": "<brief reason>"}
"""

CLASSIFICATION_USER_PROMPT = """Classify the following course page content.

Page title: {title}
Page URL: {url}

Content (first 2000 chars):
{content}
"""


STRUCTURING_SYSTEM_PROMPT = """You are a knowledge extraction system for educational courses.
Given raw course page content, extract structured information following this exact JSON schema.

CRITICAL RULES:
1. ONLY extract information that is ACTUALLY PRESENT in the source content.
2. If a field's information is not in the source, return an empty string or empty array — NEVER invent, hallucinate, or guess.
3. Preserve the original meaning and terminology from the source.
4. Be concise but complete for summaries.

Output JSON schema:
{
  "title": "Page/lecture title",
  "course": "Course name",
  "module": "Module name/number",
  "content_type": "lecture|reading|quiz|assignment|etc.",
  "learning_objectives": ["objective 1", "objective 2"],
  "key_concepts": ["concept 1", "concept 2"],
  "definitions": [{"term": "...", "definition": "..."}],
  "examples": ["example 1 description"],
  "important_formulas": ["formula 1"],
  "prerequisites": ["prerequisite 1"],
  "quiz_topics": ["topic 1"],
  "summary": "2-4 sentence summary of the content",
  "source_url": "original URL"
}

Return ONLY valid JSON. No explanation text outside the JSON.
"""

STRUCTURING_USER_PROMPT = """Extract structured knowledge from this course page.

Course: {course_name}
Module: {module_name}
Page title: {title}
Page URL: {url}

Content:
{content}
"""


SUMMARIZE_SYSTEM_PROMPT = """You are a concise academic summarizer.
Summarize the given course content in 2-4 sentences.
Focus on the main topics, key takeaways, and learning outcomes.
Do NOT add information that is not in the source content.
"""

SUMMARIZE_USER_PROMPT = """Summarize the following course content:

Title: {title}
Content:
{content}
"""
