import os
import psycopg2
import sys
import signal
import traceback
import logging
import json
from psycopg2 import pool
import helper_functions
import re


# encryption module
from cryptography.fernet import Fernet




### Setup the connection pool ###
DATABASE_URL = os.environ.get('DATABASE_URL')
connection_pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=10, dsn=DATABASE_URL)
# print(f"DATABASE URL ESTABLISHED {DATABASE_URL}")



# Retrieve the key from environment variables
fernet_key = os.getenv('FERNET_KEY')
cipher_suite = Fernet(fernet_key)


# Get environment variables
OWNER_USER_ID = os.environ.get('OWNER_UID', "7032361920")
OPENAI_FREE_KEY = os.environ.get('OPENAI_FREE_KEY', "sk-notvalid")



LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(stream=sys.stdout, level=getattr(logging, LOG_LEVEL, logging.INFO), format='%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(message)s')
# logger = helper_classes.CustomLoggerAdapter(logging.getLogger(__name__), {'dyno_name': DYNO_NAME}) # < creates an custom logger adapter
logger = logging.getLogger(__name__)


### variables and templates ###
valid_table_names = ["chat_configs", "user_configs", "system_configs"]


#####
# For any config changes, remember to update the versions.
#####

default_system_config = {
    "version": "0.0.3", # version of the config schema
    # "system_active" : True, # determines whether the bot is active or not, if False, the bot does not respond to any messages. Useful for system maintenance.
    # system_active is sunset to use redis instead.
    "onwer_id": OWNER_USER_ID,
    "admins": [OWNER_USER_ID], # list of administrators of the bot
    "system_oai_key": OPENAI_FREE_KEY,
    "banned_users": [], # list of user_ids that are banned from using the service.
}

default_chat_config = {
    "version": "0.1.1", # the version determines the current version of the configs
    # "is_premium": False, # determines whether a group is a premium group; if it is not, then it cannot have persistence on. A chat cannot be premium.

    # below are changeable by users / system
    # chat configuration determines the behaviour of the bot within a chat group
    # "persistence": False, # determines whether a the bot keeps chat history for a given chat has persistence and context awareness within that chat
    # "vectorstore_endpoint" : "", # new endpoints are not necessary
    "lm_temp": 0.5, # default is 0.5, but language model can be made more deterministic
    "openai_api_key": "", # group's OpenAI API Key, this is used if the user's API key is not valid.
    "language_model": "gpt-3.5-turbo", # determines the default language model used by the user
    "t1": "eng", # translation 1
    "t2": "chi", # translation 2
    "t3": "kor", # translation 3
    "contexts": {}, # contexts for users given a chat group, it is created in a;
    "agent_voice": "alloy"
  }

default_user_config = {
    "version": "0.1.2", # the version determines the current version of the configs

    # below are changeable by users / system
    # user configurations determines how the bot interacts with commands requested by the user
    "free_credits": 5, # for users that do not have an openAI API key
    "is_premium": False, # determines whether the user is a premium user and has access to premium features.
    "persistent_chats": [], # list of chat groups that a user is persistent in.
    # "language_model": "gpt-3.5-turbo", # determines the default language model used by the user
    "openai_api_key": "", # determines the OpenAI API Key of a given user
    "image_mask_map": [ # determines how each user wants to edit the images
          [0, 0, 0],
          [0, 0, 0],
          [1, 1, 1]
        ],
    "user_context": "", # user context allows user to have context about themselves that persist between chat groups.

    "premium_image_mask_map": [ # determines how each user wants to edit the images
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
        ]
  }

valid_configval_patterns = {
    # valid_formats contain the syntaxes in regex that are accepted by a configuration that is typed / entered by the user.
    "openai_api_key": r'^sk-[A-Za-z0-9]{45,60}$' # regex
}

valid_configval_options = {
    "language_model": ['gpt-4', 'gpt-3.5-turbo'],
}




# database connection helpers
def get_conn_from_pool():
    """Get a connection from the pool with logging."""
    logger.info("Attempting to fetch a connection from the pool.")
    conn = connection_pool.getconn()
    if conn:
        logger.info("Connection fetched successfully.")
    else:
        logger.warning("Failed to fetch a connection from the pool.")
    return conn

def put_conn_back_in_pool(conn):
    """Return a connection to the pool with logging."""
    logger.info("Returning a connection to the pool.")
    connection_pool.putconn(conn)
    logger.info("Connection returned successfully.")


### Define and create the necessary tables if they are not already created ###
def create_config_table(table_name, config_type):
    # Ensure table_name is a safe string to prevent SQL injection
    # This is a simplified example. In production, use more robust validation or whitelisting.
    if table_name not in valid_table_names:
        raise ValueError("Invalid table name")
    
    if config_type not in ['chat', 'user', 'owner']:
        raise ValueError("Invalid config type")

    conn = get_conn_from_pool()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    {config_type+"_id"} BIGINT PRIMARY KEY,
                    config JSONB
                );
            """)
            conn.commit()
    finally:
        put_conn_back_in_pool(conn)

# Create the necessary tables
# create_config_table("chat_configs", "chat")
# create_config_table("user_configs", "user")
# create_config_table("system_configs", "owner")



### Define Database Utility function (getting connection and putting down the connection) ###
def get_or_create_chat_config(id, config_type):
    """
    def get_or_create_chat_config(id): takes an id, and the configuration type (either chat, or user). Returns a configuration. If None exist for the given ID, a 
    new record is created for that given user or chat group in the relevant tables: chat_configs or user_configs.
    """
    conn = connection_pool.getconn()
    if config_type not in ['chat', 'user', 'owner']:
        raise ValueError("Invalid config type")

    # determine which configuration type is being retrieved or created.
    if config_type == "chat":
        default_config = default_chat_config
        config_table = "chat_configs"
    elif config_type == "user":
        default_config = default_user_config
        config_table = "user_configs"
    else:
        default_config = default_system_config
        config_table = "system_configs"
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT config FROM {config_table} WHERE {config_type}_id = %s;", (id,))
            config_row = cursor.fetchone()

            # if the config row does not exist, a table is created
            if config_row is None:
                # default config is imported as a python dict of a Default Config from templates.py; from templates import default_config at the top of the app.
                # this automatically sets it to the most up to date version of default configs as written above.
                cursor.execute(f"""INSERT INTO {config_table} ({config_type}_id, config) VALUES (%s, %s) RETURNING config;""", (id, json.dumps(default_config)))
                conn.commit()
                config = default_config 
                # print(f"config default is {type(config)}")
            
            # if a config row is found;
            else:
                if isinstance(config_row[0], str):
                    config = json.loads(config_row[0])  # Type assertion: deserialize if it's a string
                else:
                    config = config_row[0]  # Use directly if it's already a dictionary
                
                # if there is an existing configuration, we check the versions and then do the dynamic migrations as needed.
                current_version = default_config['version'] # get the current default version
                existing_config_version = config['version'] # check the version of the returned config for the id
                

                ## dynamic datastructure updating;
                # only if the versions do not match here, then we update the existing configurations with the new attribute and its default value.
                if existing_config_version != current_version:
                    updated_config = default_config.copy() # make a copy
                    # we loop through the current version of the config for each attribute.
                    for key in updated_config.keys():
                        # if the key in the default config exists, get the value of it from the existing key EXCEPT the version (the default one is retained).
                        if key in config.keys() and (key != "version"):
                            updated_config[key] = config[key]
                        # if the key does not exist in the new one, the default configuration is maintained
                        # if a key exists in the existing config, but is deleted in the default schema, then it is also dropped.
                    

                    # dump the updated default configuration into the targeted ID;
                    ## the default config should now have: 
                    ## 1.) All existing configuration from existing config copied except version num, thus preserving the data.
                    ## 2.) Any new configurations and default values, and 3.) Any old attribute in existing config that is no longer supported is dropped.
                    cursor.execute(f"UPDATE {config_table} SET config = %s WHERE {config_type}_id = %s", (json.dumps(updated_config), id))
                    conn.commit()

                    # overwrite the config variable to the modified / combined default config from above so that it can be returned and used in the command handlers.
                    config = updated_config

            return config
    except Exception as e:
        tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
        print(f"Database error: {e} \n\n {tb_str}")
        raise
    finally:
        connection_pool.putconn(conn)






def set_new_config(id, config_type, new_config):
    """
    Updates the configuration value for a specified attribute and configuration type (chat or user).
    This function assumes the relevant chat or user configuration has already been initialized and is up to date by 
    calling get_or_create_chat_config() on the user or chat first.
    
    Args:
        id (str): The unique identifier for the chat or user.
        config_type (str): The type of configuration ('chat' or 'user').
        new_config (dict): The new configuration value to be set for the specified attribute.
        
    """
    conn = connection_pool.getconn()
    # check if the configuration type is valid.
    if config_type not in ['chat', 'user', 'owner']:
        raise ValueError("Invalid config type")
    
    # check if the configuration attribute it is trying to retrieve is value.
    # valid_keys = set(default_chat_config.keys()) | set(default_user_config.keys())
    # determine which configuration type is being retrieved or created.
    config_table = ""

    if config_type == "chat":
        config_table = "chat_configs"
    elif config_type == "user":
        config_table = "user_configs"
    elif config_type == "owner":
        config_table = "system_configs"
    else:
        print("Invalid config type!")
        return
    
    try:
        with conn.cursor() as cursor:
            # Safe way to insert variable table names into SQL queries
            query = f"UPDATE {config_table} SET config = %s WHERE {config_type}_id = %s"
            cursor.execute(query, (json.dumps(new_config), id))
            conn.commit()
    except Exception as e:
        tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
        print(f"Database error: {e} \n\n {tb_str}")
        raise

    finally:
        connection_pool.putconn(conn)





def check_configval_pattern(configval, config_attr):
    """
    check_api_key(message, config_attr): returns True or False based on whether the entered config value in message is in its valid format
    """
    # config_pattern = re.compile(valid_configval_patterns[config_attr])
    # print(configval)
    # print(config_pattern)
    # return bool(config_pattern.fullmatch(configval))
    return True


def check_configval_options(message, config_attr):
    """
    check_api_key(message, config_attr): returns True or False based on whether the entered config value in message is in its valid format
    """
    configval = helper_functions.extract_body(message)
    return configval in valid_configval_options[config_attr]






def encrypt(text):
    """
    Encrypts a plaintext string using Fernet encryption.

    Args:
        text (str): Plaintext string to be encrypted.
    
    Returns:
        str: Encrypted text encoded in base64.
    """
    # Convert the plaintext string to bytes
    text_bytes = text.encode()
    # Encrypt the text
    encrypted_text = cipher_suite.encrypt(text_bytes)
    # Return the encrypted text encoded in base64 as a string
    return encrypted_text.decode()


def decrypt(token):
    try:
        token_bytes = token.encode()
        decrypted_text = cipher_suite.decrypt(token_bytes)
        return decrypted_text.decode()
    except Exception as e:
        # Handle or log the decryption error appropriately
        return None

def get_apikey_list(user_config, chat_config):
    openai_api_keys = [user_config['openai_api_key'], chat_config['openai_api_key']]

    decrypted_keys = []
    for key in openai_api_keys:
        if key:
            decrypted_key = decrypt(key)
            if decrypted_key:
                decrypted_keys.append(decrypted_key)
    decrypted_keys.append(OPENAI_FREE_KEY)
    return decrypted_keys









### Set up the shutdown handler ###
def shutdown_handler(signum, frame):
    # Close database connection pool
    connection_pool.closeall()
    sys.exit(0)

# Register the signal handler for graceful shutdown
signal.signal(signal.SIGTERM, shutdown_handler)








