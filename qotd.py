#!/usr/bin/python
# Licensed under the terms of the MIT License

# Setup
# 	pip install slackclient
# Copy your slack bot token into bot_token.txt
# Create quotes.csv file.

# Starting:
# python qotd.py

# Add bot to a channel by inviting it once you authorize the bot for your slack group.
from __future__ import division
from __future__ import unicode_literals

import datetime
import random
import time
from pprint import PrettyPrinter as PP

from slackclient import SlackClient

# botuid = '<@U1F54AWA3>: ' #  @qotd:
BOT_NAME = 'mpqotd'
botuid = '<@U0LJ6Q4S0>: ' #  @mpqotd

# with file('bot_token.txt', 'r') as tokenfile:
#     token = tokenfile.read()
#     '''xoxb-49868132742-2Pgt5bXPkSm1GCxhc3ZJg3nj   bot token for @mpqotd'''
token = 'xoxb-49868132742-2Pgt5bXPkSm1GCxhc3ZJg3nj'
with file('quotes.csv', 'r') as quotesfile:
    quotes = [line.split('|||')[0] for line in quotesfile]

with file('attributions.csv', 'r') as attributionsfile:
    attributions = [line.strip() for line in attributionsfile.readlines()]


#Slack formatting
#*bold* `code` _italic_ ~strike~

def addQuote(chan, msg):
    q = msg['text'].strip('"')
    with file('quotes.csv', 'a') as quotesfile:
        line = ''.join(["\n", q, "|||", msg['user'], "|||", str(datetime.datetime.utcnow())])
        quotesfile.write(line)
    quotes.append(q)
    # l = len(botuid) + 4
    # q = msg['text'][l:].replace('"', '')
    # f = open('quotes.csv', 'a')
    # f.write("\n" + q + '|||' + msg['user'] + '|||' + str(datetime.datetime.utcnow()))
    # f.close()
    # quotes.append(q)
    print sc.api_call('chat.postMessage', as_user='true', channel=chan,
                      text='\t_*"' + q + '"*_\n\tQuote added. High Five <@' + msg['user'] + '>!')


def printQuote(chan, msg):
    print sc.api_call('chat.postMessage', as_user='true', channel=chan,
                      text='\t' + random.choice(attributions) + ':\n\t\t_*"' + random.choice(quotes) + '"*_')


def listQuotes(chan, msg):
    mylist = ['\t_*' + q + '*_\n' for q in quotes if q is not None]
    print sc.api_call('chat.postMessage', as_user='true', channel=chan,
                      text='\t' + mylist + '\n\n\t' + str(len(quotes)) + ' total quotes.')


def help(chan, msg):
    print sc.api_call('chat.postMessage', as_user='true', channel=chan,
                      text=helptext + '.\n\t' + str(len(quotes)) + ' total quotes.')


### :TODO: convert it to a dictionary so we can call commands by name not position in list
commands = [
    #{'command':botuid+'are you alive', 'response':'_*Yes, I\'m ALLLIIIVE*_'},
    { 'command':botuid + 'quote', 'action':printQuote, 'help':botuid + 'quote [prints random quote], or by "lol"' },
    { 'command':botuid + 'add', 'action':addQuote, 'help':botuid + 'add <some witty quote I want to add>' },
    { 'command':botuid + 'list', 'action':listQuotes, 'help':botuid + 'list [prints out all quotes]' },
    { 'command':botuid + 'help', 'action':help, 'help':botuid + 'help [this help text]' }
]

commandsB = { 'quote':(printQuote, botuid + 'quote [prints random quote]'),
              'lol'  :(printQuote, botuid + 'lol [prints random quote]'),
              'add'  :(addQuote, botuid + 'add <some witty quote I want to add, no need for quote marks>'),
              'list' :(listQuotes, botuid + 'list [prints out all quotes]'),
              'help' :(help, botuid + 'help [this help text]'),
              }

helptext = 'Greetings traveler! Commands are:\n'
# for c in commands:
#     helptext += "\t'" + c['help'] + "'\n"
helptext += '\n'.join(["\t'" + c['help'] + "'\n" for c in commands])
#commands[len(commands) - 1]['response'] = helptext
commands[-1]['response'] = helptext


def sendReply(chan, msg):
    if 'lol' in msg['text']:
        commands[0]['action'](chan, msg)
        return

    if command in commands:
        if command['command'] in msg['text']:
            command['action'](chan, msg)

    """{   u'channel': u'G1FS1CJ84',
    u'team': u'T05311JTT',
    u'text': u'<@U1FRJ3WMU>: lol',
    u'ts': u'1465583194.000034',
    u'type': u'message',
    u'user': u'U0LJ6Q4S0'}"""   ### Typical structure of a command packet
    cmd = msg['text']

            #
            # _ = [command['action'](chan, msg) for command in commands if command['command'] in msg['text']]


def send_message(channel_id, message):
    sc.api_call("chat.postMessage",
                channel=channel_id,
                text=message,
                username=BOT_NAME,
                icon_emoji=':robot_face:')


def autoping(last):
    ### hardcode the interval to 3 seconds
    now = int(time.time())
    if last + 3 < now:
        sc.server.ping()
    return now


def get_bot_id():
    api_call = sc.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                return ({ user['name']:user.get('id') })
    else:
        return "could not find bot user with the name " + BOT_NAME


pp = PP(indent=4)
sc = SlackClient(token)

### Different structure for main loop:
# new_evts = sc.rtm_read()
# for evt in new_evts:
#     print(evt)
#     if "type" in evt:
#         if evt["type"] == "message" and "text" in evt:
#             message = evt["text"]


# pp.pprint(sc.api_call("auth.test"))
# while sc.rtm_connect():
if sc.rtm_connect():
    pp.pprint("StarterBot connected and running!")
    pp.pprint(get_bot_id())
    last_ping = int(time.time())
    while True:
        messages = sc.rtm_read()
        #print messages
        last_ping = autoping(last_ping)
        for message in messages:
            if message['type'] not in ['presence_change', 'user_typing']:
                pp.pprint(message)
            if 'type' in message \
                    and message['type'] == 'message' \
                    and 'bot_id' not in message \
                    and (botuid in message['text']
                         or 'lol' in message['text']):
                pp.pprint(message)
                sendReply(message['channel'], message)
        time.sleep(1)
else:
    print "Connection Failed, invalid token?"
    pp.pprint(sc)
