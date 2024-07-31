import templates
import json
import re
import os
import base64
import settings
import ai_commands
import spacy



# handler helper functions
def extract_body(message_text):
    """
    def extract_body(message): returns the message body of a telegram message
    """
    try:
        return " ".join(message_text.split(' ')[1:])
    except Exception as e:
        return ""

def extract_command(message_text):
    """
    def extract_command(message): returns the command
    """
    try:
        return message_text.split(' ')[0]
    except Exception as e:
        return ""


def encode_image(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def start_menu():
    """
    def start_menu(): returns the current template menu message
    """
    return settings.getting_started_string





# logging helpers
def construct_logs(message, result_message):
    """
    def construct_logs(message): takes a message object and returns a string of all the necessary and important metadata / information.
    """
    command = extract_command(message.text)
    username = getattr(message.from_user, 'username', 'N/A')
    try:
        log_string = f"COMMAND: {command} | USER_ID: {message.from_user.id} | USERNAME: {username}| CHAT_ID: {message.chat.id} | CHAT_TYPE: {message.chat.type} | MESSAGE_ID: {message.message_id} | CONTENT_TYPE: {message.content_type} | RESULT: {result_message}"
        # print(log_string) < unclog stdout
        return log_string
    except Exception as e:
        return f"Error occured in: {e}"


def bot_has_delete_permission(chat_id, bot):
    bot_user = bot.get_me()  # Get bot's own user info
    bot_member = bot.get_chat_member(chat_id, bot_user.id)  # Get bot's membership info in the chat
    # Check if bot has permission to delete messages
    return bot_member.can_delete_messages


def user_has_admin_permission(bot, chat_id, user_id):
    """
    Checks if a user is an administrator in a given chat.

    Args:
        chat_id (int): The unique identifier for the target chat or username of the target supergroup.
        user_id (int): The unique identifier of the user to check.

    Returns:
        bool: True if the user is an admin, False otherwise.
    """
    try:
        # Fetch all administrators in the chat
        chat_administrators = bot.get_chat_administrators(chat_id)
        # Check if the user_id is in the list of administrators
        for admin in chat_administrators:
            if admin.user.id == user_id:
                return True
        return False
    except Exception as e:
        print(f"Failed to check admin status: {e}")
        return False


def find_full_word(text, word):
    # Create a regex pattern with word boundaries
    pattern = r'\b' + re.escape(word) + r'\b'
    # Search for the pattern in the text
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False
# Example usage
# sentence = "Hello, my name is Jack and I am learning Python."
# word = "jack"
# match_found = find_full_word(sentence, word)
# print("Word found:", match_found)



def strip_non_alphabet_chars(s):
    # This regex pattern matches any character that is NOT a lowercase or uppercase letter
    pattern = '[^a-zA-Z]'
    # Replace these characters with an empty string
    cleaned_string = re.sub(pattern, '', s)
    return cleaned_string


def construct_context(user_config, chat_config, message):
    # basic imports and string construction
    returned_context = ""
    divider = "\n" + ("-----" * 3) + '\n'
    user_set_context = user_config['user_context']
    chat_context = ""
    user_context_string = settings.user_context_string
    chat_context_string = settings.chat_context_string

    # establishing the user context
    if user_set_context == "":
        # if the  context is NOT set, then the whole import context string is NOT used to simplify things
        pass
    else:
        returned_context = user_context_string + user_set_context + divider
    
    # establish the chat context
    try:
        chat_context = chat_config['contexts'][str(message.from_user.id)]
    except KeyError:
        print("No context was set for user")
    
    if chat_context == "":
        # if the  context is NOT set, then the whole import context string is NOT used to simplify things
        pass
    else:
        returned_context += chat_context_string + chat_context + divider
    
    # if neither user or chat context is set, then the returned string is an empty string
    print(returned_context)
    return returned_context





def construct_chat_history(user_config, message, api_key, pinecone_key):
    returned_history = ""

    # check if the message is in direct reply to it
    if message.reply_to_message:
        returned_history = f"THIS MESSAGE iS IN DIRECT REPLY TO THIS MESSAGE, USE IT AS A HIGH PRIORITY CONTEXT:\n{message.reply_to_message.text}\n\n\n{'---'*3}"
    else:
        pass # returned history is kept at ""

    # check if the user is a premium user that has persistence on:
        
    if user_config['is_premium'] and (message.chat.id in user_config['persistent_chats']):
        similarity_search_result_string = ai_commands.similarity_search_on_index(message, api_key, pinecone_key)
        returned_history += similarity_search_result_string
    return returned_history    



def upsert_chat_history(user_config, message, response_text, api_key, pinecone_key):
    body_text = extract_body(message.text)
    if user_config['is_premium'] and (message.chat.id in user_config['persistent_chats']):
        upload_string = f"""USER QUERY/PROMPT:\n{body_text}\n\n\n{'---' * 5}\n\n\nAI RESPONSE:\n{response_text}"""
        ai_commands.create_and_upsert_embeddings(message, upload_string, api_key, pinecone_key)
        print("Safely upserted data into pinecone")
    
    else:
        # print("User does not have this feature turned on.")
        return


def decode_bytestring(byte_string):
    # Decode the byte string to a normal string
    decoded_string = byte_string.decode('utf-8')

    # Convert the JSON string to a Python dictionary
    data_dict = json.loads(decoded_string)
    return data_dict




def chunk_text_spacy(text, max_words=350):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    chunks = []
    current_chunk = []
    current_count = 0

    for sent in doc.sents:
        sentence_words = sent.text.split()
        if current_count + len(sentence_words) > max_words:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_count = 0
        current_chunk.append(sent.text)
        current_count += len(sentence_words)

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks
# Example usage
# text = "Your very large text. It should be more than 4000 words for meaningful chunking. Each sentence is considered for intelligent splitting."
# chunks = chunk_text_spacy(text)
# for i, chunk in enumerate(chunks):
#     print(f"Chunk {i+1}: {chunk[:100]}...")  # Displaying first 100 characters of each chunk for brevity

def safe_send(message, bot, text):
    """
    Sends the text in manageable chunks if it exceeds a certain length limit (3500 characters),
    attempting to use Markdown formatting. If Markdown formatting fails (typically due to incorrect
    Markdown syntax or Telegram API formatting restrictions), the text is sent as plain text.

    Args:
        message: The Telegram message context used for replying.
        bot: The Telegram bot instance.
        text: The text string that needs to be sent.

    This function first checks if the text length exceeds 3500 characters and splits it into
    chunks if necessary. Each chunk is then sent as a reply to the original message. If a Markdown
    formatting error occurs, it falls back to sending the chunk as plain text.
    """
    chunks = []
    if len(text) > 3500:
        # Assuming chunk_text_spacy is a function that splits text while respecting
        # sentence boundaries and does not break words inappropriately.
        chunks = chunk_text_spacy(text)  # Splitting text into smaller parts
    else:
        chunks.append(text)
    
    for chunk in chunks:
        try:
            bot.reply_to(message, text=chunk, parse_mode='Markdown')
        except Exception as e:
            # Assuming the exception 'e' is due to Markdown parse errors,
            # logs the error and falls back to plain text sending
            print(f"Failed to send markdown message: {e}. Sending as plain text.")
            bot.reply_to(message, text=chunk)







