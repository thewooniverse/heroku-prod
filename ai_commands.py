import openai
import os
from openai import OpenAI
import requests
# from langchain.chat_models import ChatOpenAI <<- Deprecated
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
# from templates import system_template




# constructing the models
OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY', 'YourAPIKey_BACKUP')
client = OpenAI(api_key=OPENAI_API_KEY)


def chat_completion(query, model='gpt-3.5-turbo'):
    """
    def chat_completion(query): This function calls the OpenAI API endpoint. Default Model is 
    """
    completion_object = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant - reply all responses in markdown"},
        {"role": "user", "content": query}])
    print(completion_object)
    response_text = completion_object.choices[0].message.content
    print(response_text)
    return(response_text)



def generate_image(query):
    """
    Takes a message object, unpacks and returns a response.
    """
    ImagesResponse = client.images.generate(
        model='dall-e-3',
        prompt=query,
        n=1,
        size='1024x1024',
        response_format='url'
    )

    print(ImagesResponse) # remember, inside the image object, the data is a list.
    response = requests.get(ImagesResponse.data[0].url)
    if response.status_code == 200:
        return response.content
    else:
        return None




"""
Example response object:
2024-02-03T09:53:58.515753+00:00 app[web.1]: 
ImagesResponse(created=1706954038, 
data=[Image(b64_json=None, 
revised_prompt='A stunning depiction of a woman of Turkish descent. 
She is dressed in traditional Turkish attire, adorned with vivid and intricate embroidery. 
Her almond-shaped eyes, prominent cheekbones, and dark hair, neatly combed, give her a distinctive allure. 
She carries with her an air of grace and poise, exuding a warm, inviting aura.', 
url='https://EXAMPLEIURL.com')])
"""








# # define overarching querying function
# def chat_agent_langchain(query):
#     """
#     Takes a message object, unpacks and returns a response.
#     """
#     # instantiate the agent;
#     agent = ChatOpenAI(model='gpt-4-0613', openai_api_key=OPENAI_API_KEY, model_name="gpt-4-0613")

#     # extract the query from the message object
#     chat_history = [
#         SystemMessage(content="You are a helpful AI agent."),
#         HumanMessage(content=query)
#     ]

#     # query the LLM with context provided
#     response = agent(chat_history)
#     print(response)
#     return {"response_text": response.content}

