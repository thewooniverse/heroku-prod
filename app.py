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

# state management
import redis

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
0. OpenAI API key format checker reset;
1. Go through settigs, strings etc... tidy that up, and get a function to change the settings.py name import to conversation strings.
2. Suggestions for commands, pre-completion options

So pretty much its:

redis for persistent bot states across restarts that admin can turn on and off;
+ wrapper function for all command handlers to check whether the command is good to go;
++ wrapper wrapper function to check all other checks like is_bot, reply etc...
>>>> additional wrapper checkers for isadmin, isowner, isuser
>>>> Write decorator for isadmin checker, isowner is not needed as owner can run any function at any time, always.
>>>> Then also write ban function for admin;

Admin / Owner Features:
1. Owner can add new admins or remove admins, and has all the permissions that an admin does. <<- done
6. Owners can give users premium access <<- done
2. Admins can turn the bot on and off (accepting or not accepting features) <<- this needs to have redis and caching in there. <<- done
4. Admins can ban users


--> reset user context, reset group context (per user);
--> then using the contexts properly in the prompts in ai_commands and passing it as variables in calling it
--> Then, also formatting; <- HTML / Markdown V2 etc.. or plaintext.

1. Chat troubleshooting and logging
chat formatting issues resolved;
clear context.
clear chat context.

--
Free trial credit spec:
- Implemented initially without redis (we will implement batch processing and in-memory storage eventually to scale), simply using user_configs as its already necessary. <-- done
- Add system level OpenAI API key for default usage (create a new key, and set limitations) <-- done


>> FREE TRIAL CREDITS <<
- chat implementation
-- in the chat response message it will contain that this will run out.
Then implement free trial credits for user_config schemas, adding or subtracting from it.
2. Implementation of free trial credits and system level API keys -> I think I can afford; also reject any requests with too many tokens. <<- this is important for trials;
2. a. What this entails is implementing it in /chat first and then implementing it for imagine and other requests;

5. Admins can add more "free trial" credits for users; free trial credits need to be updated for users and checked / subtracted.
5.5. All users have a "free trial" state where they can query commands using the default key --> I need to ask GPT here how to change code in multiple places, tedious.
---> this means, that per request if the thing is not set -> then a default chat request is sent.
--------> it feels like an overhaul in general of the chatting request is required; to handle errors more effectively, as well as to accommodate logic for free trial credits.
I need to specify exactly what users can do on a free trial credit before implementing this logic.


--> user calls chat;
--> if there is no API key, then check whether they have free trial credits remaining;
--> if there is an API key, then try using the key, if the api key returns failed response / wrong key -> use the trial credit key.
--> if no trial credit key left, then we handle it in another way;
--> all functionality should be nested within.


1. Decorator / Wrapper function for API key checking;
2. Implementation for all /chat and other requests

2. Presets / audio agent types in chat settings;
- create the buttons
- change config
- integrate into speechto commands
-- fix stc requests

1. Button settings for turning on speech to speech for premium users
2. Setting agent voice
- develop stsc command handling for targeted requests for proof of concept and to use the codebase later on;
- include context
- /set_assistant_name: manually setting the name of the voice assistant 

1. Refactoring speech to speech configurations. - turning the speech to speech chat functionality on or off in group_settings? <- this should be in group settings tbqh; refactor.
^ deprecated because I don't think it should be in group settings actually.

2. Develop the STS feature
2.a. Detect all speech, if the user is premium and they have it turned on in the group, then process the thing.
2.b. Convert all the incoming requests into stt
2.c. Check the first 5 characters of the string to see whether there is a match for the given name;
2.d. call for the request in text, convert the response into voice note and reply;

FIX PERSISTENCE <<<<<<

Speech to Chat Development timeline:
2.e. implement context awareness / chat history involvement (probably want to abstract this out as a function as well)
3. Brings me to fixing how contexts and history works in general need to be imrpoved
3.a. Fix contexts and how they are stored and used <- done
3.b. Fix and abstract out how chat history is handled and used: construct chat history, and save chat history

1. Reconfigure free trial credits and credit checks to be stored in the system config instead of user settings (this is crucial for not letting users reset)


>> SCALABILITY REFACTORING - Redis and caching for configurations: <<
--- Caching Implementation V2 ---
What will be cached?
- All configurations (system config, chat configs and user configs)

0. Connection / Load Policies:
- Connection pooling introduced and used (this needs to be used in both database and redis in-memory access)

1. On Reads:
- Read-Through Caching: Optionally, you can implement a more automated form of caching where your caching layer 
  directly handles fetching from the database if the data is not available in the cache.

2. On Writes / Updates:
- Write-Through Strategy: When updates or new data are written, they should be written to both the database and the cache simultaneously to keep them in sync.

3. Cache Invalidation strategy for updating and invalidating old cache
- Use explicit invalidation for scenarios where data must be accurate immediately after updates, such as user permissions or critical configuration changes.
- Use TTL for general cache expiration to handle data that is not ultra-sensitive to being slightly outdated. 
  This reduces the frequency of database accesses and simplifies cache management.

4. Fallback Policies << this is implemented already
- Handling Cache Failures: Ensure that your system can gracefully handle failures of the caching layer by falling back to database reads.
- Consistency: Consider eventual consistency issues where the cache might temporarily hold outdated data. 
  Ensure that your application's functionality can tolerate this.

5. Cache Eviction Policies
- LRU (Least Recently Used): Evict data that hasn't been accessed for the longest time first.
- Size-based Eviction: If you are limited by memory, you might choose to evict larger items first or simply evict items to maintain a certain cache size.

Refactoring the read_or_create configs:
- Current config get_or_create (they are the same for all, and creates a new config in db before retrieving if it doesn't exist)
-> Picks up db connection
-> Checks DB if config exist in table, creates one if not
-> then returns it for usage
-> put down db connection

This needs to be changed to:
-> pick up redis connection
-> check the config is in redis
-> if it is not in redis, check the database, pick up db connection
-> if it is not in database, create the entry for the config in the relevant table (system, user or chat)
-> put down db connection
-> write this new config into the redis in-memory configs
-> put down the redis connection
-> returns the config for usage

Refactoring updates / writes to the config:
-> pick up db connection
-> write new config
-> put down connection

This needs to be:
-> pick up db and redis conn
-> update db
-> update redis
-> put down db and redis conn

-------
Next steps:
I will need to implement the refactoring as strategized above, then introduce fallback and eviction policies, and fallbacks.
1. Develop the redis connection picking up and putting down
2. Look through how it is currently being used for system configuration checks
--> think here on TTL strategies.
+++ currently, how it works is that there is a redis dict of the bot being on or off (this does not interact at all with the database)
+++ this is used by isboton checks for all commands
+++++ I think this is good overall, however, need to rethink on how it fits into the whole picture;
I think that the bot state should exist in the system config overall, and it should be handled in the same way as all of the others.

So I can first just straight up implement connection pooling, then implement the read-through and write-through functionalities.
- connection pools implemented;
- implement read-through and write-through functionalities.


So connection pooling and read through / write through seems to be implemented,
> carry out basic testing for changing / seeing how things are handled in terms of config saves and changes.
Then implement eviction / handling for crashes and regular checks

------
Bugfix completed, and connection pooling to database logic is re-handled (much less access now!)
Mostly working... now:
- Cache invalidation policy << this is good enough for now;
- Cache eviction policy << implement this;

Then pretty much refactoring for caching is complete!
heroku redis:maxmemory --app telebot-staging --policy volatile-lru

--------
++ Safe send feature (clearing syntatcical issues with markup, and retrying in plaintext, along with max word count for telegram API limits and chopping words)
1. Safe send -> check and catch formatting issues, and check and catch word / character limit in the response / divide into two if needed.

++ bug log chat and sending specific bug logging messages to a telegram thread with the owner for critical bugs
--> next up is to implement all of the functionalities of the log output handlers into all of the different chat requests;

Command Suggestions < done
Variate feature fix -> as it is is not very useful, need to do image recognition, few prompts -> generate a few image calls.

----- done above ---------- done above ---------- done above ---------- done above ---------- done above -----
=========================================================================================================
Feature Icebox:
--
1. Command suggestions + settings screen tidy up + write up the gitbook
1.a. Why its different, why its useful.

2. Redeploy to production stack / correct bot handle / features and separate the repository from staging (a single build is enough)
3. Deploy simple webpage for TS Systems

4. Ads
5. 1000 free calls for premium users
Context aware voice messages;

SECURITY:
- Admin Watchlist: create watchlist group / add it to configval, build the new feature to add people to the watchlist /watchlist [user_id]
- Rate limiting: 







---------------------------------------------------------------------------------------------------------
Current Focus:
Security features
1. Fix admin adding + removal and calling and how the list operates with checking for strings and numbers for userid
1.a. Check whether the admin feature works <- admin stuff works
1.b. 

2. Do the same for fixing banned users, watchlists etc... how that is handled








--------
1. Gitbook write up with feature examples: why its useful etc... and examples
2. Settings string reformatting.

Setting string tidy up / reformatting  <--- string is fine, but need to do in hand with gitbook. Keep messages as short as possible, messy / hard to read.

----
Develop the clear history functionality
Develop testing modules
Callback limitations
----
Check all functionality on production build with config vals
redeploy the production build with new bot name and new ownership
Link the gitbook to the website + deploy a simple app


















--- Notes V1 ---
2. Decide on the architecture and caching strategy:
2. a. What to cache, what is being used frequently (reading and writing)
2. b. When to cache from the database, Populate the cache after a database query if the data isn't already present in the cache.
2. c. Cache Invalidation: Update the cache when user configurations are updated or deleted.
3. Fallback policites (interacting with the database directly)
- I think it will be like this:
-- Get and set config should be abstracted to a functionality (it already is, thankfully)
-- This will now include some degree of redis logic;
---- Get checks whether the configuration is stored in data, if it is not it calls it and stores it in memory.
---- Set/Update calls (which should be in the param) - will have another logic flow to update both the in-memory and database with new configurations.
4. Decide on cache eviction policies
SCALABILITY IMPROVEMENT --> CONFIGS (notes first):
- Deprecate user config and chat configs totally, save everything into system configs and per user configurations that is stored within redis and updated 
every now and then.
>>>> REFACTOR CONFIGS SO THAT FREE TRIAL CREDITS WITH USER ID IS STORED IN SYSTEM CONFIG AS A TABLE (and used in-memory, while updating every now and then)
X. Overhaul on how configs are called and stored; they should be called for users and stored in redis / in-memory and functions around how to handle this
X. If it is in memory, if it is not, and handling long term database config updates / storage in shutdowns
-. Address users being able to reset their user settings, this should be stored in system config that is stored in-memory?
---> should their free trial credits be stored in system config -> redis and checked in this way, such that reading + writing is more convenient?
-------








Bug Fixes and shipping:
1. Handling chat requests and response objects that require it to search the web or a search engine.
2. Logging upgrades and tidy up of print statements
3. Baseline testing
4. Redeploy onto new Heroku environment thats NOT AB69 / Telebot; 
5. Hosting it onto a website TeleGPT.bot, new bot token etc...
--> although I can just change the endpoint to another bot API token, redploying is good practice for backend skills.


Potential future features:
- "Hey Siri" type voice message prompts enabled; you can customize and set up your own voice agent that doesn't require a command handler. This should be in setting.
- Voice agent / type options for
- Free users getting up to 10 free requests of any type;
- Then make it available / tidy everything up, and put up a marketing video that is generated using AI.

--- up to here today ---
X. Forking it into TeleGPT.bot -> host the website and making the bot public for usage; @TeleGPT_dot_bot.
Then you can drop AB69 staging, and build on the main environment, and fork it again for Wooniverse_bot that is gated;
--> Wooniverse bot will interact with my webpages etc...

That then marks the end of it;
Additional optional features:
- Context saving from pictures;
==========================================

"""




# instantiate the app
app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN') # for prod and staging environments it means this would be different
OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY', 'YourAPIKey_BACKUP') # again, same environment variable, different api keys accessed
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'
# ADMIN_USER_ID = os.environ.get('ADMIN_UID', "7032361920")
OWNER_USER_ID = os.environ.get('OWNER_UID', "7032361920")

# setting up web app and webhooks
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

# basic openAI apikey
OPENAI_FREE_KEY = os.environ.get('OPENAI_FREE_KEY', "sk-notvalid")
LOG_CHAT = os.environ.get('LOG_CHAT_ID')













# create logging objects
LOG_LEVEL = os.getenv('LOG_LEVEL', 'ERROR').upper()
print(f"Logging started with {LOG_LEVEL}")
logging.basicConfig(stream=sys.stdout, level=getattr(logging, LOG_LEVEL, logging.INFO), format='%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(message)s')
logger = logging.getLogger(__name__)
"""
logger.debug('This is a debug message')
logger.info('This is an info message')
logger.warning('This is a warning message')
logger.error('This is an error message')
logger.critical('This is a critical message')
"""



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




"""
Wrapper functions
"""
# decorator / wrapper function to check whether bot is active
def is_bot_active(func):
    def wrapper(message):
        # Check the bot state
        system_config = get_or_create_chat_config(OWNER_USER_ID, 'owner')
        if system_config['is_on']:
            return func(message)
        else:
            bot.send_message(message.chat.id, "Bot is currently turned OFF.")
    return wrapper


# decorator / wrapper function to check whether bot is active
def is_valid_user(func):
    def wrapper(message):
        system_config = get_or_create_chat_config(OWNER_USER_ID, 'owner')
        
        # Check if the sender is a bot
        if message.from_user.is_bot:
            bot.send_message(message.chat.id, "The bot is not available for other bots to use.")
            return  # Just return without calling the decorated function
        
        # Check if the user is banned
        elif message.from_user.id in system_config['banned_users']:
            bot.reply_to(message, "It appears that you are currently banned from using this bot, please contact admin.")
            return  # Just return without calling the decorated function
        
        else:
            # Call the original function if the user is valid
            return func(message)
    
    return wrapper

# decorator / wrapper function to check whether a user is an admin
def is_admin(func):
    def wrapper(message):
        system_config = get_or_create_chat_config(OWNER_USER_ID, 'owner')

        # Check if the user is listed as an admin in the system configuration
        if message.from_user.id in system_config['admins']:
            return func(message)
        else:
            # Notify the user they do not have permission if they are not an admin
            bot.send_message(message.chat.id, "You do not have permission to use this command. This command is only available to admins.")
            return None  # Explicitly return None to indicate no further action should be taken
    
    return wrapper


# develop is owner.
def is_owner(func):
    def wrapper(message):
        system_config = get_or_create_chat_config(OWNER_USER_ID, 'owner')

        # Check if the user is listed as an admin in the system configuration
        if message.from_user.id == system_config['owner_id']:
            return func(message)
        else:
            # Notify the user they do not have permission if they are not an admin
            bot.send_message(message.chat.id, "You do not have permission to use this command. This is only available to the owner of the bot.")
            return None  # Explicitly return None to indicate no further action should be taken
    
    return wrapper





def is_in_reply(func):
    def wrapper(message):
        if message.reply_to_message:
            return func(message)
        else:
            return None
    return wrapper

def escape_markdown_v2(text):
    escape_chars = '-_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)


def check_and_get_valid_apikeys(message, user_cfg, chat_cfg):
    """
    
    """
    try:
        # check for API Keys
        system_config = get_or_create_chat_config(OWNER_USER_ID, 'owner')
        api_keys = config_db_helper.get_apikey_list(user_cfg, chat_cfg)
        # print(api_keys)
        user_id = message.from_user.id
        # print(user_id)
        intkey_dict = {int(k): v for k, v in system_config['user_credit_dict'].items()}

        # if the first API key returned is a free credit (meaning the user did not set any of their own keys)
        if api_keys[0] == OPENAI_FREE_KEY:
            print(f"{user_id} is a free user without a key")
            # check whether the user is inside the system_config for a free trial credit, add a fallback value if it is not
            # convert the retrieved dictionary back into integer keys for processing
            # print("Converted to integer keys")

            if user_id not in intkey_dict:
                # print("user is not in the config!")
                intkey_dict[user_id] = 5

            # now check how much credit the user has, if its 0, it is returned out and the function is NOT called
            if intkey_dict[user_id] < 1:
                bot.reply_to(message, "OpenAI API could not be called as there is no API Key entered and the user has run out of free credits.")
                # config_db_helper.set_new_config(OWNER_USER_ID, 'owner', system_config) < a save is not necessary here
                return None
            
            # use the system config
            intkey_dict[user_id] -= 1
            bot.reply_to(message, f"Using free trial credits, remaining: {intkey_dict[user_id]}")
        
        # if it is not, then just simply return the API keys
        # convert back to string keys
        # print(intkey_dict)
        system_config['user_credit_dict'] = {str(k): v for k, v in intkey_dict.items()}
        # print(system_config['user_credit_dict'])
        config_db_helper.set_new_config(OWNER_USER_ID, 'owner', system_config)
        return api_keys
    except Exception as e:
        logger.error(helper_functions.construct_logs(message, f"Error: {e}"))












"""
Core bot functionalities;
"""

@bot.message_handler(commands=['start'])
@is_bot_active
@is_valid_user
def handle_start(message):
    try:
        # import the configs
        # previous test, to be deleted. Commented out to prevent unnecessary database connections.
        # chat_config = get_or_create_chat_config(message.chat.id, 'chat')
        # user_config = get_or_create_chat_config(message.from_user.id, 'user')
        # bot.reply_to(message, f"Chat language model: {chat_config['language_model']}, user language model: {user_config['language_model']}")
        bot.reply_to(message, settings.getting_started_string, parse_mode='HTML')
        logger.info(helper_functions.construct_logs(message, "Success: command successfully executed"))
    
    except Exception as e:
        helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
        logger.error(helper_functions.construct_logs(message, f"Error: {e}"))







# text handlers
@bot.message_handler(commands=['chat'])
@is_bot_active
@is_valid_user
def handle_chat(message):
    """
    Refactor the code to: 
    - 
    """
    context = ""

    try:
        ### Bring in configs, call and construct all of the contexts parcels ###
        user_config = get_or_create_chat_config(message.from_user.id, 'user')
        chat_config = get_or_create_chat_config(message.chat.id, 'chat')
        # system_config = get_or_create_chat_config(OWNER_USER_ID, 'owner') 
        # body_text = helper_functions.extract_body(message.text) 
        api_keys = check_and_get_valid_apikeys(message, user_cfg=user_config, chat_cfg=chat_config)
        if not api_keys:
            # no message is printed or replied here because the function above to check and get valid API keys already sends a status message
            return

        # check for both user configs (all threads) or chat configs has been set
        context = helper_functions.construct_context(user_config=user_config, chat_config=chat_config, message=message)
        # check for persistence and chat history
        chat_history = helper_functions.construct_chat_history(user_config=user_config, message=message, api_key=api_keys[0], pinecone_key=PINECONE_KEY)

        ### calling the chat completion with the relevant context and chat history provided and with the right configs for the user###
        try:
            response_text = ai_commands.chat_completion(message, context, chat_history = chat_history, openai_api_key=api_keys[0], model=chat_config['language_model'], temperature=chat_config['lm_temp'])
            helper_functions.safe_send(message, bot, response_text)
            # bot.reply_to(message, text=response_text, parse_mode="Markdown")
            logger.info(helper_functions.construct_logs(message, f"Success: response generated and sent."))
            # helper_functions.handle_error_output(bot, message, exception="Test test", notify_admin=True, notify_user=True)
        except Exception as e:
            logger.error(helper_functions.construct_logs(message, f"Error: {e}"))
            helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
        
        # logging
        helper_functions.upsert_chat_history(user_config=user_config, message=message, response_text=response_text, api_key=api_keys[0], pinecone_key=PINECONE_KEY)

    except Exception as e:
        helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
        logger.error(helper_functions.construct_logs(message, f"Error: {e}"))






@bot.message_handler(commands=['t1'])
@is_bot_active
@is_valid_user
def handle_translate_1(message):
    try:
        user_config = get_or_create_chat_config(message.from_user.id, 'user')
        chat_config = get_or_create_chat_config(message.chat.id, 'chat')
        api_keys = check_and_get_valid_apikeys(message, user_cfg=user_config, chat_cfg=chat_config)
        if not api_keys:
            return

        if api_keys:
            response_text = ai_commands.translate(message, openai_api_key=api_keys[0], target_language=chat_config['t1'], model=chat_config['language_model'])
            helper_functions.safe_send(message, bot, response_text)
            logger.info(helper_functions.construct_logs(message, "Success"))
    except Exception as e:
        helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
        logger.error(helper_functions.construct_logs(message, f"Error: {e}"))


@bot.message_handler(commands=['t2'])
@is_bot_active
@is_valid_user
def handle_translate_2(message):
    try:
        user_config = get_or_create_chat_config(message.from_user.id, 'user')
        chat_config = get_or_create_chat_config(message.chat.id, 'chat')
        api_keys = check_and_get_valid_apikeys(message, user_cfg=user_config, chat_cfg=chat_config)
        if not api_keys:
            return

        if api_keys:
            response_text = ai_commands.translate(message, openai_api_key=api_keys[0], target_language=chat_config['t2'], model=chat_config['language_model'])
            helper_functions.safe_send(message, bot, response_text)
            logger.info(helper_functions.construct_logs(message, "Success"))
        
    except Exception as e:
        helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
        logger.error(helper_functions.construct_logs(message, f"Error: {e}"))

    
@bot.message_handler(commands=['t3'])
@is_bot_active
@is_valid_user
def handle_translate_3(message):
    try:
        user_config = get_or_create_chat_config(message.from_user.id, 'user')
        chat_config = get_or_create_chat_config(message.chat.id, 'chat')
        api_keys = check_and_get_valid_apikeys(message, user_cfg=user_config, chat_cfg=chat_config)
        if not api_keys:
            return

        if api_keys:
            response_text = ai_commands.translate(message, openai_api_key=api_keys[0], target_language=chat_config['t3'], model=chat_config['language_model'])
            helper_functions.safe_send(message, bot, response_text)
            logger.info(helper_functions.construct_logs(message, "Success"))
    except Exception as e:
        helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
        logger.error(helper_functions.construct_logs(message, f"Error: {e}"))







# voice based handlers
@bot.message_handler(commands=['tts'])
@is_bot_active
@is_valid_user
def handle_tts(message):
    
    try:
        chat_config = get_or_create_chat_config(message.chat.id, 'chat')
        user_config = get_or_create_chat_config(message.from_user.id, 'user')
        api_keys = check_and_get_valid_apikeys(message, user_cfg=user_config, chat_cfg=chat_config)
        if not api_keys:
            return

        if api_keys:
            tts_response = ai_commands.text_to_speech(message, openai_api_key=api_keys[0], voice=chat_config['agent_voice'])
            if tts_response:
                logger.info(helper_functions.construct_logs(message, "Success: Audio response generated"))
                bot.send_voice(message.chat.id, tts_response)
        else:
            bot.reply_to(message, "Text received but failed to fetch or generate speech, please contact admin.")
            logger.warning(helper_functions.construct_logs(message, "Warning: tts response could not be generated")) 

    except Exception as e:
        helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
        logger.error(helper_functions.construct_logs(message, f"Error: {e}"))




@bot.message_handler(commands=['stt'])
@is_bot_active
@is_valid_user
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
            
            chat_config = get_or_create_chat_config(message.chat.id, 'chat')
            user_config = get_or_create_chat_config(message.from_user.id, 'user')
            api_keys = check_and_get_valid_apikeys(message, user_cfg=user_config, chat_cfg=chat_config)
            if not api_keys:
                return


            if api_keys:
                stt_response = ai_commands.speech_to_text(temp_voice_file_path, openai_api_key=api_keys[0]) # receives a transcribed text
                if stt_response:
                    helper_functions.safe_send(message, bot, stt_response)
                    logger.info(helper_functions.construct_logs(message, "Success: text to speech sent"))
                else:
                    bot.reply_to(message, "Could not convert speech to text")
                    logger.warning(helper_functions.construct_logs(message, "Warning: Voice note downloaded, but stt translation could not be completed"))

            # Clean up: Remove the temporary file
            os.remove(temp_voice_file_path)
        
        except Exception as e:
            helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
            bot.reply_to(message, "Failed to process the voice note, please check logs.")
        
    else:
        bot.reply_to(message, "Please reply to a voice note")
        logger.debug(helper_functions.construct_logs(message, "Debug: No target message"))





@bot.message_handler(commands=['stc'])
@is_bot_active
@is_valid_user
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
            
            api_keys = check_and_get_valid_apikeys(message, user_cfg=user_config, chat_cfg=chat_config)
            if not api_keys:
                return

            if api_keys:
                stt_response = ai_commands.speech_to_text(temp_voice_file_path, openai_api_key=api_keys[0]) # receives a transcribed text
                if stt_response:
                    
                    # send the stt response as well if the user wants to (optional?) - but for now, we keep it so that ppl can edit it if its wrong.
                    bot.reply_to(message, stt_response)
                    logger.info(helper_functions.construct_logs(message, "Success: text to speech sent"))

                    # use the stt text response to call the chat and send the response
                    # check for both user configs (all threads) or chat configs has been set
                    context = helper_functions.construct_context(user_config=user_config, chat_config=chat_config, message=message)
                    # check for persistence and chat history
                    chat_history = helper_functions.construct_chat_history(user_config=user_config, message=message, api_key=api_keys[0], pinecone_key=PINECONE_KEY)
                    response_text = ai_commands.chat_completion(stt_response, context, openai_api_key=api_keys[0], model=chat_config['language_model'], temperature=chat_config['lm_temp'], chat_history=chat_history)
                    helper_functions.upsert_chat_history(user_config=user_config, message=message, response_text=response_text, api_key=api_keys[0], pinecone_key=PINECONE_KEY)


                    helper_functions.safe_send(message, bot, response_text)
                    logger.info(helper_functions.construct_logs(message, f"Success: query response generated and sent."))
                else:
                    bot.reply_to(message, "Could not convert speech to text")
                    logger.warning(helper_functions.construct_logs(message, "Warning: Voice note downloaded, but stt translation could not be completed"))

            # Clean up: Remove the temporary file
            os.remove(temp_voice_file_path)
        
        except Exception as e:
            logger.error(helper_functions.construct_logs(message, f"Error: Error occured {e}"))
            helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
        
    else:
        bot.reply_to(message, "Please reply to a voice note")
        logger.debug(helper_functions.construct_logs(message, "Debug: No target message"))





"""
SPEECH TO SPEECH CHAT FUNCTIONALITY:
"""
@bot.message_handler(commands=['stsc'])
@is_bot_active
@is_valid_user
def handle_stsc(message):
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
            
            api_keys = check_and_get_valid_apikeys(message, user_cfg=user_config, chat_cfg=chat_config)
            if not api_keys:
                return

            if api_keys:
                stt_response = ai_commands.speech_to_text(temp_voice_file_path, openai_api_key=api_keys[0]) # receives a transcribed text
                if stt_response:
                    
                    # send the stt response as well if the user wants to (optional?) - but for now, we keep it so that ppl can edit it if its wrong.
                    bot.reply_to(message, stt_response)
                    logger.info(helper_functions.construct_logs(message, "Success: text to speech sent"))

                    # use the stt text response to call the chat and send the response
                    # import contexts:
                    context = helper_functions.construct_context(user_config=user_config, chat_config=chat_config, message=message)
                    # check for persistence and chat history
                    chat_history = helper_functions.construct_chat_history(user_config=user_config, message=message, api_key=api_keys[0], pinecone_key=PINECONE_KEY)
                    response_text = ai_commands.chat_completion(stt_response, context, openai_api_key=api_keys[0], model=chat_config['language_model'], temperature=chat_config['lm_temp'], chat_history=chat_history)
                    helper_functions.upsert_chat_history(user_config=user_config, message=message, response_text=response_text, api_key=api_keys[0], pinecone_key=PINECONE_KEY)
                    bot.reply_to(message, text=response_text)
                    logger.info(helper_functions.construct_logs(message, f"Success: query response generated and sent."))

                    # additional step to convert the chat response into a speech response
                    tts_response = ai_commands.text_to_speech(response_text, openai_api_key=api_keys[0], voice=chat_config['agent_voice'])
                    if tts_response:
                        logger.info(helper_functions.construct_logs(message, "Success: Audio response generated"))
                        bot.send_voice(message.chat.id, tts_response)

                else:
                    bot.reply_to(message, "Could not convert speech to text")
                    logger.warning(helper_functions.construct_logs(message, "Warning: Voice note downloaded, but stt translation could not be completed"))

            # Clean up: Remove the temporary file
            os.remove(temp_voice_file_path)
        
        except Exception as e:
            logger.error(helper_functions.construct_logs(message, f"Error: Error occured {e}"))
            helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
        
    else:
        bot.reply_to(message, "Please reply to a voice note")
        logger.debug(helper_functions.construct_logs(message, "Debug: No target message"))






# speech chat functionality "Hey Friend"
@bot.message_handler(content_types=['voice'])
@is_bot_active
@is_valid_user
def handle_speech_chat(message):
    # import configs
    user_config = get_or_create_chat_config(message.from_user.id, 'user')
    chat_config = get_or_create_chat_config(message.chat.id, 'chat')

    # check whether the user is a premium user AND whether they have turned both of these features
    if user_config['speech_chat'] and user_config['is_premium']:
        try:

            ### code section on downloading the original voice note ###
            voice_note = message.voice
            voice_file_info = bot.get_file(voice_note.file_id)
            downloaded_voice = bot.download_file(voice_file_info.file_path)
            logger.debug(helper_functions.construct_logs(message, "Check: voice note downloaded"))

            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_voice_file:
                temp_voice_file.write(downloaded_voice)
                temp_voice_file_path = temp_voice_file.name
            
            chat_config = get_or_create_chat_config(message.chat.id, 'chat')
            user_config = get_or_create_chat_config(message.from_user.id, 'user')
            api_keys = check_and_get_valid_apikeys(message, user_cfg=user_config, chat_cfg=chat_config)
            if not api_keys:
                bot.reply_to(message, "API key is not set!")
                return
            
            stt_response = ai_commands.speech_to_text(temp_voice_file_path, openai_api_key=api_keys[0]) # receives a transcribed text
            if stt_response:
                bot.reply_to(message, stt_response)
                logger.info(helper_functions.construct_logs(message, "Success: text to speech sent"))
            else:
                bot.reply_to(message, "Could not convert speech to text")
                logger.warning(helper_functions.construct_logs(message, "Warning: Voice note downloaded, but stt translation could not be completed"))

            ### code section on checking the downloaded voice note for the keywords ###
            agent_name = user_config["speech_assistant_name"].lower()
            # get the chunk of the first 5 words, clean them such that they do not include any special characters, and join them into a sentence
            first_five_words = " ".join([helper_functions.strip_non_alphabet_chars(item) for item in stt_response.split(" ")[0:5]]).lower()
            
            # if the agent name is not found in the sentence
            if not helper_functions.find_full_word(first_five_words, agent_name):
                return
            
            # if the agent name is found, then continue
            # bot.reply_to(message, "Agent name is found!!") # this works

            ### Section here to process the stt request into a chat completion, convert it into voice message and send this response ###
            # import contexts:
            context = helper_functions.construct_context(user_config=user_config, chat_config=chat_config, message=message)
            # check for persistence and chat history
            chat_history = helper_functions.construct_chat_history(user_config=user_config, message=message, api_key=api_keys[0], pinecone_key=PINECONE_KEY)
            # remove the agent name from the response, or give it the necessary context:
            stt_response = "Please ignore any names I am referring directly to you by as it may be incorrect and get right to the question / request at hand:\n" + stt_response

            response_text = ai_commands.chat_completion(stt_response, context, openai_api_key=api_keys[0], model=chat_config['language_model'], temperature=chat_config['lm_temp'], chat_history=chat_history)
            helper_functions.upsert_chat_history(user_config=user_config, message=message, response_text=response_text, api_key=api_keys[0], pinecone_key=PINECONE_KEY)
            bot.reply_to(message, text=response_text)
            logger.info(helper_functions.construct_logs(message, f"Success: query response generated."))

            # additional step to convert the chat response into a speech response
            tts_response = ai_commands.text_to_speech(response_text, openai_api_key=api_keys[0], voice=chat_config['agent_voice'])
            if tts_response:
                logger.info(helper_functions.construct_logs(message, "Success: Audio response generated"))
                bot.send_voice(message.chat.id, tts_response)

            else:
                bot.reply_to(message, "Could not convert text to speech")
                logger.warning(helper_functions.construct_logs(message, "Warning:"))

            # Clean up: Remove the temporary file
            os.remove(temp_voice_file_path)

        except Exception as e:
            logger.error(helper_functions.construct_logs(message, f"Error: Error occured {e}"))
            helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
    
    else:
        # no message is sent to user as it is not an explicit request or command, it is simply ignored
        return
    























# image based handlers
@bot.message_handler(commands=['imagine'])
@is_bot_active
@is_valid_user
def handle_imagine(message):
    # query = helper_functions.extract_body(message.text)
    system_context = ""

    try:
        chat_config = get_or_create_chat_config(message.chat.id, 'chat')
        user_config = get_or_create_chat_config(message.from_user.id, 'user')
        api_keys = check_and_get_valid_apikeys(message, user_cfg=user_config, chat_cfg=chat_config)
        if not api_keys:
            return


        if api_keys:
            image_content = ai_commands.generate_image(message.text, api_keys[0], system_context)
            bot.send_photo(message.chat.id, photo=image_content)
            logger.info(helper_functions.construct_logs(message, "Success: Generated and sent image to chat"))

    except Exception as e:
        helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
        logger.error(helper_functions.construct_logs(message, f"Error: Could not complete image generation, error: {e}"))





@bot.message_handler(commands=['variate'])
@is_bot_active
@is_valid_user
def handle_variate_v2(message):
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
                chat_config = get_or_create_chat_config(message.chat.id, 'chat')
                user_config = get_or_create_chat_config(message.from_user.id, 'user')
                api_keys = check_and_get_valid_apikeys(message, user_cfg=user_config, chat_cfg=chat_config)
                if not api_keys: # if there is no 
                    return
                
                # get the image description through image recognition
                image_recongition_prompt = "describe this image in detail without mentioning any copyrighted IP or characters, as close as possible to be recreated using AI."
                text_response = ai_commands.image_vision(image_recongition_prompt, encoded_img, openai_api_key=api_keys[0])

                # generate images using the text response
                context = ""
                image_content = ai_commands.generate_image(text_response, api_keys[0], "")
                bot.send_photo(message.chat.id, photo=image_content)



                # helper_functions.safe_send(message, bot, text_response) # sending of the prompt itself is disabled
                logger.info(helper_functions.construct_logs(message, f"Debug: Image successfully analyzed and response and sent"))
    
        except Exception as e:
            # handle various exceptions
            logger.error(helper_functions.construct_logs(message, f"Error: Error occured at {e}"))
            helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
        finally:
            # handle file cleanup
            os.remove(temp_img_path)
            logger.debug(helper_functions.construct_logs(message, f"Debug: Image file cleanup successful"))
    
    else:
        print("No reply message or image found")
        bot.reply_to(message, "Please reply to an image message")






# @bot.message_handler(commands=['variate'])
# @is_bot_active
# @is_valid_user
# def handle_variations(message):
#     """
#     Should eventually also support multiple n, but TBD; n shoudl be from config so after config is created I can handle this.
#     """
#     # base condition is that we are replying to an image with the /edit command with some query / requests, with an optional mask image.
#     if message.reply_to_message and message.reply_to_message.content_type == 'photo':

#         # Download & get the original message and the image contained in it
#         original_message = message.reply_to_message
#         original_image = original_message.photo[-1]
#         original_image_file_info = bot.get_file(original_image.file_id)

#         # try and get the original image and process it as a PNG file
#         try:
#             # tryt to download the original image and process it as a PNG file
#             downloaded_original_img = bot.download_file(original_image_file_info.file_path)
#             logger.debug(helper_functions.construct_logs(message, "Debug: Image successfully downloaded"))

#             with io.BytesIO(downloaded_original_img) as image_stream:
#                 # Open the image using Pillow with another 'with' block
#                 with Image.open(image_stream).convert('RGBA') as img:
#                     width, height = 1024, 1024
#                     img = img.resize((width, height)) # resize to standard image, same as the mask image
#                     logger.debug(helper_functions.construct_logs(message, "Debug: Image successfully converted and resized"))

#                     # Convert the resized image to a BytesIO object again
#                     with io.BytesIO() as byte_stream:
#                         img.save(byte_stream, format='PNG')
#                         byte_array = byte_stream.getvalue()

#                         chat_config = get_or_create_chat_config(message.chat.id, 'chat')
#                         user_config = get_or_create_chat_config(message.from_user.id, 'user')
#                         api_keys = check_and_get_valid_apikeys(message, user_cfg=user_config, chat_cfg=chat_config)
#                         if not api_keys:
#                             return
                        
#                         if api_keys:
#                             img_var_response = ai_commands.variate_image(message, byte_array, openai_api_key=api_keys[0])
#                             if img_var_response:
#                                 logger.info(helper_functions.construct_logs(message, "Info: Image variation successfully generated"))
#                                 bot.send_photo(message.chat.id, photo=img_var_response)
#                             else:
#                                 logger.warning(helper_functions.construct_logs(message, "Info: Original image received and converted, however image failed to generate"))
#                                 bot.reply_to(message, "Could not generate Variations of the image")
                            
#         # if the image could not be converted, then we print the error and return the handler and exit early
#         except Exception as e:
#             if isinstance(e, IOError):
#                 helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
#                 logger.error(helper_functions.construct_logs(message, f"Error: error occured during file operations: {e}"))
#             elif isinstance(e, PIL.UnidentifiedImageError):
#                 helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
#                 logger.error(helper_functions.construct_logs(message, f"Error: error occured during Image Conversion to PNG: {e}"))
#             else:
#                 helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
#                 logger.error(helper_functions.construct_logs(message, f"Error: unidentified error, please check logs. Details {str(e)}"))
#             return
#     # if the base condition is not met where the reply message is not an image; then we exit the function early
#     else:
#         bot.reply_to(message, "Original Message does not include an image")
#         logger.warning(helper_functions.construct_logs(message, f"Warning: Original message did not include an image"))







@bot.message_handler(commands=['vision'])
@is_bot_active
@is_valid_user
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
                chat_config = get_or_create_chat_config(message.chat.id, 'chat')
                user_config = get_or_create_chat_config(message.from_user.id, 'user')
                api_keys = check_and_get_valid_apikeys(message, user_cfg=user_config, chat_cfg=chat_config)
                if not api_keys:
                    return

                if api_keys:
                    text_response = ai_commands.image_vision(message.text, encoded_img, openai_api_key=api_keys[0])
                    helper_functions.safe_send(message, bot, text_response)
                    logger.info(helper_functions.construct_logs(message, f"Debug: Image successfully analyzed and response and sent"))
        
        except Exception as e:
            # handle various exceptions
            logger.error(helper_functions.construct_logs(message, f"Error: Error occured at {e}"))
            helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
        finally:
            # handle file cleanup
            os.remove(temp_img_path)
            logger.debug(helper_functions.construct_logs(message, f"Debug: Image file cleanup successful"))
    
    else:
        print("No reply message or image found")
        bot.reply_to(message, "Please reply to an image message")












@bot.message_handler(commands=['edit_img'])
@is_bot_active
@is_valid_user
def handle_edit(message):
    # base condition is that we are replying to an image with the /edit command with some query / requests, with an optional mask image.
    if message.reply_to_message and message.reply_to_message.content_type == 'photo':
    
        # get the original message and the image contained in it
        original_message = message.reply_to_message
        original_image = original_message.photo[-1]
        original_image_file_info = bot.get_file(original_image.file_id)

        user_config = get_or_create_chat_config(message.from_user.id, 'user')
        chat_config = get_or_create_chat_config(message.chat.id, 'chat')
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
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_mask_file:
                        mask.save(temp_mask_file, format='PNG')
                        bot.send_photo(message.chat.id, photo=mask) # test

                        temp_mask_file_path = temp_mask_file.name
                        logger.debug(helper_functions.construct_logs(message, f"Debug: Mask Image generated and saved at {temp_mask_file_path}"))

                    # Convert the resized image to a BytesIO object again
                    with io.BytesIO() as byte_stream:
                        img.save(byte_stream, format='PNG')
                        byte_array = byte_stream.getvalue()
                        api_keys = check_and_get_valid_apikeys(message, user_cfg=user_config, chat_cfg=chat_config)
                        if not api_keys:
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
                helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
                logger.error(helper_functions.construct_logs(message, f"Error: error occured during file operations: {e}"))
            elif isinstance(e, PIL.UnidentifiedImageError):
                helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
                logger.error(helper_functions.construct_logs(message, f"Error: error occured during Image Conversion to PNG: {e}"))
            else:
                helper_functions.handle_error_output(bot, message, exception=e, notify_admin=True, notify_user=True)
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
    markup.row(types.InlineKeyboardButton("🤖 Voice Assisstant", callback_data='voice_assistant_settings'))
    # markup.row(types.InlineKeyboardButton("Contexts ON", callback_data='context_awareness_on'),
        # types.InlineKeyboardButton("Contexts OFF", callback_data='context_awareness_off'))
    markup.row(types.InlineKeyboardButton("🔙 Back", callback_data='user_settings'))
    return markup

def voice_assistant_settings_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🟢 Voice Activation ON", callback_data='voice_activation_on'),
               types.InlineKeyboardButton("🔴 Voice Activation OFF", callback_data='voice_activation_off'))
    markup.row(types.InlineKeyboardButton("🔙 Back", callback_data='premium_user_settings'))
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
    markup.row(types.InlineKeyboardButton("🎤 Agent Voice", callback_data='agent_voice_menu'))
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


# define the agent's voice presets
def agent_voice_settings_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🧑🏻 Alloy", callback_data='voiceset_alloy'), types.InlineKeyboardButton("👨🏻 Echo", callback_data='voiceset_echo'))
    markup.row(types.InlineKeyboardButton("💂 Fable", callback_data='voiceset_fable'), types.InlineKeyboardButton("🕵🏾‍♂️ Onyx", callback_data='voiceset_onyx'))
    markup.row(types.InlineKeyboardButton("👩🏻 Nova", callback_data='voiceset_nova'), types.InlineKeyboardButton("👩‍⚖️ Shimmer", callback_data='voiceset_shimmer'))
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
@is_bot_active
@is_valid_user
def handle_settings(message):
    bot.send_message(chat_id=message.chat.id, text=settings.settings_string, parse_mode="HTML")



@bot.message_handler(commands=['group_settings'])
@is_bot_active
@is_valid_user
def handle_group_settings(message):
    bot.send_message(chat_id=message.chat.id, text=settings.group_settings_string, reply_markup=group_settings_markup(), parse_mode="HTML")

@bot.message_handler(commands=['user_settings'])
@is_bot_active
@is_valid_user
def handle_user_settings(message):
    if message.chat.type != 'private':
        bot.reply_to(message, "You cannot change user specific settings in a group, you can only do it in private DM sessions.", parse_mode="HTML")
        return
    else:
        bot.send_message(chat_id=message.chat.id, text=settings.user_settings_string, reply_markup=user_settings_markup(), parse_mode="HTML")


@bot.message_handler(commands=['reset_user_settings'])
@is_bot_active
@is_valid_user
def handle_user_settings_reset(message):
    """
    Resets user settings
    """
    
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
        # print(premium_user_image_mask)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=settings.premium_image_mask_settings_string, reply_markup=premium_image_mask_options_menu(premium_user_image_mask), parse_mode="HTML")
    
    elif call.data[0:4] == "pim_":
        # get the image settings
        user_config = get_or_create_chat_config(call.from_user.id, 'user')
        premium_user_image_mask = user_config['premium_image_mask_map']
        # print(premium_user_image_mask)

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





    elif call.data == "voice_assistant_settings":
        user_config = get_or_create_chat_config(call.from_user.id, 'user')
        current_status = f"\n\nVoice Activation: {user_config['speech_chat']}\nVoice Assistant Name: {user_config['speech_assistant_name']}"
        status_aware_settings = settings.voice_activation_settings_string + current_status
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=status_aware_settings, reply_markup=voice_assistant_settings_markup(), parse_mode="HTML")

    elif call.data == "voice_activation_on":
        user_config = get_or_create_chat_config(call.from_user.id, 'user')
        user_config['speech_chat'] = True
        config_db_helper.set_new_config(call.from_user.id, 'user', user_config)

        current_status = f"\n\nVoice Activation: {user_config['speech_chat']}\nVoice Assistant Name: {user_config['speech_assistant_name']}"
        status_aware_settings = settings.voice_activation_settings_string + current_status
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=status_aware_settings, reply_markup=voice_assistant_settings_markup(), parse_mode="HTML")

    elif call.data == "voice_activation_off":
        user_config = get_or_create_chat_config(call.from_user.id, 'user')
        user_config['speech_chat'] = False
        config_db_helper.set_new_config(call.from_user.id, 'user', user_config)

        current_status = f"\n\nVoice Activation: {user_config['speech_chat']}\nVoice Assistant Name: {user_config['speech_assistant_name']}"
        status_aware_settings = settings.voice_activation_settings_string + current_status
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=status_aware_settings, reply_markup=voice_assistant_settings_markup(), parse_mode="HTML")




    # Group Settings callback handler
    elif call.data == "group_settings":
        # Update message to show chat settings with a "Back" button
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=settings.group_settings_string, reply_markup=group_settings_markup(), parse_mode="HTML")
    
    elif call.data == "language_model_menu":

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




    # handle voice 
    elif call.data == "agent_voice_menu":
        # populate and send string
        chat_config = get_or_create_chat_config(call.message.chat.id, 'chat')
        current_choice = chat_config['agent_voice']
        new_string = settings.agent_voice_string + f"\nCurrent choice: {current_choice}"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=new_string, reply_markup=agent_voice_settings_markup(), parse_mode="HTML")

    elif call.data[0:9] == "voiceset_":
        #sample call data = voiceset_alloy, we need to extract alloy
        voice_selection = call.data.split('_')[1]
        chat_config = get_or_create_chat_config(call.message.chat.id, 'chat')
        chat_config['agent_voice'] = voice_selection
        config_db_helper.set_new_config(call.message.chat.id, 'chat', chat_config)

        # populate and send string
        current_choice = chat_config['agent_voice']
        new_string = settings.agent_voice_string + f"\nCurrent choice: {current_choice}"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=new_string, reply_markup=agent_voice_settings_markup(), parse_mode="HTML")



    elif call.data == "persistence_on":
        user_config = get_or_create_chat_config(call.from_user.id, 'user')

        # check whether the user is a premium user
        if not user_config['is_premium']:
            bot.answer_callback_query(call.id, "Persistence is a premium feature, please buy a premium subscription to turn this feature on!")
            return
        
        # if they are, then you are free to add this group to the list of persistent chats for that given user.
        current_persistent_chat_groups = user_config['persistent_chats']
        if call.message.chat.id not in current_persistent_chat_groups:
            try:
                current_persistent_chat_groups.append(call.message.chat.id) # adds the chat id, which essentially turns the persistence "on" for this chat group.
                user_config['persistent_chats'] = current_persistent_chat_groups # set it to the newly appended list
                config_db_helper.set_new_config(call.from_user.id, 'user', user_config)
                bot.answer_callback_query(call.id, "Persistence on. NOTE: chat requests may become more expensive.")
                print(f"persistence on for this user {call.from_user.id} in group {call.message.chat.id}")
            except Exception as e:
                print(e)
        else:
            bot.answer_callback_query(call.id, "Persistence is already on for this group.")


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












@bot.message_handler(commands=['set_name'])
@is_bot_active
@is_valid_user
def handle_agent_name_setting(message):
    """
    sets the agent's name
    """
    
    try:
        user_config = get_or_create_chat_config(message.from_user.id, 'user')
        new_agent_name = helper_functions.extract_body(message.text)
        if new_agent_name.isalpha():
            user_config['speech_assistant_name'] = new_agent_name
            config_db_helper.set_new_config(message.from_user.id, 'user', user_config)
            bot.reply_to(message, f"Agent name has been set to: {new_agent_name}")
        else:
            bot.reply_to(message, f"Please try again without any special characters.")
    except Exception as e:
        # Generic error handling
        bot.reply_to(message, "Failed to set context for user in chat group, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {str(e)}"))








# Manual configurations of settings that require users to type
@bot.message_handler(commands=['user_set_openai_key'])
@is_bot_active
@is_valid_user
def handle_user_set_openai_apikey(message):
    """
    handle_user_openai_apikey(message): sets openAI key for the user
    """
    try:
        new_openai_key = helper_functions.extract_body(message.text)
        if config_db_helper.check_configval_pattern(new_openai_key, config_attr='openai_api_key'): # config val checking is temporary turned off for now as openAI Api Key formats continue to change.

            # encrypt the key;
            new_openai_key = config_db_helper.encrypt(new_openai_key)

            # get the configurations
            user_config = get_or_create_chat_config(message.from_user.id, 'user')
            user_config['openai_api_key'] = new_openai_key
            config_db_helper.set_new_config(message.from_user.id, 'user', user_config)

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


@bot.message_handler(commands=['group_set_openai_key'])
@is_bot_active
@is_valid_user
def handle_group_set_openai_apikey(message):
    """
    handle_group_set_openai_apikey(message): sets openAI key for the user
    """

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
                bot.reply_to(message, f"New API key for group successfully set. Message could not be deleted due to insufficient permissions, please delete this message to keep your API Key private.")
        
        else:
            bot.reply_to(message, f"Entered API Key is not in the correct format, please check again and try again.")
    
    except Exception as e:
        bot.reply_to(message, "/group_set_openai_key command request could not be completed, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {e}")) # traceback?




# Manual configurations of settings that require users to type
@bot.message_handler(commands=['set_temperature'])
@is_bot_active
@is_valid_user
def handle_set_temperature(message):
    """
    Sets the language model temperature for a user or chat. Valid range is between 0 and 2.
    """
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
@is_bot_active
@is_valid_user
def handle_set_t1(message):
    """
    Sets the translation 1 preset of the group.
    """
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
@is_bot_active
@is_valid_user
def handle_set_t2(message):
    """
    Sets the translation 2 preset of the group.
    """
    
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
@is_bot_active
@is_valid_user
def handle_set_t2(message):
    """
    Sets the translation 3 preset of the group.
    """
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








# context setting
## set and reset group context
@bot.message_handler(commands=['set_context'])
@is_bot_active
@is_valid_user
def handle_set_context_in_group(message):
    """
    Sets the context for the group, whatever instructions it wants to give.
    """
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


@bot.message_handler(commands=['reset_context'])
@is_bot_active
@is_valid_user
def handle_reset_context_in_group(message):
    """
    Sets the context for the group, whatever instructions it wants to give.
    """
    # Check permissions for group chats if the user is an administrator -> commented out as ANYBODY should be able to set their context within a group
    # if message.chat.type != 'private' and not helper_functions.user_has_admin_permission(bot, message.chat.id, message.from_user.id):
    #     bot.reply_to(message, "You do not have permissions to set the temperature for this chat group.")
    #     return
    
    try:
        # Retrieve and update the chat configuration and the context stored for the user in group with an empty string
        chat_config = get_or_create_chat_config(message.chat.id, 'chat')
        chat_config['contexts'][str(message.from_user.id)] = ""
        config_db_helper.set_new_config(message.chat.id, 'chat', chat_config)
        bot.reply_to(message, f"Context has been reset.")

    except Exception as e:
        # Generic error handling
        bot.reply_to(message, "Failed to set context for user in chat group, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {str(e)}"))


## set and reset user context (spans across groups)
@bot.message_handler(commands=['set_user_context'])
@is_bot_active
@is_valid_user
def handle_set_user_context(message):
    """
    Sets the context for the user, whatever instructions it wants to give.
    """

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


@bot.message_handler(commands=['reset_user_context'])
@is_bot_active
@is_valid_user
def handle_reset_user_context(message):
    """
    Sets the context for the user, whatever instructions it wants to give.
    """

    try:
        user_config = get_or_create_chat_config(message.from_user.id, 'user')
        user_config['user_context'] = ""

        config_db_helper.set_new_config(message.from_user.id, 'user', user_config)
        bot.reply_to(message, f"User context across groups has been reset.")
    except Exception as e:
        # Generic error handling
        bot.reply_to(message, "Failed to set context for user in chat group, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {str(e)}"))




# check contexts:
@bot.message_handler(commands=['check_context'])
@is_bot_active
@is_valid_user
def check_context(message):
    """
    Sets the context for the user, whatever instructions it wants to give.
    """

    try:
        user_config = get_or_create_chat_config(message.from_user.id, 'user')
        chat_config = get_or_create_chat_config(message.chat.id, 'chat')
        user_context = user_config['user_context']
        chat_context = chat_config['contexts'][str(message.from_user.id)]

        bot.reply_to(message, f"User Context (all groups):\n{user_context} \n\n\n Chat context:\n{chat_context}")
    except Exception as e:
        # Generic error handling
        bot.reply_to(message, "Failed to set context for user in chat group, please contact admin.")
        logger.error(helper_functions.construct_logs(message, f"Error: {str(e)}"))




# admin set group context - 







 
# Handler for managing chat history as context for the given group;
@bot.message_handler(commands=['clear_history'])
def handle_clear_chat_history(message):
    """
    handle_clear_memory(message): clears the chat history and logs saved on the vectorstore and basically resets the conversation history.
    - clear_group_history -> delete the whole group's chat history, only available to admins with delete permissions.
    """
    # deletes the namespace
    if message.from_user.is_bot:
        return
    
    # check whether the person requesting the clear_history request is an administrator with delete permissions

    # if so - go to the namespace in pinecone and delete the chat.


 



















#########################################################
################## PAYMENTS FUNCTIONS: ##################
#########################################################

# Action
# - Integrate with test payment rails; and setting the configuration for the given user who called the message;
def generate_txid(user_id):
    current_date = datetime.date.today()
    return f"{user_id}_{current_date}"


@bot.message_handler(commands=['subscribe'])
@is_bot_active
@is_valid_user
def command_pay(message):
    
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
################## PAYMENTS FUNCTIONS: ##################
#########################################################
# - Where will Admin user_ids be stored? Perhaps in system configurations, where I can turn the bot on and off and all commands are handled by that; I think that will be p cool.
    

# Admin features
#### ---> this code still needs testing + rework; also ask GPT in what format user_ids are stored in Telebot, is it string? is it number;


# watchlist user
@bot.message_handler(commands=['watchlist'])
@is_bot_active
@is_admin
@is_in_reply
def watchlist_user(message):
    """
    
    """
    try:
        system_config = get_or_create_chat_config(OWNER_USER_ID, 'owner')
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        elif helper_functions.extract_body(message) != "":
            user_id = helper_functions.extract_body(message)
        else:
            bot.reply_to(message, f"Invalid, either reply to a user's message OR provide their user ID.")
            return
        
        if user_id not in system_config['watchlist']:
            system_config['watchlist'].append(user_id)
        config_db_helper.set_new_config(OWNER_USER_ID, 'owner', system_config)
        bot.reply_to(message, f"User has been successfully put on watchlist.")

    except Exception as e:
        bot.reply_to(message, "Failed to complete command, please see logs")
        logger.error(helper_functions.construct_logs(message, f"Error: {str(e)}"))


@bot.message_handler(commands=['unwatchlist'])
@is_bot_active
@is_admin
@is_in_reply
def unwatchlist_user(message):
    try:
        system_config = get_or_create_chat_config(OWNER_USER_ID, 'owner')
        user_id = helper_functions.extract_body(message)
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id


        if user_id in system_config['watchlist']:
            system_config['watchlist'].remove(user_id)
            config_db_helper.set_new_config(OWNER_USER_ID, 'owner', system_config)
            bot.reply_to(message, f"User has been successfully unbanned.")
        else:
            bot.reply_to(message, f"User is not in banned list")

    except Exception as e:
        bot.reply_to(message, "Failed to complete command, please see logs")
        logger.error(helper_functions.construct_logs(message, f"Error: {str(e)}"))





# ban user
@bot.message_handler(commands=['ban'])
@is_bot_active
@is_admin
@is_in_reply
def ban_user(message):
    """
    
    """
    try:
        system_config = get_or_create_chat_config(OWNER_USER_ID, 'owner')
        if message.reply_to_message:
            user_id_banned = message.reply_to_message.from_user.id
        elif helper_functions.extract_body(message) != "":
            user_id_banned = helper_functions.extract_body(message)
        else:
            bot.reply_to(message, f"Invalid, either reply to a user's message OR provide their user ID.")
            return
        
        if user_id_banned not in system_config['banned_users']:
            system_config['banned_users'].append(user_id_banned)
        config_db_helper.set_new_config(OWNER_USER_ID, 'owner', system_config)
        bot.reply_to(message, f"User has been successfully banned.")

    except Exception as e:
        bot.reply_to(message, "Failed to complete command, please see logs")
        logger.error(helper_functions.construct_logs(message, f"Error: {str(e)}"))


# unban user
@bot.message_handler(commands=['unban'])
@is_bot_active
@is_admin
@is_in_reply
def unban_user(message):
    try:
        system_config = get_or_create_chat_config(OWNER_USER_ID, 'owner')
        user_id = helper_functions.extract_body(message)
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id


        if user_id in system_config['banned_users']:
            system_config['banned_users'].remove(user_id)
            config_db_helper.set_new_config(OWNER_USER_ID, 'owner', system_config)
            bot.reply_to(message, f"User has been successfully unbanned.")
        else:
            bot.reply_to(message, f"User is not in banned list")

    except Exception as e:
        bot.reply_to(message, "Failed to complete command, please see logs")
        logger.error(helper_functions.construct_logs(message, f"Error: {str(e)}"))











# Owner-only feature

@bot.message_handler(commands=['add_admin'])
def owner_add_admin(message):
    # check that the user is an owner
    if (str(message.from_user.id) != str(OWNER_USER_ID)): # later this needs to be changed to check whether it is within the list of Administrators;

        bot.reply_to(message, f"Your ID is {message.from_user.id} - {type(message.from_user.id)}  | {OWNER_USER_ID} - {type(OWNER_USER_ID)}")
        bot.reply_to(message, f"This command is only available to the owner of the bot")
        return
    
    if not message.reply_to_message:
        bot.reply_to(message, f"Please make")
        return

    try:
        new_admin_uid = message.reply_to_message.from_user.id
        system_config = get_or_create_chat_config(OWNER_USER_ID, 'owner')
        system_config['admins'].append(new_admin_uid) #<- double check whether return None and inplace or I need to copy
        config_db_helper.set_new_config(OWNER_USER_ID, 'owner', system_config)
        bot.reply_to(message, f"User: {message.reply_to_message.from_user.username} has now been added to the admin list")
    
    except Exception as e:
        # Generic error handling
        bot.reply_to(message, "Failed to complete command, please see logs")
        logger.error(helper_functions.construct_logs(message, f"Error: {str(e)}"))
    
@bot.message_handler(commands=['remove_admin'])
def owner_remove_admin(message):
    # check that the user is an owner
    if (str(message.from_user.id) != str(OWNER_USER_ID)): # later this needs to be changed to check whether it is within the list of Administrators;

        bot.reply_to(message, f"Your ID is {message.from_user.id} - {type(message.from_user.id)}  | {OWNER_USER_ID} - {type(OWNER_USER_ID)}")
        bot.reply_to(message, f"This command is only available to the owner of the bot")
        return
    
    if not message.reply_to_message:
        bot.reply_to(message, f"Please make")
        return

    try:
        new_admin_uid = message.reply_to_message.from_user.id
        system_config = get_or_create_chat_config(OWNER_USER_ID, 'owner')
        try:
            system_config['admins'].remove(new_admin_uid) #<- double check whether return None and inplace or I need to copy
            bot.reply_to(message, f"User: {message.reply_to_message.from_user.username} has now been removed from the admin list")
        except ValueError:
            bot.reply_to(message, f"User: {message.reply_to_message.from_user.username} is not in the admin list.")
        config_db_helper.set_new_config(OWNER_USER_ID, 'owner', system_config)
        
    
    except Exception as e:
        # Generic error handling
        bot.reply_to(message, "Failed to complete command, please see logs")
        logger.error(helper_functions.construct_logs(message, f"Error: {str(e)}"))




@bot.message_handler(commands=['give_premium'])
@is_bot_active
# @is_valid_user < change to admin check
def owner_give_premium(message):
    # check that the user is an owner
    if (str(message.from_user.id) != str(OWNER_USER_ID)): # later this needs to be changed to check whether it is within the list of Administrators;

        bot.reply_to(message, f"Your ID is {message.from_user.id} - {type(message.from_user.id)}  | {OWNER_USER_ID} - {type(OWNER_USER_ID)}")
        bot.reply_to(message, f"This command is only available to the owner of the bot")
        return
    
    if not message.reply_to_message:
        bot.reply_to(message, f"Please make sure that you are responding to a user messge, so that the bot knows who to perform actions towards.")
        return
    # gets the user ID from the tagged username.
    try:
        new_premium_user_id = message.reply_to_message.from_user.id
        user_config = get_or_create_chat_config(new_premium_user_id, 'user')
        user_config['is_premium'] = True
        config_db_helper.set_new_config(new_premium_user_id, 'user', user_config)
        bot.reply_to(message, f"Premium Features enabled for {message.reply_to_message.from_user.username}! Congrats!")
    
    except Exception as e:
        # Generic error handling
        bot.reply_to(message, "Failed to give premmium for this user, please see logs.")
        logger.error(helper_functions.construct_logs(message, f"Error: {str(e)}"))





"""
Bot State control commands
"""
# turning bot on and off
@is_admin
@bot.message_handler(commands=['start_bot'])
# @wrapper function to check whether the sender is an admin or owner
def start_bot(message):
    system_config = get_or_create_chat_config(OWNER_USER_ID, 'owner')
    system_config['is_on'] = True
    config_db_helper.set_new_config(OWNER_USER_ID, 'owner', system_config)
    bot.reply_to(message, "Bot is now ON and will respond to commands.")

@is_admin
@bot.message_handler(commands=['stop_bot'])
# @wrapper function to check whether the sender is an admin or owner
def stop_bot(message):
    # Set the bot state to "off" in Redis
    system_config = get_or_create_chat_config(OWNER_USER_ID, 'owner')
    system_config['is_on'] = False
    config_db_helper.set_new_config(OWNER_USER_ID, 'owner', system_config)
    bot.reply_to(message, "Bot is now OFF and will not respond to other commands.")











#########################################################
######################## RUN BOT ########################
#########################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))



