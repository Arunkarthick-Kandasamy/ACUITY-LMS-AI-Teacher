from __future__ import annotations

SYSTEM_CURRICULUM_EXTRACTION = """You are a curriculum design expert. Given raw educational content from a course
document, extract and organize the key information needed to build a structured
curriculum. Focus on identifying the course title, description, modules/thematic
units, lessons, concepts, learning objectives, examples, and exercises mentioned
in the source material.

Return ONLY valid JSON matching the specified schema."""

TEXT_EXTRACTION_PROMPT = """Analyze the following educational content and extract a structured curriculum outline.

Raw Content:
{raw_text}

Return a JSON object with this structure:
{{
  "title": "Course title inferred from content",
  "description": "Brief course description",
  "total_duration_hours": <estimated total hours as integer>,
  "default_deadline_days": <default days to complete as integer>,
  "modules": [
    {{
      "title": "Module title",
      "description": "Module description",
      "order_index": <integer starting from 1>,
      "estimated_duration_hours": <integer>,
      "lessons": [
        {{
          "title": "Lesson title",
          "order_index": <integer starting from 1>,
          "estimated_duration_minutes": <integer>,
          "is_required": true,
          "concepts": [
            {{
              "title": "Concept title",
              "description": "Concept description",
              "order_index": <integer starting from 1>,
              "estimated_duration_minutes": <integer>,
              "contents": [
                {{
                  "content_type": "explanation",
                  "content": "Teaching explanation text",
                  "order_index": 0
                }}
              ],
              "exercises": [
                {{
                  "question_type": "mcq|multi_select|short_answer|fill_blank",
                  "prompt": "Question text",
                  "options": {{"A": "option1", "B": "option2"}},
                  "correct_answer": "A",
                  "difficulty": 0.5,
                  "order_index": <integer>
                }}
              ],
              "examples": [
                {{
                  "content": "Example content",
                  "explanation": "Why this example works",
                  "order_index": <integer>,
                  "tags": ["tag1"]
                }}
              ]
            }}
          ],
          "objectives": [
            {{
              "code": "MOD{{module_number}}.LSN{{lesson_number}}.01",
              "description": "Learning objective description",
              "order_index": <integer>
            }}
          ]
        }}
      ]
    }}
  ],
  "knowledge_graph": [
    {{
      "source_concept_title": "Concept that is prerequisite",
      "target_concept_title": "Concept that depends on it",
      "relationship": "requires",
      "weight": 0.8
    }}
  ]
}}

Rules:
- Extract concepts from the content, do not invent concepts not present in the source material
- Generate appropriate exercises based on the content type
- Create realistic knowledge graph edges identifying prerequisite relationships
- Assign reasonable duration estimates
- If the content does not specify a duration, estimate based on content complexity
  (1-60 minutes per concept, 10-60 minutes per lesson, 2-20 hours per module,
  10-100 total hours for course, 30-180 default_deadline_days)
- module_number and lesson_number in objective codes should reflect actual order_index values
- Return valid JSON only, no markdown formatting"""
