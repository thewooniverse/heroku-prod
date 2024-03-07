from flask import Flask, request, jsonify
import requests, os
import telebot
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
from templates import default_config
import traceback

# database modules
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from psycopg2 import pool















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
- translate - t1, t2, t3 <<<- translate whatever 

Current dev priorities;
- speech to text and various sorts of it; 
-- Speech to Text (speech to text) <- need to do reply to
-- Speech to Chat (transcribe and then chat) <- basically spt and then calling the /chat function
- stt bugfix
- imagine bugfix
- setwebhook coded into the app sourcecode; << fixed this to instead run once within startup.sh, and procfile to trigger a startup script.
- /variant dalle2
- /chat v2 with reply functions << this is complete, and I am not building addl. features on top of it because the bot will have built in chat history in the future

- /Vision << works as is.
logging conflicts and basic logging throughout helper functions as well as centralized logging in main app.py

Finish logging v1 throughout;
logging -> 
----- done above -----









DATABASE INTEGRATION WORKFLOW:
- Read through and learn basics of CRUD / SQL and Psycopg2 to integrate with Heroku PostgreSQL
- Design the initial configurations based on the configurability of the different functions and handlers
-- chat_model, name etc...
- Test implementation of returning "name" value from the configuration file for each chat along with connection pooling and test model implementations.



- Bulk update script for updating configurations with new configuration structures; bot is down while configs are being updated and maintained.






database -> database based features -> tidy up code, fork it and make it customer facing with good bot name; then this repo will be used to develop jarvis.
- now just building out logging properly into the different levels of the system for proper logs w different levels. Logging to replace printing on screen for std output errors.
- Errors with levels
- then, implement database solution, implement settingsa nd config.





-- Post database --

1. /edit dalle v2
-- /edit_mask(alpha targeting) /edit_img
-- /edit_img mask settings to target different chunks of the image (divided into 9 cells) - you can activate which area you want to create the alpha with buttons.
-- takes the /edit_img configurations for the chat, and creates a mask copy of the image, and then runs the edit_img command through OpenAI Dalle2 endpoint

2. /variate v2
-- supports n number of variations depending on configurations

3. /chat v3
-- chat history based persistence / threads << need to read more on it, or implement context awareness and chat history awareness

4. /settings

--- Build it out robustly to a degree where I can have it as a customer facing interface / product.







Current dev priorities;
ADD A FEW MORE FEATURES

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




# instantiate the app
app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN') # for prod and staging environments it means this would be different
OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY', 'YourAPIKey_BACKUP') # again, same environment variable, different api keys accessed
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'
ROOT_URL = os.environ.get('ROOT_URL')
WEBHOOK_URL_PATH = '/webhook'  # This path should match the path component of WEBHOOK_URL
WEBHOOK_URL = (ROOT_URL + WEBHOOK_URL_PATH)
DYNO_NAME = os.environ.get('DYNO', 'unknown-dyno')

# instantiate the bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)




# create logging objects
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
print(f"Logging started with {LOG_LEVEL}")
logging.basicConfig(stream=sys.stdout, level=getattr(logging, LOG_LEVEL, logging.INFO), format='%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(message)s')
# logger = helper_classes.CustomLoggerAdapter(logging.getLogger(__name__), {'dyno_name': DYNO_NAME}) # < creates an custom logger adapter
logger = logging.getLogger(__name__)



##############################################
############### DATABASE SETUP ###############
##############################################

# Setup the connection pool
DATABASE_URL = os.environ.get('DATABASE_URL')
connection_pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=10, dsn=DATABASE_URL)


# Define and create the necessary tables if they are not already created
def create_table(table_name):
    # Ensure table_name is a safe string to prevent SQL injection
    # This is a simplified example. In production, use more robust validation or whitelisting.
    if table_name not in ["chat_configs"]:
        raise ValueError("Invalid table name")

    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    chat_id BIGINT PRIMARY KEY,
                    config JSONB
                );
            """)
            conn.commit()
    finally:
        connection_pool.putconn(conn)


# Define Database Utility function (getting connection and putting down the connection)
def get_or_create_chat_config(chat_id):
    """
    def get_or_create_chat_config(chat_id): takes a chat_id and returns a config as Python Dict. If no config is found then we write a new default config.
    """
    conn = connection_pool.getconn()
    print(f"default config is {type(default_config)}")


    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT config FROM chat_configs WHERE chat_id = %s;", (chat_id,))
            config_row = cursor.fetchone()
            if config_row is None:
                # default config is imported as a python dict of a Default Config from templates.py; from templates import default_config at the top of the app.
                cursor.execute("INSERT INTO chat_configs (chat_id, config) VALUES (%s, %s) RETURNING config;", (chat_id, json.dumps(default_config)))
                conn.commit()
                config = default_config
                print(f"config default is {type(config)}")
            else:
                if isinstance(config_row[0], str):
                    config = json.loads(config_row[0])  # Deserialize if it's a string
                else:
                    config = config_row[0]  # Use directly if it's already a dictionary
            return config
    except Exception as e:
        tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
        logger.error(f"Database error: {e} \n\n {tb_str}")
        raise
    finally:
        connection_pool.putconn(conn)


# Create the table
create_table("chat_configs")


# Set up the shutdown handler
def shutdown_handler(signum, frame):
    # Close database connection pool
    connection_pool.closeall()
    sys.exit(0)

# Register the signal handler for graceful shutdown
signal.signal(signal.SIGTERM, shutdown_handler)



##############################################
##############################################
##############################################








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
    try:
        chat_config = get_or_create_chat_config(message.chat.id)
        bot.reply_to(message, helper_functions.start_menu())
        bot.reply_to(message, chat_config)
        logger.info(helper_functions.construct_logs(message, "Success: command successfully executed"))
    except Exception as e:
        bot.reply_to(message, "/start command request could not be completed, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {e}"))


# text handlers
@bot.message_handler(commands=['chat'])
def handle_chat(message):
    context = ""
    try:
        if message.reply_to_message:
            context = message.reply_to_message.text
        response_text = ai_commands.chat_completion(message, context, model='gpt-4')
        bot.reply_to(message, text=response_text, parse_mode='Markdown')
        logger.info(helper_functions.construct_logs(message, "Success"))
    except Exception as e:
        bot.reply_to(message, "/chat command request could not be completed, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {e}"))


@bot.message_handler(commands=['t1'])
def handle_translate_1(message):
    try:
        response_text = ai_commands.translate(message, target_language='eng',model='gpt-4')
        bot.reply_to(message, text=response_text, parse_mode='Markdown')
        logger.info(helper_functions.construct_logs(message, "Success"))
    except Exception as e:
        bot.reply_to(message, "/translate command request could not be completed, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {e}"))


@bot.message_handler(commands=['t2'])
def handle_translate_2(message):
    try:
        response_text = ai_commands.translate(message, target_language='kor',model='gpt-4')
        bot.reply_to(message, text=response_text, parse_mode='Markdown')
        logger.info(helper_functions.construct_logs(message, "Success"))
    except Exception as e:
        bot.reply_to(message, "/translate command request could not be completed, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {e}"))

    
@bot.message_handler(commands=['t3'])
def handle_translate_3(message):
    try:
        response_text = ai_commands.translate(message, target_language='chi',model='gpt-4')
        bot.reply_to(message, text=response_text, parse_mode='Markdown')
        logger.info(helper_functions.construct_logs(message, "Success"))
    except Exception as e:
        bot.reply_to(message, "/translate command request could not be completed, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {e}"))





# voice based handlers
@bot.message_handler(commands=['tts'])
def handle_tts(message):
    try:
        tts_response = ai_commands.text_to_speech(message)
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
            
            stt_response = ai_commands.speech_to_text(temp_voice_file_path) # receives a transcribed text
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





# image based handlers
@bot.message_handler(commands=['imagine'])
def handle_imagine(message):
    query = helper_functions.extract_body(message.text)
    system_context = "I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:"

    try:
        image_content = ai_commands.generate_image(message, system_context)
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
                        img_var_response = ai_commands.variate_image(message, byte_array)
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

    - <<IMG>> // Caption
    - /vision {text} (reply_to above image message)
    -- in this case, image and the {text} after /vision is used
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
                text_response = ai_commands.image_vision(message, encoded_img)
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

                    # Apply transparency to the bottom half of the mask
                    for x in range(width):
                        for y in range(height // 2, height):
                            # Get the current pixel's color
                            r, g, b, a = mask.getpixel((x, y))
                            # Set alpha to 0 (fully transparent) for the bottom half
                            mask.putpixel((x, y), (r, g, b, 0))
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_mask_file:
                        mask.save(temp_mask_file, format='PNG')
                        temp_mask_file_path = temp_mask_file.name
                        logger.debug(helper_functions.construct_logs(message, f"Debug: Mask Image generated and saved at {temp_mask_file_path}"))

                    # Convert the resized image to a BytesIO object again
                    with io.BytesIO() as byte_stream:
                        img.save(byte_stream, format='PNG')
                        byte_array = byte_stream.getvalue()
                        
                        img_edit_response = ai_commands.edit_image(message, byte_array, temp_mask_file_path)

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









# Bot configuration handlers and commands
@bot.message_handler(commands=['clear_memory'])
def handle_clear_memory(message):
    """
    handle_clear_memory(message): clears the chat history and logs saved on the vectorstore and basically resets the conversation history
    """
    pass














            
























if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))


