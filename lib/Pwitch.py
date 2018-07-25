#!/usr/bin/env python2.7

import socket
import readline
import select
import os
import re
import sys

from multiprocessing import Process
from threading import Thread
from datetime import datetime
from time import sleep

## incorporate loyalty points
## Add method to log mod command useage.

class Pwitch:
    def __init__(self,
                username, 
                oauth, 
                ircRoom, 
                updateRate=(10/30),
                verbose=False,
                host="irc.twitch.tv",
                port=6667,
                logging=False,
                chatCommands=None,
                loyaltyMode=False
                ):

        self.username = username
        self.oauth = oauth
        self.ircRoom = ircRoom
        self.updateRate = updateRate
        self.verbose = verbose
        self.host = host
        self.port = port
        self.logging = logging
        self.autolog = False
        self.chatCommands = chatCommands
        self.mod_only_mode = False
        self.connected = True
        self.sock = self.connectIRC()
        self.mod_list = self.getMods()

        ##Scaffold
        self.logging = True

        if self.logging:
            self._createLogDirectory()
            ## Thread terminates when not self.connected.
            ## Note: May want to include this in the controller :. all
            ## monitoring threads only use a single _getDate thread.
            Thread(target=self._getDate).start()

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
            - True (Log to log/#IRCROOM).
            - FILE (log to specified file).

        Note: verbose/logging False by default.
        Note: updateRate default = 10/30 (30 commands per 10 secs).

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
        :param sock:   Socket object returned from connectIRC.
        """

        if not sock:
            sock=self.sock

        if self.autolog:
            logDir = os.path.join(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))))

            print(logDir)
            #os.makedirs(logDir

        ## Create log dir if autologging enabled.
#        if self.autolog:
#            import os.path
#            logDir = os.path.join(os.path.dirname(os.path.dirname(
#                os.path.abspath(__file__))))
#            os.makedirs(logDir, mode=0755, exist_ok=True)



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
                notice = re.search('NOTICE.*:+?(.*)', response, re.M|re.I)

                if self.verbose:
                    ## Store user input into buffer.
                    ## Note: Careful if implement GUI.
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
                    sys.stdout.write("\r{}: {}".format(self.username,
                        readline.get_line_buffer().lstrip(self.username)))
                    sys.stdout.flush()

                if self.logging:
                    pass

        ## Close logfile.

        #if self.moderating:
        #    pass
                    
    def _createLogDirectory(self):
        """
        _createLogDirectory
        Create log directory if logging enabled.

        Note: If logging is True a default logfile is created; otherwise
        logging is used as the log directory.
        """

        home_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        if self.logging == True:
            log_dir = os.path.join(home, logs, ircRoom.lstrip("#"))
        else:
            log_dir = os.path.dirname(self.logging)

        if not os.path.isdir(log_dir):
            try:
                os.makedirs(log_dir, mode=0o755, exist_ok=True)
            except (OSError, IOError):
                print("Could not create log directory : {}".format(log_dir))

        return log_dir

    def _getDate(self):
        """
        _getDate
        Helper/Thread function for _dateThread, and logging methods.
        A recursive method which updates self.logfile to the current date, and
        sleeps untill the next update.
        """

        while self.connected:
            time = datetime.now()

            try:
                FH = os.path.join(self.logging, str(time.date())) # FileHandle
                self.logFile = open(FH, "a+")
            except (OSError, IOError):
                ## create logging... log.
                sys.stderr.write("Could not create log directory: {}".format(FH))

            ## number of seconds remaining in day
            secs_remaining = 86400 - ((time.hour*3600) + (time.minute*60) + 
                    time.second)
            sleep(secs_remaining)

    def _dateThread(self):
        """
        _dateThread
        Creates date monitoring thread. Inexpensive method to prefix logfiles
        with modification dates.
        """
        ## Note Thread terminates when not self.connected.
        thread = Thread(target = self._dateGet)


    def chatCommand(self):
        pass

    def createThread(self):
        pass

    def loadCommands(self):
        """Load chat commands."""
        pass

    def loadBannedWords(self, banCfg=None):
        """Load list of banned words for channel."""
        pass




    #def _logMethod(self, logInput, logfile=None, autolog=self.autolog):
    #    """
    #    _logMethod
    #    Pwitch chat logging method.

    #    Parameter:-
    #    :param logInput:   Message to log.
    #    :param logfile:    Previous logging file.
    #    :param autolog:    Specify Pwitch default date/time logging is enabled
    #                       (Bool).
    #    """

        ## if autologging Create dir named after irc room, then year, then month
        ## Log each file as Month_day.log


    
    def getMods(self):
        """
        getMods
        Returns a list of moderators for the current channel.
        """
        
        sock = self.connectIRC()
        n=None

        while not n:
            ready = select.select([sock], [], [], self.updateRate)
            if ready[0]:
                response = sock.recv(1024).decode("utf-8")
            else:
                continue
            if response == "PING :tmi.twitch.tv\r\n":
                sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))

            self.chat(".mods", socket=sock)
            n = re.search(r':+\s(.*)', response, re.I|re.M)

        outlist = list(n.group().strip("\r: ").split(", "))
        sock.close()

        return outlist

    def chat(self, message, socket=None):
        """Send message to twitch irc room."""
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
