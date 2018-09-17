#!/usr/bin/env python3.6

import time

from .Pwitch import Pwitch
from threading import Thread
from multiprocessing import Process, Queue

## Enable users to check status of each thread if input is enabled
## i.e. Pwitch.userBuffer
## Enable users to kill certain threads
## Check activity of threads, and restart if they have went down.
## Reconnect to disconnected channels every 60 seconds.

class PwitchServer:
    def __init__(self,
                 cfg, 
                 channels, 
                 #timeout):
                 ):
        """
        PwitchServer

        Pwitch process handling class
        Multithreads Pwitch objects enabling multiple bots to be run
        simultaneously.

        Parameters:-
        :param cfg:             cfg dictionary - Check cfg/cfg.json
        :param channels:        List of irc channels to monitor - Check
                                cfg/irc_channels.json
        :param timeout:         Set the 
        """

        self.cfg = cfg
        self.channels = channels

    def start(self):
        """
        start

        Initialises and starts all Pwitch processes.
        """
        self.process_dict = self._create_process_dict()
        self.start_processes(self.process_dict)

        ## Watchdog thread -- Monitors process status.
        watchdog_thread = Thread(target=self.watchdog)
        watchdog_thread.start()


    def watchdog(self, timeout=10):
        """
        watchdog

        Watches the queue object for updates, and sends a signal to it if the
        status of the child process has changed

        Paramters:-
        :param timeout:         Time for process to shutdown before termination.
        """
        ## Extensive logging required.
        while True:
            for process,queue,flag in self.process_dict.values():

            ## try to terminate if attempt to close failed.
                if not flag: 
                    process.terminate()
                    time.sleep(0.1)
                    if not process.is_alive():
                        process.join(timeout=1.0)
                        queue.close()
                        self.process_dict.pop(i)
                        continue

                if not process.is_alive():
                    ## restart dead process
                    pass

                time.sleep(0.1)

    def _create_process_dict(self):
        """
        create_process_dictionary

        Generates dictionary containing Pwitch obejcts, and process object.
        e.g. adict["ircRoom"] = [PwitchObject, Process]
        """

        adict = {}

        username = self.cfg["nick"]
        oauth = self.cfg["oauth"]
        channels = self.channels

        for i in channels:
            q = Queue()
            a = Pwitch(username, oauth, i, process_queue=q)
            adict[i] = [Process(target=a.start), q, True]

        return adict

    def add_process(self, username, oauth, ircRoom):
        """
        add_process

        Paramters:-
        :param username:        bot username.
        :param oauth:           bot oauth key.
        :param ircRoom:         Channel for Pwitch to monitor.
        """
        q = Queue()
        a = Pwitch(username, oauth, i, process_queue=q)

        ## Note: Final True is a flag for the watchdog method.
        self.process_dict[ircRoom] = [Process(target=a.start), q, True]

    def start_processes(self, process_dict):
        """
        start_processes

        Helper function; starts all Pwitch processes.

        Parameters:-
        :param process_dict:    Dictionary of Pwitch processes generated from
                                create_process_dict.
                                i.e. adict["ircRoom"] = [Process, Queue]
        """
        print("[SERVER] Starting...")
        for i in process_dict.keys():
            process_dict[i][0].name = i
            process_dict[i][0].start()
            print("[CONNECTED] {}".format(i.lstrip("#")))

    def stop_process(self, pwitch_process):
        """
        stop_process

        Parameters:-
        :param pwitch_process:         list containing process and Queue.
        """

        pwitch_process[1].put(False)
        ## Watchdog to make sure it shuts down

    def stop_processes(self):
        """
        stop_threads

        Helper function; stops all pwitch threads
        """
        try:
            self.process_dict
        except:
            print("Processes may not have been initalised.")
        else:
            for i in self.adict.keys():
                self.adict[i][0].put(False)

        ## use watchdog to see if threads close properly
        ## Join threads

if __name__ == "__main__":
     import json
     cfg_dir = "/home/jonathan/projects/Pwitch/cfg/"
     cfg = cfg_dir+"cfg.json"
     channels = cfg_dir+"irc_channels.json"

     with open(cfg, 'r') as w:
         cfg = json.load(w)

     channel_list = cfg["channels"]

     ob = PwitchServer(bot_cfg, channel_list)
     ob.startThreads()
