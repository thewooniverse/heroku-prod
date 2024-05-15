from flask import Flask, request, jsonify
from telebot import types
import requests, os
import telebot
from telebot import types
import helper_functions
import ai_commands
import tempfile
import io
from PIL import Image
import PIL
import logging
import sys
import helper_classes
import signal
import sys
import json
import traceback
import config_db_helper # this also runs all of the necessary functions in creating all the tables
from config_db_helper import get_or_create_chat_config
import re
import settings
from iso_codes import get_code_and_name
import pandas
import datetime



# payments modules;
from telebot.types import LabeledPrice

# database modules
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from psycopg2 import pool

# vectorstore related modules
from pinecone import Pinecone, ServerlessSpec


import templates















"""
1. Go through settigs, strings etc... tidy that up, and get a function to change the settings.py name import to conversation strings.

----- done above ---------- done above ---------- done above ---------- done above ---------- done above -----
=========================================================================================================
So pretty much its:
2. Suggestions for commands, pre-completion options
Admin Command Handlers; Clear chat history command.

--- up to here today ---
3. Forking it into TeleGPT.bot -> host the website and making the bot public for usage; @TeleGPT_dot_bot.

4. Then you can drop AB69 staging, and build on the main environment, and fork it again for Wooniverse_bot that is gated;
--> Wooniverse bot will interact with my webpages etc...

That then marks the end of it;
Additional optional features:
- Context saving from pictures;
==========================================

Potential future features:
- "Hey Siri" type voice message prompts enabled; you can customize and set up your own voice agent that doesn't require a command handler.


"""




# instantiate the app
app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN') # for prod and staging environments it means this would be different
OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY', 'YourAPIKey_BACKUP') # again, same environment variable, different api keys accessed
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'
ROOT_URL = os.environ.get('ROOT_URL')
WEBHOOK_URL_PATH = '/webhook'  # This path should match the path component of WEBHOOK_URL
WEBHOOK_URL = (ROOT_URL + WEBHOOK_URL_PATH)
DYNO_NAME = os.environ.get('DYNO', 'unknown-dyno')

# payments keys
STRIPE_PAYMENT_KEY_TEST = os.environ.get('STRIPE_TEST_KEY')
STRIPE_PAYMENT_KEY = os.environ.get('STRIPE_KEY')

# vectorstore setup
PINECONE_KEY = os.environ.get('PINECONE_API')
pc = Pinecone(api_key=PINECONE_KEY)




# instantiate the bot and any key helper functions
bot = telebot.TeleBot(TELEGRAM_TOKEN)












# create logging objects
LOG_LEVEL = os.getenv('LOG_LEVEL', 'ERROR').upper()
print(f"Logging started with {LOG_LEVEL}")
logging.basicConfig(stream=sys.stdout, level=getattr(logging, LOG_LEVEL, logging.INFO), format='%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(message)s')
# logger = helper_classes.CustomLoggerAdapter(logging.getLogger(__name__), {'dyno_name': DYNO_NAME}) # < creates an custom logger adapter
logger = logging.getLogger(__name__)

# create necessary tables
config_db_helper.create_config_table("chat_configs", "chat")
config_db_helper.create_config_table("user_configs", "user")





@app.route('/')
def hello_world():
    return helper_functions.start_menu()

# Your web application needs to listen for POST requests on the path you specified in your webhook URL. Here's an example using Flask:
@app.route(WEBHOOK_URL_PATH, methods=['POST']) # Define Route: We're telling our Flask app that whenever it receives a POST request at the WEBHOOK_URL_PATH, /webhook
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
    if message.from_user.is_bot:
        return

    try:
        # import the configs
        # previous test, to be deleted. Commented out to prevent unnecessary database connections.
        # chat_config = get_or_create_chat_config(message.chat.id, 'chat')
        # user_config = get_or_create_chat_config(message.from_user.id, 'user')
        # bot.reply_to(message, f"Chat language model: {chat_config['language_model']}, user language model: {user_config['language_model']}")
        bot.reply_to(message, templates.start_menu)
        logger.info(helper_functions.construct_logs(message, "Success: command successfully executed"))
    except Exception as e:
        bot.reply_to(message, "/start command request could not be completed, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {e}"))





# text handlers
@bot.message_handler(commands=['chat'])
def handle_chat(message):
    # bot check
    if message.from_user.is_bot:
        return

    context = ""
    try:
        user_config = get_or_create_chat_config(message.from_user.id, 'user')
        chat_config = get_or_create_chat_config(message.chat.id, 'chat')
        body_text = helper_functions.extract_body(message.text)

        # handle API Keys, the usage of the group's API key is prioritized over individual.
        api_keys = config_db_helper.get_apikey_list(message)
        if not api_keys:
            bot.reply_to(message, "OpenAI API could not be called as there is no API Key entered, please set an OpenAI API Key for the group or the user.")
            return

        # Construct the chat histories based on whether the user is replying, and whether the user has premium + persistence on;
        if message.reply_to_message:
            chat_history = f"THIS MESSAGE iS IN DIRECT REPLY TO THIS MESSAGE, USE IT AS CONTEXT:\n{message.reply_to_message.text}\n\n\n{'---'*3}"
        else:
            chat_history = ""
        
        if user_config['is_premium'] and (message.chat.id in user_config['persistent_chats']):
            history_similarity_search_result_string = ai_commands.similarity_search_on_index(message, api_keys[0], PINECONE_KEY)
            # print(history_similarity_search_result_string)
            chat_history += history_similarity_search_result_string

        if api_keys:
            try:
                context = chat_config['contexts'][str(message.from_user.id)]
                # print(context)
            except KeyError:
                print("No context was set for user")

            response_text = ai_commands.chat_completion(message, context, chat_history = chat_history, openai_api_key=api_keys[0], model=chat_config['language_model'], temperature=chat_config['lm_temp'])
            bot.reply_to(message, text=response_text, parse_mode='Markdown')
            logger.info(helper_functions.construct_logs(message, f"Success: response generated and sent."))

            # if the user is a premium user, and is the user wanting to save chat history for this chat group?
            if user_config['is_premium'] and (message.chat.id in user_config['persistent_chats']):
                # construct the string to upload;
                upload_string = f"""USER QUERY/PROMPT:\n{body_text}\n\n\n{'---' * 5}\n\n\nAI RESPONSE:\n{response_text}"""
                openai_api_key = api_keys[0]

                # create and upsert the embeddings into the index
                ai_commands.create_and_upsert_embeddings(message, upload_string, openai_api_key, PINECONE_KEY)
                print("Safely upserted data into pinecone")


    except Exception as e:
        bot.reply_to(message, "/chat command request could not be completed, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {e}"))








@bot.message_handler(commands=['t1'])
def handle_translate_1(message):
    try:
        api_keys = config_db_helper.get_apikey_list(message)
        user_config = get_or_create_chat_config(message.from_user.id, 'user')
        chat_config = get_or_create_chat_config(message.chat.id, 'chat')

        if not api_keys:
            bot.reply_to(message, "OpenAI API could not be called as there is no API Key entered, please set an OpenAI API Key for the group or the user.")
            return

        if api_keys:
            response_text = ai_commands.translate(message, openai_api_key=api_keys[0], target_language=chat_config['t1'], model=chat_config['language_model'])
            bot.reply_to(message, text=response_text, parse_mode='Markdown')
            logger.info(helper_functions.construct_logs(message, "Success"))
    except Exception as e:
        bot.reply_to(message, "/translate command request could not be completed, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {e}"))


@bot.message_handler(commands=['t2'])
def handle_translate_2(message):
    try:
        api_keys = config_db_helper.get_apikey_list(message)
        user_config = get_or_create_chat_config(message.from_user.id, 'user')
        chat_config = get_or_create_chat_config(message.chat.id, 'chat')

        if not api_keys:
            bot.reply_to(message, "OpenAI API could not be called as there is no API Key entered, please set an OpenAI API Key for the group or the user.")
            return

        if api_keys:
            response_text = ai_commands.translate(message, openai_api_key=api_keys[0], target_language=chat_config['t2'], model=chat_config['language_model'])
            bot.reply_to(message, text=response_text, parse_mode='Markdown')
            logger.info(helper_functions.construct_logs(message, "Success"))
        
    except Exception as e:
        bot.reply_to(message, "/translate command request could not be completed, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {e}"))

    
@bot.message_handler(commands=['t3'])
def handle_translate_3(message):
    try:

        api_keys = config_db_helper.get_apikey_list(message)
        user_config = get_or_create_chat_config(message.from_user.id, 'user')
        chat_config = get_or_create_chat_config(message.chat.id, 'chat')


        if not api_keys:
            bot.reply_to(message, "OpenAI API could not be called as there is no API Key entered, please set an OpenAI API Key for the group or the user.")
            return

        if api_keys:
            response_text = ai_commands.translate(message, openai_api_key=api_keys[0], target_language=chat_config['t3'], model=chat_config['language_model'])
            bot.reply_to(message, text=response_text, parse_mode='Markdown')
            logger.info(helper_functions.construct_logs(message, "Success"))
    except Exception as e:
        bot.reply_to(message, "/translate command request could not be completed, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {e}"))





# voice based handlers
@bot.message_handler(commands=['tts'])
def handle_tts(message):
    try:
        api_keys = config_db_helper.get_apikey_list(message)

        if not api_keys:
            bot.reply_to(message, "OpenAI API could not be called as there is no API Key entered, please set an OpenAI API Key for the group or the user.")
            return

        if api_keys:
            tts_response = ai_commands.text_to_speech(message, openai_api_key=api_keys[0])
            if tts_response:
                logger.info(helper_functions.construct_logs(message, "Success: Audio response generated"))
                bot.send_voice(message.chat.id, tts_response)
        else:
            bot.reply_to(message, "Text received but failed to fetch or generate speech, please contact admin.")
            logger.warning(helper_functions.construct_logs(message, "Warning: tts response could not be generated")) 

    except Exception as e:
        bot.reply_to(message, "/tts command request could not be completed, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {e}"))





@bot.message_handler(commands=['stt'])
def handle_stt(message):
    # check whether it is replying to a message - must be used in reply to a message
    if message.reply_to_message and message.reply_to_message.content_type == 'voice':
        original_message = message.reply_to_message
        voice_note = original_message.voice
        voice_file_info = bot.get_file(voice_note.file_id)

        try:
            downloaded_voice = bot.download_file(voice_file_info.file_path)
            logger.debug(helper_functions.construct_logs(message, "Check: voice note downloaded"))

            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_voice_file:
                temp_voice_file.write(downloaded_voice)
                temp_voice_file_path = temp_voice_file.name
            
            api_keys = config_db_helper.get_apikey_list(message)
            if not api_keys:
                bot.reply_to(message, "OpenAI API could not be called as there is no API Key entered, please set an OpenAI API Key for the group or the user.")
                return

            if api_keys:
                stt_response = ai_commands.speech_to_text(temp_voice_file_path, openai_api_key=api_keys[0]) # receives a transcribed text
                if stt_response:
                    bot.reply_to(message, stt_response)
                    logger.info(helper_functions.construct_logs(message, "Success: text to speech sent"))
                else:
                    bot.reply_to(message, "Could not convert speech to text")
                    logger.warning(helper_functions.construct_logs(message, "Warning: Voice note downloaded, but stt translation could not be completed"))

            # Clean up: Remove the temporary file
            os.remove(temp_voice_file_path)
        
        except Exception as e:
            logger.error(helper_functions.construct_logs(message, f"Error: Error occured {e}"))
            bot.reply_to(message, "Failed to process the voice note, please check logs.")
        
    else:
        bot.reply_to(message, "Please reply to a voice note")
        logger.debug(helper_functions.construct_logs(message, "Debug: No target message"))





@bot.message_handler(commands=['stc'])
def handle_stc(message):
    """
    handle_stc(message): handles a speech / voice note, transcribes it to text and prompts the language model with it.
    """
    # check whether it is replying to a message - must be used in reply to a message
    if message.reply_to_message and message.reply_to_message.content_type == 'voice':
        original_message = message.reply_to_message
        voice_note = original_message.voice
        voice_file_info = bot.get_file(voice_note.file_id)

        try:
            downloaded_voice = bot.download_file(voice_file_info.file_path)
            logger.debug(helper_functions.construct_logs(message, "Check: voice note downloaded"))
            user_config = get_or_create_chat_config(message.from_user.id, 'user')
            chat_config = get_or_create_chat_config(message.chat.id, 'chat')

            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_voice_file:
                temp_voice_file.write(downloaded_voice)
                temp_voice_file_path = temp_voice_file.name
            
            api_keys = config_db_helper.get_apikey_list(message)
            if not api_keys:
                bot.reply_to(message, "OpenAI API could not be called as there is no API Key entered, please set an OpenAI API Key for the group or the user.")
                return

            if api_keys:
                stt_response = ai_commands.speech_to_text(temp_voice_file_path, openai_api_key=api_keys[0]) # receives a transcribed text
                if stt_response:
                    
                    # send the stt response as well if the user wants to (optional?) - but for now, we keep it so that ppl can edit it if its wrong.
                    bot.reply_to(message, stt_response)
                    logger.info(helper_functions.construct_logs(message, "Success: text to speech sent"))

                    # use the stt text response to call the chat and send the response
                    context=''
                    response_text = ai_commands.chat_completion(message, context, openai_api_key=api_keys[0], model=chat_config['language_model'], temperature=chat_config['lm_temp'])
                    bot.reply_to(message, text=response_text, parse_mode='Markdown')
                    logger.info(helper_functions.construct_logs(message, f"Success: query response generated and sent."))
                else:
                    bot.reply_to(message, "Could not convert speech to text")
                    logger.warning(helper_functions.construct_logs(message, "Warning: Voice note downloaded, but stt translation could not be completed"))

            # Clean up: Remove the temporary file
            os.remove(temp_voice_file_path)
        
        except Exception as e:
            logger.error(helper_functions.construct_logs(message, f"Error: Error occured {e}"))
            bot.reply_to(message, "Failed to process the voice note, please check logs.")
        
    else:
        bot.reply_to(message, "Please reply to a voice note")
        logger.debug(helper_functions.construct_logs(message, "Debug: No target message"))









# image based handlers
@bot.message_handler(commands=['imagine'])
def handle_imagine(message):
    # query = helper_functions.extract_body(message.text)
    system_context = "I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:"

    try:
        api_keys = config_db_helper.get_apikey_list(message)

        if not api_keys:
            bot.reply_to(message, "OpenAI API could not be called as there is no API Key entered, please set an OpenAI API Key for the group or the user.")
            return

        if api_keys:
            image_content = ai_commands.generate_image(message, api_keys[0], system_context)
            bot.send_photo(message.chat.id, photo=image_content)
            logger.info(helper_functions.construct_logs(message, "Success: Generated and sent image to chat"))

    except Exception as e:
        bot.reply_to(message, "Failed to fetch or generate image")
        logger.error(helper_functions.construct_logs(message, f"Error: Could not complete image generation, error: {e}"))





@bot.message_handler(commands=['variate'])
def handle_variations(message):
    """
    Should eventually also support multiple n, but TBD; n shoudl be from config so after config is created I can handle this.
    """
    # base condition is that we are replying to an image with the /edit command with some query / requests, with an optional mask image.
    if message.reply_to_message and message.reply_to_message.content_type == 'photo':

        # Download & get the original message and the image contained in it
        original_message = message.reply_to_message
        original_image = original_message.photo[-1]
        original_image_file_info = bot.get_file(original_image.file_id)

        # try and get the original image and process it as a PNG file
        try:
            # tryt to download the original image and process it as a PNG file
            downloaded_original_img = bot.download_file(original_image_file_info.file_path)
            logger.debug(helper_functions.construct_logs(message, "Debug: Image successfully downloaded"))

            with io.BytesIO(downloaded_original_img) as image_stream:
                # Open the image using Pillow with another 'with' block
                with Image.open(image_stream).convert('RGBA') as img:
                    width, height = 1024, 1024
                    img = img.resize((width, height)) # resize to standard image, same as the mask image
                    logger.debug(helper_functions.construct_logs(message, "Debug: Image successfully converted and resized"))

                    # Convert the resized image to a BytesIO object again
                    with io.BytesIO() as byte_stream:
                        img.save(byte_stream, format='PNG')
                        byte_array = byte_stream.getvalue()
                        api_keys = config_db_helper.get_apikey_list(message)
                        if not api_keys:
                            bot.reply_to(message, "OpenAI API could not be called as there is no API Key entered, please set an OpenAI API Key for the group or the user.")
                            return

                        if api_keys:
                            img_var_response = ai_commands.variate_image(message, byte_array, openai_api_key=api_keys[0])
                            if img_var_response:
                                logger.info(helper_functions.construct_logs(message, "Info: Image variation successfully generated"))
                                bot.send_photo(message.chat.id, photo=img_var_response)
                            else:
                                logger.warning(helper_functions.construct_logs(message, "Info: Original image received and converted, however image failed to generate"))
                                bot.reply_to(message, "Could not generate Variations of the image")
                            
        # if the image could not be converted, then we print the error and return the handler and exit early
        except Exception as e:
            if isinstance(e, IOError):
                logger.error(helper_functions.construct_logs(message, f"Error: error occured during file operations: {e}"))
            elif isinstance(e, PIL.UnidentifiedImageError):
                print(f"Error: error occured during Image Conversion to PNG")
                logger.error(helper_functions.construct_logs(message, f"Error: error occured during Image Conversion to PNG: {e}"))
            else:
                logger.error(helper_functions.construct_logs(message, f"Error: unidentified error, please check logs. Details {str(e)}"))
            return
    # if the base condition is not met where the reply message is not an image; then we exit the function early
    else:
        bot.reply_to(message, "Original Message does not include an image")
        logger.warning(helper_functions.construct_logs(message, f"Warning: Original message did not include an image"))







@bot.message_handler(commands=['vision'])
def handle_vision(message):
    """
    Queries: Returns a chat completion text response from a image + query
    - /vision {text} 
    """
    # check if we are replying to a message, and that message contains an image.
    if message.reply_to_message and message.reply_to_message.content_type == 'photo':

        # ensure that the file format is in PNG
        original_message = message.reply_to_message
        original_image = original_message.photo[-1]
        original_image_file_info = bot.get_file(original_image.file_id)

        try:
            downloaded_img_file = bot.download_file(original_image_file_info.file_path)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp:
                temp.write(downloaded_img_file)
                temp_img_path = temp.name
                logger.debug(helper_functions.construct_logs(message, f"Debug: Image successfully donwloaded, converted and resized at {temp.name}"))

                # encode the image to base64
                encoded_img = helper_functions.encode_image(temp_img_path)
                api_keys = config_db_helper.get_apikey_list(message)
                if not api_keys:
                    bot.reply_to(message, "OpenAI API could not be called as there is no API Key entered, please set an OpenAI API Key for the group or the user.")
                    return

                if api_keys:
                    text_response = ai_commands.image_vision(message, encoded_img, openai_api_key=api_keys[0])
                    bot.reply_to(message, text_response)
                    logger.info(helper_functions.construct_logs(message, f"Debug: Image successfully analyzed and response and sent"))
        
        except Exception as e:
            # handle various exceptions
            logger.error(helper_functions.construct_logs(message, f"Error: Error occured at {e}"))
            bot.reply_to(message, "Unable to analyze image")
        finally:
            # handle file cleanup
            os.remove(temp_img_path)
            logger.debug(helper_functions.construct_logs(message, f"Debug: Image file cleanup successful"))
    
    else:
        print("No reply message or image found")
        bot.reply_to(message, "Please reply to an image message")












@bot.message_handler(commands=['edit_img'])
def handle_edit(message):
    # base condition is that we are replying to an image with the /edit command with some query / requests, with an optional mask image.
    if message.reply_to_message and message.reply_to_message.content_type == 'photo':
    
        # get the original message and the image contained in it
        original_message = message.reply_to_message
        original_image = original_message.photo[-1]
        original_image_file_info = bot.get_file(original_image.file_id)

        user_config = get_or_create_chat_config(message.from_user.id, 'user')  # Assume this fetches user-specific config
        if user_config['is_premium']:
            user_image_mask_map = user_config['premium_image_mask_map']
        else:
            user_image_mask_map = user_config['image_mask_map']


        print(user_image_mask_map)

        # try and get the original image and process it as a PNG file
        try:
            # tryt to download the original image and process it as a PNG file
            downloaded_original_img = bot.download_file(original_image_file_info.file_path)
            width, height = 1024, 1024

            with io.BytesIO(downloaded_original_img) as image_stream:
                # Open the image using Pillow with another 'with' block
                with Image.open(image_stream).convert('RGBA') as img:
                    img = img.resize((width, height)) # resize to standard image, same as the mask image
                    mask = img.copy()
                    logger.debug(helper_functions.construct_logs(message, f"Debug: Image successfully donwloaded and resized"))

                    # determine the grid cells;
                    cell_width = width // len(user_image_mask_map[0])
                    cell_height = height // len(user_image_mask_map)

                    # Apply transparency to designated areas defined in the image mask map
                    for row_index, row in enumerate(user_image_mask_map):
                        for col_index, cell in enumerate(row):
                            if cell == 1:  # If the cell is marked for transparency
                                for x in range(col_index * cell_width, (col_index + 1) * cell_width):
                                    for y in range(row_index * cell_height, (row_index + 1) * cell_height):
                                        mask.putpixel((x, y), (0, 0, 0, 0))  # Set alpha to 0 (transparent)
                    # # OLD APPROACH - Apply transparency to the bottom half of the mask
                    # for x in range(width):
                    #     for y in range(height // 2, height):
                    #         # Get the current pixel's color
                    #         r, g, b, a = mask.getpixel((x, y))
                    #         # Set alpha to 0 (fully transparent) for the bottom half
                    #         mask.putpixel((x, y), (r, g, b, 0))

                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_mask_file:
                        mask.save(temp_mask_file, format='PNG')
                        bot.send_photo(message.chat.id, photo=mask) # test

                        temp_mask_file_path = temp_mask_file.name
                        logger.debug(helper_functions.construct_logs(message, f"Debug: Mask Image generated and saved at {temp_mask_file_path}"))

                    # Convert the resized image to a BytesIO object again
                    with io.BytesIO() as byte_stream:
                        img.save(byte_stream, format='PNG')
                        byte_array = byte_stream.getvalue()
                        api_keys = config_db_helper.get_apikey_list(message)
                        if not api_keys:
                            bot.reply_to(message, "OpenAI API could not be called as there is no API Key entered, please set an OpenAI API Key for the group or the user.")
                            return  

                        if api_keys:
                            img_edit_response = ai_commands.edit_image(message, byte_array, temp_mask_file_path, openai_api_key=api_keys[0])

                            if img_edit_response:
                                logger.info(helper_functions.construct_logs(message, f"Info: Generated image edit with mask"))
                                bot.send_photo(message.chat.id, photo=img_edit_response)
                            else:
                                logger.warning(helper_functions.construct_logs(message, f"Warning: Image could not be generated"))
                                bot.reply_to(message, "Could not generate image, please contact admin to check logs.")

        # if the image could not be converted, then we print the error and return the handler and exit early
        except Exception as e:
            if isinstance(e, IOError):
                logger.error(helper_functions.construct_logs(message, f"Error: error occured during file operations: {e}"))
            elif isinstance(e, PIL.UnidentifiedImageError):
                logger.error(helper_functions.construct_logs(message, f"Error: error occured during Image Conversion to PNG: {e}"))
            else:
                logger.error(helper_functions.construct_logs(message, f"Error: unidentified error, please check logs. Details {str(e)}"))
            return
        
        finally:
            os.remove(temp_mask_file_path)

    # if the base condition is not met where the reply message is not an image; then we exit the function early
    else:
        print("Original Message does not include an image")
        bot.reply_to(message, "Original Message does not include an image")
















###############################################
### Bot configuration handlers and commands ###
###############################################

# Helper functions for generating different markups
# def settings_markup():
#     markup = types.InlineKeyboardMarkup()
#     user_settings_btn = types.InlineKeyboardButton("👤 User Settings", callback_data='user_settings') # telebot.types if it was not direct import
#     chat_settings_btn = types.InlineKeyboardButton("👥 Group Settings", callback_data='chat_settings')
#     markup.add(user_settings_btn, chat_settings_btn)
#     return markup

# User settings
def user_settings_markup():
    # back_btn = types.InlineKeyboardButton("🔙 Back", callback_data='back_to_main')
    # Add other buttons for user settings here
    image_mask_btn = types.InlineKeyboardButton("🖼️ Basic Image Mask", callback_data='image_mask_settings')
    premium_features = types.InlineKeyboardButton("🌟 Premium Features", callback_data='premium_user_settings')
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(image_mask_btn, premium_features)
    return markup


# premium user settings
def premium_user_settings_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🌌 Granular Image Masks", callback_data='premium_image_mask_settings'))
    # markup.row(types.InlineKeyboardButton("Contexts ON", callback_data='context_awareness_on'),
        # types.InlineKeyboardButton("Contexts OFF", callback_data='context_awareness_off'))
    markup.row(types.InlineKeyboardButton("🔙 Back", callback_data='user_settings'))
    return markup



# Image Mask markup
def image_mask_options_menu(mask_vector):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(f"{mask_vector[0][0]}", callback_data="im_00"),
                types.InlineKeyboardButton(f"{mask_vector[0][1]}", callback_data="im_01"),
                types.InlineKeyboardButton(f"{mask_vector[0][2]}", callback_data="im_02"))
    markup.row(types.InlineKeyboardButton(f"{mask_vector[1][0]}", callback_data="im_10"),
                types.InlineKeyboardButton(f"{mask_vector[1][1]}", callback_data="im_11"),
                types.InlineKeyboardButton(f"{mask_vector[1][2]}", callback_data="im_12"))
    markup.row(types.InlineKeyboardButton(f"{mask_vector[2][0]}", callback_data="im_20"),
                types.InlineKeyboardButton(f"{mask_vector[2][1]}", callback_data="im_21"),
                types.InlineKeyboardButton(f"{mask_vector[2][2]}", callback_data="im_22"))
    markup.row(types.InlineKeyboardButton("🌌 Granular Masks (Premium)", callback_data="premium_user_settings"))
    markup.row(types.InlineKeyboardButton("🔙 Back", callback_data="user_settings"))
    return markup

# Image Mask markup
def premium_image_mask_options_menu(mask_vector):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(f"{mask_vector[0][0]}", callback_data="pim_00"),
                types.InlineKeyboardButton(f"{mask_vector[0][1]}", callback_data="pim_01"),
                types.InlineKeyboardButton(f"{mask_vector[0][2]}", callback_data="pim_02"),
                types.InlineKeyboardButton(f"{mask_vector[0][3]}", callback_data="pim_03"),
                types.InlineKeyboardButton(f"{mask_vector[0][4]}", callback_data="pim_04"))
    markup.row(types.InlineKeyboardButton(f"{mask_vector[1][0]}", callback_data="pim_10"),
                types.InlineKeyboardButton(f"{mask_vector[1][1]}", callback_data="pim_11"),
                types.InlineKeyboardButton(f"{mask_vector[1][2]}", callback_data="pim_12"),
                types.InlineKeyboardButton(f"{mask_vector[1][3]}", callback_data="pim_13"),
                types.InlineKeyboardButton(f"{mask_vector[1][4]}", callback_data="pim_14"))
    markup.row(types.InlineKeyboardButton(f"{mask_vector[2][0]}", callback_data="pim_20"),
                types.InlineKeyboardButton(f"{mask_vector[2][1]}", callback_data="pim_21"),
                types.InlineKeyboardButton(f"{mask_vector[2][2]}", callback_data="pim_22"),
                types.InlineKeyboardButton(f"{mask_vector[2][3]}", callback_data="pim_23"),
                types.InlineKeyboardButton(f"{mask_vector[2][4]}", callback_data="pim_24"))
    markup.row(types.InlineKeyboardButton(f"{mask_vector[3][0]}", callback_data="pim_30"),
                types.InlineKeyboardButton(f"{mask_vector[3][1]}", callback_data="pim_31"),
                types.InlineKeyboardButton(f"{mask_vector[3][2]}", callback_data="pim_32"),
                types.InlineKeyboardButton(f"{mask_vector[3][3]}", callback_data="pim_33"),
                types.InlineKeyboardButton(f"{mask_vector[3][4]}", callback_data="pim_34"))
    markup.row(types.InlineKeyboardButton(f"{mask_vector[4][0]}", callback_data="pim_40"),
                types.InlineKeyboardButton(f"{mask_vector[4][1]}", callback_data="pim_41"),
                types.InlineKeyboardButton(f"{mask_vector[4][2]}", callback_data="pim_42"),
                types.InlineKeyboardButton(f"{mask_vector[4][3]}", callback_data="pim_43"),
                types.InlineKeyboardButton(f"{mask_vector[4][4]}", callback_data="pim_44"))
    markup.row(types.InlineKeyboardButton("🔙 Back", callback_data="premium_user_settings"))
    return markup







# Chat settings
def group_settings_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🤖 Language Models", callback_data='language_model_menu'))
    markup.row(types.InlineKeyboardButton("🌐 Translation Presets", callback_data='translations_menu'))
    markup.row(types.InlineKeyboardButton("🟢 Persistence ON", callback_data='persistence_on'),
        types.InlineKeyboardButton("🔴 Persistence OFF", callback_data='persistence_off'))
    return markup

# define the language_model_menu
def langauge_model_settings_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("GPT 3.5 Turbo", callback_data='set_lm_gpt3.5'),
        types.InlineKeyboardButton("GPT 4.0 ", callback_data='set_lm_gpt4'))
    markup.row(types.InlineKeyboardButton("🔙 Back", callback_data='group_settings')) # back to main should point to previous chat setting.)
    return markup

# define the translations option menu
def translation_options_menu(t1,t2,t3):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(f"1:{t1}", callback_data="t1"),
                types.InlineKeyboardButton(f"2:{t2}", callback_data="t2"),
                types.InlineKeyboardButton(f"3:{t3}", callback_data="t3"))
    markup.row(types.InlineKeyboardButton("🔙 Back", callback_data="group_settings"))
    return markup



# define translation langauge choice menu
def language_selection_menu(preset_num):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(f"🇬🇧", callback_data=f"lset_{preset_num}_eng"),
                types.InlineKeyboardButton(f"🇨🇳", callback_data=f"lset_{preset_num}_chi"),
                types.InlineKeyboardButton(f"🇮🇳", callback_data=f"lset_{preset_num}_hin"))
    markup.row(types.InlineKeyboardButton(f"🇪🇸", callback_data=f"lset_{preset_num}_spa"),
                types.InlineKeyboardButton(f"🇫🇷", callback_data=f"lset_{preset_num}_fre"),
                types.InlineKeyboardButton(f"🇸🇦", callback_data=f"lset_{preset_num}_ara"))
    markup.row(types.InlineKeyboardButton(f"🇵🇹", callback_data=f"lset_{preset_num}_por"),
                types.InlineKeyboardButton(f"🇷🇺", callback_data=f"lset_{preset_num}_rus"),
                types.InlineKeyboardButton(f"🇰🇷", callback_data=f"lset_{preset_num}_kor"))
    markup.row(types.InlineKeyboardButton("🔙 Back", callback_data="translations_menu"))
    return markup








# Core settings button functionality;
@bot.message_handler(commands=['settings'])
def handle_settings(message):
    bot.send_message(chat_id=message.chat.id, text=settings.settings_string, parse_mode="HTML")



@bot.message_handler(commands=['group_settings'])
def handle_group_settings(message):
    bot.send_message(chat_id=message.chat.id, text=settings.group_settings_string, reply_markup=group_settings_markup(), parse_mode="HTML")

@bot.message_handler(commands=['user_settings'])
def handle_user_settings(message):
    if message.chat.type != 'private':
        bot.reply_to(message, "You cannot change user specific settings in a group, you can only do it in private DM sessions.", parse_mode="HTML")
        return
    else:
        bot.send_message(chat_id=message.chat.id, text=settings.user_settings_string, reply_markup=user_settings_markup(), parse_mode="HTML")


@bot.message_handler(commands=['reset_user_settings'])
def handle_user_settings_reset(message):
    """
    Resets user settings
    """
    if message.from_user.is_bot:
        return
    
    try:
        config_db_helper.set_new_config(message.from_user.id, 'user', config_db_helper.default_user_config)
        bot.reply_to(message, "User configurations and settings have been reset to defaults.")
 
    except Exception as e:
        bot.reply_to(message, "/user_set_openai_key command request could not be completed, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {e}")) # traceback?



@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):

    # User Settings callback handler
    if call.data == "user_settings":
        # Update message to show user settings with a "Back" button
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=settings.user_settings_string, reply_markup=user_settings_markup(), parse_mode="HTML")

    if call.data == "premium_user_settings":
        # check whether the calling user has a premium subscriptipn
        user_config = get_or_create_chat_config(call.from_user.id, 'user')
        if user_config['is_premium']:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=settings.premium_user_settings_string, reply_markup=premium_user_settings_markup(), parse_mode="HTML")
        else:
            # if they don't then
            bot.answer_callback_query(call.id, "You do not have administrative permissions to change this setting. Pleaes subscribe using /subscribe")


    elif call.data == "image_mask_settings":
        user_config = get_or_create_chat_config(call.from_user.id, 'user')
        user_image_mask = user_config['image_mask_map']
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=settings.image_mask_settings_string, reply_markup=image_mask_options_menu(user_image_mask), parse_mode="HTML")
    
    elif call.data[0:3] == "im_":
        # get the image settings
        user_config = get_or_create_chat_config(call.from_user.id, 'user')
        user_image_mask = user_config['image_mask_map']

        # get the mask number clicked
        mask_idx = call.data[3:] # such that if im_00 is called, 00 is returned
        current_value_at_idx = user_image_mask[int(mask_idx[0])][int(mask_idx[1])]
        # set the values
        if current_value_at_idx == 0:
            new_value = 1
        else:
            new_value = 0

        # change the settings / configurations
        user_image_mask[int(mask_idx[0])][int(mask_idx[1])] = new_value
        user_config['image_mask_map'] = user_image_mask
        config_db_helper.set_new_config(call.from_user.id, 'user', user_config)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=settings.image_mask_settings_string, reply_markup=image_mask_options_menu(user_config['image_mask_map']), parse_mode="HTML")



    elif call.data == "premium_image_mask_settings":
        user_config = get_or_create_chat_config(call.from_user.id, 'user')
        premium_user_image_mask = user_config['premium_image_mask_map']
        print(premium_user_image_mask)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=settings.premium_image_mask_settings_string, reply_markup=premium_image_mask_options_menu(premium_user_image_mask), parse_mode="HTML")
    
    elif call.data[0:4] == "pim_":
        # get the image settings
        user_config = get_or_create_chat_config(call.from_user.id, 'user')
        premium_user_image_mask = user_config['premium_image_mask_map']
        print(premium_user_image_mask)

        # get the mask number clicked
        mask_idx = call.data[4:] # such that if pim_00 is called, 00 is returned
        current_value_at_idx = premium_user_image_mask[int(mask_idx[0])][int(mask_idx[1])]
        # set the values
        if current_value_at_idx == 0:
            new_value = 1
        else:
            new_value = 0
        # change the settings / configurations
        premium_user_image_mask[int(mask_idx[0])][int(mask_idx[1])] = new_value
        print(premium_user_image_mask)
        user_config['premium_image_mask_map'] = premium_user_image_mask
        config_db_helper.set_new_config(call.from_user.id, 'user', user_config)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=settings.premium_image_mask_settings_string, reply_markup=premium_image_mask_options_menu(user_config['premium_image_mask_map']), parse_mode="HTML")








    # Group Settings callback handler
    elif call.data == "group_settings":
        # Update message to show chat settings with a "Back" button
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=settings.group_settings_string, reply_markup=group_settings_markup(), parse_mode="HTML")
    
    elif call.data == "language_model_menu":
        # User pressed the "Back" button, return to main settings screen
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=settings.lm_settings_string, reply_markup=langauge_model_settings_markup(), parse_mode="HTML")
    
    # Handle callback data for changing language model in group;
    elif call.data == "set_lm_gpt3.5":
        # check that the clicker is an administrator
        if (call.message.chat.type != 'private'):
            if not helper_functions.user_has_admin_permission(bot, call.message.chat.id, call.from_user.id):
                bot.answer_callback_query(call.id, "You do not have administrative permissions to change this setting.")
                return
            
        # change the configuration for the group for the following;
        try:
            ## get the currenct chat config
            chat_config = get_or_create_chat_config(call.message.chat.id, 'chat')
            chat_config['language_model'] = "gpt-3.5-turbo"
            config_db_helper.set_new_config(call.message.chat.id, 'chat', chat_config)
            bot.send_message(chat_id=call.message.chat.id, text="Group's Language Model set to GPT 3.5! All chats here onwards will use this model")
        
        except Exception as e:
            bot.send_message(call.message.chat.id, "Configuration could not be completed, please check logs")
            logger.error(helper_functions.construct_logs(call.message, f"Error: {e}")) # traceback?


    # Handle callback data for changing language model in group;
    elif call.data == "set_lm_gpt4":
        # check that the clicker is an administrator
        if (call.message.chat.type != 'private'):
            if not helper_functions.user_has_admin_permission(bot, call.message.chat.id, call.from_user.id):
                bot.answer_callback_query(call.id, "You do not have administrative permissions to change this setting.")
                return
            
        # change the configuration for the group for the following;
        try:
            ## get the currenct chat config
            chat_config = get_or_create_chat_config(call.message.chat.id, 'chat')
            chat_config['language_model'] = "gpt-4"
            config_db_helper.set_new_config(call.message.chat.id, 'chat', chat_config)
            bot.send_message(chat_id=call.message.chat.id, text="Group's Language Model set to GPT 4! All chats here onwards will use this model")
        
        except Exception as e:
            bot.send_message(call.message.chat.id, "Configuration could not be completed, please check logs")
            logger.error(helper_functions.construct_logs(call.message, f"Error: {e}")) # traceback?


    elif call.data == "persistence_on":
        user_config = get_or_create_chat_config(call.from_user.id, 'user')

        # check whether the user is a premium user
        if not user_config['is_premium']:
            bot.answer_callback_query(call.id, "Persistence is a premium feature, please buy a premium subscription to turn this feature on!")
            return
        
        # if they are, then you are free to add this group to the list of persistent chats for that given user.
        current_persistent_chat_groups = user_config['persistent_chats']
        current_persistent_chat_groups.append(call.message.chat.id) # adds the chat id, which essentially turns the persistence "on" for this chat group.
        user_config['persistent_chats'] = current_persistent_chat_groups # set it to the newly appended list
        config_db_helper.set_new_config(call.from_user.id, 'user', user_config)
        bot.answer_callback_query(call.id, "Persistence has been turned on for your chats within this chat. Please note that in a public group with more users, your converesation in this group may be saved and used as context in prompts by other users.")
        print(f"persistence on for this user {call.from_user.id} in group {call.message.chat.id}")


    elif call.data == "persistence_off":
        user_config = get_or_create_chat_config(call.from_user.id, 'user')

        # check whether the user is a premium user
        if not user_config['is_premium']:
            bot.answer_callback_query(call.id, "Persistence is a premium feature, please buy a premium subscription to turn this feature on!")
            return
        
        # if they are, then you are free to add this group to the list of persistent chats for that given user.
        current_persistent_chat_groups = user_config['persistent_chats']

        try:
            current_persistent_chat_groups.remove(call.message.chat.id) # remove the list from its copy
            user_config['persistent_chats'] = current_persistent_chat_groups # set it to the newly removed list
            config_db_helper.set_new_config(call.from_user.id, 'user', user_config) # save the new config to the database
            print(f"persistence removed for this user {call.from_user.id} in group {call.message.chat.id}")
            bot.answer_callback_query(call.id, "Persistence is turned off for this group.")
        except ValueError as e:
            bot.answer_callback_query(call.id, "Persistence is already off for this group.")



    elif call.data == 'translations_menu':
        chat_config = get_or_create_chat_config(call.message.chat.id, 'chat')
        t1,t2,t3 = chat_config['t1'], chat_config['t2'], chat_config['t3']
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=settings.translation_presets_string, reply_markup=translation_options_menu(t1,t2,t3), parse_mode="HTML")
    
    elif call.data in ['t1', 't2', 't3']:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=settings.construct_translation_preset_string(call.data), reply_markup=language_selection_menu(call.data), parse_mode="HTML")
    
    elif call.data[0:4] == "lset":
        chat_config = get_or_create_chat_config(call.message.chat.id, 'chat')
        preset_nubmer = call.data.split('_')[1]
        language_choice = call.data.split('_')[2]
        chat_config[preset_nubmer] = language_choice
        config_db_helper.set_new_config(call.message.chat.id, 'chat', chat_config)
        bot.send_message(chat_id=call.message.chat.id, text=f"Translation preset {preset_nubmer} changed to {language_choice}!")






















# Manual configurations of settings that require users to type
@bot.message_handler(commands=['user_set_openai_key'])
def handle_user_set_openai_apikey(message):
    """
    handle_user_openai_apikey(message): sets openAI key for the user
    """
    if message.from_user.is_bot:
        return
    
    try:
        new_openai_key = helper_functions.extract_body(message.text)
        if config_db_helper.check_configval_pattern(new_openai_key, config_attr='openai_api_key'):

            # encrypt the key;
            new_openai_key = config_db_helper.encrypt(new_openai_key)

            # get the configurations
            user_config = get_or_create_chat_config(message.from_user.id, 'user')
            user_config['openai_api_key'] = new_openai_key
            new_config = user_config.copy()
            config_db_helper.set_new_config(message.from_user.id, 'user', new_config)

            if helper_functions.bot_has_delete_permission(message.chat.id, bot):
                bot.reply_to(message, f"New API key for user successfully set. Deleting message.")
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

            else:
                bot.reply_to(message, f"New API key for user successfully set. Message could not be deleted due to insufficient permissions, please delete this message to keep your API Key private.")
        else:
            bot.reply_to(message, f"Entered API Key is not in the correct format, please check again and try again.")

 
    except Exception as e:
        bot.reply_to(message, "/user_set_openai_key command request could not be completed, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {e}")) # traceback?


@bot.message_handler(commands=['chat_set_openai_key'])
def handle_chat_set_openai_apikey(message):
    """
    handle_chat_set_openai_apikey(message): sets openAI key for the user
    """
    if message.from_user.is_bot:
        return

    # Check permissions for group chats
    if message.chat.type != 'private' and not helper_functions.user_has_admin_permission(bot, message.chat.id, message.from_user.id):
        bot.reply_to(message, "You do not have permissions to set the temperature for this chat group.")
        return
        
    try:
        new_openai_key = helper_functions.extract_body(message.text)

        if config_db_helper.check_configval_pattern(new_openai_key, config_attr='openai_api_key'):
            
            # encrypt the key;
            new_openai_key = config_db_helper.encrypt(new_openai_key)

            # get the configurations
            chat_config = get_or_create_chat_config(message.chat.id, 'chat')
            chat_config['openai_api_key'] = new_openai_key
            new_config = chat_config.copy()
            config_db_helper.set_new_config(message.chat.id, 'chat', new_config)

            if helper_functions.bot_has_delete_permission(message.chat.id, bot):
                bot.reply_to(message, f"New API key for chat group successfully set. Deleting message.")
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

            else:
                bot.reply_to(message, f"New API key for user successfully set. Message could not be deleted due to insufficient permissions, please delete this message to keep your API Key private.")
        
        else:
            bot.reply_to(message, f"Entered API Key is not in the correct format, please check again and try again.")
    
    except Exception as e:
        bot.reply_to(message, "/user_set_openai_key command request could not be completed, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {e}")) # traceback?




# Manual configurations of settings that require users to type
@bot.message_handler(commands=['set_temperature'])
def handle_set_temperature(message):
    """
    Sets the language model temperature for a user or chat. Valid range is between 0 and 2.
    """
    if message.from_user.is_bot:
        return
    
    # Check permissions for group chats
    if message.chat.type != 'private' and not helper_functions.user_has_admin_permission(bot, message.chat.id, message.from_user.id):
        bot.reply_to(message, "You do not have permissions to set the temperature for this chat group.")
        return

    try:
        # Extract and validate the new temperature setting
        new_temperature = float(helper_functions.extract_body(message.text))
        if new_temperature < 0 or new_temperature > 2:
            bot.reply_to(message, "Invalid temperature. Please enter a value between 0 and 2.")
            return

        # Retrieve and update the chat configuration
        chat_config = get_or_create_chat_config(message.chat.id, 'chat')
        chat_config['lm_temp'] = new_temperature
        config_db_helper.set_new_config(message.chat.id, 'chat', chat_config)
        
        bot.reply_to(message, f"Temperature setting updated to {new_temperature}.")

    except ValueError:
        # Handle non-integer input gracefully
        bot.reply_to(message, "Please enter a valid integer for the temperature.")
    except Exception as e:
        # Generic error handling
        bot.reply_to(message, "Failed to set temperature, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {str(e)}"))







# Manual configurations of settings that require users to type
@bot.message_handler(commands=['set_t1'])
def handle_set_t1(message):
    """
    Sets the translation 1 preset of the group.
    """
    if message.from_user.is_bot:
        return
    
    # Check permissions for group chats if the user is an administrator
    if message.chat.type != 'private' and not helper_functions.user_has_admin_permission(bot, message.chat.id, message.from_user.id):
        bot.reply_to(message, "You do not have permissions to set the temperature for this chat group.")
        return
    
    try:
        new_iso_code = helper_functions.extract_body(message.text)
        # print(new_iso_code)


        retrieved_code, english_name = get_code_and_name(new_iso_code) ## This is where the issue is; probably simplify the code a bit here.
        print(retrieved_code, english_name)
        if not retrieved_code:
            bot.reply_to(message, "ISO is not in the ISO codes, please look up and try again.")
            return

        # Retrieve and update the chat configuration
        chat_config = get_or_create_chat_config(message.chat.id, 'chat')
        chat_config['t1'] = retrieved_code
        config_db_helper.set_new_config(message.chat.id, 'chat', chat_config)
        bot.reply_to(message, f"Translation Preset 1 (/t1) changed to {retrieved_code}: {english_name}.")

    except Exception as e:
        # Generic error handling
        bot.reply_to(message, "Failed to set translation preset, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {str(e)}"))





@bot.message_handler(commands=['set_t2'])
def handle_set_t2(message):
    """
    Sets the translation 2 preset of the group.
    """
    if message.from_user.is_bot:
        return
    
    # Check permissions for group chats if the user is an administrator
    if message.chat.type != 'private' and not helper_functions.user_has_admin_permission(bot, message.chat.id, message.from_user.id):
        bot.reply_to(message, "You do not have permissions to set the temperature for this chat group.")
        return
    
    try:
        new_iso_code = helper_functions.extract_body(message.text)
        # print(new_iso_code)

        
        retrieved_code, english_name = get_code_and_name(new_iso_code) ## This is where the issue is; probably simplify the code a bit here.
        # print(retrieved_code, english_name)
        if not retrieved_code:
            bot.reply_to(message, "ISO is not in the ISO codes, please look up and try again.")
            return

        # Retrieve and update the chat configuration
        chat_config = get_or_create_chat_config(message.chat.id, 'chat')
        chat_config['t2'] = retrieved_code
        config_db_helper.set_new_config(message.chat.id, 'chat', chat_config)
        bot.reply_to(message, f"Translation Preset 2 (/t2) changed to {retrieved_code}: {english_name}.")

    except Exception as e:
        # Generic error handling
        bot.reply_to(message, "Failed to set translation preset, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {str(e)}"))


@bot.message_handler(commands=['set_t3'])
def handle_set_t2(message):
    """
    Sets the translation 3 preset of the group.
    """
    if message.from_user.is_bot:
        return
    
    # Check permissions for group chats if the user is an administrator
    if message.chat.type != 'private' and not helper_functions.user_has_admin_permission(bot, message.chat.id, message.from_user.id):
        bot.reply_to(message, "You do not have permissions to set the temperature for this chat group.")
        return
    
    try:
        new_iso_code = helper_functions.extract_body(message.text)
        # print(new_iso_code)

        
        retrieved_code, english_name = get_code_and_name(new_iso_code) ## This is where the issue is; probably simplify the code a bit here.
        # print(retrieved_code, english_name)
        if not retrieved_code:
            bot.reply_to(message, "ISO is not in the ISO codes, please look up and try again.")
            return

        # Retrieve and update the chat configuration
        chat_config = get_or_create_chat_config(message.chat.id, 'chat')
        chat_config['t3'] = retrieved_code
        config_db_helper.set_new_config(message.chat.id, 'chat', chat_config)
        bot.reply_to(message, f"Translation Preset 3 (/t3) changed to {retrieved_code}: {english_name}.")

    except Exception as e:
        # Generic error handling
        bot.reply_to(message, "Failed to set translation preset, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {str(e)}"))



@bot.message_handler(commands=['set_context'])
def handle_set_context(message):
    """
    Sets the context for the group, whatever instructions it wants to give.
    """
    if message.from_user.is_bot:
        return
    
    # Check permissions for group chats if the user is an administrator -> commented out as ANYBODY should be able to set their context within a group
    # if message.chat.type != 'private' and not helper_functions.user_has_admin_permission(bot, message.chat.id, message.from_user.id):
    #     bot.reply_to(message, "You do not have permissions to set the temperature for this chat group.")
    #     return
    
    try:
        new_context = helper_functions.extract_body(message.text)
        
        # Retrieve and update the chat configuration
        chat_config = get_or_create_chat_config(message.chat.id, 'chat')
        chat_config['contexts'][str(message.from_user.id)] = new_context
        # print(chat_config['contexts'])
        config_db_helper.set_new_config(message.chat.id, 'chat', chat_config)
        bot.reply_to(message, f"Context has been set.")

    except Exception as e:
        # Generic error handling
        bot.reply_to(message, "Failed to set context for user in chat group, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {str(e)}"))



@bot.message_handler(commands=['set_user_context'])
def handle_set_user_context(message):
    """
    Sets the context for the user, whatever instructions it wants to give.
    """
    if message.from_user.is_bot:
        return
    
    try:
        new_context = helper_functions.extract_body(message.text)
        user_config = get_or_create_chat_config(message.from_user.id, 'user')
        user_config['user_context'] = new_context

        config_db_helper.set_new_config(message.from_user.id, 'user', user_config)
        bot.reply_to(message, f"New user context has been set to \n{new_context}.")
    except Exception as e:
        # Generic error handling
        bot.reply_to(message, "Failed to set context for user in chat group, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {str(e)}"))





 
# Handler for managing chat history as context for the given group;
@bot.message_handler(commands=['clear_chat_hist'])
def handle_clear_memory(message):
    """
    handle_clear_memory(message): clears the chat history and logs saved on the vectorstore and basically resets the conversation history
    """
    pass




















#########################################################
################## PAYMENTS FUNCTIONS: ##################
#########################################################

# Action
# - Integrate with test payment rails; and setting the configuration for the given user who called the message;
def generate_txid(user_id):
    current_date = datetime.date.today()
    return f"{user_id}_{current_date}"


@bot.message_handler(commands=['subscribe'])
def command_pay(message):
    if message.from_user.is_bot:
        return
    
    title = "🌟OpenAIssistant Premium Subscription🌟"
    description = settings.premium_subscription_string
    payload = generate_txid(message.from_user.id)
    provider_token = STRIPE_PAYMENT_KEY_TEST
    start_parameter = "premium-feature-subscription"
    currency = "USD"
    price = [LabeledPrice("Lifetime Subscription", 1000)]  # price in cents

    # print(f"Payload: {payload}")
    # print(f"Provider Token: {provider_token}")
    # print(f"Price: {price}")

    try:
        bot.send_invoice(message.chat.id, title, description, payload,
                         provider_token, currency, price, start_parameter)
    except Exception as e:
        print(f"Failed to send invoice: {str(e)}")
        bot.send_message(message.chat.id, f"Failed to send invoice: {str(e)}")

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    # Confirm the payment, thank the user, and grant access to the premium features.
    ## Get the configuration for the user;
    user_config = get_or_create_chat_config(message.from_user.id, 'user')

    ## change state and re-save it
    user_config['is_premium'] = True
    config_db_helper.set_new_config(message.from_user.id, 'user', user_config)

    ## Thank the user
    bot.send_message(message.chat.id, "Thank you for your payment. Premium features have been enabled for your account!")













#########################################################
######################## RUN BOT ########################
#########################################################




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))



