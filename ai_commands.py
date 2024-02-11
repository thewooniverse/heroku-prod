import openai
import os
from openai import OpenAI
import requests
# from langchain.chat_models import ChatOpenAI <<- Deprecated
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
# from templates import system_template
from pathlib import Path
import helper_functions




# constructing the models
OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY', 'YourAPIKey_BACKUP')
client = OpenAI(api_key=OPENAI_API_KEY)



def chat_completion(message, model='gpt-3.5-turbo'):
    """
    def chat_completion(query): This function calls the OpenAI API endpoint. Default Model is 
    """
    body_text = helper_functions.extract_body(message.text)

    system_prompt = "You are a helpful AI assistant - reply all responses in markdown"

    completion_object = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": body_text}])
    print(completion_object)
    response_text = completion_object.choices[0].message.content
    print(response_text)
    return response_text


def translate(message, target_language="eng" ,model='gpt-3.5-turbo'):
    """
    translate(message, target, model): translates

    This is commonly used by the user with different configurations like t1 = to EN, t2 = to CN, t3 = to KR.
    """
    body_text = helper_functions.extract_body(message.text)

    system_prompt = f"You are an expert translator agent. You will be given a body of text to translate into a target language, translate the body text into the best most accurate translation possible with awareness of context and language based nuances. Do not include any other sentences in the response text than the translation with the exception of Chinese, please include the Pinyin if the target language is Chinese. The target language to be translated is given in a ISO 639-2 Code format. The target language is {target_language}."
    
    completion_object = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": body_text}])
    print(completion_object)

    response_text = completion_object.choices[0].message.content
    print(body_text)
    print(response_text)
    return response_text


def generate_image(message):
    """
    Takes a message object, unpacks and returns a response.
    """
    body_text = helper_functions.extract_body(message.text)

    ImagesResponse = client.images.generate(
        model='dall-e-3',
        prompt=body_text,
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


def text_to_speech(message, voice="alloy"):
    """
    def text_to_speech(message): takes a message, and returns a voice file containing its dictated version.
    """
    # extract the query
    query = helper_functions.extract_body(message.text)


    # get the query:
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=query)
    
    if response:
        print(f"Response received: {type(response)}")
        return response
    else:
        print("Response not received")
        return None

    # speech_file_path = Path(__file__).parent / "temp_tts_mp3" / f"{str(message.chat.id)}_{str(message.message_id)}.mp3"

    # if response:
    #     print("Response received")
    #     response.stream_to_file(speech_file_path)
    #     return speech_file_path




def speech_to_text(voice_file):
    """
    def speech_to_text(message): takes a voice file, and returns a transcribed version of it.
    """
    transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=voice_file)
    return transcript















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

