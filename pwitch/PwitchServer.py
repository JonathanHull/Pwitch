#!/usr/bin/env python3.6

import time

from .Pwitch import Pwitch
from .PwitchLogging import PwitchStats
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
                 verbose = True,
                 channel_stats=True,
                 timeout = 10,
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
        :param verbose:         Enable verbose output.
        :param channel_stats:   Enable logging of channel statistics (Bool).
        :param timeout:         Set max hang time for threads. [Implement]
        """

        self.cfg = cfg
        self.channels = channels
        self.verbose = verbose
        self.channel_stats = channel_stats
        self.timeout = timeout

        self.connected = True     # watchdog thread flag

        if self.channel_stats:
            self.db_path = cfg["db_path"]
            self.api_key = cfg["api_key"]

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

        ## Channel statistics process -- Gathers statistics on Twitch channels.
        if self.channel_stats:
            db_path = self.cfg["db_path"]
            channel_stats = PwitchStats(db_path, self.channels, self.api_key)
            channel_stats_process = Process(target=channel_stats.start)
            channel_stats_process.start()


    def watchdog(self, timeout=10):
        """
        watchdog

        Watches the queue object for updates, and sends a signal to it if the
        status of the child process has changed

        Paramters:-
        :param timeout:         Time for process to shutdown before termination.
        """
        ## Extensive logging required.
        while self.connected:
            remove = []
            for key, values in self.process_dict.items():
                process, queue, flag = values

                ## try to terminate if attempt to close failed.
                ## May need to loop through this untill process is successfully
                ## terminated.
                if not flag: 
                    process.terminate()
                    time.sleep(0.2)
                    if not process.is_alive():
                        print(1)
                        remove.append(key)
                        process.join(timeout=1.0)
                        queue.close()
                        continue

                if not process.is_alive():
                    ## restart dead process
                    pass

            ## Removes any stopped processes after iterating through process dict.
            for i in remove:
                self.process_dict.pop(i)

            time.sleep(0.2)


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
        a = Pwitch(username, oauth, ircRoom, process_queue=q)

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
        if self.verbose:
            print("[SERVER] Starting...")
        for i in process_dict.keys():
            process_dict[i][0].name = i
            process_dict[i][0].start()
            print("[CONNECTED] {}".format(i))

    def stop_process(self, channel_name):
        """
        stop_process

        Parameters:-
        :param pwitch_process:  Twitch channel name to stop pwitch.
        """
        self.process_dict[channel_name][1].put(False)
        time.sleep(0.1)
        self.process_dict[channel_name][2] = False

        if all([x[2] is False for x in self.process_dict.values()]):
            self.connected = False

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
            for i in self.process_dict.keys():
                self.process_dict[i][1].put(False)
                self.process_dict[i][2] = False
                if self.verbose:
                    print("[DISCONNECTED] {}".format(i))

            self.connected = False

        ## use watchdog to see if threads close properly
        ## Join threads
