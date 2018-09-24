#!/usr/bin/env python3.6

import re

class PwitchAdmin:
    def __init__(self, command):

        """
        PwitchAdmin
        Pwitch plugin class - Enables use of admin commands

        Paramters:-
        :param command:         Passed user command.
        """

        self.command = command

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

    def help(self):
        return "This is the help method."

    def custom(self, *command):
        return "This is the custom command"

    def getMods(self):
        """
        getMods

        Returns a list of moderators for the current channel.
        """
        sock = self.connectIRC()
        n=None

        ## Try loops stops script from breaking if server doesn't reply
           
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

    def whisper(self, *arguments):
        """Send a whisper to the specified user."""
        ## Needs implementing.
        pass

    def ban(self, *user):
        """Ban the specified user from the current channel."""
        self.chat(".ban {}".format(user))

    def unban(self, *user):
        """Unban the specified user from the current channel."""
        self.chat(".unban {}".format(user))

    def timeout(self, *args):
        """Timeout the specified user for the given number of seconds."""
        self.chat(".timeout {} {}".format(args[0], args[1]))

    def untimeout(self, *args):
        """Remove timeout for the specified user."""
        self.chat(".untimeout {}".format(args[0]))

    def slow(self, *args):
        """Limit how often users may send messages, in seconds."""
        self.chat(".slow {}".format(args[0]))

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

    def followerMode(self, *args):
        """Turn on followers only mode."""
        self.chat(".followers {}".format(args[0]))

    def followerModeOff(self):
        """Turn off followers only mode."""
        self.chat(".followersoff")

    def host(self, *args):
        """Host the specified channel."""
        self.chat(".host {} {}".format(args[0], " ".join(args[1:])))

    def unhost(self):
        """Stop hosting channels."""
        self.chat(".unhost")

    def commercial(self, *args):
        """Start commercials for x number of seconds"""
        self.chat(".commercial {}".format(args[0]))

    def mod(self, *args):
        """Grant mod status to a user."""
        self.chat(".mod {}".format(args[0]))

    def unmod(self, *args):
        """Revoke mod status from a user."""
        self.chat(".unmod {}".format(args[0]))

    def test(self, *args):
        print("This is text: {}".format(" ".join(args)))

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
