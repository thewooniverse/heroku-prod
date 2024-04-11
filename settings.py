# settings button mapping;


"""
Architecture / Functionality:
- /settings: gives instructions for manual setting, but is mainly for overview.

- /group_settings: can be called by anyone within the group, but changes to options are limited to administrators of the given group chat.
- /user_settings: can only be called by direct messaging to the bot for each unique user it will be different.

"""



settings_string = """⚙️OpenAIssistant Settings⚙️

Customize telebot with the following options:
/group_settings - Only available to administrators. Customize how the bot functions within a group setting.
/user_settings - Only available by DM-ing the bot. Customize and personalize how the bot functions or responds to your requests across all interactions with the bot.


"""

group_settings_string = """👥Chat Group Settings👥

Customize how your assistant functions in this group (including DMs):
All settings and configurations for a group is ONLY availble to be changed by the administrator of the group / chat;
To customize new bots with new configurations and settings, you can create new groups and invite the bot in to customize different conversations with the bot.

-- Button Settings --
Persistence - customize whether your bot remembers the conversation history of this group and remains context aware.
Language Model - choose which language model your assistant will use to complete your chat requests.

-- Manual Settings --
/lm_temp [0-2] - customize sampling temperature, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
/chat_set_openai_key [sk-abcdefg...] - set the openai api key for your group
"""


user_settings_string = """👤User Settings👤

Customize how your bot responds to your requests (applies to all interactions in any group):
-- Button Settings --
Image Edit Mask - which section of the image

-- Manual (typed) Settings -
/user_set_openai_key [sk-abcdefg...] - set the openai api key for yourself (works across all groups)
"""

lm_settings_string = """💬Language Model Settings💬

GPT 3.5 turbo - Baseline model for OpenAI's ChatGPT. Fast and cheaper.
GPT 4 - Premium model for OpenAI's ChatGPT. Better logic and conversational capabilities.
"""





