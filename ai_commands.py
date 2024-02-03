import openai
import os
from openai import OpenAI
# from langchain.chat_models import ChatOpenAI <<- Deprecated
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
# from templates import system_template




# constructing the models
OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY', 'YourAPIKey_BACKUP')
client = OpenAI(api_key=OPENAI_API_KEY)


# define overarching querying function
def chat_agent(message):
    """
    Takes a message object, unpacks and returns a response.
    """
    # instantiate the agent;
    agent = ChatOpenAI(model='gpt-4-0613', openai_api_key=OPENAI_API_KEY, model_name="gpt-4-0613")

    # extract the query from the message object
    text = message['text']
    body_text = ' '.join(text.split(' ')[1:])
    chat_history = [
        SystemMessage(content="You are a helpful AI agent."),
        HumanMessage(content=body_text)
    ]


    # query the LLM with context provided
    response = agent(chat_history)
    print(response)
    return {"response_text": response.content}



def generate_image(message):
    """
    Takes a message object, unpacks and returns a response.
    """
    text = message['text']
    body_text = ' '.join(text.split(' ')[1:])
    response = client.images.generate(
        model='dall-e-3',
        prompt=body_text,
        n=1,
        size='1024x1024',
        response_format='url'
    )
    print(response)
    return {"response_text": response.data['url']}


