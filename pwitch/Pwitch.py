#!/usr/bin/env python2.7

import socket
import select
import readline
import os
import re
import sys

from .PwitchLogging import *

#if __name__ == "__main__":
#    from PwitchLogging import *
#else:
#    from .PwitchLogging import *

from .PwitchUtils import parent_dir
from threading import Thread
from datetime import datetime
from time import sleep

## Pwitch main module.

## incorporate loyalty points
## Add method to log mod command useage.
## Add game specific commands i.e. Detect game user playing, if user has
## specified commands associated with that game.

## Add way to share banned lists between rooms.

## Enable reconnection if interupted.

class Pwitch:
    def __init__(self,
                username, 
                oauth, 
                ircRoom,
                updateRate=(10/30),
                verbose=False,
                host="irc.twitch.tv",
                port=6667,
                logging=True,
                userBuffer=False,
                chatCommands=None,
                loyaltyMode=False,
                process_queue=None
                ):

        """
        Pwitch
        Parent Pwitch package class.

        Parameters:-
        :param username:   Twitch account username.
        :param oauth:      Twitch account OAuth token.
        :param ircRoom:    Twitch IRC room to connect to.
        :param updateRate: Limit number of connections to twitch server (per sec).
        :param verbose:    Turn on verbose output : Boolean.
        :param host:       The Twitch IRC sever (irc.twitch.tv).
        :param port:       Port to connect to server (6667).
        :param logging:    Toggle chat logging (Default False). Options are:
            - True (Log to log/pwitch.db).
            - FILE (log to specified file).

        Note: verbose/logging False by default.
        Note: updateRate default = 10/30 (30 commands per 10 secs).

        Usage: x = Pwitch("Twitch_username", "oauth_token", "#ircRoom", True|False)
               x.ban("Twitch_username")
        """

        self.username = username
        self.oauth = oauth
        self.ircRoom = ircRoom
        self.updateRate = updateRate
        self.verbose = verbose
        self.host = host
        self.port = port
        self.logging = logging
        self.autolog = False
        self.userBuffer = userBuffer
        self.chatCommands = chatCommands
        self.mod_only_mode = False
        self.sock = self.connectIRC()
        self.process_queue = process_queue

        self.connected = True

    def start(self):
        """
        start

        Helper function; starts the Pwitch bot using user defined options.
        """

        self._createLogDirectory()
        self.mod_list = self.getMods()

        try:
            self.updateIRC()
        except KeyboardInterrupt:
            pass

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
        s.send("CAP REQ :twitch.tv/commands\r\n".encode("utf-8"))
        s.send("CAP REQ :twitch.tv/tags\r\n".encode("utf-8"))
        s.send("CAP REQ :twitch.tv/membership\r\n".encode("utf-8"))
        s.settimeout(None)

        return s

    def updateIRC(self, sock=None):
        """
        updateIRC
        
        Allow connection to Twitch IRC server, and monitor for keywords (i.e.
        banned words / Commands).

        paramers:-
        :param sock:       Socket object returned from connectIRC (i.e. connection
                           to twitch irc servers)
        """

        if not sock:
            sock=self.sock

        while self.connected:
            ready = select.select([sock], [], [], self.updateRate)

            if ready[0]:
                response = sock.recv(1024).decode("utf-8")
            else:
                continue
            if response == "PING :tmi.twitch.tv\r\n":
                sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))

            else:
                ## name search groups: 1: mod, 2: name, 3: chat
                ## name searches for chat messages from users.
                name = re.search('.*mod=(\d).*:(.*)!.*:+?(.*)', response,
                        re.I|re.M)
                ## notice = re.search('NOTICE.*:+?(.*)', response, re.M|re.I)

                if self.verbose:
                    ## Store user input into buffer.
                    ## Note: Careful if implement GUI.

                    if self.userBuffer:
                        sys.stdout.write('\r'+' '*(len(readline.get_line_buffer())
                            +len(self.username)+2)+'\r')

                    if name:
                        if name.group(2) == self.ircRoom.lstrip('#'):
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

                if self.logging and name:
                    ## Imporve PwitchLogging to detect database used, rewrite to
                    ## allow to write using same syntax.
                    dt = datetime.utcnow()
                    date = ",".join(str(i) for i in dt.timetuple()[:3]).replace(",","-")
                    time = ":".join(str(i) for i in dt.timetuple()[3:6])
                    d = "M".join([date,time])
                    self.database.log_chat(name.group(2), d, name.group(3))
                    #d = "N".join([date,time])

                    ## Check for errors/SQL injections
                    #try:
                    #    #self.database.sql_insert(name.group(2), date, time,
                    #    #    name.group(3))

                    #    print("here")
                    #    self.database.log_chat(name.group(2), d, name.group(3))
                    #except:
                    #    ## Implement logging 
                    #    print("Unable to log...")
                    #    pass

                ## PwitchServer flag
                try:
                    self.connected = self.process_queue.get_nowait()
                except:
                    pass

        #if self.moderating:
        #    pass
                    
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
            #self.database = PwitchLogging(db_path, self.ircRoom.lstrip('#'))
            self.database = PwitchChannelStats(db_path, self.ircRoom.lstrip('#'))

    def chatCommand(self):
        pass

    def loadCommands(self):
        """Load chat commands."""
        pass

    def loadBannedWords(self, banCfg=None):
        """Load list of banned words for channel."""
        pass
    
    def getMods(self):
        """
        getMods

        Returns a list of moderators for the current channel.
        """
        sock = self.connectIRC()
        n=None

        ## Try loops stops script from breaking if server doesn't reply
        ## immediately
        while not n:
            try:
                ready = select.select([sock], [], [], self.updateRate)
                if ready[0]:
                    response = sock.recv(1024).decode("utf-8")
                else:
                    continue
                if response == "PING :tmi.twitch.tv\r\n":
                    sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                self.chat(".mods", socket=sock)
                n = re.search(r':+\s(.*)', response, re.I|re.M)
            except:
                n = None

        outlist = list(n.group().strip("\r: ").split(", "))
        sock.close()

        return outlist

    def chat(self, message, socket=None):
        """
        chat

        Fundamental Pwitch method.
        Sends IRC commands to Twitch.

        Parameters:-
        :param message:    Command sent to Twitch IRC servers.
        :param socket:     Socket connection to Twitch IRC servers.

        """
        if not socket:
            socket = self.sock
        socket.send("PRIVMSG {} :{}\r\n".format(self.ircRoom, message).encode("utf-8"))

    def whisper(self, user, message):
        """Send a whisper to the specified user."""
        ## Needs implementing.
        pass

    def ban(self, user):
        """Ban the specified user from the current channel."""
        self.chat(".ban {}".format(user))

    def unban(self, user):
        """Unban the specified user from the current channel."""
        self.chat(".unban {}".format(user))

    def timeout(self, user, secs=600):
        """Timeout the specified user for the given number of seconds."""
        self.chat(".timeout {} {}".format(user, secs))

    def untimeout(self, user):
        """Remove timeout for the specified user."""
        self.chat(".untimeout {}".format(user))

    def slow(self, duration=30):
        """Limit how often users may send messages, in seconds."""
        self.chat(".slow {}".format(duration))

    def slowoff(self):
        """Disable slowmode."""
        self.chat(".slowoff")

    def clear(self):
        """Clear chatroom."""
        self.chat(".clear")
        print("Chat was cleared by a moderator")

    def subscribers(self):
        """Turn on subscribers only mode."""
        self.chat(".subscribers")

    def subscribersoff(self):
        """Turn off subscribers only mode."""
        self.chat(".subscribersoff")

    def followerMode(self, duration):
        """Turn on followers only mode."""
        self.chat(".followers {}".format(duration))

    def followerModeOff(self):
        """Turn off followers only mode."""
        self.chat(".followersoff")

    def host(self, channel, *tagline):
        """Host the specified channel."""
        self.chat(".host {} {}".format(channel, tagline[0]))

    def unhost(self):
        """Stop hosting channels."""
        self.chat(".unhost")

    def commercial(self, *duration):
        """Start commercials for x number of seconds"""
        self.chat(".commercial {}".format(duration[0]))

    def mod(self, user):
        """Grant mod status to a user."""
        self.chat(".mod {}".format(user))

    def unmod(self, user):
        """Revoke mod status from a user."""
        self.chat(".unmod {}".format(user))
