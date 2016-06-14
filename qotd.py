#!/usr/bin/python
# Licensed under the terms of the MIT License

import time
import json
import datetime
import random
from slackclient import SlackClient

s = None

sFile = open('settings.json')
s = json.load(sFile)
sFile.close()

botcheck = '<@' + s['bot']['id'] + '>: '

f = open('quotes.csv','r')
quotes = []
for line in f:
	quotes.append( line.split('|||')[0] )
f.close()	

f = open('attributions.csv','r')
attributions = []
for line in f:
	attributions.append( line.replace('\n','') )
f.close()	


#Slack formatting
#*bold* `code` _italic_ ~strike~

def addQuote(chan, msg):
	l = len(s["bot"]["id"]) + 4
	q = msg['text'][l:].replace('"','').replace('|||',' ')
	f = open('quotes.csv','a')
	f.write("\n" + q + '|||' + msg['user'] + '|||' + str(datetime.datetime.utcnow()))
	f.close()
	quotes.append(q)
	print sc.api_call('chat.postMessage', as_user='true', channel=chan, text='\t_*"' + q + '"*_\n\tQuote added. High Five <@' + msg['user'] + '>!')

def printQuote(chan, msg):
	print sc.api_call('chat.postMessage', as_user='true', channel=chan, text='\t' + random.choice(attributions) + ':\n\t\t_*"' + random.choice(quotes) + '"*_')

def listQuotes(chan, msg):
	mylist = '';
	for q in quotes:
		mylist += '\t_*' + q + '*_\n'
	print sc.api_call('chat.postMessage', as_user='true', channel=chan, text='\t' + mylist + '\n\n\t' + str(len(quotes)) + ' total quotes.')

def help(chan, msg):
	print sc.api_call('chat.postMessage', as_user='true', channel=chan, text=helptext + '\n\t' + str(len(quotes)) + ' total quotes.')

commands = [
#{'command':s["bot"]["id"]+'are you alive', 'response':'_*Yes, I\'m ALLLIIIVE*_'},
{'command':botcheck+'quote', 'action':printQuote, 	'help':botcheck+'quote [prints random quote], or by "lol"' },
{'command':botcheck+'add',   'action':addQuote, 		'help':botcheck+'add <some witty quote I want to add>' },
{'command':botcheck+'list',  'action':listQuotes, 	'help':botcheck+'list [prints out all quotes]' },
{'command':botcheck+'help',  'action':help, 			  'help':botcheck+'help [this help text]'}
]

helptext = 'Greetings traveler! Commands are:\n'
for c in commands:
	helptext += "\t" + c['help'] + "\n"
commands[len(commands)-1]['response'] = helptext


def sendReply(chan, msg):
	if 'lol' in msg['text']:
		commands[0]['action'](chan, msg)
		return
		
	for command in commands:
		if command['command'] in msg['text']:
			command['action'](chan, msg)

sc = SlackClient(s["token"])

if sc.rtm_connect():
    while True:
        messages = sc.rtm_read()
        #print messages
        for message in messages:
        	#print message
        	if all(k in message for k in ('type','text')) and message['type'] == 'message' and 'bot_id' not in message and any(j in message['text'] for j in (botcheck,'lol')):
        		print message
        		sendReply(message['channel'], message)
        time.sleep(1)
else:
    print "Connection Failed, invalid token?"
    
