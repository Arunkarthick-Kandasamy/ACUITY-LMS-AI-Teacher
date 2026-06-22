from __future__ import annotations

PROMPT_MEMORY_EXTRACT = """Analyze the following teaching interaction and extract key observations about the student's learning patterns.

Concept: {concept_title}
Student Response: {student_response}
Mastery Estimate: {mastery_estimate}
Evaluation: {evaluation}
Diagnosis Type: {diagnosis_type}
Misconception: {misconception}
Knowledge Gap: {knowledge_gap}
Recommended Action: {recommended_action}

Return a JSON object with these fields:
- struggles (array of strings): concepts or skills the student struggles with
- excels (array of strings): concepts or skills the student shows strength in
- misconceptions (array of strings): recurring misconception patterns detected
- learning_preferences (array of strings): observed learning style preferences
- pacing_notes (string): observations about the student's learning pace"""
