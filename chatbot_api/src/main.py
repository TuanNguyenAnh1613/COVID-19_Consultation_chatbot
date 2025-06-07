from fastapi import FastAPI, HTTPException
from vector_search.search import COVID19ConsultantChatbot
from utils.async_utils import async_retry
from models.chatbot_query_model import ChatbotQueryInput, ChatbotQueryOutput
from models.user_request import UserRequest, MessageStoreRequest
from user_management.chat_graph import ChatGraph
import asyncio
import os 
import dotenv
dotenv.load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


app = FastAPI(
    title="COVID-19 CONSULTATION CHATBOT",
    description="Endpoints for a COVID-19 consultation chatbot"
)
graph_db = ChatGraph(uri=NEO4J_URI, user=NEO4J_USERNAME, password=NEO4J_PASSWORD)
covid19ConsultantChatbot = COVID19ConsultantChatbot()

@async_retry(max_retries=10, delay=1)
async def query_covid_consultation_with_retry(query: str):
    """Retry the search if a tool fails to run.
    
    This can help when there are intermittent connection issues
    to external APIs.
    """
    loop = asyncio.get_running_loop()
    search_response = await loop.run_in_executor(None, covid19ConsultantChatbot.query, query)
    external_data = {
        "input": query,
        "output": search_response
    }
    return ChatbotQueryOutput(**external_data)

@app.get("/")
async def get_status():
    return {"status": "running"}

@app.post("/covid-consultation")
async def query_covid_consultation(query: ChatbotQueryInput) -> ChatbotQueryOutput:
    graph_db.store_message(query.user_id, query.text, "user")
    query_response = await query_covid_consultation_with_retry(query.text)
    extracted_data = covid19ConsultantChatbot.extract_information(query.text)
    print(extracted_data)
    graph_db.update_user_info(extracted_data, query.user_id)
    graph_db.store_message(query.user_id, query_response.output, "assistant")
    return query_response

@app.post("/user-request")
async def handle_user_request(user_request: UserRequest):
    user = graph_db.get_user_by_username(user_request.username)

    if user_request.is_register:
        if user:
            raise HTTPException(status_code=400, detail="Username already exists")
        user_id = graph_db.create_user(user_request.username, user_request.password)
        return {"message": "User registered", "user_id": user_id}
    else:
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not graph_db.check_password(user_request.password, user["password"]):
            raise HTTPException(status_code=403, detail="Incorrect password")
        return {"message": "Login successful", "user_id": user["user_id"]}
    
@app.get("/chat-history/{user_id}")
async def get_chat_history(user_id: str):
    chat_history = graph_db.get_user_chat_history(user_id)
    print(chat_history)
    if not chat_history:
        raise HTTPException(status_code=404, detail="No chat history found for this user")
    return chat_history

@app.post("/store-message")
async def store_message(message: MessageStoreRequest):
    user = graph_db.get_user_by_username(message.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    graph_db.store_message(user["user_id"], message.text, message.role)
    return {"message": "Message stored successfully"}

   
   



