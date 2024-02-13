#!/bin/bash

# Access environment variables
TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
ROOT_URL=${ROOT_URL}  # Ensure this is set in Heroku's Config Vars


# Set the webhook
curl -F "url=${ROOT_URL}/webhook" https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook
echo "Webhook set response: $response"

# Start the Flask Application
gunicorn app:app