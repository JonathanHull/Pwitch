#!/usr/bin/env python3.6

import json

from time import sleep
from .Pwitch import Pwitch
from multiprocessing import Process

## Enable users to check status of each thread if input is enabled
## i.e. Pwitch.userBuffer
## Enable users to kill certain threads
## Check activity of threads, and restart if they have went down.
## Reconnect to disconnected channels every 60 seconds.

class PwitchServer:
    def __init__(self, cfg, channels):
        """
        PwitchServer

        Pwitch process handling class
        Multithreads Pwitch objects enabling multiple bots to be run
        simultaneously.

        Parameters:-
        :param cfg:         cfg dictionary - Check cfg/cfg.json
        :param channels:    List of irc channels to monitor - Check
                            cfg/irc_channels.json
        """

        self.cfg = cfg
        self.channels = channels

    def _generateThreadDict(self):
        """
        _generateThreadList

        Generates dictionary containing Pwitch obejcts, and process object.
        e.g. adict["ircRoom"] = [PwitchObject, Process]
        """

        adict = {}

        username = self.cfg["nick"]
        oauth = self.cfg["oauth"]
        channels = self.channels

        for i in channels:
            pwitch_object = Pwitch(username, oauth, i)
            adict[i] = [pwitch_object, Process(target=pwitch_object.start)]

        return adict

    def startThreads(self):
        """
        startThreads

        Helper function; intialises pwitch threads
        """
        print("### Starting Pwitch Server ###")

        self.adict = self._generateThreadDict()

        for i in self.adict.keys():
            print("### Starting : {} ###".format(i.lstrip("#")))
            self.adict[i][1].start()


    def stopThreads(self):
        """
        stopThreads

        Helper function; stops all pwitch threads
        """
        
        try:
            self.adict_keys()
        except:
            print("Processes have not been initalised.")
        else:
            for i in self.adict.keys():
                self.adict[i][0].connected = False

if __name__ == "__main__":
     cfg_dir = "/home/jonathan/projects/Pwitch/cfg/"
     cfg = cfg_dir+"cfg.json"
     channels = cfg_dir+"irc_channels.json"

     with open(cfg, 'r') as w:
         cfg = json.load(w)

     channel_list = cfg["channels"]

     ob = PwitchServer(bot_cfg, channel_list)
     ob.startThreads()

