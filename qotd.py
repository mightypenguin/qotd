#!/usr/bin/python
# -*- coding: utf-8 -*-
# Licensed under the terms of the MIT License
from __future__ import division
from __future__ import unicode_literals

import time
import logging
import json
import datetime
import random

from slackclient import SlackClient

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

with file('settings.json', 'r') as settingsfile:
	s = json.load(settingsfile)

with file('quotes.json', 'r') as quotesfile:
	quotes = [json.loads(line) for line in quotesfile.readlines()]

with file('attributions.csv', 'r') as attributionsfile:
	attributions = [line.strip() for line in attributionsfile.readlines()]

botcheck = '<@' + s['bot']['id'] + '>: '

#Slack formatting
#*bold* `code` _italic_ ~strike~

def get_bot_id():
	api_call = sc.api_call("users.list")
	if api_call.get('ok'):
		# retrieve all users so we can find our bot
		users = api_call.get('members')
		for user in users:
			if 'name' in user and user.get('name') == s["bot"]["name"]:
				s["bot"]["id"] = user.get('id')
				botcheck = '<@' + s['bot']['id'] + '>: '
				return ({ user['name']:user.get('id') })
	else:
		return "could not find bot user with the name " + s["bot"]["name"]

def autoping(last):
	### hardcode the interval to 3 seconds
	now = int(time.time())
	if last + 3 < now:
		sc.server.ping()
	return now

def addQuote(chan, msg):
	l = len(botcheck) + 4
	q = {}
	q["quote"] = msg['text'][l:].strip('"“')
	logging.info('Quote is: ' + q["quote"])
	q["user"]	= msg['user']
	q["time"]	= str(datetime.datetime.utcnow())

	f = open('quotes.json','a')
	f.write("\n" + json.dumps(q))
	f.close()
	
	quotes.append(q)
	output = sc.api_call('chat.postMessage', as_user='true', channel=chan, 
						text='\t_*"' + q["quote"] + '"*_\n\tQuote added. High Five <@' + msg['user'] + '>!')
	logging.debug(output)

def printQuote(chan, msg):
	output = sc.api_call('chat.postMessage', as_user='true', channel=chan, 
						text='\t' + random.choice(attributions) + ':\n\t\t_*"' + random.choice(quotes)["quote"] + '"*_')
	logging.debug(output)

def listQuotes(chan, msg):
	mylist = 'Quotes:\n';
	for q in quotes:
		mylist += '\t_*' + q["quote"] + '*_\n'
	output = sc.api_call('chat.postMessage', as_user='true', channel=chan, 
						text=mylist + '\n\n\t' + str(len(quotes)) + ' total quotes.')
	logging.debug(output)

def help(chan, msg):
	output = sc.api_call('chat.postMessage', as_user='true', channel=chan, 
						text=helptext + '\n\t' + str(len(quotes)) + ' total quotes.')
	logging.debug(output)

commands = {
	#{'command':s["bot"]["id"]+'are you alive', 'response':'_*Yes, I\'m ALLLIIIVE*_'},
	'quote':{ 'action':printQuote, 	'help':'quote [prints random quote], or by "lol"' },
	'add':	{ 'action':addQuote, 	'help':'add <some witty quote I want to add>' },
	'list': { 'action':listQuotes, 	'help':'list [prints out all quotes]' },
	'help': { 'action':help, 		'help':'help [this help text]' }
}

helptext = 'Greetings traveler! Commands are:\n'
for c in commands:
	helptext += "\t" + botcheck + commands[c]['help'] + "\n"
commands['help']['response'] = helptext


"""{	 u'channel': u'G1FS1CJ84',
	u'team': u'T05311JTT',
	u'text': u'<@U1FRJ3WMU>: lol',
	u'ts': u'1465583194.000034',
	u'type': u'message',
	u'user': u'U0LJ6Q4S0'}"""	 ### Typical structure of a command packet

def sendReply(chan, msg):
	text = msg['text']

	if 'lol' in text:
		commands['quote']['action'](chan, msg)
		return

	text = text[len(botcheck):]
	pos = len(text)
	try:
		pos = text.index(' ')
	except ValueError:
		pass

	cmd = text[:pos] # grab command string up to first space
	logging.info('cmd ="' + cmd + '"')
	if cmd in commands:
		commands[cmd]['action'](chan, msg)

sc = SlackClient(s["token"])

logging.info("Connecting as " + s["bot"]["name"])
if sc.rtm_connect():
	logging.info("...Connected!")
	logging.debug( get_bot_id() )
	last_ping = int(time.time())
	while True:
		messages = sc.rtm_read()
		#logging.debug(messages)
		last_ping = autoping(last_ping)
		for message in messages:
			if all(k in message for k in ('type','text')) \
						and message['type'] == 'message' \
						and 'bot_id' not in message \
						and any(j in message['text'] for j in (botcheck,'lol')):
				logging.debug(message)
				sendReply(message['channel'], message)
		time.sleep(1)
else:
	logging.info("Connection Failed, invalid token?")
	