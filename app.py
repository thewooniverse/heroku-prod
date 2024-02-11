from flask import Flask, request, jsonify
import requests, os
import telebot
import helper_functions
import ai_commands



"""
Use this bot as a test environment for building out whatever features that you want to build out;
To its maximum, it doesn't matter if it breaks, it can be rolled back as well.
Its a playground; its also pretty exciting to just like build bigger and bigger projects with more and more features.
Eventually, it would be really cool and amazing to write a full fledged AI assistant that can really help automate MANY parts of my life.

To do lists:
# Completed
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
----- done above -----

# GPT features

Current dev priorities;
- speech to text and various sorts of it; 
-- Speech to Text (speech to text) <- need to do reply to
-- Speech to Chat (transcribe and then chat) <- basically spt and then calling the /chat function

- stt bugfix
- imagine bugfix
- logging
- setwebhook coded into the app sourcecode.






- RAG using threads / Assistant integration, or Chroma vectorstore to introduce persistence in context / chat history.
- Fine tuning the model for different use cases
- AI Committee? Eventually I suppose

# Bot Features
- /start <- really just about writing functions;
- /configs <- print out all the settings / configurations
- Buttons 
- Configurations and safety checking best practices using Postgres, key management etc..
- Google calendar API << I can connect it to onenote, to zapier for waaaaaaaaaaaaay more things
- premium subscriptions, ability to make different types of requests;

# Development
- Port over and fork it for family usage version
- Local testing environments + CI/CD devops stuff so I can test apps locally in Dev environment, test things in test builds, and then deploy to production.



# setting up the webhook for prod and staging
# curl --http1.1 -F "url=https://telebot-prod-2f34e594e894.herokuapp.com/webhook" https://api.telegram.org/bot6355794369:AAHnqUS6p8K4xVFkryZFmmmpF4LBG-gzyv4/setWebhook
# curl --http1.1 -F "url=https://telebot-staging-cf8f61dc178a.herokuapp.com/webhook" https://api.telegram.org/bot6734553403:AAF60yWJI_aFjn4A47hDKnmKv-7FSrRH-lQ/setWebhook <<< this was the hard reset
"""





app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN') # for prod and staging environments it means this would be different
OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY', 'YourAPIKey_BACKUP') # again, same environment variable, different api keys accessed
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'
WEBHOOK_URL_PATH = '/webhook'  # This path should match the path component of WEBHOOK_URL
WEBHOOK_URL = os.environ.get('ROOT_URL' + WEBHOOK_URL_PATH)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def set_telegram_webhook():
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={WEBHOOK_URL}'
    response = requests.get(url)
    if response.status_code == 200 and response.json().get('ok'):
        print("Webhook set successfully")
    else:
        print("Failed to set webhook")        

@app.before_first_request
def initialize_bot():
    set_telegram_webhook()



# Flask routes and other configurations follow...









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


@bot.message_handler(commands=['imagine'])
def handle_imagine(message):
    query = helper_functions.extract_body(message.text)
    system_context = "I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:"
    print(query)
    image_content = ai_commands.generate_image(query)
    if image_content:
        bot.send_photo(message.chat.id, photo=image_content)
    else:
        bot.reply_to(message, "Failed to fetch or generate image")
    # bot.reply_to(message, response_text)


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
    if message.reply_to_message:
        original_message = message.reply_to_message
        # check that it is a voice note
        if original_message.content_type == 'voice':
            # access the voice note and file_id
            voice_note = message.reply_to_message.voice
            voice_file_id = voice_note.file_id

            # download the voice note
            voice_file_info = bot.get_file(voice_file_id) # these need to be handled here.
            downloaded_voice = bot.download_file(voice_file_info.file_path)

            # send it to OpenAI for speech to text
            stt_response = ai_commands.speech_to_text(downloaded_voice)
            bot.reply_to(original_message, stt_response)
        
        else:
            print("The target message is not a voice file")
            bot.reply_to(message, "The target message is not a voice file")
    
    else:
        print("No target message")
        bot.reply_to(message, "Please reply to a voice note")















if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))



















