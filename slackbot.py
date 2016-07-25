# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from collections import namedtuple
import json
import logging
import time
from collections import namedtuple

from slackclient import SlackClient


class SlackBot(object):
    def __init__(self, settingsFilePath='settings.json'):
        self.s = {}
        self.sclient = {}
        ### Not necessary, moved to settings?
        # self.botcheck = ''  #<@' + s['bot']['id'] + '>: '
        with file(settingsFilePath, 'r') as settingsfile:
            self.s = json.load(settingsfile)

        logging.debug(self.s)
        self.lastping = int(time.time())
        self.sclient = SlackClient(self.s["token"])

        self.CommandBody = namedtuple('CommandBody', 'action help')
        self.botcheck = ''  # <@' + s['bot']['id'] + '>: '
        self.commands = {}

#"""{	 u'channel': u'G1FS1CJ84',
#    u'team': u'T05311JTT',
#    u'text': u'<@U1FRJ3WMU>: lol',
#    u'ts': u'1465583194.000034',
#    u'type': u'message',
#    u'user': u'U0LJ6Q4S0'}"""  ### Typical structure of a command packet


    def help(self, msg):
        output = self.sclient.api_call('chat.postMessage',
                                as_user='true',
                                channel=msg['channel'],
                                text=self.commands["help"].help)
        logging.debug(output)

    def generateHelp(self):
        helptext = 'Commands are:\n'
        for c in self.commands:
            helptext += "\t" + self.botcheck + self.commands[c].help + "\n"
        helptext += "\t" + self.botcheck + "help [this help text]\n"
        self.commands['help'] = self.CommandBody(action=self.help, help=helptext)


    def get_bot_id(self):
        api_call = self.sclient.api_call("users.list")
        if api_call.get('ok'):
            # retrieve all users so we can find our bot
            users = api_call.get('members')
            for user in users:
                if 'name' in user and user.get('name') == self.s["bot"]["name"]:
                    self.s["bot"]["id"] = user.get('id')
                    self.botcheck = '<@' + self.s['bot']['id'] + '>: '
                    return ({user['name']: user.get('id')})
        else:
            return "could not find bot user with the name " + s["bot"]["name"]


    def autoping(self,last):
        ### hardcode the interval to 3 seconds
        now = int(time.time())
        if last + 3 < now:
            self.sclient.server.ping()
        return now


    def addCommand(self, command, action, help):
        self.commands[command] = self.CommandBody(action=action, help=help)

    def sendReply(self, msg):
        text = msg['text'][len(self.botcheck):]
        pos = len(text)
        try:
            pos = text.index(' ')
        except ValueError:
            pass

        cmd = text[:pos]  # grab command string up to first space
        logging.info('cmd ="' + cmd + '"')
        if cmd in self.commands:
            self.commands[cmd].action(msg)


    def monitor(self):
        #self.sclient = SlackClient(s["token"])

        logging.info("Connecting as " + self.s["bot"]["name"])
        if self.sclient.rtm_connect():
            logging.info("...Connected!")
            logging.debug(self.get_bot_id())
            self.generateHelp()
            last_ping = int(time.time())
            while True:
                messages = self.sclient.rtm_read()
                # logging.debug(messages)
                last_ping = self.autoping(last_ping)
                for message in messages:
                    if all(k in message for k in ('type', 'text')) \
                            and message['type'] == 'message' \
                            and 'bot_id' not in message \
                            and self.botcheck in message['text']:
                        logging.debug(message)
                        self.sendReply(message)
                time.sleep(1)
        else:
            logging.info("Connection Failed, invalid token?")
