# 🩺 COVID-19 Consultation chatbot

**_An AI-powered conversational chatbot for COVID-19 consultation, built using **Large language models (LLMs)**, **vector search**, and **contextual memory**._**
---
## 🎯 Objective
1. **Consulting users about COVID-19 symptoms, prevention, and treatment** in multiple languages.
2. **Maintaining memory** of prior conversations and **user profiles** to offer more personalized responses.
3. **Recognizing relationships** between the user and other individuals (e.g., family members, colleagues) and offering contextual guidance based on these connections.

## 🧠 Key Technologies

| Component              | Technology Used                   |
|------------------------|------------------------------------|
| 🧠 Large Language Model | DeepSeek-r1-0528-qwen3-8b via free OpenRouterAPI provider   |
| 📚 Vector Search Engine | all-MiniLM-L6-v2 model for embedding text and Faiss for vector search  |
| 💬 Chat Interface        | Streamlit                         |
| 🌐 API Backend          | FastAPI and GraphDB (Neo4J) to store chat history, user profile                         |
| 🧵 Session Management   | Streamlit `st.session_state`       |
| 🐳 Deployment           | Docker & Docker Compose           |

## 📘 Description

This chatbot system integrates several AI components to enable intelligent, personalized consultations about COVID-19. Below is an overview of how key functionalities are implemented:

### 🔍 1. Vector Search Engine

- The chatbot uses **FAISS** (Facebook AI Similarity Search) to perform fast vector-based retrieval over a knowledge base of COVID-19 domain data.
- The texts are embedded using the **`all-MiniLM-L6-v2`** model from `sentence-transformers`, a compact yet powerful transformer that balances performance and speed.
- The indexing process will load the data from Json file with structure {'user':...., 'assistant':...}. The user query and assistant's response will combine into the text block. Then, This combined text is passed through all-MiniLM-L6-v2 to generate a vector embedding.
The embedding is stored and indexed in FAISS, enabling fast similarity search during chat interactions. All the index and metadata file are stored in the `chatbot_api/src/Output`. We can update this by deleting this Output folder, Adding the Json file to the `chatbot_api/src/data`, and then, will automatically create the vector database in the first. 
- When a user query is submitted:
  - It’s converted into a vector using `all-MiniLM-L6-v2`
  - FAISS is queried to return top relevant context passages
  - These passages are included in the prompt sent to the LLM for informed, grounded responses

### 🧠 2. Response Generation

- The chatbot uses a **Large Language Model (LLM)** (i.e., DeepSeek-r1-0528-qwen3-8) via free OpenRouterAPI provider (https://openrouter.ai/models) to generate fluent, human-like responses.
- Prompts are constructed based on:
  - System Prompt: Describe the task of this chatbot and define how model generate the response and use the external information. 
  - Retrieved knowledge from vector search
  - User Input
- The LLM is called via API in the backend (FastAPI) to return contextual and domain-relevant answers.
- **On-going Improvement**: Injecting the current and past history chat message into the prompt to enhance the memory and context of LLM model to accurately generate response for lack of specific questions (e.g., what about my father..) 

### 🗃 3. Information Extraction

- The user's input is parsed using rule-based logic or LLM-assisted parsing to extract relevant information, such as:
  - Symptoms mentioned
  - Risk factors
  - Mentioned individuals (e.g., family members, colleagues)
- Extracted data is stored in memory to support future turns in the conversation.
- Named Entity Recognition (NER) or simple regex may be used to identify key elements.

### 👤 4. User Profile and Context Management

- Each user has an associated **context memory** that includes:
  - Basic profile (e.g., age, existing conditions)
  - Conversation history
  - Related individuals and their attributes
- Session state is tracked using `st.session_state` in Streamlit for temporary memory.
- For longer retention, user profiles can be stored in a database (e.g., Neo4j for relationships, or MongoDB for flexible schema).

## 🚀 Running the Project

### 📦 Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Docker Compose (comes with Docker Desktop)

### 🔧 Run the Full Stack

In the project root directory:

```bash
docker compose up --build
