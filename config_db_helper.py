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


### Setup the connection pool ###
DATABASE_URL = os.environ.get('DATABASE_URL')
connection_pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=10, dsn=DATABASE_URL)
# print(f"DATABASE URL ESTABLISHED {DATABASE_URL}")


LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(stream=sys.stdout, level=getattr(logging, LOG_LEVEL, logging.INFO), format='%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(message)s')
# logger = helper_classes.CustomLoggerAdapter(logging.getLogger(__name__), {'dyno_name': DYNO_NAME}) # < creates an custom logger adapter
logger = logging.getLogger(__name__)


### variables and templates ###
valid_table_names = ["chat_configs", "user_configs"]


#####
# For any config changes, remember to update the versions.
#####
default_chat_config = {
    "version": "0.0.1", # the version determines the current version of the configs

    # below are changeable by users / system
    # chat configuration determines the behaviour of the bot within a chat group
    "persistence": False, # determines whether a the bot keeps chat history for a given chat has persistence and context awareness within that chat
    "vectorestore_endpoint" : "", # default is blank, but once the persistence trial is on it will check for 
    "openai_api_key": "", # group's OpenAI API Key, this is used if the user's API key is not valid.
    "is_premium": False, # determines whether a group is a premium group; if it is not, then it cannot have persistence on.
  }

default_user_config = {
    "version": "0.0.1", # the version determines the current version of the configs

    # below are changeable by users / system
    # user configurations determines how the bot interacts with commands requested by the user
    "is_premium": False, # determines whether the user is a premium user and has access to premium features.
    "language_model": "gpt-4", # determines the default language model used by the user
    "openai_api_key": "", # determines the OpenAI API Key of a given user
    "image_mask_map": [ # determines how each user wants to edit the images
          [0, 0, 0],
          [0, 0, 0],
          [1, 1, 1]
        ]
  }


valid_configval_patterns = {
    # valid_formats contain the syntaxes in regex that are accepted by a configuration that is typed / entered by the user.
    "openai_api_key": r'sk-.{20}T3BlbkFJ.{20}' # regex,
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
    
    if config_type not in ['chat', 'user']:
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
create_config_table("chat_configs", "chat")
create_config_table("user_configs", "user")




### Define Database Utility function (getting connection and putting down the connection) ###
def get_or_create_chat_config(id, config_type):
    """
    def get_or_create_chat_config(id): takes an id, and the configuration type (either chat, or user). Returns a configuration. If None exist for the given ID, a 
    new record is created for that given user or chat group in the relevant tables: chat_configs or user_configs.
    """
    conn = connection_pool.getconn()
    if config_type not in ['chat', 'user']:
        raise ValueError("Invalid config type")

    # determine which configuration type is being retrieved or created.
    if config_type == "chat":
        default_config = default_chat_config
        config_table = "chat_configs"
    else:
        default_config = default_user_config
        config_table = "user_configs"
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT config FROM {config_table} WHERE {config_type}_id = %s;", (id,))
            config_row = cursor.fetchone()
            if config_row is None:
                # default config is imported as a python dict of a Default Config from templates.py; from templates import default_config at the top of the app.
                # this automatically sets it to the most up to date version of default configs as written above.
                cursor.execute(f"""INSERT INTO {config_table} ({config_type}_id, config) VALUES (%s, %s) RETURNING config;""", (id, json.dumps(default_config)))
                conn.commit()
                config = default_config 
                # print(f"config default is {type(config)}")
            else:
                if isinstance(config_row[0], str):
                    config = json.loads(config_row[0])  # Deserialize if it's a string
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
                    ## 1.) All existing configuration from existing config copied except version num. 
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
        config_attribute (str): The attribute name within the configuration to be updated.
        new_config (dict): The new configuration value to be set for the specified attribute.
        
    Raises:
        ValueError: If `config_type` is not 'chat' or 'user', or if `config_attribute` is invalid.
    """
    conn = connection_pool.getconn()
    # check if the configuration type is valid.
    if config_type not in ['chat', 'user']:
        raise ValueError("Invalid config type")
    
    # check if the configuration attribute it is trying to retrieve is value.
    # valid_keys = set(default_chat_config.keys()) | set(default_user_config.keys())
    # determine which configuration type is being retrieved or created.
    config_table = "chat_configs" if config_type == "chat" else "user_configs"

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


    



def check_configval_format(message, config_attr):
    """
    check_api_key(message, config_attr): returns True or False based on whether the entered config value in message is in its valid format
    """
    configval = helper_functions.extract_body(message)
    config_pattern = re.compile(valid_configval_patterns[config_attr])
    return bool(config_pattern.fullmatch(configval))


def get_apikey_list(message):
    """
    get_apikey_list(message): returns a list of associated Api Keys. If empty
    """
    chat_config = get_or_create_chat_config(message.chat.id, 'chat')
    user_config = get_or_create_chat_config(message.from_user.id, 'user')
    openai_api_keys = [chat_config['openai_api_key'], user_config['openai_api_key']]

    # returns an empty list of there are no api keys or both are ["", ""]
    return [key for key in openai_api_keys if key]







### Set up the shutdown handler ###
def shutdown_handler(signum, frame):
    # Close database connection pool
    connection_pool.closeall()
    sys.exit(0)

# Register the signal handler for graceful shutdown
signal.signal(signal.SIGTERM, shutdown_handler)








