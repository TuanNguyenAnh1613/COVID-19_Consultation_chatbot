from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI

query_template = """
You are an AI assistant that extracts structured health information from user messages related to COVID-19.

Your task is to extract and return the following information in JSON format:
- name: (string) the user's name
- age: (integer) the user's age
- symptoms: (list of strings) symptoms the user is experiencing
- health_conditions: (list of strings) any pre-existing conditions the user mentions
- family_members: (list of objects) each with:
    - name: (string) the family member's name
    - relation: (string) e.g., "mother", "son", etc.
    - condition: (list of strings) conditions the family member has
    - symptoms: (list of strings) symptoms the family member has
    - age: (integer) the family member's age

If any field is not mentioned, return it as an empty list or null (for age, name). Just response for me the Json, not with any prefix. 

Example Input:
"Hi, I'm John, 42. I have a sore throat and fever. My father has diabetes."

Example Output:
{{
  "name": "John",
  "age": 42,
  "symptoms": ["sore throat", "fever"],
  "health_conditions": [],
  "family_members": [
    {{
      "relation": "father",
      "age": null
      "condition": ["diabetes"]
    }}
  ]
}}
Now process this input:
{user_input}



"""
extraction_prompt_template = PromptTemplate(
    input_variables=["user_input"],
    template=query_template
)
