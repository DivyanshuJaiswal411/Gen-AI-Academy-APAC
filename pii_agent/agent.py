import os
import asyncio
import json
import re
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict
from google import adk

from google.adk.agents import Agent, SequentialAgent
from google.adk.runners import InMemoryRunner
from google.adk.flows.llm_flows.contents import types
from dotenv import load_dotenv

# 1. Load the environment variables from .env
load_dotenv()

# Define the Structured Output Schema for validation
class RedactedMetadata(BaseModel):
    model_config = ConfigDict(extra='allow')
    category: str = Field(description="The type of PII found (e.g., EMAIL, NAME, PHONE)")
    original_found: str = Field(description="The actual sensitive snippet identified")
    placeholder: str = Field(description="The unique placeholder used (e.g., [EMAIL_1])")

class RedactionResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    redacted_text: str = Field(description="The full text with all PII replaced by placeholders")
    pii_map: List[RedactedMetadata] = Field(description="A list of all redacted items for audit purposes")
    safety_score: int = Field(description="A score from 1-10 on how confident the agent is that all PII was removed")

# 2. Define Step 1: Identification Agent
IDENTIFIER_INSTRUCTION = """
You are a PII Identification Expert. 
Your task is to scan the input text and list all Personally Identifiable Information (PII).
Identify: Names, Email Addresses, Physical Addresses, Phone Numbers, Credit Card Numbers, and Indian Identifiers (Aadhaar, PAN).

CRITICAL: Process only the latest user message. Ignore any previous JSON blocks or context markers in the input.

Return the results as a JSON object with:
- pii_found: List of objects with 'type' and 'value'
- original_text: The original text
"""

identifier_agent = Agent(
    name="pii_identifier",
    model="gemini-2.5-flash",
    instruction=IDENTIFIER_INSTRUCTION
)

# 3. Define Step 2: Redaction & Confirmation Agent
REDACTOR_INSTRUCTION = """
You are a Redaction Specialist. 
You will receive a list of PII and the original text from the previous agent. 
Your task is to:
1. Replace each unique PII entity in the text with a consistent placeholder like [NAME_1], [EMAIL_1].
2. Create a mapping between the original PII and the placeholder.
3. Ensure the final text is fully redacted and safe to share.
4. Provide a safety score (1-10) for the redaction.

CRITICAL: Process only the latest user message. Ignore any previous JSON blocks or context markers in the input.

IMPORTANT: You MUST return ONLY a valid JSON object matching this schema:
{
  "redacted_text": "string",
  "pii_map": [
    {"category": "string", "original_found": "string", "placeholder": "string"}
  ],
  "safety_score": integer
}
Do not include markdown formatting or any other text.
"""

redactor_agent = Agent(
    name="pii_redactor",
    model="gemini-2.5-flash",
    instruction=REDACTOR_INSTRUCTION
)

# 4. Initialize the SequentialAgent
root_agent = SequentialAgent(
    name="pii_redactor_pro",
    sub_agents=[identifier_agent, redactor_agent]
)

def extract_json(text: str) -> Optional[dict]:
    """Extracts JSON from text, handling markdown blocks if present."""
    # Try to find JSON in markdown blocks
    match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        text = match.group(1)
    else:
        # Try to find the first '{' and last '}'
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
    
    try:
        return json.loads(text)
    except:
        return None

# 5. Corrected Local Test (Async + Runner)
async def test_zero_trust():
    runner = InMemoryRunner(agent=root_agent)
    sample_text = "My name is Divyanshu Jaiswal. My email is divyanshu@iitbhu.ac.in and my phone is +91-9876543210."
    
    print("--- 🛡️ Running Local Zero-Trust Test ---")
    
    try:
        # Manually create session
        await runner.session_service.create_session(
            app_name=runner.app_name, 
            user_id="test_user", 
            session_id="test_session"
        )
        
        new_message = types.Content(role='user', parts=[types.Part(text=sample_text)])
        
        async for event in runner.run_async(
            user_id="test_user", 
            session_id="test_session", 
            new_message=new_message
        ):
            print(f"Received event: {type(event).__name__} from {event.author}")
            
            # Extract text content from the event
            text_content = ""
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        text_content += part.text
            
            if text_content:
                print(f"\n[Agent {event.author}]: {text_content}")
                
                # If it's the final agent (pii_redactor), try to parse the JSON
                if event.author == "pii_redactor":
                    data = extract_json(text_content)
                    if data:
                        try:
                            response = RedactionResponse(**data)
                            print("\n--- ✅ Final Structured Output ---")
                            print(response.model_dump_json(indent=2))
                        except Exception as ve:
                            print(f"Validation error: {ve}")
    except Exception as e:
        print(f"❌ Error during execution: {e}")

if __name__ == "__main__":
    asyncio.run(test_zero_trust())
