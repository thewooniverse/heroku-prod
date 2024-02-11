
# setting up the webhook for prod and staging
# curl --http1.1 -F "url=https://telebot-prod-2f34e594e894.herokuapp.com/webhook" https://api.telegram.org/bot6355794369:AAHnqUS6p8K4xVFkryZFmmmpF4LBG-gzyv4/setWebhook
# curl --http1.1 -F "url=https://telebot-staging-cf8f61dc178a.herokuapp.com/webhook" https://api.telegram.org/bot6734553403:AAF60yWJI_aFjn4A47hDKnmKv-7FSrRH-lQ/setWebhook <<< this was the hard reset



## Old hardcoded telegram webhook.
# def set_telegram_webhook():
#     # bot.remove_webhook()
#     # bot.set_webhook(url=WEBHOOK_URL)
#     url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={WEBHOOK_URL}'
#     response = requests.get(url)
#     print(response.text)
#     if response.status_code == 200 and response.json().get('ok'):
#         print("Webhook set successfully")
#     else:
#         print("Failed to set webhook")        

# # @app.before_first_request << has been deprecated, replaced with the below solution app.app_context()
# with app.app_context():
#     print(DYNO_NAME)
#     set_telegram_webhook()
# # Flask routes and other configurations follow...
