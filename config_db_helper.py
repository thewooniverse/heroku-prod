import os
import psycopg2
import sys
import signal
import traceback
import logging
import json


### Setup the connection pool ###
DATABASE_URL = os.environ.get('DATABASE_URL')
connection_pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=10, dsn=DATABASE_URL)

### create logging objects ###
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
print(f"Logging started with {LOG_LEVEL}")
logging.basicConfig(stream=sys.stdout, level=getattr(logging, LOG_LEVEL, logging.INFO), format='%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(message)s')
# logger = helper_classes.CustomLoggerAdapter(logging.getLogger(__name__), {'dyno_name': DYNO_NAME}) # < creates an custom logger adapter
logger = logging.getLogger(__name__)


### variables and templates ###
valid_table_names = ["chat_configs", "user_configs"]


default_chat_config = {
    # chat configuration determines the behaviour of the bot within a chat group

    "persistence": False, # determines whether a the bot keeps chat history for a given chat has persistence and context awareness within that chat
    "openai_api_key": "",
    "is_premium": False, # determines whether a chat has a premium subscription
    "language_model": "gpt-3.5-turbo", # determines
  }

default_user_config = {
    # user configurations determines how the bot interacts with commands requested by the user

    "override": True, # determines whether a user configuration overrides a chat configuration, if the setting is off then chat_config is used
    "is_premium": False,
    "language_model": "gpt-4", # determines the default language model used by the user
    "openai_api_key": "", # determines the OpenAI API Key of a given user
    "image_mask_map": [ # determines how each user wants to edit the images
          [0, 0, 0],
          [0, 0, 0],
          [1, 1, 1]
        ]
  }


### Define and create the necessary tables if they are not already created ###
def create_config_table(table_name, config_type):
    # Ensure table_name is a safe string to prevent SQL injection
    # This is a simplified example. In production, use more robust validation or whitelisting.
    if table_name not in valid_table_names:
        raise ValueError("Invalid table name")
    
    if config_type not in ['chat', 'user']:
        raise ValueError("Invalid config type")

    conn = connection_pool.getconn()
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
        connection_pool.putconn(conn)

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

    # determine which configuration type is being retrieved or created.
    if config_type == "chat":
        default_config = default_chat_config
    else:
        default_config = default_user_config
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT config FROM chat_configs WHERE chat_id = %s;", (id,))
            config_row = cursor.fetchone()
            if config_row is None:
                # default config is imported as a python dict of a Default Config from templates.py; from templates import default_config at the top of the app.
                cursor.execute("INSERT INTO chat_configs (chat_id, config) VALUES (%s, %s) RETURNING config;", (id, json.dumps(default_config)))
                conn.commit()
                config = default_config 
                # print(f"config default is {type(config)}")
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







### Set up the shutdown handler ###
def shutdown_handler(signum, frame):
    # Close database connection pool
    connection_pool.closeall()
    sys.exit(0)

# Register the signal handler for graceful shutdown
signal.signal(signal.SIGTERM, shutdown_handler)

















