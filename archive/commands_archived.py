# # Configure the SQLAlchemy part of the app instance
# DATABASE_URL = os.environ['DATABASE_URL']

# conn = psycopg2.connect(DATABASE_URL, sslmode='require')
# # Create a connection pool
# connection_pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=10, 
#                                                       dsn="dbname=yourdbname user=youruser password=yourpassword host=yourhost")

# # Get a connection from the pool
# conn = connection_pool.getconn()

# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)  # Fix for postgres:// scheme
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # Create the SQLAlchemy db instance
# db = SQLAlchemy(app)








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








# @bot.message_handler(commands=['edit'])
# def handle_edit(message):
#     # base condition is that we are replying to an image with the /edit command with some query / requests, with an optional mask image.
#     if message.reply_to_message and message.reply_to_message.content_type == 'photo':
#         print("Original Image file received")

#         # Create the temporary mask image
#         width, height = 1024, 1024
#         mask = Image.new("RGBA", (width,height), (0,0,0,1)) # create an opaque mask image mask

#         # short script to set bottom half to be transparent
#         for x in range(width):
#             for y in range(height //2, height): # only loop over the bottom half of the mask
#                 # set alpha (A) to zero to turn pixel transparent
#                 alpha = 0
#                 mask.putpixel((x, y), (0,0,0,alpha))
#                 # this results in the folllwing
#                 # 1 1 1 1
#                 # 1 1 1 1
#                 # 0 0 0 0
#                 # 0 0 0 0

#         with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_mask_file:
#             mask.save(temp_mask_file, format='PNG')
#             temp_mask_file_path = temp_mask_file.name
    
#         # get the original message and the image contained in it
#         original_message = message.reply_to_message
#         original_image = original_message.photo[-1]
#         original_image_file_info = bot.get_file(original_image.file_id)

#         # try and get the original image and process it as a PNG file
#         try:
#             # tryt to download the original image and process it as a PNG file
#             downloaded_original_img = bot.download_file(original_image_file_info.file_path)
#             print("Original Image downloaded")

#             with io.BytesIO(downloaded_original_img) as image_stream:
#                 # Open the image using Pillow with another 'with' block
#                 with Image.open(image_stream).convert('RGBA') as img:
#                     img = img.resize((width, height)) # resize to standard image, same as the mask image

#                     # Convert the resized image to a BytesIO object again
#                     with io.BytesIO() as byte_stream:
#                         img.save(byte_stream, format='PNG')
#                         byte_array = byte_stream.getvalue()

#                         # try processing the image through the openAI edit function
#                         print("Image processing: no mask")
#                         img_edit_response = ai_commands.edit_image(message, byte_array, temp_mask_file_path)

#                         if img_edit_response:
#                             print("Edited image generated")
#                             bot.send_photo(message.chat.id, photo=img_edit_response)
#                         else:
#                             print("Edited image with just the original image could not be generated")
#                             bot.reply_to(message, "Could not generate image")
                            
#         # if the image could not be converted, then we print the error and return the handler and exit early
#         except Exception as e:
#             if isinstance(e, IOError):
#                 print("Error: error occured during file operations")
#             elif isinstance(e, PIL.UnidentifiedImageError):
#                 print("Error: error occured during Image Conversion to PNG")
#             else:
#                 print(f"Error: unidentified error, please check logs. Details {str(e)}")
#             return
        
#         finally:
#             os.remove(temp_mask_file_path)

#     # if the base condition is not met where the reply message is not an image; then we exit the function early
#     else:
#         print("Original Message does not include an image")
#         bot.reply_to(message, "Original Message does not include an image")
        



# @bot.message_handler(commands=['edit_img'])
# def handle_edit(message):
#     # base condition is that we are replying to an image with the /edit command with some query / requests, with an optional mask image.
#     if message.reply_to_message and message.reply_to_message.content_type == 'photo':
#         print("Original Image file received")

#         # Create the temporary mask image
#         width, height = 1024, 1024
#         mask = Image.new("RGBA", (width,height), (0,0,0,1)) # create an opaque mask image mask

#         # short script to set bottom half to be transparent
#         for x in range(width):
#             for y in range(height //2, height): # only loop over the bottom half of the mask
#                 # set alpha (A) to zero to turn pixel transparent
#                 alpha = 0
#                 mask.putpixel((x, y), (0,0,0,alpha))
#                 # this results in the folllwing
#                 # 1 1 1 1
#                 # 1 1 1 1
#                 # 0 0 0 0
#                 # 0 0 0 0

#         with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_mask_file:
#             mask.save(temp_mask_file, format='PNG')
#             temp_mask_file_path = temp_mask_file.name
    
#         # get the original message and the image contained in it
#         original_message = message.reply_to_message
#         original_image = original_message.photo[-1]
#         original_image_file_info = bot.get_file(original_image.file_id)

#         # try and get the original image and process it as a PNG file
#         try:
#             # tryt to download the original image and process it as a PNG file
#             downloaded_original_img = bot.download_file(original_image_file_info.file_path)
#             print("Original Image downloaded")

#             with io.BytesIO(downloaded_original_img) as image_stream:
#                 # Open the image using Pillow with another 'with' block
#                 with Image.open(image_stream).convert('RGBA') as img:
#                     img = img.resize((width, height)) # resize to standard image, same as the mask image

#                     # Convert the resized image to a BytesIO object again
#                     with io.BytesIO() as byte_stream:
#                         img.save(byte_stream, format='PNG')
#                         byte_array = byte_stream.getvalue()

#                         # try processing the image through the openAI edit function
#                         print("Image processing: no mask")
#                         img_edit_response = ai_commands.edit_image(message, byte_array, temp_mask_file_path)

#                         if img_edit_response:
#                             print("Edited image generated")
#                             bot.send_photo(message.chat.id, photo=img_edit_response)
#                         else:
#                             print("Edited image with just the original image could not be generated")
#                             bot.reply_to(message, "Could not generate image")
                            
#         # if the image could not be converted, then we print the error and return the handler and exit early
#         except Exception as e:
#             if isinstance(e, IOError):
#                 print("Error: error occured during file operations")
#             elif isinstance(e, PIL.UnidentifiedImageError):
#                 print("Error: error occured during Image Conversion to PNG")
#             else:
#                 print(f"Error: unidentified error, please check logs. Details {str(e)}")
#             return
        
#         finally:
#             os.remove(temp_mask_file_path)

#     # if the base condition is not met where the reply message is not an image; then we exit the function early
#     else:
#         print("Original Message does not include an image")
#         bot.reply_to(message, "Original Message does not include an image")
