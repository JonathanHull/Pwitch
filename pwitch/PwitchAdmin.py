#!/usr/bin/env python3.6

import re
import socket
import select

## Need to check whether user has permission to use command.
## Log user commands (only if successful i.e. have correct permissions).

class PwitchAdmin:
    def __init__(self,
                 sock,
                 channel,
                 mod_list,
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
        self.mod_list = self.mod_list

    def switch(self, command):
        command = re.match(r"^[\\.!](\w*)\s*(\w*)\s*(\w*)", command, re.I|re.M)
        c = command.group(1)
        a1 = command. group(2)
        a2 = command. group(3)

        ## Strange method of doing this.
        function = {
            'help'           : self.help,
            'mods'           : self.getMods,
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

        return function(a1, a2)

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
        socket.send("PRIVMSG {} :{}\r\n".format(self.channel, message).encode("utf-8"))

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
