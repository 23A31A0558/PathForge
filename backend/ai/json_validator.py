# backend/ai/json_validator.py

import json
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError
from ai.logger import logger

class ResourceSchema(BaseModel):
    title: str = Field(..., min_length=1)
    url: str = Field(..., min_length=1)

class TopicSchema(BaseModel):
    topic: str = Field(..., min_length=1)
    difficulty: str = Field(..., min_length=1)
    estimated_hours: int = Field(..., ge=1)
    resources: List[ResourceSchema] = Field(..., min_items=1)
    mini_project: str = Field(..., min_length=1)
    quiz_required: bool

class PhaseSchema(BaseModel):
    phase_number: int = Field(..., ge=1)
    phase_title: str = Field(..., min_length=1)
    estimated_duration: str = Field(..., min_length=1)
    topics: List[TopicSchema] = Field(..., min_items=1)


class SingleRoadmapSchema(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    phases: List[PhaseSchema] = Field(..., min_items=1)

class RoadmapListSchema(BaseModel):
    roadmaps: List[SingleRoadmapSchema] = Field(..., min_items=2)  # Fast Track and Deep Learning

def validate_ai_output(json_str: str) -> dict:
    """
    Validates that the JSON string conforms to the expected Pydantic schema structure.
    Ensures that phases, topics, hours, mini projects, and resources exist.
    """
    logger.info("Starting JSON validation check")
    
    # Clean potential markdown code block fences (e.g. ```json ... ```)
    clean_str = json_str.strip()
    if clean_str.startswith("```"):
        lines = clean_str.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        clean_str = "\n".join(lines).strip()
    
    # Try parsing first
    try:
        data = json.loads(clean_str)
    except json.JSONDecodeError as decode_err:
        logger.error(f"JSON decoding error encountered: {str(decode_err)}")
        raise ValueError(f"AI response is not valid JSON: {str(decode_err)}")

        
    try:
        # Validate against the Pydantic schema
        validated = RoadmapListSchema(**data)
        dumped = validated.model_dump()
        
        # Additional semantic checks
        for roadmap in dumped["roadmaps"]:
            for phase in roadmap["phases"]:
                for topic in phase["topics"]:
                    # Verify required non-empty string fields
                    if not topic.get("topic").strip():
                        raise ValueError("Topic title cannot be empty")
                    if not topic.get("mini_project").strip():
                        raise ValueError("Topic mini_project description cannot be empty")
                        
        logger.info("JSON response schema validated successfully")
        return dumped
    except ValidationError as val_err:
        logger.error(f"Schema validation errors: {val_err.errors()}")
        raise ValueError(f"AI response JSON structure is invalid: {val_err.errors()}")
