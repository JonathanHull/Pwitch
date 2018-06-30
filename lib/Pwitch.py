#!/usr/bin/env python2.7

import socket
import re

from time import sleep

## Command line argument parser.

class Pwitch:

    def __init__(self,
                username, 
                oauth, 
                ircRoom, 
                updateRate=(20/30),
                verbose=False,
                host="irc.twitch.tv",
                port=6667,
                logging=False
                ):

        self.username = username
        self.oauth = oauth
        self.ircRoom = ircRoom
        self.updateRate = updateRate
        self.verbose = verbose
        self.host = host
        self.port = port
        self.logging = logging

        self.sock = self.connectIRC()

        if logging:
            import datetime

        """
        Pwitch

        Parameters:-

        :param username:   Twitch account username.
        :param oauth:      Twitch account OAuth token.
        :param ircRoom:    Twitch IRC room to connect to.
        :param updateRate: Limit number of connections to twitch server (per sec).
        :param verbose:    Turn on verbose output : Boolean.
        :param host:       The Twitch IRC sever (irc.twitch.tv).
        :param port:       Port to connect to server (6667).
        :param logging:    Toggle chat logging (Default False).

        Note: verbose/logging False by default.
        Note: updateRate default = 20/30 (20 commands per 30 secs).

        Usage: x = Pwitch("Twitch_username", "oauth_token", "#ircRoom", True|False)
               x.ban("Twitch_username")
        """

    def connectIRC(self, ircRoom=None):
        """
        connectIRC
        
        Connect to Twtich irc room using specified login."""

        if not ircRoom:
            ircRoom = self.ircRoom

        s = socket.socket()
        s.connect((self.host, self.port))
        s.send("PASS {}\r\n".format(self.oauth).encode("utf-8"))
        s.send("NICK {}\r\n".format(self.username).encode("utf-8"))
        s.send("JOIN {}\r\n".format(ircRoom).encode("utf-8"))
        if s.recv(1024).decode("utf-8") and self.verbose:
            print("Username: {}\nChannel: {}\n".format(self.username,
                ircRoom.lstrip('#')))

        return s

    def updateIRC(self, s):

        ## Active connection with Twitch irc sever.

        while True:
            response = s.recv(1024).decode("utf-8")
            if response == "PING :tmi.twitch.tv\r\n":
                s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        
            else:

                ## If a line of chat is detected.

                name = re.match(r'^:(.*)![^:]*:(.*)', response, re.M|re.I)
                if name:
                    if self.verbose:
                        print("{}: {}".format(name.group(1), name.group(2)))

                    if self.logging:
                        pass

                    ## Detect !commands.
                    if name and re.match(r'^!.*$', name.group(2), re.M|re.I):
                        print(name.group(2))
        
            sleep(self.updateRate)

    def loadCommands(self):
        pass

    def loadBannedWords(self):
        pass

    def logChat(self):
        pass

    def chat(self, message):
        "Send message to twitch irc room."""
        self.sock.send("PRIVMSG {} :{}\r\n".format(self.ircRoom, message).encode("utf-8"))

    def ban(self, user):
        """Ban the specified user from the current channel."""
        self.chat(".ban {}".format(user))

    def unban(self, user):
        pass

    def timeout(self, user, secs=600):
        """Timeout the specified user for the given number of seconds."""
        self.chat(".timeout {}".format(user, secs))

    def test(self, atest="words"):
        self.chat(atest)

    def logging(self):
        pass
