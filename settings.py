# settings button mapping;



getting_started_string = """

Chat Functionality
/chat [query] - 
/t1/t2/t3 - 

Voice Functionality
/tts [text] - text-to-speech function,
/stt [in reply to a speech] - 

Image Functionality

Configurations

"""



settings_string = """⚙️OpenAIssistant Settings⚙️

**Customize telebot with the following options:**

**/group_setting** - Only available to administrators of groups. Customize how the bot functions within a group setting. 
**/user_settings** - Only available by DM-ing the bot. Customize and personalize how the bot functions or responds to your requests across all interactions with the bot.
"""

group_settings_string = """👥Chat Group Settings👥

Customize how your assistant functions in this group (DM covnersation is also considered a group):
All settings and configurations for a group is ONLY availble to be changed by the administrator of the group / chat;
To customize new bots with new configurations and settings, you can create new groups and invite the bot in to customize different chat threads with the bot.

-- Button Settings --
*Persistence ON or OFF* - Premium users only. ON - your /chat queries remain context aware, and your /chat conversations with the bot in this group is saved for context.
Along with context - this is useful for creating different conversation threads with the bot with persistent memory for different topics.

*Language Model* - choose which language model your assistant will use to complete your chat requests.
*Language Presets* - choose which languages /t1 /t2 /t3 translate to for each group.

-- Manual Settings --
*/set_context* [200 words] - Set the context for yourself in the given chatgroup. You can set things like what you want this conversation to be about, or what you want the bot to call you or remember.
This is a more lightweight version to pass your bot some persistent context

*/set_temperature* [0-2] - set sampling temperature, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
*/chat_set_openai_key* [sk-abcdefg...] - set the openai api key for this group. ONLY USE in public groups when you want to allow other useres to also use your API Key to access Open AI. For most use cases, please set your personal API key in DM with the bot.
"""


user_settings_string = """👤User Settings👤

Customize how your bot responds to your requests (applies to all interactions in any group):
-- Button Settings --
*Image Edit Mask* - which section of the image
*Premium Features* - 

-- Manual Settings -
*/set_context* [200 words] - Set the context for yourself across all chat groups. You can set things like what the bot should call you, your preferences.
/user_set_openai_key [sk-abcdefg...] - set the openai api key for yourself (works across all groups)
"""

image_mask_settings_string = """🎨Image Mask Settings🎨
Below is the current image mask settings; 1 is the section of the image where you want to create a mask over to instruct the image model where to edit the image.
"""





lm_settings_string = """💬Language Model Settings💬
GPT 3.5 turbo - Baseline model for OpenAI's ChatGPT. Fast and cheaper.
GPT 4 - Premium model for OpenAI's ChatGPT. Better logic and conversational capabilities.
"""


translation_presets_string = """🌐Language Presets🌐

Translations /t1 /t2 /t3 [prompt] translates any prompt entered to a preset language without the need to ask GPT to "translate X into Y"
-- Button Settings --
Press the options below to change your translation language presets to popular language choices.

-- Manual Settings --
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

premium_subscription_string = """--Premium Features--

1. Context Awareness and Persistence 🧠
Bot can now remember.

2. Ads-Free 💨
Poof, your ads gone.

3. Image Mask Granualrity and variations🖼️
Multi-image generation, mask targeting granularity.
"""

premium_user_settings_string = """🌟Premium User Settings🌟

Customize how your bot responds to your requests (applies to all interactions in any group):
-- Button Settings --
Context Awareness ON or OFF - control whether your bot uses conversation history from the group to search for relevant conversation threads.
Granual Image Mask Settings - Image Mask, but with more granular targeting of image sections.
"""


premium_image_mask_settings_string = """🌌Granual Image Mask Settings🌌
Below is the current image mask settings; 1 is the section of the image where you want to create a mask over to instruct the image model where to edit the image.
Premium features give you additional granular targeting for image edits.
"""

