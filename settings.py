# settings button mapping;



getting_started_string = """
All new accounts get a free trial of 10 free requests before being required to enter their own OpenAI API Key.

<b>Chat Functionality</b>
/chat [prompt] - replies with AI response to the prompt, based on several parameters.
- In-reply context: simplest way to provide context, replying to a text message will provide the message that the /chat request is in reply to as context for the request.
- User context: set in user_settings, context that user set for all chat requests from the user. Things like "my name is Jon Applepeel".
- Chat context: set in chat groups, context that the user wants to keep in mind for a specific chat group or thread. Things like "You are an expert fitness chef, for all recipes please answer with exact measurements and estimated calories"
- Chat history / persistence: premium feature that allows users to have all of their /chat and other conversations within a chat thread / group with the bot and used as context and history for all future chat requests.

/vision [in-reply to image + prompt] - image recognition powered chat completion. Embeddings from provided image as primary context. Useful for things like "What is this menu in English?"

/t1/t2/t3 [prompt] - translates the prompted text into the preset languages. 
e.g. if /t1 is set to english, any other text in any languages as prompt to /t1 will translate it to English.

<b>Voice Functionality</b>
/tts [prompt] - text-to-speech, narrate and read out the prompt provided.
/stt [in reply to a voice note] - speech-to-text, transcribe the voice note into text
/stc [in reply to a voice note]- speech-to-chat, transcribe the voice note and use it as a prompt for chat completion.
/sts [in reply to a voice note] - speech-to-speech(chat), transcribe the voice note, use it as a prompt for chat completion, and send the chat completion response in a voice message.
"Hey Telebot" (in development) - voice activated /stc feature, without needing to type, send a voice note with your prompt starting with the trigger word set to generate a chat completion request.


<b>Image Functionality</b>
/imagine [prompt] - generate image, using image models. Default is Dall-E 3.
/variate [in-reply-to-image] - generate variations of image that the request is in reply to.
/edit_img [in-reply-to-image + mask settings + prompt] - generate an edited version of the image, based on the prompt, the image mask area targeting the area of the image that you want to edit.

<b>Configurations:</b>
/user_settings - configure how your bot behaves with ALL of your interactions over different groups and chat threads.
/group_settings - configure how your bot behaves to your requests in a given chat group. Useful for creating multiple conversations for different topics with the bot.
"""



settings_string = """⚙️<b>TeleGPT Settings</b>⚙️

<b>Customize telebot with the following options:</b>

/group_settings - Only available to administrators of groups. Customize how the bot functions within a group setting. 
/user_settings - Only available by DM-ing the bot. Customize and personalize how the bot functions or responds to your requests across all interactions with the bot.
"""

group_settings_string = """👥<b>Chat Group Settings</b>👥

Customize how your assistant functions in this group (DM covnersation is also considered a group):
All settings and configurations for a group is ONLY availble to be changed by the administrator of the group / chat;
To customize new bots with new configurations and settings, you can create new groups and invite the bot in to customize different chat threads with the bot.

<b>-- Button Settings --</b>
Persistence ON or OFF - Premium users only. ON - your /chat queries remain context aware, and your /chat conversations with the bot in this group is saved for context.
Along with context - this is useful for creating different conversation threads with the bot with persistent memory for different topics.

Language Models - choose which language model your assistant will use to complete your chat requests.
Language Presets - choose which languages /t1 /t2 /t3 translate to for each group.

Agent Voice - choose which voice you would like your AI to respond to you in speech requests.

<b>-- Manual Settings --</b>
/set_context [200 words] - Set the context for yourself in the given chatgroup. You can set things like what you want this conversation to be about, or what you want the bot to call you or remember.
This is a more lightweight version to pass your bot some persistent context

/set_temperature [0-2] - set sampling temperature, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
/chat_set_openai_key [sk-abcdefg...] - set the openai api key for this group. ONLY USE in public groups when you want to allow other useres to also use your API Key to access Open AI. For most use cases, please set your personal API key in DM with the bot.
"""


user_settings_string = """👤<b>User Settings</b>👤
Customize how your bot responds to your requests (applies to all interactions in any group):

<b>-- Button Settings --</b>
Image Edit Mask - which section of the image
Premium Features - 

<b>-- Manual Settings -</b>
/set_context [200 words] - Set the context for yourself across all chat groups. You can set things like what the bot should call you, your preferences.
/user_set_openai_key [sk-abcdefg...] - set the openai api key for yourself (works across all groups)
"""

image_mask_settings_string = """🎨Image Mask Settings🎨

Below is the current image mask settings; 1 is the section of the image where you want to create a mask over to instruct the image model where to edit the image.
"""




lm_settings_string = """💬Language Model Settings💬

GPT 3.5 turbo - Baseline model for OpenAI's ChatGPT. Fast and cheaper.
GPT 4 - Premium model for OpenAI's ChatGPT. Better logic and conversational capabilities.
"""

agent_voice_string = """🎤Agent Voice Menu🎤
Experiment with different voices (alloy, echo, fable, onyx, nova, and shimmer) to find one that matches your desired tone and audience. 
The current voices are optimized for English.
"""






translation_presets_string = """🌐Language Presets🌐
Translations /t1 /t2 /t3 [prompt] translates any prompt entered to a preset language without the need to ask GPT to "translate X into Y"

<b>-- Button Settings --</b>
Press the options below to change your translation language presets to popular language choices.

<b>-- Manual Settings --</b>
For languages not supported in the options below, you can find the 3 character ISO 639-2 code for your desired language and set it manually with the commands below.
Find your lannguage's code on: https://www.loc.gov/standards/iso639-2/php/code_list.php

/t1_set xxx
/t2_set xxx
/t3_set xxx
"""



def construct_translation_preset_string(preset_num):
    return f"""🌐{preset_num}: Language Options🌐
Press the desired language option, press back to see current configuration:
"""











# PREMIUM SUBSCRIPTION STRINGS:

premium_subscription_string = """🌟Premium Features🌟

1. Context Awareness and Persistence 🧠
Bot can now remember what you have said in the past without needing to reply to anything. The context window can now be expanded into everything you've asked of the bot, and its response.

2. Ads-Free 💨
Poof, your ads gone.

3. Image Mask Granualrity and variations🖼️
Multi-image generation, mask targeting granularity.
"""

premium_user_settings_string = """🌟Premium User Settings🌟
Customize how your bot responds to your requests (applies to all interactions in any group):

<b>-- Button Settings --</b>
Granual Image Mask Settings - Image Mask, but with more granular targeting of image sections.
Voice Assistant
"""


premium_image_mask_settings_string = """🌌Granual Image Mask Settings🌌
Below is the current image mask settings; 1 is the section of the image where you want to create a mask over to instruct the image model where to edit the image.
Premium features give you additional granular targeting for image edits.
"""


voice_activation_settings_string = """👤<b>Voice Activated Agent Settings</b>👤
Here you may turn the voice activated agent on or off. Below are the current settings, the agent name is what you need to say in the beginning five words of your voice activated request.
For example, if the default agent name is GPT, this would be:
- "Hey GPT, [request]"
- "GPT, [request]"
- "Good Morning GPT, [request]"

Voice Agent name can be set manually by using the /set_name [name] command, please make it unique and easily and clearly pronouncable!

IMPORTANT NOTE: turning this feature on will increase the frequency of API calls.

"""


