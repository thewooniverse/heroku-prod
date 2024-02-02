from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = '6355794369:AAHnqUS6p8K4xVFkryZFmmmpF4LBG-gzyv4'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'



"""
To do lists:
- Secure environment variables
- Different chat request sorters that sort through chat requests and call different commands and responses to the texts.
- Integration with basic ChatGPT
- Then using RAG to store chat history, clear data etc...
"""












@app.route('/') # root directory
def hello_world():
    return 'Hello, World!'
# https://telebot-test-59f8f075f509.herokuapp.com/

@app.route('/goodbye_world')
def goodbye_world():
    return 'Goodbye, World!'
# https://telebot-test-59f8f075f509.herokuapp.com/goodbye_world


@app.route('/webhook', methods=['POST'])
def webhook():
    #  This line defines a route in your Flask application at the endpoint /webhook. 
    #  It's set to only accept POST requests, which is the method typically used by webhooks to send data to your server. 
    #  In this context, Telegram sends updates to this endpoint whenever there's a new message for your bot.

    update = request.get_json() #  This line retrieves the JSON data sent by Telegram to your webhook. 
    # This data (update) contains information about the incoming message, such as the sender's chat ID and the message text.

    chat_id = update['message']['chat']['id']
    # chat_id = update['message']['chat']['id']: Extracts the chat ID from the incoming update. 
    # The chat ID is used to send replies back to the correct Telegram chat.

        # Check if 'text' key exists in the message dict
    if 'text' in update['message']:
        text = update['message']['text']

        if text == '/hello':
            send_message(chat_id, 'Hello, World!')
            
    else:
        # If there's no text in the message, you can log it, ignore it, or handle it differently
        print("Received a non-text message")

    return 'Webhook received!', 200



def send_message(chat_id, text):
    """
    def send_message(chat_id, text): This function defines how to send a message back to the user. 
    It takes two parameters: chat_id (to know where to send the message) and text (the content of the message to send).
    """

    url = TELEGRAM_API_URL + 'sendMessage'
    # url = TELEGRAM_API_URL + 'sendMessage': Constructs the API request URL for sending a message through the Telegram Bot API. 
    # TELEGRAM_API_URL should be the base URL for the Telegram API, including your bot's token.

    payload = {'chat_id': chat_id, 'text': text}
    # payload = {'chat_id': chat_id, 'text': text}: Prepares the data to be sent in the API request. 
    # This includes the chat_id to reply to and the text of the message you want to send.

    requests.post(url, json=payload)
    # requests.post(url, json=payload): Sends a POST request to the Telegram API with the constructed URL and payload. 
    # This request tells Telegram to send your message to the specified chat.




"""
When deploying webhooks in production, consider security best practices such as
validating incoming requests, using HTTPS, and possibly implementing authentication 
or verification mechanisms to ensure that incoming data is from trusted sources.

Setting Webhooks:
# https://api.telegram.org/botYOUR_TELEGRAM_TOKEN/setWebhook?url=https://your-app-name.herokuapp.com/webhook
# https://api.telegram.org/bot6355794369:AAHnqUS6p8K4xVFkryZFmmmpF4LBG-gzyv4/setWebhook?url=https://telebot-test-59f8f075f509.herokuapp.com/webhook
# ^ this worked, 
# {"ok":true,"result":true,"description":"Webhook was set"}

# https://api.telegram.org/bot6355794369:AAHnqUS6p8K4xVFkryZFmmmpF4LBG-gzyv4/getWebhookInfo


"""



# test 
# curl -X POST https://telebot-test-59f8f075f509.herokuapp.com/webhook -H "Content-Type: application/json" -d '{"key":"value"}'
# Webhook received!%                                                                                                                                              

if __name__ == '__main__':
    app.run()


