#!/usr/bin/python
# -*- coding: utf-8 -*-
# Licensed under the terms of the MIT License
from __future__ import division
from __future__ import unicode_literals

import logging
import json
import datetime
import random
import slackbot as sb

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

with file('quotes.json', 'r') as quotesfile:
    quotes = [json.loads(line) for line in quotesfile.readlines()]

with file('attributions.csv', 'r') as attributionsfile:
    attributions = [line.strip() for line in attributionsfile.readlines()]

sb.setup()

#Slack formatting
#*bold* `code` _italic_ ~strike~


def addQuote(msg):
    l = len(botcheck) + 4
    q = {
        'quote': msg['text'][l:].strip('"“'),
        'user': msg['user'],
        'time': str(datetime.datetime.utcnow())
    }
    logging.info('Quote is: ' + q["quote"])
    f = open('quotes.json', 'a')
    f.write("\n" + json.dumps(q))
    f.close()

    quotes.append(q)
    output = sb.sclient.api_call(
        'chat.postMessage',
        as_user='true',
        channel=msg['channel'],
        text='\t_*"' + q["quote"] + '"*_\n\tQuote added. High Five <@' +
        msg['user'] + '>!')
    logging.debug(output)


def printQuote(msg):
    output = sb.sclient.api_call(
        'chat.postMessage',
        as_user='true',
        channel=msg['channel'],
        text='\t' + random.choice(attributions) + ':\n\t\t_*"' +
        random.choice(quotes)["quote"] + '"*_')
    logging.debug(output)


def listQuotes(msg):
    mylist = 'Quotes:\n'
    for q in quotes:
        mylist += '\t_*' + q["quote"] + '*_\n'
    output = sb.sclient.api_call(
        'chat.postMessage',
        as_user='true',
        channel=msg['channel'],
        text=mylist + '\n\n\t' + str(len(quotes)) + ' total quotes.')
    logging.debug(output)

# Help command is auto added
sb.addCommand('quote', printQuote, 'quote [prints random quote]')
sb.addCommand('add', addQuote, 'add <some witty quote I want to add>')
sb.addCommand('list', listQuotes, 'list [prints out all quotes]')

# Begin monitoring the channel and respond when a command is triggered, this call blocks
sb.monitor()
