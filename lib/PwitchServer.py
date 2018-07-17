#!/usr/bin/env python3.5

from Pwitch import Pwitch

## Monitor user input -- quit etc.

class PwitchServer(Pwitch):
    def __init__(self, *kwd, **kwdargs):
        super().__init__(*kwd, **kwdargs)


    def startServices(self):
        ## Read file containing irc channels using PwitchBot.
        ## create dictionary { ircRoom: Pwitch_Object }
        pass

