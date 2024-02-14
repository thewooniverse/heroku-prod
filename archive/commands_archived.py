

# ## import modules ##
# # commands dict / mapping at the bottom of the folder
# import ai_commands




# ## define functions ##
# # Function Schema - each function takes a message object(dict), and returns a dictionary as a response

# def hello_world(message):
#     """
#     def hello_world(message): test function
#     """
#     return {"response_text": "Hello, World!"}


# def hello_bro(message):
#     user_info = message['from']
#     username = user_info.get('username', None)  # Using .get() is safer in case 'username' key doesn't exist
#     return {"response_text": f"Whats up my G {username}"}

# def mock(message):
#     body_text = " "
#     text = message['text']

#     if len(text.split(' ')) > 1:
#         body_text = ' '.join(text.split(' ')[1:])
    
#     user_info = message['from']
#     username = user_info.get('username', None)  # Using .get() is safer in case 'username' key doesn't exist
#     return {"response_text": f"{username} said \"{body_text}\" - LOL what a loser"}






# ## command/function dictionary / mapping ##
# # payload requirements only looks at REQUIRED  


# commands_map = {

#     # test commands
#     '/hello_world': {"function": hello_world, "payload_req": ['text']},
#     '/hello_bro': {"function": hello_bro, "payload_req": ['text']},
#     '/mock': {"function": mock, "payload_req": ['text']},

#     # AI commands
#     # '/vision': {"function": ai_commands.vision_agent, "payload_req": ['text', 'photo']},
#     '/depict': {"function": ai_commands.generate_image, "payload_req": ['text']},
#     '/chat': {'function': ai_commands.chat_agent, 'payload_req': ['text']}

#     # config commands

#     }








# OTHER ARCHIRVED




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


## Reference commands to set API keys
# heroku config:set TELEGRAM_TOKEN=6355794369:AAHnqUS6p8K4xVFkryZFmmmpF4LBG-gzyv4 --app telebot-prod
# heroku config:set OPENAI_API_KEY=sk-ABCDEFYOURAPIKEYHERE --app telebot-prod









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
