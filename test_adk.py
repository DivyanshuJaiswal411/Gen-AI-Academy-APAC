import asyncio
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from pydantic import BaseModel, Field

class InputSchema(BaseModel):
    text: str

class OutputSchema(BaseModel):
    result: str

agent = Agent(
    name="test",
    model="gemini-1.5-flash",
    instruction="Reverse the text",
    input_schema=InputSchema,
    output_schema=OutputSchema
)

async def test():
    runner = InMemoryRunner(agent=agent)
    print("Running...")
    async for event in runner.run_async(user_id="u", session_id="s", new_message="hello"):
        print(f"Event: {type(event).__name__}")
        if hasattr(event, 'message') and event.message:
            print(f"Message: {event.message.content}")

if __name__ == "__main__":
    asyncio.run(test())
