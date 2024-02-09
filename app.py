from flask import Flask, request, jsonify
import requests, os
import telebot
import helper_functions
import ai_commands



## Reference commands to set API keys
# heroku config:set TELEGRAM_TOKEN=6355794369:AAHnqUS6p8K4xVFkryZFmmmpF4LBG-gzyv4 --app telebot-prod
# heroku config:set OPENAI_API_KEY=sk-ABCDEFYOURAPIKEYHERE --app telebot-prod


"""
Use this bot as a test environment for building out whatever features that you want to build out;
To its maximum, it doesn't matter if it breaks, it can be rolled back as well.
Its a playground; its also pretty exciting to just like build bigger and bigger projects with more and more features.
Eventually, it would be really cool and amazing to write a full fledged AI assistant that can really help automate MANY parts of my life.


>>>> tts bugfix



To do lists:
# Completed
- Secure environment variables <- done
- Different chat request sorters that sort through chat requests and call different commands and responses to the texts. <-
- Integration with basic ChatGPT using langchain
- Dall-E 3 Image generation commands with optional image inputand sending --> need to update the send message function as well.
-- v1 it will send just the URL link, but the next version it w ill save and delete.
----- done above -----

# GPT features
- Text to Speech
- Vision
- Speech to Text
- Translate
- RAG using threads / Assistant integration, or Chroma vectorstore to introduce persistence in context / chat history.
- Fine tuning the model for different use cases
- AI Committee? Eventually I suppose

# Bot Features
- /start
- Buttons
- Configurations and safety checking best practices using Postgres, key management etc..
- Google calendar API << I can connect it to onenote, to zapier for waaaaaaaaaaaaay more things
- premium subscriptions

# Development
- Port over and fork it for family usage version
- Local testing environments + CI/CD devops stuff so I can test apps locally in Dev environment, test things in test builds, and then deploy to production.
"""


app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN') # for prod and staging environments it means this would be different
OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY', 'YourAPIKey_BACKUP') # this can be the same
API_TOKEN = TELEGRAM_TOKEN
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'
WEBHOOK_URL = 'https://telebot-prod-2f34e594e894.herokuapp.com/webhook'
WEBHOOK_URL_PATH = '/webhook'  # This path should match the path component of WEBHOOK_URL

bot = telebot.TeleBot(API_TOKEN)
# bot.remove_webhook()  # Remove previous webhook if any 
# bot.set_webhook(url=WEBHOOK_URL) # <- essentially does the same thing as below, but using telebot bot method.
# https://api.telegram.org/botYOUR_TELEGRAM_TOKEN/setWebhook?url=https://your-app-name.herokuapp.com/webhook
# https://api.telegram.org/bot6355794369:AAHnqUS6p8K4xVFkryZFmmmpF4LBG-gzyv4/setWebhook?url=https://telebot-test-59f8f075f509.herokuapp.com/webhook
# curl --http1.1 -F "url=https://telebot-prod-2f34e594e894.herokuapp.com/webhook" https://api.telegram.org/bot6355794369:AAHnqUS6p8K4xVFkryZFmmmpF4LBG-gzyv4/setWebhook <<< this was the hard reset




app = Flask(__name__)

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
    query = helper_functions.extract_body(message.text)
    response_text = ai_commands.chat_completion(query, model='gpt-4')
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
    # logging to terminal / parsing data
    query = helper_functions.extract_body(message.text)
    print(query)

    # generating the speech response and sending it
    tts_file_path = ai_commands.text_to_speech(message)

    if os.path.exists(tts_file_path):
        with open(tts_file_path, 'rb') as audio:
            print("Successfully sent audio message")
            bot.send_voice(message.chat.id, audio)
    else:
        print("filepath does not exist.")
        bot.reply_to(message, "Failed to fetch or generate speech.")
    
    helper_functions.delete_temp(tts_file_path)
    











# @bot.message_handler(func=lambda message: True)
# def echo_message(message):
#     bot.reply_to(message, message.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))







"""                                                                                                                       
# running the app
if __name__ == '__main__':
    app.run()
"""



















## Deployment: directories and webhooks ##

# @app.route('/') # root directory
# def hello_world():
#     return 'Hello, World!'
# # https://telebot-test-59f8f075f509.herokuapp.com/

# @app.route('/goodbye_world')
# def goodbye_world():
#     return 'Goodbye, World!'
# # https://telebot-test-59f8f075f509.herokuapp.com/goodbye_world


# @app.route('/webhook', methods=['POST'])
# def webhook():
#     """
#     Webhook request handling, this is kept pretty simple and the various handling and functions are contained in separate functions
#     """
#     #  This line defines a route in your Flask application at the endpoint /webhook. 
#     #  It's set to only accept POST requests, which is the method typically used by webhooks to send data to your server. 
#     #  In this context, Telegram sends updates to this endpoint whenever there's a new message for your bot.

#     update = request.get_json() #  This line retrieves the JSON data sent by Telegram to your webhook. 
#     # This data (update) contains information about the incoming message, such as the sender's chat ID and the message text.

#     chat_id = update['message']['chat']['id']
#     # chat_id = update['message']['chat']['id']: Extracts the chat ID from the incoming update. 
#     # The chat ID is used to send replies back to the correct Telegram chat.


#     # handle the message type coming in;
#     if 'text' in update['message']: # if it has text / is text.
#         text = update['message']['text']

#         command_text = text.split(' ')[0] # e.g. (/chat What is your name?) -> /chat
#         if check_command(command_text): # check if the command exists in the supported commands map
#             payload_requirements = commands.commands_map[command_text]['payload_req']

#             if check_payload_req(update['message'], payload_requirements):
#                 # execute the function to construct and send response payload
#                 response_object = commands.commands_map[command_text]['function'](update['message'])
#                 send_message(chat_id, response_object['response_text'])

#             else:
#                     print("Payload requirements not met")
            
#         else:
#             print(f"Command {command_text} does not exist!")
    
#     else:
#         print("Received a non-text message")
    

#     return 'Webhook received!', 200 # generally good practice to return normal response

    

"""
When deploying webhooks in production, consider security best practices such as
validating incoming requests, using HTTPS, and possibly implementing authentication 
or verification mechanisms to ensure that incoming data is from trusted sources.

Setting Webhooks:
# https://api.telegram.org/botYOUR_TELEGRAM_TOKEN/setWebhook?url=https://your-app-name.herokuapp.com/webhook
# https://api.telegram.org/bot6355794369:AAHnqUS6p8K4xVFkryZFmmmpF4LBG-gzyv4/setWebhook?url=https://telebot-prod-2f34e594e894.herokuapp.com/webhook
# ^ this worked, 
# {"ok":true,"result":true,"description":"Webhook was set"}

Getting info
# https://api.telegram.org/bot6355794369:AAHnqUS6p8K4xVFkryZFmmmpF4LBG-gzyv4/getWebhookInfo
# https://api.telegram.org/bot6355794369:AAHnqUS6p8K4xVFkryZFmmmpF4LBG-gzyv4/getWebhookInfo


# test 
# curl -X POST https://telebot-test-59f8f075f509.herokuapp.com/webhook -H "Content-Type: application/json" -d '{"key":"value"}'
# Webhook received!%          
"""


### Message and Command handling logic ###


# def check_command(command_text):
#     """
#     def check_command(text): This function checks for whether the command within the text is a valid command contained within the commands folder. 
#     If the command is found and has valid prefix, returns True.
#     If the command is not found in the command mapping, returns False.
#     """
#     valid_commands = commands.commands_map.keys()
#     return command_text in valid_commands # returns True if command_text exists within valid commands
    


# def check_payload_req(message, payload_req):
#     """
#     def check_payload_req(payload_requirements, message): This function checks whether the payload requirements passed are all within the message object.
#     It iterates through payload_req which is a list of payload requirements for a given function.
#     """
#     # if the payload requirement is an empty list, then return True because there is no addl requirement that needs to be met
#     if payload_req == []:
#         return True
    
#     for payload in payload_req:
#         # if any of the payloads are not in, we return False.
#         if payload not in message:
#             return False
        
#     # if we iterated through all, we pass and return True as well.
#     return True






# def send_message(chat_id, text):
#     """
#     def send_message(chat_id, text): This function defines how to send a message back to the user. 
#     It takes two parameters: chat_id (to know where to send the message) and text (the content of the message to send).
#     """

#     url = TELEGRAM_API_URL + 'sendMessage'
#     # url = TELEGRAM_API_URL + 'sendMessage': Constructs the API request URL for sending a message through the Telegram Bot API. 
#     # TELEGRAM_API_URL should be the base URL for the Telegram API, including your bot's token.

#     payload = {'chat_id': chat_id, 'text': text}
#     # payload = {'chat_id': chat_id, 'text': text}: Prepares the data to be sent in the API request. 
#     # This includes the chat_id to reply to and the text of the message you want to send.

#     requests.post(url, json=payload)
#     # requests.post(url, json=payload): Sends a POST request to the Telegram API with the constructed URL and payload. 
#     # This request tells Telegram to send your message to the specified chat.






