import templates
import os
import base64
import settings





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





# def delete_temp(path):
#     """
#     def delete_temp(path): Takes a temporary file at Pathlib Path and tries to delete it, returns deleted or not.
#     """
#     if os.path.isfile(path):
#         print("Removed file")
#         os.remove(path)
#     else:
#         print("Failed to remove file, file does not exist")
#         return None




