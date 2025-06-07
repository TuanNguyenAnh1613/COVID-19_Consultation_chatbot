import os
import requests
import streamlit as st



"""
    This COVID-19 consultation chatbot frontend was built depending on the Streamlit Library.
    References: "https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps"
"""

CHATBOT_GENERATE_URL = os.getenv("CHAT_GENERATE_URL", "http://localhost:8000/covid-consultation")
CHATBOT_URL = os.getenv("CHATBOT_URL", "http://localhost:8000/user-request")
CHATBOT_HISTORY_URL = os.getenv("CHATBOT_HISTORY_URL", "http://localhost:8000/chat-history")
with st.sidebar:
    st.header("User Login or Register")
    username = st.text_input("Username", placeholder="Enter your username", key="username")
    password = st.text_input("Password", placeholder="Enter your password", type="password", key="password")
    is_register = st.checkbox("Register", key="is_register")
    login_btn = st.button("Login/Register", key="login_button")

    st.header("About")
    st.markdown(
        """
        This chatbot interfaces with a
        [LangChain](https://python.langchain.com/docs/get_started/introduction)
        chatbot designed to answer the questions concerning about COVID-19 including: 
        COVID's symtoms, what they should do to prevent the COVID-19, or providing general guidance treatments, etc..
        This chatbot uses  retrieval-augment generation (RAG) over
        structured data that has been generated and DeepSeek's LLM model to generate the response.
        """
    )
    st.header("Example Questions")
    st.markdown("- What are the symptoms of COVID-19?")
    st.markdown("- How can I prevent the spread of COVID-19?")
    st.markdown(
        "- I have a sore throat, slight cough, tiredness. Should I get tested for covid 19??"
    )
    st.markdown("- Will I be covered if I get corona 19 with my medival aid??")
    st.markdown(
        "- What should I do if I have been in contact with someone who has COVID-19?"
    )
    
st.title("COVID-19 Consultation Chatbot")
st.info(
    "Ask me questions about COVID-19: Symtoms, Prevention, or Treatment!"
)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []
# ---Handle Login/Register---
if login_btn and username and password:
    payload = {
        "username": username,
        "password": password,
        "is_register": is_register
    }
    response = None 
    try:
        response = requests.post(CHATBOT_URL, json=payload)
        if response.status_code == 200:
            st.session_state.authenticated = True
            st.success("Login/Register successful!")
            st.session_state.user_id = response.json()['user_id']
            # Fetch the history is login (not register)
            if not is_register:
                chat_history_response = requests.get(
                    f"{CHATBOT_HISTORY_URL}/{response.json()['user_id']}"
                )
            
                if chat_history_response.status_code == 200:
                    history_message = []
                    for i in chat_history_response.json():
                        chat_message = {"role": i['role'], "output": i["text"]}
                        history_message.append(chat_message)

                    st.session_state.messages = history_message
                elif chat_history_response.status_code == 404:
                    st.session_state.messages = []
                else:
                    st.error("Failed to fetch chat history.")
            else:
                st.session_state.messages = []
        else:
            st.session_state.authenticated = False
            st.session_state.messages = []
            st.error(response.json().get("detail", "Login/Register failed."))
    except Exception as e:
        st.session_state.authenticated = False
        st.session_state.messages = []
        st.error(f"An error occurred: {str(e)}")
            
if st.session_state.get("authenticated", False):
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "output" in message.keys():
                st.markdown(message["output"])

            if "explanation" in message.keys():
                with st.status("How was this generated", state="complete"):
                    st.info(message["explanation"])

    if prompt := st.chat_input("What do you want to know?"):
        st.chat_message("user").markdown(prompt)

        st.session_state.messages.append({"role": "user", "output": prompt})

        data = {"user_id": st.session_state.user_id, "text": prompt}

        with st.spinner("Searching for an answer..."):
            response = requests.post(CHATBOT_GENERATE_URL, json=data)

            if response.status_code == 200:
                output_text = response.json()["output"]
                #explanation = response.json()["intermediate_steps"]

            else:
                output_text = """An error occurred while processing your message.
                Please try again or rephrase your message."""
                #explanation = output_text

        st.chat_message("assistant").markdown(output_text)
        #st.status("How was this generated", state="complete").info(explanation)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "output": output_text
            }
        )
else:
    st.warning("Please login or register to start chatting.")