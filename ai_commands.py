import openai
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
# from templates import system_template



OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY', 'YourAPIKey_BACKUP')


# define overarching querying function
def chat(message):
    """
    Takes a message object, unpacks and returns a response.
    """
    # instantiate the agent;
    agent = ChatOpenAI(model='gpt-4-0613', openai_api_key=OPENAI_API_KEY, model_name="gpt-4-0613")

    # extract the query from the message object
    text = message['text']
    body_text = ' '.join(text.split(' ')[1:])
    
    # query the LLM with context provided
    response = agent(body_text)
    return {"response_text": response}



