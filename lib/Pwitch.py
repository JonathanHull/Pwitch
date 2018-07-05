#!/usr/bin/env python2.7

import socket
import readline
import re
import sys

from multiprocessing import Process
from time import sleep

## Command line argument parser.

## Create multithreading wrapper
def threaded(func):
    def wrapper(n):
        t = Process(target=func, args=(n.sock,))
        t.start()
        return 5
    return wrapper

class Pwitch:
    def __init__(self,
                username, 
                oauth, 
                ircRoom, 
                updateRate=(20/30),
                verbose=False,
                host="irc.twitch.tv",
                port=6667,
                logging=False,
                chatCommands=None
                ):

        self.username = username
        self.oauth = oauth
        self.ircRoom = ircRoom
        self.updateRate = updateRate
        self.verbose = verbose
        self.host = host
        self.port = port
        self.logging = logging
        self.chatCommands = chatCommands
        self.connected = True

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

        Initialise connection to twitch irc room using class login/oauth.

        Prameters:-
        :param ircRoom:    Twitch IRC room to connect to.
        """

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

    ##@threaded
    def updateIRC(self, sock):
        """
        updateIRC
        
        Allow connection to Twitch IRC server, and monitor for keywords (i.e.
        banned words / Commands).

        paramers:-
        :param sock:   Socket object returned from connectIRC.
        """
        ## Active connection with Twitch irc sever.

        while self.connected:

            response = sock.recv(1024).decode("utf-8")
            if response == "PING :tmi.twitch.tv\r\n":
                sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        
            else:
                name = re.match(r'^:(.*)![^:]*:(.*)', response, re.M|re.I)
                if name:

                    ## Stores user input to buffer; stops irc chat overwriting
                    ## terminal input.
                    sys.stdout.write('\r'+' '*(len(readline.get_line_buffer())+2)+'\r')
                    if self.verbose:
                        print("{}: {}".format(name.group(1), name.group(2)))

                    if self.logging:
                        pass

                    ## Detect !commands.
                    if name and re.match(r'^!.*$', name.group(2), re.M|re.I):
                        print("Disconnecting...")
                        self.connected = False

                    ## Restores user input from buffer.
                    sys.stdout.write("{}: {}".format(self.username,
                        readline.get_line_buffer()))
                    sys.stdout.flush()

            sleep(self.updateRate)


    def getAdmins(self):
        """Get a list of admins"""
        pass

    def loadCommands(self):
        """Load chat commands."""
        pass

    def loadBannedWords(self):
        """Load list of banned words for channel."""
        pass

    def logChat(self):
        """Start logging chat"""
        pass

    def chat(self, message):
        """Send message to twitch irc room."""
        self.sock.send("PRIVMSG {} :{}\r\n".format(self.ircRoom, message).encode("utf-8"))

    def whisper(self, user, message):
        """Send a whisper to the specified user."""
        self.chat(".w {} {}".format(user, message).format("utf-8"))

    def ban(self, user):
        """Ban the specified user from the current channel."""
        self.chat(".ban {}".format(user).encode("utf-8"))

    def unban(self, user):
        """Unban the specified user from the current channel."""
        self.chat(".unban {}".format(user).encode("utf-8"))

    def timeout(self, user, secs=600):
        """Timeout the specified user for the given number of seconds."""
        self.chat(".timeout {} {}".format(user, secs).encode("utf-8"))

    def untimeout(self, user):
        """Remove timeout for the specified user."""
        self.chat(".untimeout {}".format(user).encode("utf-8"))


## Create multithreading wrapper
def threaded(func):
    def wrapper(socket):
        Process(target=func, args=(socket,))
    return wrapper
