# backend/groq_ai_service.py

import os
import time
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

from ai.logger import logger
from ai.prompt_builder import build_prompt
from ai.json_validator import validate_ai_output
from ai.resource_mapper import map_resources_for_topics

# Get current folder
BASE_DIR = Path(__file__).resolve().parent

# Load .env
dotenv_file = BASE_DIR / ".env"
load_dotenv(dotenv_path=dotenv_file)

# Read key
api_key = os.getenv("GROQ_API_KEY")

# Create Groq client
if not api_key:
    logger.warning("GROQ_API_KEY environment variable is not set")
    # Don't crash immediately on load to allow FastAPI server initialization, but fail when client is used
    client = None
else:
    client = Groq(api_key=api_key)

def generate_personalized_roadmap(profile_data: dict) -> dict:
    """
    Executes the full roadmap generation pipeline:
    Prompt building -> Call Groq Client with retries -> JSON Schema Validation -> Curated Resource Mapping.
    Includes up to 3 automatic retries if API errors, timeouts, or JSON validation fails.
    """
    global client
    if not client:
        # Re-check key in case environment was loaded dynamically
        api_key_check = os.getenv("GROQ_API_KEY")
        if not api_key_check:
            logger.error("GROQ_API_KEY environment variable is not set")
            raise ValueError("GROQ_API_KEY is not configured in the environment or .env file")
        client = Groq(api_key=api_key_check)

    logger.info("AI Roadmap generation pipeline execution started using Groq")
    
    # 1. Build prompt
    prompt = build_prompt(profile_data)
    logger.info("Prompt Generated [OK]")
    
    max_retries = 3
    last_error = None
    
    for attempt in range(1, max_retries + 2): # total 4 attempts (1 initial + 3 retries)
        try:
            if attempt > 1:
                logger.info("Retry Started")
            
            logger.info("Groq Request Sent")
            logger.info(f"Groq API call initiated (Attempt {attempt}/{max_retries + 1}). Prompt length: {len(prompt)}")
            start_time = time.time()
            
            # 2. Call Groq
            # default to llama-3.1-8b-instant if not specified
            model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
                timeout=60.0 # Handle timeout
            )
            
            elapsed_time = time.time() - start_time
            logger.info("Groq Response Received")
            logger.info("Groq Response Received [OK]")
            
            raw_content = response.choices[0].message.content
            if not raw_content:
                raise ValueError("Empty response received from Groq API")
                
            # 3. Validate structure (handles malformed JSON and raises error if invalid)
            validated_data = validate_ai_output(raw_content)
            logger.info("JSON Validated")
            logger.info("JSON Valid [OK]")
            
            # 4. Map curated learning resources
            final_data = map_resources_for_topics(validated_data)
            logger.info("AI Roadmap generation pipeline executed successfully using Groq")
            return final_data
            
        except Exception as e:
            last_error = e
            logger.warning(
                f"Error executing Groq call/validation (Attempt {attempt}/{max_retries + 1}): {str(e)}."
            )
            if attempt <= max_retries:
                delay = 2 ** attempt
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                
    logger.error(f"Failed to generate roadmap after {max_retries + 1} attempts. Last error: {str(last_error)}")
    raise RuntimeError(f"Failed to generate a valid roadmap using Groq API: {str(last_error)}")
