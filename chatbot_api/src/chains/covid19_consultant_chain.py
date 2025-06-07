from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from langchain.chat_models import ChatOpenAI

query_template = """
Your are a medical expert specializing in COVID-19. Your job is to answer the user's questions related their health's conditions specifically concerning about COVID-19 includind: 
COVID's symtoms, what they should do to prevent the COVID-19, or providing general guidance treatments, etc.. You can use the past user-assistant interactions to answer the medical-questions as accurately and cautionsly as possible. 
. You should not answer any questions that are not related to COVID-19, or any other medical questions. Be detailed, but **Do not make up** any information, and if you don't know the answer, say you don't know. Use the following context to answer the questions.
{context}
"""

query_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["context"],
        template=query_template,
    )
)

query_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["question"],
        template="{question}",
    )
)

# Wrap into a full chat prompt template 
review_template = ChatPromptTemplate.from_messages(
    [
        query_system_prompt,
        query_human_prompt,
    ]
)