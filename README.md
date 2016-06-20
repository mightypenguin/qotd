### Setup
* Setup bot account (https://api.slack.com/bot-users)
* Create API token (https://get.slack.help/hc/en-us/articles/215770388-Creating-and-regenerating-API-tokens)
* Add token id to settings.json
* Add bot username to settings.json (id will be automatically detected)
* Add bot to a channel by inviting it once you authorize the bot for your slack group.
* run: pip install slackclient
* Create quotes.json file (See quotes.json_example, each line is it's own JSON object, not a global list)

### Starting:
 python qotd.py

### Usage:
  * @botname: help
  * @botname: quote
  
      or a message contains "lol", print out a random quote.

### Version
0.0.1

### Tech

* python v2.7.10 (tested)
* slackclient (https://github.com/slackhq/python-slackclient)

### Contributors
* @mightypenguin
* @marcinpohl

