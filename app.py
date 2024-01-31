from flask import Flask, request



app = Flask(__name__)

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
    data = request.json  # Extract the data from the incoming request
    print(data)  # Log or process the data
    return 'Webhook received!', 200  # Respond to the sender


if __name__ == '__main__':
    app.run()
