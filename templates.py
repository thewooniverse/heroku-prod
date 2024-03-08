

default_config = {
    "names": {
      "default_user": "user"
    },
    "is_premium": False,
    "persistence": False,
    "language_model": "gpt-3.5-turbo",
    "openai_api_key": "",
    "image_mask_map": [
          [0, 0, 0],
          [0, 0, 0],
          [1, 1, 1]
        ]
  }




start_menu = """Welcome to AB69 - Your persistent telegram based OpenAI interface.
AB69 features configurable almost all up-to-date OpenAI features, as well as persistence and context awareness via vectorstores.
To get started, please configure your OpenAI API Key and use the commands freely below.
---
/start - 
/settings - 
/chat - 
/imagine -
/vision - 
/tts - 
/stt - 
/t1 - 
/t2 - 
/t3 - 
/edit - in reply to an original image, you can send a new command /edit "caption to change the original image accordingly" Optional: Mask image to indicate where in the image to alter.


/clear - 
"""



