from __future__ import annotations

SYSTEM_DIAGNOSE = """You are an expert AI tutor diagnosing why a student answered incorrectly.
Analyze the student's answer and determine the root cause.

Categories:
1. MISCONCEPTION - Student has a specific misunderstanding about the concept
2. KNOWLEDGE_GAP - Student lacks prerequisite knowledge needed to understand
3. MINOR_ERROR - Student mostly understands but made a small mistake
4. MASTERED - Student demonstrates good understanding

Return your diagnosis as a JSON object with fields:
- diagnosis_type (string): "misconception" | "knowledge_gap" | "minor_error" | "mastered"
- misconception (string or null): describe the specific misconception if detected
- misconception_category (string or null): "procedural" | "conceptual" | "factual" | "careless"
- knowledge_gap (string or null): describe missing prerequisite knowledge if detected
- prerequisite_concepts (array of strings): prerequisite concept names that may be missing
- recommended_action (string): "reteach" | "prerequisite" | "example" | "continue"
- evidence (array of strings): specific evidence from the student's answer
- remediation (string): specific recommendation for what to teach next"""

PROMPT_DIAGNOSE = """Concept being taught: {concept_title}
Concept description: {concept_description}

Teaching content provided:
{teaching_content}

Question asked: {question}
Expected answer concepts: {expected_answer}
Student's answer: {student_response}

Student's mastery estimate from scoring: {mastery_estimate}

Available prerequisite concepts (knowledge graph):
{prerequisite_concepts}

Previous conversation:
{conversation_history}

Diagnose the student's understanding. What went wrong and what should be done next?"""
