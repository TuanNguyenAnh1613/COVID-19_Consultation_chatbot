from pydantic import BaseModel

class ChatbotQueryInput(BaseModel):
    user_id: str
    text: str

class ChatbotQueryOutput(BaseModel):
    input: str
    output: str