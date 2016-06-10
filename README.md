### Setup
* Setup bot account (https://api.slack.com/bot-users)
* Create API token (https://get.slack.help/hc/en-us/articles/215770388-Creating-and-regenerating-API-tokens)
* Update bot_uid.txt file to include your new bot "botname,BOTUID1234".
* Add bot to a channel by inviting it once you authorize the bot for your slack group.
* run: pip install slackclient
* Copy your slack bot token into bot_token.txt
* Create quotes.csv file. ( Delimited with ||| )

### Starting:
 python qotd.py

### Usage:
  * @botname: help
  * @botname: quote
  
      or a message contains "lol", print out a random quote.

### Version
0.0.1

### Tech

* python
* slackbot (https://github.com/slackhq/python-slackclient)
