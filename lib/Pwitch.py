#!/usr/bin/env python2.7

import socket
import readline
import select
import re
import sys

from multiprocessing import Process
from time import sleep

## incorporate loyalty points
## Add method to log mod command useage.


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
        self.chatCommands = chatCommands

        self.mod_only_mode = False

        self.connected = True
        self.sock = self.connectIRC()

        if logging:
            import datetime
    #        if logging == True:
    #            file_handle = open(

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
        if s.recv(1024).decode("utf-8") and self.verbose:
            print("Username: {}\nChannel: {}\n".format(self.username,
                ircRoom.lstrip('#')))

        s.settimeout(None)

        return s

    ##@threaded
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



                #name = re.search('broadcaster/(\d).*mod=(\d).*:(.*)!.*:+?(.*)',
                #        response, re.I|re.M)

                name = re.search('.*mod=(\d).*:(.*)!.*:+?(.*)', response,
                        re.I|re.M)
                notice = re.search('NOTICE.*:+?(.*)', response, re.M|re.I)

                print(response)

                if self.verbose:
                    if name:
                        ## Store user input into buffer; stop print from
                        ## overwriting terminal input.
                        ## Note: Careful if implement GUI.
                        sys.stdout.write('\r'+' '*(len(readline.get_line_buffer())
                                +len(self.username)+2)+'\r')

                        ## Check whether user is a mod or the broadcaster.
                        ## Need to check modlist instead
                        ## if self.ircRoom == name then B

                        if name.group(2) == self.ircRoom.lstrip('#'):
                            print("[B] {}: {}".format(name.group(2),
                                name.group(3)))

                            #print("[B] {}: {}".format(name.group(3),
                            #    name.group(4)))

                        if int(name.group(1)) > 1:
                            print("[M] {}: {}".format(name.group(2),
                                name.group(3)))

                        #elif int(name.group(2)) >  1:
                        #    print("[M] {}: {}".format(name.group(3),
                        #        name.group(4)))

                        elif not self.mod_only_mode:
                            #print("{}: {}".format(name.group(3), name.group(4)))
                            print("{}: {}".format(name.group(2), name.group(3)))

                    if notice:
                        print(notice.group(1))

                    if self.logging:
                        if self.logging == True:
                            pass
                        else:
                            pass




                    ## Detect !commands.
                    #if name and re.match(r'^!.*$', name.group(2), re.M|re.I):
                    #    print("Disconnecting...")
                    #    self.connected = False

                    ## Restores user input from buffer.
                    sys.stdout.write("{}: {}".format(self.username,
                        readline.get_line_buffer()))
                    sys.stdout.flush()


    def createThread(self):
        pass

    def loadCommands(self):
        """Load chat commands."""
        pass

    def loadBannedWords(self):
        """Load list of banned words for channel."""
        pass

    def logChat(self):
        """Start logging chat"""
        self.log = open(self.ircRoom, 'a+')

    
    def getMods(self):
        """Get a list of admins"""
        new_socket = self.connectIRC()
        n=None

        while not n:
            ready = select.select([new_socket], [], [], self.updateRate)
            if ready[0]:
                response = new_socket.recv(1024).decode("utf-8")
            else:
                continue
            if response == "PING :tmi.twitch.tv\r\n":
                sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))

            self.chat(".mods", socket=new_socket)
            n = re.search(r':+\s(.*)', response, re.I|re.M)

        outlist = list(n.group().strip("\r: ").split(", "))

        return outlist

    def chat(self, message, socket=None):
        """Send message to twitch irc room."""
        if not socket:
            socket = self.sock

        socket.send("PRIVMSG {} :{}\r\n".format(self.ircRoom, message).encode("utf-8"))

    def whisper(self, user, message):
        """Send a whisper to the specified user."""
        #self.chat(".w {} {}".format(user, message))

        #self.sock.send("CAP REQ :twitch.tv/commands\r\n".encode("utf-8"))
        #self.sock.send("PRIVMSG {} :{}\r\n".format(user,
        #    message).encode("utf-8"))

        #while True:

        #    ready = select.select([self.sock], [], [], self.updateRate)
        #    if ready[0]:
        #        response = self.sock.recv(1024).decode("utf-8")
        #    else:
        #        continue
        #    print(response)

        #if ready[0]:
        #    response = sock.recv(1024).decode("utf-8")

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

    def slow(self, duration):
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

    def mod_list(self):
        self.chat(".mods")





## Create multithreading wrapper
def threaded(func):
    def wrapper(socket):
        Process(target=func, args=(socket,))
    return wrapper
