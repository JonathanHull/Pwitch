#!/usr/bin/env python3.5

from Pwitch import Pwitch

## Monitor user input -- quit etc.

class PwitchServer(Pwitch):
    def __init__(self):
        pass

    def _buildThreads(self):
        """
        _buildThreads



        Builds dictonary containing ircRoom monitoring threads. 
        Initial method call useed

        """
        


    def startServices(self):
        ## Read file containing irc channels using PwitchBot.
        ## create dictionary { ircRoom: Pwitch_Object }
        pass

    def stopService(self):
        """
        stopService
        Stop monitoring ircRoom.

        Parameters:-
        :param ircRoom:   Name of the irc room to stop monitoring -
                          Note: do not prefix with '#'.
        """
