from chains.covid19_consultant_chain import review_template
import dotenv
import os 
from vector_search.search_engine import VectorSearchEngine
import numpy as np
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from chains.user_info_extract_chain import extraction_prompt_template
import json

dotenv.load_dotenv()
LLM_MODEL_NAME  = os.getenv("LLM_MODEL_NAME")
DATA_DIRECTORY = os.getenv("DATA_DIRECTORY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


class COVID19ConsultantChatbot:
    def __init__(self, model_name=LLM_MODEL_NAME):
        self.model_name = model_name
        self.search_engine = VectorSearchEngine(DATA_DIRECTORY)
        self.embedder = self.search_engine.embedder
        self.index_path = self.search_engine.index_path
        self.metadata_path = self.search_engine.metadata_path
        # Load the FAISS Index and Metata 
        if not os.path.exists(self.index_path) or not os.path.exists(self.metadata_path):
            self.faiss_index, self.metadata_store = self.search_engine.build_search_index()
            print("Index and metadata created successfully.")
        else:
            self.faiss_index, self.metadata_store = self.search_engine.load_vector_index(self.index_path, self.metadata_path)
        # Initialize the chat model

        os.environ["OPENAI_API_KEY"] = OPENROUTER_API_KEY
        self.chat_pipeline = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            model_name=self.model_name,
            temperature=0.7
        )
        
    def query(self, question):
        # Perform Vector Similarity Search 
        context = self.search_engine.vector_similarity_search(query=question, k=5)
        prompt = review_template.format(
            context=context,
            question=question
        )
        # Generate the response using the chat model
        response = self.chat_pipeline([HumanMessage(content=prompt)])
        return response.content.strip()
    
    def extract_information(self, question):
        prompt = extraction_prompt_template.format(
            user_input=question
        )
        response = self.chat_pipeline([HumanMessage(content=prompt)])
        response_str= response.content.strip()
        data = json.loads(response_str)
        return data
    
if __name__ == "__main__":
    chatbot = COVID19ConsultantChatbot()
    
    question = "my son who is 19, suffered from mono last spring with a tonsillar abscess requiring hospitalization for steroid and antibiotic infusion. due to how ill he was, they did not want to remove the tonsils but recommended he have them removed when he improved. he went off to college, became ill, was diagnosed with pneumonia and still had a positive mono spot. so we were unable to schedule it for the christmas break as we planned but now he has a piece of his tonsil that is actually hanging off=it looks like the strands between his cryptic tonsil areas broke off and left this piece dangling. it is umcomfortable but i am not sure if it is emergent. no fever or c/o sore throat right now, but overall still not up to par since this continued bouts of illness."
    answer = chatbot.extract_information(question)
    print("Answer:", answer)

    