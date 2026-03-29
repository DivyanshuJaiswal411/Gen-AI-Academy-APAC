from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import uuid
import json
import re
from typing import Optional
from google.adk.runners import InMemoryRunner
from google.adk.flows.llm_flows.contents import types

from pii_agent.agent import root_agent, RedactionResponse

# Define input schema for the API
class RedactionRequest(BaseModel):
    text: str

app = FastAPI(
    title="Zero-Trust PII Redaction Gateway",
    description="Redacts PII from text using Gemini and returns a structured response.",
    version="1.0.0",
)

def extract_json(text: str) -> Optional[dict]:
    """Extracts JSON from text, handling markdown blocks if present."""
    match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        text = match.group(1)
    else:
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
    
    try:
        return json.loads(text)
    except:
        return None

@app.post("/redact", response_model=RedactionResponse)
async def redact_pii(request: RedactionRequest):
    """
    Redact Personally Identifiable Information (PII) from the input text.
    """
    try:
        runner = InMemoryRunner(agent=root_agent)
        
        user_id = "api_user"
        session_id = str(uuid.uuid4())
        
        await runner.session_service.create_session(
            app_name=runner.app_name, 
            user_id=user_id, 
            session_id=session_id
        )
        
        new_message = types.Content(role='user', parts=[types.Part(text=request.text)])
        
        final_output = None
        
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=new_message
        ):
            # If it's the final agent (pii_redactor), try to parse the JSON
            if event.author == "pii_redactor":
                text_content = ""
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            text_content += part.text
                
                if text_content:
                    data = extract_json(text_content)
                    if data:
                        try:
                            final_output = RedactionResponse(**data)
                        except:
                            pass
        
        if final_output:
            return final_output
        else:
            raise HTTPException(status_code=500, detail="Agent failed to produce structured output.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# Optional: Add a simple health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}
