#!/usr/bin/env python2.7

import socket
import select
import readline # Remove - Use ncurses instead.
import json
import time
import sys
import os
import re

from .PwitchLogging import *
from .PwitchUtils import parent_dir, get_datetime

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
                channel,
                channel_cfg= None,          ## This should be required.
                update_rate=(10/30),
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
        :param channel_cfg:     Channel configuration dictionary (see cfg/cfg.json).
        :param update_rate:     Limit number of connections to twitch server (per sec).
        :param verbose:         Turn on verbose output (Default: False).
        :param host:            The Twitch IRC sever (irc.twitch.tv).
        :param port:            Port to connect to server (6667).
        :param logging:         Toggle chat logging. Options are:
            - True (Log to log/pwitch.db).
            - FILE (log to specified file).
        :param admin:           Enable administration of channel.

        Note: Default stat_rate is 60 seconds.
        Note: update_rate default = 10/30 (30 commands per 10 secs).
        """

        ## Default variable Initialisations/definitions
        self.username = username
        self.oauth = oauth
        self.channel = channel
        self.channel_cfg = channel_cfg
        self.update_rate = update_rate
        self.verbose = verbose
        self.host = host
        self.port = port
        self.sock = self.connectIRC()
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
        self.mod_list = self.get_mods()

        if self.admin:
            self.admin_object = PwitchAdmin(self.sock, self.channel,
                    self.update_rate)

        if self.logging:
            from .PwitchLogging import PwitchLogging
            self._create_log_directory()
        #if self.chatCommands:                       ## rename
        #    from .PwitchAdmin import PwitchCron

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

    def updateIRC(self, sock=None):
        """
        updateIRC
        
        Allow connection to Twitch IRC server, and monitor for keywords (i.e.
        banned words / Commands).

        paramers:-
        :param sock:       sock object returned from connectIRC (i.e. connection
                           to twitch irc servers)
        """

        if not sock:
            sock=self.sock

        while self.connected:
            try:
                self.connected = self.process_queue.get_nowait()
            except:
                pass

            ready = select.select([sock], [], [], self.update_rate)

            if ready[0]:
                response = sock.recv(1024).decode("utf-8")
            else:
                continue
            if response == "PING :tmi.twitch.tv\r\n":
                sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
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

    def _create_log_directory(self):
        """
        _create_log_directory
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

    def chat(self, message, sock=None):
        """
        chat

        Fundamental Pwitch method.
        Sends IRC commands to Twitch.

        Parameters:-
        :param message:    Command sent to Twitch IRC servers.
        :param sock:     sock connection to Twitch IRC servers.

        """
        if not sock:
            sock = self.sock
        sock.send("PRIVMSG {} :{}\r\n".format(self.channel, message).encode("utf-8"))

    def get_mods(self, sock=None):
        """
        get_mods

        Returns a list of moderators for the current channel.
        """
        if not sock:
            sock = self.sock

        n=None

        ## Try loops stops script from breaking if server doesn't reply
        ## immediately

        while not n:
            try:
                ready = select.select([sock], [], [], self.update_rate)
                if ready[0]:
                    response = sock.recv(1024).decode("utf-8")
                else:
                    continue
                if response == "PING :tmi.twitch.tv\r\n":
                    sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                self.chat(".mods", sock=sock)
                n = re.search(r':+\s(.*)', response, re.I|re.M)
            except Exception as e:
                #print(e)
                n = None

        outlist = list(n.group().strip("\r: ").split(", "))
        #sock.close()

        return outlist

class PwitchAdmin(Pwitch):
    def __init__(self,
                 sock,
                 channel,
                 update_rate,
                ):

        """
        PwitchAdmin
        Pwitch plugin class - Enables use of admin commands

        Paramters:-
        :param sock:            Socket object connected to twitch irc server.
        :param channel:         The moderated channel.
        :param mod_list:            List of channel mods.
        """
        self.sock = sock
        self.channel = "#"+channel
        self.update_rate = update_rate
        self.mod_list = self.get_mods()

    def switch(self, username, command):
        """
        Switch
        Pythonised switch statement. Executes PwitchAdmin method thorugh command
        parameter.

        Paramters:-
        :param username:        Name of user who issued the command.
        :param command:         Command to be executed by Pwitch.
        """

        command = re.match(r"^[\\.!](\w*)\s*(\w*)\s*(\w*)", command, re.I|re.M)
        c = command.group(1)
        a1 = command. group(2)
        a2 = command. group(3)

        ## Pythonised Switch statement for admin-level bot commands.
        ## Remove self.test.
        function = {
            'help'           : self.help,
            'mods'           : self.get_mods,
            'ban'            : self.ban,
            'unban'          : self.unban,
            'timeout'        : self.timeout,
            'untimeout'      : self.untimeout,
            'slow'           : self.slow,
            'slowoff'        : self.slowoff,
            'clear'          : self.clear,
            'subscribers'    : self.subscribers,
            'subscribersoff' : self.subscribersoff,
            'followers'      : self.followerModeOff,
            'followersoff'   : self.followerModeOff,
            'host'           : self.host,
            'unhost'         : self.unhost,
            'commercial'     : self.commercial,
            'mod'            : self.mod,
            'unmod'          : self.unmod,
            'test'           : self.test,
        }.get(c, self.custom)

        ## Non-mod commands.
        if function in [self.test, self.help, self.get_mods, self.custom]:
            return function(a1,a2)

        ## Mod commands
        elif username in self.mod_list:
            return function(a1,a2)

    def get_command_permissions(self):
        """
        get_command_permissions
        Get command permissions i.e. allow non-mods to use specific commands or
        make specific commands broadcaster only commands.

        There are three command levels:
            - Broadcaster
            - Administrator 
            - User
        """
        return None

    def add_pwitch_mod(self):
        """
        add_pwitch_mod
        Add user to list of users who can use pwtich admin commands.
        """

    def test(self, *args):
        self.chat("This is a test!")

    def help(self, *args):
        return "This is the help method."

    def custom(self, *command):
        return "This is the custom command"

    def whisper(self, *args):
        """Send a whisper to the specified user."""
        ## Needs implementing.
        pass

    def ban(self, *args):
        """Ban the specified user from the current channel."""
        self.chat(".ban {}".format(args[0]))

    def unban(self, *args):
        """Unban the specified user from the current channel."""
        self.chat(".unban {}".format(args[0]))

    def timeout(self, *args):
        """Timeout the specified user for the given number of seconds."""
        self.chat(".timeout {} {}".format(args[0], args[1]))

    def untimeout(self, *args):
        """Remove timeout for the specified user."""
        self.chat(".untimeout {}".format(args[0]))

    def slow(self, *args):
        """Limit how often users may send messages, in seconds."""
        self.chat(".slow {}".format(args[0]))

    def slowoff(self, *args):
        """Disable slowmode."""
        self.chat(".slowoff")

    def clear(self, *args):
        """Clear chatroom."""
        self.chat(".clear")
        print("Chat was cleared by a moderator")

    def subscribers(self, *args):
        """Turn on subscribers only mode."""
        self.chat(".subscribers")

    def subscribersoff(self, *args):
        """Turn off subscribers only mode."""
        self.chat(".subscribersoff")

    def followerMode(self, *args):
        """Turn on followers only mode."""
        self.chat(".followers {}".format(args[0]))

    def followerModeOff(self):
        """Turn off followers only mode."""
        self.chat(".followersoff")

    def host(self, *args):
        """Host the specified channel."""
        self.chat(".host {} {}".format(args[0], " ".join(args[1:])))

    def unhost(self, *args):
        """Stop hosting channels."""
        self.chat(".unhost")

    def commercial(self, *args):
        """Start commercials for x number of seconds"""
        self.chat(".commercial {}".format(args[0]))

    def mod(self, *args):
        """Grant mod status to a user."""
        self.chat(".mod {}".format(args[0]))
        self.mod_list.append(arg[0])

    def unmod(self, *args):
        """Revoke mod status from a user."""
        self.chat(".unmod {}".format(args[0]))
        self.mod_list.remove(args[0])


class PwitchCron:
    def __init__(self,
                 cfg,
                ):
        """
        PwitchCron
        Class enabling scheduled chat commands (i.e. motds)

        Parameters:-
        :param cfg:             Path to configuration 
        """
        pass

    def start(self):
        pass


    def motd(command):
        print(command)

if __name__ == "__main__":
    x = PwitchAdmin("help")
    x.switch("!est one two")
