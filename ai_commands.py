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
# OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY', 'YourAPIKey_BACKUP')






## Text Handling Commands ##
def chat_completion(message, context, openai_api_key, chat_history, model='gpt-3.5-turbo', temperature=1):
    """
    """
    client = OpenAI(api_key=openai_api_key)
    if isinstance(message, str):
        body_text = message
    else:
        body_text = helper_functions.extract_body(message.text)

    system_prompt = f"You are a helpful AI assistant - reply all responses in markdown. The context provided by this given user is as follows \n\n {context}"
    chat_history = f"This is the summary of the relevant parts of the conversation / chat history that we've had so far: {chat_history}"

    completion_object = client.chat.completions.create(
    model=model,
    temperature = temperature,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": chat_history},
        {"role": "user", "content": body_text}])
    print(completion_object)
    response_text = completion_object.choices[0].message.content
    print(response_text)
    return response_text







def translate(message, openai_api_key, target_language="eng" ,model='gpt-3.5-turbo'):
    """
    translate(message, target, model): translates

    This is commonly used by the user with different configurations like t1 = to EN, t2 = to CN, t3 = to KR.
    """
    client = OpenAI(api_key=openai_api_key)
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








## Image Handling Commands ##
def generate_image(message, openai_api_key, context):
    """
    Takes a message object, unpacks and returns a response.
    """
    client = OpenAI(api_key=openai_api_key)
    body_text = f"{context}\n"+ helper_functions.extract_body(message.text)

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


def image_vision(message, base64_image, openai_api_key):
    """
    def image_vision(message, encoded_image):
    """
    client = OpenAI(api_key=openai_api_key)
    query = helper_functions.extract_body(message.text)

    # construct the message payload
    input_messages = [{"role": "user",
                 "content": [
                    {
                         "type": "text",
                         "text": query},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
    try:
        completion_object = client.chat.completions.create(
            model='gpt-4-vision-preview',
            messages=input_messages,
            max_tokens=500
        )
        response_text = completion_object.choices[0].message.content
        if response_text:
            return response_text
        else:
            return "Unable to analyze image"            
        
    except Exception as e:
        print(f"Error occured: {e}")






def variate_image(message, org_image_file_byte_array, openai_api_key):
    """
    def variate_image(message, org_image_file_byte_array): returns variations of an image based on the 
    """
    # print(f"creating variations of original image with OpenAI")
    client = OpenAI(api_key=openai_api_key)

    try:
        ImagesResponse = client.images.create_variation(
            model="dall-e-2",
            image=org_image_file_byte_array,
            n=1,
            size="1024x1024",
            response_format='url'
            )
        print(ImagesResponse)
        response = requests.get(ImagesResponse.data[0].url)
        return response.content
    
    except openai.OpenAIError as e:
        print(e)
        return None
    except Exception as e:
        print(e)
        return None


def edit_image(message, org_image_file_byte_array, temp_mask_file_path, openai_api_key):
    """
    def edit_image(message, image_file_path): returns an edited image based on the query, original image provided and mask file
    
    """
    query = helper_functions.extract_body(message.text)
    client = OpenAI(api_key=openai_api_key)

    print(f"creating an edit of the original image with OpenAI and the edit query: {query}")
    try:
        ImagesResponse = client.images.edit(
            model="dall-e-2",
            image=org_image_file_byte_array,
            mask=open(temp_mask_file_path, 'rb'),
            prompt=query,
            n=1,
            size="1024x1024",
            response_format='url'
            )
        
        # print(ImagesResponse)
        response = requests.get(ImagesResponse.data[0].url)
        return response.content
    
    except openai.OpenAIError as e:
        print(e)
        return None
    except Exception as e:
        print(e)
        return None
    
        
    







## Speech Handling Commands ##
def text_to_speech(message, openai_api_key, voice="alloy"):
    """
    def text_to_speech(message): takes a message, and returns a voice file containing its dictated version.
    """
    client = OpenAI(api_key=openai_api_key)
    query = helper_functions.extract_body(message.text)


    # execute the query:
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


def speech_to_text(voice_file_path, openai_api_key):
    """
    def speech_to_text(message): takes a voice file, and returns a transcribed version of it.
    """
    client = OpenAI(api_key=openai_api_key)
    transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=open(voice_file_path, 'rb'),
    response_format='text')
    if len(transcript) > 0:
        return transcript
    else:
        return False















