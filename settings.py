# settings button mapping;


"""
Architecture / Functionality:
- /settings: gives instructions for manual setting, but is mainly for overview.

- /group_settings: can be called by anyone, but options are limited to administrators of the given group chat.
- /user_settings: can only be called by direct messaging to the bot for each unique user it will be different.
"""

settings_string = """Customize telebot with the following options:

-- Button Settings --
/group_settings - customize how the bot functions within a group setting, only available to administrators.
/user_settings - customize and personalize how the bot functions or responds to your requests across all interactions.

-- Manual (typed) Settings --
/user_set_openai_key [sk-abcdefg...] - set the openai api key for yourself (works across all groups)
/chat_set_openai_key [sk-abcdefg...] - set the openai api key for your group
"""

group_settings_string = """Customize how your assistant functions in this group:

-- Button Settings --
Persistence - customize whether your bot remembers the conversation history of this group and remains context aware.
Language Model - choose which language model your assistant will use to complete your chat requests.

-- Manual Settings --
/lm_temp [0-2] - customize sampling temperature, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
"""


user_settings_string = """PLACEHOLDER

"""




lm_settings_string = """Customize how your assistant functions in this group:

-- Button Settings --
Persistence - customize whether your bot remembers the conversation history of this group and remains context aware
Temperatue - customize sampling temperature, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
Language Model - 
Image Generation Model - 

-- Manual Settings --
"""





