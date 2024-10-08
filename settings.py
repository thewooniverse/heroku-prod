# settings button mapping;
"""
Command Descriptions
- sample syntax
command1 - Description
command2 - Another description
-
start - welcome message
settings - settings overview
group_settings - for this conversation
user_settings - for all conversations
chat - [prompt, reply to (optional)] chat completion
t1 - [prompt] translate to preset 1
t2 - [prompt] translate to preset 2
t3 - [prompt] translate to preset 3
tts - [prompt] text to speech
stt - [reply_to_voice] speech to text
stc - [reply_to_voice] speech to chat
stsc - [reply_to_voice] speech to speech-chat
imagine - [prompt] image generation
vision - [reply_to_image, prompt] image recognition
variate - [reply_to_image] image variation
edit_img - [reply_to_image, prompt] image editing
set_name - [text] set agent's name for voice assistant
user_set_openai_key - [key] set api key for all conversations
group_set_openai_key - [key] set api key for this conversation
set_temperature - [0-2] set agent temperature for this conversation
set_t1 - [ABC] manually set t1 to iso code
set_t2 - [ABC] manually set t2 to iso code
set_t3 - [ABC] manually set t3 to iso code
set_context - [context] set chat agent's context for conversation
set_user_context - [context] set chat agent's context all conversations
reset_context - reset the agent's context for conversation
reset_user_context - reset the agent's context for all conversations
check_context - check the current context set for user and group
clear_history - clear history for this conversation
subscribe - subscribe to premium features
"""






getting_started_string = """<b>🤖 Welcome to TeleGPT! 🤖 </b>

TeleGPT is an AI assistant built right into telegram, use the various AI Models from OpenAI with additional features in the comfort of a messaging app!

Get started by simply typing / and explore the various commands with TeleGPT.
For detailed guides, visit https://technosocial-systems.gitbook.io/telegpt
"""


settings_string = """⚙️<b>TeleGPT Settings</b>⚙️
<b>Customize telebot with the following options:</b>
/group_settings - set the behaviour of the bot in this current group / conversation
/user_settings - set the behaviour of the bot towards all requests coming from you, in all conversations.

For more information on manual settings options, visit: https://technosocial-systems.gitbook.io/telegpt/features/configurations/manual-settings
"""

group_settings_string = """👥<b>Chat Group Settings</b>👥
Configure how TeleGPT interacts with you in this group specifically.

- Persistence - your /chat conversations have persistence going forward, all new chat requests will be used as context for future chat requests.
- Language Models - choose which language model your assistant will use to complete your chat requests.
- Language Presets - choose which languages /t1 /t2 /t3 translate to for each group.
- Agent Voice - choose which voice you would like your AI to respond to you in speech requests.
"""

user_settings_string = """👤<b>User Settings</b>👤
Configure how your bot responds to your requests (applies to all interactions in any group):

- Image Edit Mask - which section of the image to be targeted when you cal; /edit_img
- Premium Features:
-- Granualar Image Mask - granular targeting mask of which area of the image to be edited
-- Voice Assistant - turn voice activated bot on or off, set the agent name with /set_name [name]
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

2. Voice Activated Agent 🗣️
Bot can respond to your voice message that calls the agent name like "Hey Steve, who won the olympics in 1988?"

3. Ads-Free 💨
Poof, your ads gone.

4. Image Mask Granualrity and variations🖼️
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






user_context_string = "USER CONTEXT: The following is the user's instructions for you on how you should behave as an agent, use it as the most important / highest priority context in your interaction:\n"
chat_context_string = "CHAT CONTEXT: The following is the user's instructions for you on how you should behave as an agent WITHIN this conversation:\n"

