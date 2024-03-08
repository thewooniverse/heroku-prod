

# Database Architecture:
telebot postgres database structure

## chat configs
Contains all of the configurations for each chat;
(CHAT_ID:BIGINT, {config:JSONB})


## eventstream
Eventually will house all key events and entries

## usage logs





# User flow

1. ALL command handlers checks for configurations at the beginning of the handler;
2. If the handler does not find a matching record for the given chat_id in chat_configs table attached Herokue PostgreSQL database, a new entry into the chat_configs table in the Heroku PostgreSQL database is entered with the chat_id and the default configs. Then, this configuration is read and used to handle the rest of the command. If an existing configuration is found, it skips the first part of creating a new entry with default logs and simply reads and uses the configs to handle the command.
3. Users who are admins of the given telegram chat / chat_id are able to change the configuration of the bot's behaviour within the group.




# Premium vs Non premium
A user can have a premium membership
A chat group can also have a premium membership

A user with a premium membership can use premium configurations regardless of the group's membership tier.
A user without a premium membership inside a group with a premium membership, can use premium features inside that group.

So then the config checks for:
-> is the user a premium?
-> is the group a premium?
--> all configs are saved for an individual level? Or for a chat group.
--> all conversation logs are saved on a group level and NOT a individual level (so as to not run itno issues with creating multiple agents with persistence)


Is it going to be two different configs? Or no, how will the checking work against it? How will the configuration be structured?
chat_id, sender user_id.
When a connection is made to the database, both of the configurations are retrieved
