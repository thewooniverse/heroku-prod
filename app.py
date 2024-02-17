from flask import Flask, request, jsonify
import requests, os
import telebot
import helper_functions
import ai_commands
import tempfile
import io
from PIL import Image
import PIL





"""
Use this bot as a test environment for building out whatever features that you want to build out;
To its maximum, it doesn't matter if it breaks, it can be rolled back as well.
Its a playground; its also pretty exciting to just like build bigger and bigger projects with more and more features.
Eventually, it would be really cool and amazing to write a full fledged AI assistant that can really help automate MANY parts of my life.

------To do lists:--------
#### Completed ####
- Secure environment variables <- done
- Different chat request sorters that sort through chat requests and call different commands and responses to the texts. <-
- Integration with basic ChatGPT using langchain
- Dall-E 3 Image generation commands with optional image inputand sending --> need to update the send message function as well.
-- v1 it will send just the URL link, but the next version it w ill save and delete.
- Text to Speech
>>>> tts bugfix

- Local testing environments + CI/CD devops stuff so I can test apps locally in Dev environment, test things in test builds, and then deploy to production.
- In staging, the first one I'll develop is /t1 /t2 /t3; configurable languages. (defaults set to english, Chinese, Korean).

- Vision
- translate - t1, t2, t3 <<<- translate whatever 

Current dev priorities;
- speech to text and various sorts of it; 
-- Speech to Text (speech to text) <- need to do reply to
-- Speech to Chat (transcribe and then chat) <- basically spt and then calling the /chat function
- stt bugfix
- imagine bugfix
- setwebhook coded into the app sourcecode; << fixed this to instead run once within startup.sh, and procfile to trigger a startup script.

----- done above -----



- /edit_img dalle2
- /variant dalle2
- speech to chat



Current dev priorities;
ADD A FEW MORE FEATURES
- speech to translation -> spt en, spt cn etc...
- Vision

Logging
- Thorough logging: basics of logging with metadata, integrating with a persistent solution (papertrail), accessing logs

Databasing + Configurations and customizations
- Configurations and safety checking best practices using Postgres, key management etc..
- RAG using threads / Assistant integration, or Chroma vectorstore to introduce persistence in context / chat history. << databases on heroku to manage this.

Refactoring / Cleanup
- /start cleanup
- Port over and fork it for family usage version


Further Integrations and Features
- Google calendar API << I can connect it to onenote, to zapier for waaaaaaaaaaaaay more things

DevOps
- Local testing and automated testing
- Github Workflows


ADDL GPT features
- Fine tuning the model for different use cases, different finetuned stuff for different usecases.
- AI Committee? Eventually I suppose

# Bot Features
- Buttons 
- premium subscriptions, ability to make different types of requests;



>>>> FORK OUT into OpenAssistant
- OpenAssistantStaging_Bot - 
- OpenAssistantProduction_Bot - 
- AssBlaster69Staging_Bot -
- AssBlaster69Prod_Bot - 
"""





app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN') # for prod and staging environments it means this would be different
OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY', 'YourAPIKey_BACKUP') # again, same environment variable, different api keys accessed
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'
WEBHOOK_URL_PATH = '/webhook'  # This path should match the path component of WEBHOOK_URL
ROOT_URL = os.environ.get('ROOT_URL')
WEBHOOK_URL = (ROOT_URL + WEBHOOK_URL_PATH)
DYNO_NAME = os.environ.get('DYNO')


bot = telebot.TeleBot(TELEGRAM_TOKEN)






@app.route('/')
def hello_world():
    return helper_functions.start_menu()

# Your web application needs to listen for POST requests on the path you specified in your webhook URL. Here's an example using Flask:
@app.route(WEBHOOK_URL_PATH, methods=['POST']) # Define Route: We're telling our Flask app that whenever it receives a POST request at the WEBHOOK_URL_PATH,
# it should execute the function defined directly below this line.
def receive_update():
    # Receive Update Function: This is the start of a function definition called receive_update, 
    # which will be called whenever a POST request is received at our webhook URL path.

    json_string = request.stream.read().decode('utf-8') 
    # Read Request Data: This line reads the raw data from the incoming request, decodes it from UTF-8 format, and stores it as a string in json_string. 
    # This string contains the update data sent by Telegram.

    update = telebot.types.Update.de_json(json_string)
    # Parse Update Data: Here, we're converting the JSON string into a Telebot Update object using the de_json method. 
    # This Update object makes it easier to work with the data from Telegram.

    bot.process_new_updates([update])
    # Process Update: This line tells the bot to process the update we just received. 
    # Essentially, it triggers any handlers you've set up in your bot for various commands or message types.

    return '!', 200
    # Respond to Telegram: After processing the update, this line sends a response back to Telegram. 
    # The 200 status code indicates success, and '!' is just a simple response body. 
    # Telegram doesn't use the response body, but a valid HTTP response is required.



@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, helper_functions.start_menu())


@bot.message_handler(commands=['chat'])
def handle_chat(message):
    response_text = ai_commands.chat_completion(message, model='gpt-4')
    bot.reply_to(message, text=response_text, parse_mode='Markdown')

@bot.message_handler(commands=['t1'])
def handle_chat(message):
    response_text = ai_commands.translate(message, target_language='eng',model='gpt-4')
    bot.reply_to(message, text=response_text, parse_mode='Markdown')

@bot.message_handler(commands=['t2'])
def handle_chat(message):
    response_text = ai_commands.translate(message, target_language='kor',model='gpt-4')
    bot.reply_to(message, text=response_text, parse_mode='Markdown')

@bot.message_handler(commands=['t3'])
def handle_chat(message):
    response_text = ai_commands.translate(message, target_language='chi',model='gpt-4')
    bot.reply_to(message, text=response_text, parse_mode='Markdown')


# image based handlers
@bot.message_handler(commands=['imagine'])
def handle_imagine(message):
    query = helper_functions.extract_body(message.text)
    system_context = "I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:"
    print(query)
    image_content = ai_commands.generate_image(message)
    if image_content:
        bot.send_photo(message.chat.id, photo=image_content)
    else:
        bot.reply_to(message, "Failed to fetch or generate image")
    # bot.reply_to(message, response_text)






@bot.message_handler(commands=['edit'])
def handle_edit(message):
    """
    - edit image can only work with two images, and type has to be png
    - addl error handling for filesize and dimension size
    """
    # initialize and simplfied cleanup
    temp_original_img_file_path = None

    # base condition is that we are replying to an image with the /edit command with some query / requests, with an optional mask image.
    if message.reply_to_message and message.reply_to_message.content_type == 'photo':
        print("Original Image file received")
    
        # get the original message and the image contained in it
        original_message = message.reply_to_message
        original_image = original_message.photo[-1]
        original_image_file_info = bot.get_file(original_image.file_id)

        # try and get the original image and process it as a PNG file
        try:
            # tryt to download the original image and process it as a PNG file
            downloaded_original_img = bot.download_file(original_image_file_info.file_path)
            print("Original Image downloaded")
            # Use BytesIO for in-memory image processing
            image_stream = io.BytesIO(downloaded_original_img)
            image_stream.seek(0)  # Go to the start of the stream
            # Open the image using Pillow for conversion
            with Image.open(image_stream) as img:
                # Convert the image to PNG and save it to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_original_img_file:
                    img.save(temp_original_img_file, format='PNG')
                    temp_original_img_file_path = temp_original_img_file.name
                    print(f"Image converted to PNG and saved at {temp_original_img_file_path}")

        # if the image could not be converted, then we print the error and return the handler and exit early
        except Exception as e:
            if isinstance(e, IOError):
                print("Error: error occured during file operations")
            elif isinstance(e, PIL.UnidentifiedImageError):
                print("Error: error occured during Image Conversion to PNG")
            else:
                print(f"Error: unidentified erro, please check logs. Details {str(e)}")
            return
    
    # if the base condition is not met where the reply message is not an image; then we exit the function early
    else:
        print("Original Message does not include an image")
        bot.reply_to(message, "Original Message does not include an image")
        return
    
    try:
        print("Image processing: no mask")
        img_edit_response = ai_commands.edit_image(message, temp_original_img_file_path)
        print(img_edit_response)
        if img_edit_response:
            print("Edited image generated")
            bot.send_photo(message.chat.id, photo=img_edit_response)
        else:
            print("Edited image with just the original image could not be generated")
    except:
        print("Edited image could not be generated")

    if temp_original_img_file_path:
        os.remove(temp_original_img_file_path)
        print("Original iamge file removed")

            


















# voice based handlers
@bot.message_handler(commands=['tts'])
def handle_tts(message):
    tts_response = ai_commands.text_to_speech(message)
    if tts_response:
        print("Audio generated")
        bot.send_voice(message.chat.id, tts_response)
    else:
        print("Audio failed to generate")
        bot.reply_to(message, "Failed to fetch or generate speech.")


@bot.message_handler(commands=['stt'])
def handle_stt(message):
    # check whether it is replying to a message - must be used in reply to a message
    if message.reply_to_message and message.reply_to_message.content_type == 'voice':
        original_message = message.reply_to_message
        voice_note = original_message.voice
        voice_file_info = bot.get_file(voice_note.file_id)

        try:
            downloaded_voice = bot.download_file(voice_file_info.file_path)
            print("Voice note downloaded")

            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_voice_file:
                temp_voice_file.write(downloaded_voice)
                temp_voice_file_path = temp_voice_file.name
            
            stt_response = ai_commands.speech_to_text(temp_voice_file_path) # receives a transcribed text
            bot.reply_to(message, stt_response or "Could not convert speech to text")

            # Clean up: Remove the temporary file
            os.remove(temp_voice_file_path)

        
        except Exception as e:
            print(f"Error during STT process {e}")
            bot.reply_to(message, "Failed to process the voice note, please check logs.")
        
    else:
        print("No target message")
        bot.reply_to(message, "Please reply to a voice note")










if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))


