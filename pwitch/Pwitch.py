#!/usr/bin/env python2.7

import socket
import select
import readline # Remove - Use ncurses instead.
import time
import sys
import os
import re

from .PwitchLogging import *
from .PwitchAdmin import PwitchAdmin
from .PwitchUtils import parent_dir, get_datetime

## Pwitch main module.

## incorporate loyalty points
## Add method to log mod command useage.
## Add game specific commands i.e. Detect game user playing, if user has
## specified commands associated with that game.

## Add way to share banned lists between rooms.

## Enable reconnection if interupted.

class Pwitch(PwitchAdmin):
    def __init__(self,
                username, 
                oauth, 
                channel,
                updateRate=(10/30),
                verbose=False,
                host="irc.twitch.tv",
                port=6667,
                logging=True,
                admin=True,                 ## Change to false.
                userBuffer=False,
                chatCommands=None,
                loyaltyMode=False,
                process_queue=None,
                ):
        """
        Pwitch
        Parent Pwitch package class.

        Parameters:-
        :param username:        Twitch account username.
        :param oauth:           Twitch account OAuth token.
        :param channel:         Twitch IRC room to connect to.
        :param updateRate:      Limit number of connections to twitch server (per sec).
        :param verbose:         Turn on verbose output (Default: False).
        :param host:            The Twitch IRC sever (irc.twitch.tv).
        :param port:            Port to connect to server (6667).
        :param logging:         Toggle chat logging. Options are:
            - True (Log to log/pwitch.db).
            - FILE (log to specified file).
        :param admin:           Enable administration of channel.

        Note: Default stat_rate is 60 seconds.
        Note: updateRate default = 10/30 (30 commands per 10 secs).
        """

        ## Default variable Initialisations/definitions
        self.username = username
        self.oauth = oauth
        self.channel = channel
        self.updateRate = updateRate
        self.verbose = verbose
        self.host = host
        self.port = port
        self.socket = self.connectIRC()
        self.process_queue = process_queue

        ## Optional Logging / Channel administration
        self.logging = logging
        self.admin = admin
        self.chatCommands = chatCommands

        ## PwitchClient variables :: Should be bundled with Client.
        self.mod_only_mode = False      ## Should be in PwitchClient.
        self.userBuffer = userBuffer

    def start(self):
        """
        start

        Helper function; starts the Pwitch bot using user defined options.
        """
        ## Initial channel setup
        self.connected = True
        self.mod_list = self.getMods()

        if self.admin:
            self.admin_object = PwitchAdmin(self.socket, self.channel,
                self.mod_list)
        if self.logging:
            from .PwitchLogging import PwitchLogging
            self._createLogDirectory()
        if self.chatCommands:                       ## rename
            from .PwitchAdmin import PwitchCron

        #try:
        #    self.updateIRC()
        #except KeyboardInterrupt:
        #    pass
        self.updateIRC()

    def connectIRC(self, channel=None):
        """
        connectIRC

        Initialise connection to twitch irc room using class login/oauth.

        Prameters:-
        :param channel:    Twitch IRC room to connect to.
        """

        if not channel:
            channel = self.channel
        channel = "#"+channel

        s = socket.socket()
        s.connect((self.host, self.port))
        s.send("PASS {}\r\n".format(self.oauth).encode("utf-8"))
        s.send("NICK {}\r\n".format(self.username).encode("utf-8"))
        s.send("JOIN {}\r\n".format(channel).encode("utf-8"))
        s.send("CAP REQ :twitch.tv/commands\r\n".encode("utf-8"))
        s.send("CAP REQ :twitch.tv/tags\r\n".encode("utf-8"))
        s.send("CAP REQ :twitch.tv/membership\r\n".encode("utf-8"))
        s.settimeout(None)

        return s

    def updateIRC(self, socket=None):
        """
        updateIRC
        
        Allow connection to Twitch IRC server, and monitor for keywords (i.e.
        banned words / Commands).

        paramers:-
        :param socket:       Socket object returned from connectIRC (i.e. connection
                           to twitch irc servers)
        """

        if not socket:
            socket=self.socket

        while self.connected:
            try:
                self.connected = self.process_queue.get_nowait()
            except:
                pass

            ready = select.select([socket], [], [], self.updateRate)

            if ready[0]:
                response = socket.recv(1024).decode("utf-8")
            else:
                continue
            if response == "PING :tmi.twitch.tv\r\n":
                socket.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            else:
                ## name search groups: 1: mod, 2: name, 3: chat
                ## name searches for chat messages from users.
                name = re.search('.*mod=(\d).*:(.*)!.*\s:(.*)', response,
                        re.I|re.M)
                ## notice = re.search('NOTICE.*:+?(.*)', response, re.M|re.I)

                if self.verbose:
                    ## Store user input into buffer.
                    ## Note: Careful if implement GUI.

                    if self.userBuffer:
                        sys.stdout.write('\r'+' '*(len(readline.get_line_buffer())
                            +len(self.username)+2)+'\r')

                    if name:
                        if name.group(2) == self.channel:
                            print("[B] {}: {}".format(name.group(2),
                                name.group(3)))

                        elif name.group(2) in self.mod_list:
                            print("[M] {}: {}".format(name.group(2),
                                name.group(3)))

                        elif not self.mod_only_mode:
                            print("{}: {}".format(name.group(2), name.group(3)))

                    ## Restores user input from buffer.
                    if self.userBuffer:
                        sys.stdout.write("\r{}: {}".format(self.username,
                            readline.get_line_buffer().lstrip(self.username)))
                        sys.stdout.flush()

                ## Log to sqlite3 database if enabled.
                if self.logging and name:
                    self.database.log_chat(name.group(2), get_datetime(), name.group(3))

                ## Listen for user chat commands.
                if self.admin and name:
                    if re.match("^!", name.group(3)):
                        self.admin_object.switch(name.group(2), name.group(3))

    def user_chat_command(self, command):
        """
        _user_chat_command
        Handles chat commands prefixed with exclamation mark (!). 
        
        Parameters:-
        :param command:         Passed chat command.
        """

    def _createLogDirectory(self):
        """
        _createLogDirectory
        Create log directory if logging enabled.

        Note: If logging is True a default logfile is created; otherwise
        logging is used as the log directory.
        """
        if self.logging:
            if self.logging != True:
                db_path = self.logging
            else:
                db_dir = parent_dir(parent_dir(__file__))+"/log/"
                if not os.path.exists(db_dir):
                    os.mkdir(db_path)
                db_path = db_dir+"pwitch.db"
            #self.database = PwitchLogging(db_path, self.channel.lstrip('#'))
            self.database = PwitchLogging(db_path, self.channel)
