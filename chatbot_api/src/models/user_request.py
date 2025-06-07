from pydantic import BaseModel

class UserRequest(BaseModel):
    username: str
    password: str
    is_register: bool  # True for registration, False for login

class MessageStoreRequest(BaseModel):
    user_id: str
    text: str
    role: str  # 'user' or 'assistant'
