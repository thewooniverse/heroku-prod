

## import modules ##
# commands dict / mapping at the bottom of the folder
import ai_commands




## define functions ##
# Function Schema - each function takes a message object(dict), and returns a dictionary as a response

def hello_world(message):
    """
    def hello_world(message): test function
    """
    return {"response_text": "Hello, World!"}


def hello_bro(message):
    user_info = message['from']
    username = user_info.get('username', None)  # Using .get() is safer in case 'username' key doesn't exist
    return {"response_text": f"Whats up my G {username}"}

def mock(message):
    body_text = " "
    text = message['text']

    if len(text.split(' ')) > 1:
        body_text = ' '.join(text.split(' ')[1:])
    
    user_info = message['from']
    username = user_info.get('username', None)  # Using .get() is safer in case 'username' key doesn't exist
    return {"response_text": f"{username} said \"{body_text}\" - LOL what a loser"}






## command/function dictionary / mapping ##

commands_map = {
    '/hello_world': {"function": hello_world, "payload_req": ['text']},
    '/hello_bro': {"function": hello_bro, "payload_req": ['text']},
    '/mock': {"function": mock, "payload_req": ['text']},
    '/text_with_photo': {"function": hello_world, "payload_req": ['text', 'photo']},
    '/chat': {'function': ai_commands.chat_agent, 'payload_req': ['text']}
    }





