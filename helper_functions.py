import templates
import os
import base64

def extract_body(message):
    """
    def extract_body(message): returns the message body of a telegram message
    """
    return " ".join(message.split(' ')[1:])

def extract_command(message):
    """
    def extract_command(message): returns the command
    """
    return " ".join(message.split(' ')[0])


def encode_image(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def start_menu():
    """
    def start_menu(): returns the current template menu message
    """
    return templates.start_menu





# logging helpers
def construct_logs(message):
    """
    def construct_logs(message): takes a message object and returns a string of all the necessary and important metadata / information.
    """
    command = extract_command(message)
    try:
        log_string = f"/{command} | USER_ID: {message.from_user.id} | USERNAME: {message.from_user.username}| CHAT_ID: {message.chat.id} | CHAT_TYPE: {message.chat.type} | MESSAGE: {extract_body(message)}"
        return log_string
    except Exception as e:
        return f"Error: {e}"





















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




