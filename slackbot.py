# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from collections import namedtuple
import json
import logging
import time
from collections import namedtuple

from slackclient import SlackClient

CommandBody = namedtuple('CommandBody','action help')

botcheck = '' #<@' + s['bot']['id'] + '>: '
s = {}
sclient = {}

"""{	 u'channel': u'G1FS1CJ84',
	u'team': u'T05311JTT',
	u'text': u'<@U1FRJ3WMU>: lol',
	u'ts': u'1465583194.000034',
	u'type': u'message',
	u'user': u'U0LJ6Q4S0'}"""	 ### Typical structure of a command packet

def help(msg):
	global sclient
	output = sclient.api_call('chat.postMessage', as_user='true', channel=msg['channel'], 
						text=commands["help"].help)
	logging.debug(output)

commands = { }

def generateHelp():
	global commands
	helptext = 'Commands are:\n'
	for c in commands:
		helptext += "\t" + botcheck + commands[c].help + "\n"
	helptext += "\t" + botcheck + "help [this help text]\n"
	commands['help'] = CommandBody(action=help, help=helptext )


def get_bot_id():
	global sclient
	global s
	global botcheck
	api_call = sclient.api_call("users.list")
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
	global sclient
	### hardcode the interval to 3 seconds
	now = int(time.time())
	if last + 3 < now:
		sclient.server.ping()
	return now

def setup(settingsFilePath='settings.json'):
	global s
	with file(settingsFilePath, 'r') as settingsfile:
		s = json.load(settingsfile)

def addCommand(command, action, help):
	global commands
	commands[command] = CommandBody( action=action, help=help )


def sendReply(msg):
	text = msg['text'][len(botcheck):]
	pos = len(text)
	try:
		pos = text.index(' ')
	except ValueError:
		pass

	cmd = text[:pos] # grab command string up to first space
	logging.info('cmd ="' + cmd + '"')
	if cmd in commands:
		commands[cmd].action(msg)

def monitor():
	global sclient
	sclient = SlackClient(s["token"])

	logging.info("Connecting as " + s["bot"]["name"])
	if sclient.rtm_connect():
		logging.info("...Connected!")
		logging.debug( get_bot_id() )
		generateHelp()
		last_ping = int(time.time())
		while True:
			messages = sclient.rtm_read()
			#logging.debug(messages)
			last_ping = autoping(last_ping)
			for message in messages:
				if all(k in message for k in ('type','text')) \
							and message['type'] == 'message' \
							and 'bot_id' not in message \
							and botcheck in message['text']:
					logging.debug(message)
					sendReply(message)
			time.sleep(1)
	else:
		logging.info("Connection Failed, invalid token?")
		