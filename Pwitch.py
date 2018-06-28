#!/usr/bin/env python2.7

import sys
import os
import socket
import argparse
import json
import re

from argparse import RawTextHelpFormatter as RTHF
from time import sleep

## Command line argument parser.

def argumentParser(args):
    parser = argparse.ArgumentParser(prog="Pwitch", description="Twitch chat \
        bot")

    parser.add_argument("--cfg", type=str, required=False,
        default=local+"/cfg.json", help="Path to configuration script.")

    parser.add_argument("-v", "--verbose", required=False, default=False,
        help="Turn on verbose output.")

    return parser.parse_args(args)
 
if __name__ == "__main__":
    local = os.path.dirname(os.path.abspath(__file__))
    args = argumentParser(sys.argv[1:])

    ## Parse configuration file.

    with open(args.cfg) as cfg:
        data = json.load(cfg)

class Pwitch:
    """
    Pwitch

    Parameters:-

    :param username:   Twitch account username.
    :param oauth:      Twitch account OAuth token.
    :param ircRoom:    Twitch IRC room to connect to.
    :param updateRate: Limit number of connections to twitch server (per sec).
    :param verbose:    Turn on verbose output : Boolean.
        

    Note: Verbose output False by default.
    Note: updateRate default = 20/30 (20 commands per 30 secs).

    Usage: x = Pwitch("Twitch_username", "oauth_token", "#ircRoom", True|False)
           x.ban("Twitch_username")
    """

    def __init__(self,
                username, 
                oauth, 
                ircRoom, 
                updateRate=(20/30),
                verbose=False):

        self.username = username
        self.oauth = oauth
        self.ircRoom = ircRoom
        self.verbose = verbose
        self.updateRate = updateRate

        self.live_connection()


    def connectIRC(self, ircRoom=self.ircRoom)
        """Connect to Twtich irc room using specified login."""

        s = socket.socket()
        s.connect((data["host"], data["port"]))
        s.send("PASS {}\r\n".format(self.oauth).encode("utf-8"))
        s.send("NICK {}\r\n".format(self.username).encode("utf-8"))
        s.send("JOIN {}\r\n".format(ircRoom).encode("utf-8"))
        if s.recv(1024).decode("utf-8") and self.verbose:
            print("Username: {}\nChannel: {}\n".format(data["nick"],
                ircRoom.lstrip('#')))
        return s

    def live_connection(self, connection):
        """ """

        while True:
            response = self.holder.recv(1024).decode("utf-8")

    def chat(self, message):
        "Send message to twitch irc room using specified login."""
        sock.send("PRIVMSG {} :{}".format(self.ircRoom, message))

    def ban(self, user):
        """Ban the specified user from the current channel."""
        self.chat(".ban {}".format(user))

    def timeout(self, user, secs=600):
        """Timeout the specified user for the given number of seconds."""
        self.chat(".timeout {}".format(user, secs))

    def test(self, atest="words"):
        self.chat(atest)



#s.send("PRIVMSG {} :{}\r\n".format("#steelwlng", "test").encode("utf-8"))
def dmsg(sock, msg):
    """Send a direct chat message to the twitch servers"""
    sock.send("PRIVMSG {} :{}".format(cfg.CHAN, msg))

def connectIRC(username, oauth, ircRoom, verbose):
    """Connect to Twtich irc room using specified login."""

    s = socket.socket()
    s.connect((data["host"], data["port"]))
    s.send("PASS {}\r\n".format(oauth).encode("utf-8"))
    s.send("NICK {}\r\n".format(username).encode("utf-8"))
    s.send("JOIN {}\r\n".format(ircRoom).encode("utf-8"))
    if s.recv(1024).decode("utf-8") and verbose:
        print("Username: {}\nChannel: {}\n".format(data["nick"],
            ircRoom.lstrip('#')))
    return s

#s = connectIRC(data["nick"], data["oauth"], data["channel"], True)
#s = connectIRC(data["nick"], data["oauth"], "#steelwlng", True)
s = Pwitch(data["nick"], data["oauth"], data["channel"])

#while True:
#    response = s.recv(1024).decode("utf-8")
#    if response == "PING :tmi.twitch.tv\r\n":
#        s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
#
#    else:
#        name = re.match(r'^:(.*)![^:]*:(.*)', response, re.M|re.I)
#        if name:
#            #print("{}: {}".format(name.group(1), name.group(2)))
#            print(response)
#            s.test()
#
#        #if name and re.match(r'^!.*$', name.group(2), re.M|re.I):
#        #    print(name.group(2))
#
#
#
#    sleep(0.1)
