#!/usr/bin/env python3.5

import argparse
import threading
import json
import sys
import re

from Pwitch import Pwitch

## Use django
## Collect user statistics in Pwitch
## - Average number of followers over time graphs etc.
## - histograms showing average times etc.

## monitor subscribers :. count the number of times a user has subscribed
## non-concurrently

## Add banned word list to user defined text commands i.e. if user creates
## command !hello which prints "how are you", do not allow commands which are
## primary commands i.e. ban.

## Add bit tracker.

class PwitchClient(Pwitch):
    def __init__(self, *kwd, **kwdargs):
        super().__init__(*kwd, **kwdargs)

        #print("Username: {}\noauth: {}\nIrcRoom: {}\n".format(self.username,
        #    self.oauth, self.ircRoom))

        self.verbose=True
        self._monitorThread = self._monitorMethod(self.sock)
        self._writeThread(self._monitorThread)

        """
        PwitchClient
        Terminal based Twitch chat client.
        
        Parameters:-
        :param username:   Twitch account username.
        :param oauth:      Twitch account OAuth token.
        :param ircRoom:    Twitch IRC room to connect to.
        :param updateRate: Limit number of connections to twitch server (per sec).
        :param host:       The Twitch IRC sever (irc.twitch.tv).
        :param port:       Port to connect to server (6667).
        :param logging:    Toggle chat logging (Default False).
        """

    def _monitorMethod(self, sock=None):
        """
        readThread
        Helper method: creates thread object which reads irc socket output.

        Parameter:-
        :param sock:       irc socket object (output from Pwitch.connectIRC()).
        """
        if not sock:
            sock=self.sock
        return threading.Thread(target=self.updateIRC, args=(sock,))

    def _writeThread(self, _monitorThread):
        """
        _writeThread
        Monitors/adresses user input for escaped commands, and chat input.

        Parameter:-
        :_monitorThread:   threading.thread object (output from
                           _monitorMethod()).
        """

        _monitorThread.start()

        #if self.ircRoom.lstrip("#") == self.username:
        #    input_string = ("[B] {}: ".format(self.username))


        while self.connected:
            say = input("{}: ".format(self.username))
            command = re.match(r"^[\\.!](\w*)\s*(\w*)\s*(\w*)", say, re.I|re.M)

            if command:
                argument1 = command.group(2)
                argument2 = command.group(3)
                command = command.group(1).lower()

                if command == "quit":
                    print("Disconnecting")
                    self.connected = False
                    self._monitorThread.join()

                elif command == "mv":
                    print("Moving to channel: "+
                            "{}".format(argument1))
                    #self.ircRoom = "#{}".format(argument1)
                    self.changeIRC(argument1)


                    #self.connected=False
                    #self._monitorThread.join()
                    #self.ircRoom = "#{}".format(argument1)
                    #self.connected=True
                    #self.sock = self.connectIRC()
                    #self._monitorMethod().start()

                ## Default command
                elif command in ["help", "h"]:
                    ## Scary - High chance of this breaking.

                    from os import path as p

                    try:
                        ## open option help text file. 
                        d = p.join(p.dirname(p.dirname(p.abspath(__file__))),
                            "doc", "clientHelp.txt")
                        with open(d, "r") as options:
                            options = options.read()
                        x = re.search("{}[.\S\s]*?\n\n".format(argument1),
                            options).group()
                        print("\n"+x)

                    except FileNotFoundError:
                        print("unable to open {}".format(d))
                    except:
                        print("Option not found.")

                elif command in ["whisper", "w"]:
                    self.whisper(argument1.lower(), argument2)
                elif command == "startlog":
                    pass
                elif command == "stoplog":
                    pass
                elif command == "chat":
                    self.chat(argument1)

                ## Administrator commands.
                ## If user banned, then unmod them?

                elif command in ["ban", "rm"]:
                    self.ban(argument1.lower())
                elif command == "unban":
                    self.unban(argument1.lower())
                elif command == "timeout":
                    self.timeout(argument1.lower(), argument2)
                elif command == "slow":
                    self.slow(argument1)
                elif command == "slowoff":
                    self.slowoff()
                elif command == "clear":
                    self.clear()
                elif command == "subscribers":
                    self.subscribers()
                elif command == "subscribersoff":
                    self.subscribersoff()
                elif command == "followers":
                    self.followerMode(argument1)
                elif command == "followersoff":
                    self.followerModeOff()
                elif command == "host":
                    self.host(argument1, argument2)
                elif command == "unhost":
                    self.unhost()
                elif command == "commercial":
                    self.commercial(argument1)
                elif command == "mod":
                    self.mod(argument1.lower())
                elif command == "unmod":
                    self.unmod(argument1.lower())
                elif command == "mods":
                    print("Mods: {}".format(", ".join(self.mod_list)))
                    #print("Mods: {}".format(", ".join(self.getMods())))
                    #self.getMods()
                elif command == "onlymod":
                    self.mod_only_mode=True
                elif command == "onlymodoff":
                    self.mod_only_mode=False
            else:
                self.chat(say)


    def changeIRC(self, ircRoom):
        self.connected=False
        self._monitorThread.join()
        self.ircRoom = "#{}".format(ircRoom)
        self.connected=True
        self.sock = self.connectIRC()
        self.mod_list = self.getMods()
        self._monitorThread = self._monitorMethod()
        self._monitorThread.start()

#atest = PwitchClient("steelwlng", "oauth:yx77dbgaxsjhhghxe60oij7m6w1ymn",
#        "#dolphinchemist", verbose=True)

atest = PwitchClient("steelwlng", "oauth:yx77dbgaxsjhhghxe60oij7m6w1ymn",
        "#steelwlng", verbose=True)
