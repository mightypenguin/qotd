#!/usr/bin/python
# -*- coding: utf-8 -*-
# Licensed under the terms of the MIT License

"""
Setup:
# pip install slackclient
Copy your slack bot token into bot_token.txt
Create quotes.csv file.

Starting:
# python qotd.py

Add bot to a channel by inviting it once you authorize the bot for your slack group.
"""

import datetime
import json
import logging
import random
import time

from slackclient import SlackClient

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def MPsetup():
    BOT_NAME = 'mpqotd'
    botuid = '<@U0LJ6Q4S0>: ' #  @mpqotd
    token = 'xoxb-49868132742-2Pgt5bXPkSm1GCxhc3ZJg3nj'  ### bot token for @mpqotd
    return BOT_NAME, botuid, token


def MBsetup():
    botuid = '<@U1F54AWA3>: ' #  @qotd:
    with file('settings.json', 'r') as settingsfile:
        s = json.load(settingsfile)
    BOT_NAME = '<@' + s['bot']['id'] + '>: '

    with file('bot_token.txt', 'r') as tokenfile:
        token = tokenfile.read()
    return BOT_NAME, botuid, token


with file('quotes.json', 'r') as quotesfile:
    quotes = [json.loads(line) for line in quotesfile]

### with quotes being JSON, why dont we integrate the attribution of the quote into it?
with file('attributions.csv', 'r') as attributionsfile:
    attributions = [line.strip() for line in attributionsfile]

credsetup = MPsetup

(BOT_NAME, botuid, token) = credsetup()


### Slack formatting
### *bold* `code` _italic_ ~strike~

def get_bot_idA():
    global BOT_NAME
    api_call = sc.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                ### This is the only diff between our get_bot_io functions, what does it do?
                BOT_NAME = user.get('id')
                return { user['name']:user.get('id') }
    else:
        return "could not find bot user with the name " + BOT_NAME


def get_bot_idB():
    api_call = sc.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            ### This will return on the first found user, what if there's multiple?
            if 'name' in user and user.get('name') == BOT_NAME:
                return { user['name']:user.get('id') }
    else:
        return "could not find bot user with the name " + BOT_NAME


### Just to try out different implementations
get_bot_id = get_bot_idB


def addQuote(msg):
    q = dict()
    q["quote"] = msg['text'].strip('"“')
    q["user"] = msg['user']
    q["time"] = str(datetime.datetime.utcnow())
    logging.info('Quote is: ' + q["quote"])
    with file('quotes.csv', 'a') as quotesfile:
        logging.debug(" TRYING TO ADD CONTENT\n" + json.dumps(q))
        quotesfile.write("\n" + json.dumps(q))
    quotes.append(q)
    output = sc.api_call('chat.postMessage', as_user='true', channel=chan,
                         text='\t_*"' + q["quote"] + '"*_\n\tQuote added. High Five <@' + msg['user'] + '>!')
    logging.debug(output)


def autoping(last, msg):
    ### hardcode the interval to 3 seconds
    now = int(time.time())
    if last + 3 < now:
        sc.server.ping()
    return now


def printQuote(msg):
    output = sc.api_call('chat.postMessage', as_user='true', channel=msg['channel'],
                         text='\t' + random.choice(attributions) + ':\n\t\t_*"' + random.choice(quotes)[
                             "quote"] + '"*_')
    logging.debug(output)


def listQuotes(msg):
    mylist = '\n'.join('\t_*' + q["quote"] + '*_' for q in quotes if q is not None)
    output = sc.api_call('chat.postMessage', as_user='true', channel=msg['channel'],
                         text='\t' + mylist + '\n\n\t' + str(len(quotes)) + ' total quotes.')
    logging.debug(output)


def ping(msg):
    logging.debug('calling ping()')
    output = sc.api_call('chat.postMessage', as_user='true', channel=msg['channel'], text="PONG!!!\n")
    logging.debug(output)


def help(msg):
    output = sc.api_call('chat.postMessage', as_user='true', channel=msg['channel'],
                         text=helptext + '\n\t' + str(len(quotes)) + ' total quotes.')
    logging.debug(output)


commands = {
    #{'command':s["bot"]["id"]+'are you alive', 'response':'_*Yes, I\'m ALLLIIIVE*_'},
    ### This descriptive format is not consistant,  why do outputs are in [] and params in <>?
    'lol'  :{ 'action':printQuote, 'help':'lol [prints random quote]' },
    'quote':{ 'action':printQuote, 'help':'quote [prints random quote]' },
    'add'  :{ 'action':addQuote, 'help':'add <some witty quote I want to add>' },
    'list' :{ 'action':listQuotes, 'help':'list [prints out all quotes]' },
    'help' :{ 'action':help, 'help':'help [prints this help text]' },
    'ping' :{ 'action':ping, 'help':"ping [pings back, letting you know it's alive]" },
}

helptext = 'Greetings traveler! Commands are:\n'
for c in commands:
    helptext += "\t" + BOT_NAME + commands[c]['help'] + "\n"
commands['help']['response'] = helptext

"""{   u'channel': u'G1FS1CJ84',
u'team': u'T05311JTT',
u'text': u'<@U1FRJ3WMU>: lol',
u'ts': u'1465583194.000034',
u'type': u'message',
u'user': u'U0LJ6Q4S0'}"""   ### Typical structure of a command packet


def sendReply(msg):
    msgcontent = msg['text']

    ### Disabled the general LOL detector for the time being
    # if 'lol' in text:
    #     commands['quote']['action'](chan, msg)
    #     return

    logging.debug("msgcontent ::: %s" % msgcontent)
    ### Splits the username from commands+params
    fromuser, _, cmdparams = msgcontent.partition(' ')
    ### Splits the cmdparams into cmd and params
    cmd, _, params = cmdparams.partition(' ')
    logging.info('cmd ="' + cmd + '"')
    if cmd in commands:
        commands[cmd]['action'](msg)


### Different structure for main loop:
# new_evts = sc.rtm_read()
# for evt in new_evts:
#     print(evt)
#     if "type" in evt:
#         if evt["type"] == "message" and "text" in evt:
#             message = evt["text"]


sc = SlackClient(token)
logging.info("Connecting as " + BOT_NAME)
### Should the sc.rtm_connect be inside of try/except?
if sc.rtm_connect():
    logging.info("...Connected!")
    logging.debug("Bot username:userid %s", get_bot_id())
    # logging.debug("BOT_NAME: %s", BOT_NAME)
    last_ping = int(time.time())
    while True:
        messages = sc.rtm_read()
        # logging.debug(messages)
        #last_ping = autoping(last_ping)
        for message in messages:
            # logging.debug(message)
            ### simplify all these conditions into a single call function for readability
            if 'type' in message:
                if message['type'] not in ['presence_change', 'user_typing', 'reconnect_url'] \
                        and 'text' in message \
                        and not message['text'].startswith(botuid) \
                        and 'bot_id' not in message:
                    logging.debug(message)
                    sendReply(message)
        time.sleep(1)
else:
    logging.info("Connection Failed, invalid token?")

