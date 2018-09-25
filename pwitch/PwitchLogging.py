#!/usr/bin/env python3.6

"""
PwitchLogging

Library containing Pwitch logging functions.
Version: 0.1 (Alpha)

Current Support:-
    sqlite3
    postgreSQL (planned)
"""

## Count have problem with mutliple threads connected to single SQLite server
## when making commits. Could pass the self.database.commit() call up to the
## thread managing child threads and make commits all at once.

## Sqlcommit only every hour.
## Maybe make table construction / insetion names global or part of self.

import requests
import sqlite3
import json
import time

#from .PwitchUtils import parent_dir
from .PwitchUtils import parent_dir, get_datetime

class PwitchDatabase:
    def __init__(self,
                 db_path,
                 channel_list,
                ):

        """
        PwitchDataBase
        Set up Pwitch's sqlite3 database

        Parameters:-
        :param db_path:         Path to sqlite3 database.
        :param channel_list:    List of channels to monitor.
        """
        self.db_path = db_path
        self.channel_list = [x.lstrip("#") for x in channel_list]
        self.database = sqlite3.connect(self.db_path)
        self.cursor = self.database.cursor()

        self.initialise()
        self.add_channels()

    def initialise(self, table_list=None):
        """
        initialise

        Check self.db_path exists and has the correct tables
        Paramters:-
        :param *table_list:     List of tables to check/create.
        """
        missing_tables = []

        if table_list == None:
            table_list = ["stream_stats", "pwitch_channel", "chat_log"]

        for i in table_list:
            self.cursor.execute("""
                SELECT COUNT(*)
                FROM sqlite_master
                WHERE type='table'
                AND name = (?)
            """, (i,))

            if not self.cursor.fetchone()[0] == 1:
                missing_tables.append(i)

        self.create_tables(missing_tables)

    def create_tables(self, missing_tables):
        """
        _create_table

        Initialises Pwitch Channel Statistics logging database if not
        predefined.

        Parameters:-
        :param missing_tables:  List if missing sqlite3 database tables.
        """

        ## Could check to see whether each table exists independantly incase
        ## user accidentally removed one (only for chat_log, stream_stats).

        ## Records static channel properties
        if "pwitch_channel" in missing_tables:
            self.cursor.execute("""
                CREATE TABLE {} (
                ChannelId       INTEGER     PRIMARY KEY AUTOINCREMENT,
                ChannelName     VARCHAR     NOT NULL,
                IsAdmin         BOOL        NOT NULL,
                IsLog           BOOL        NOT NULL,
                PwitchAdmin     BOOL        NOT NULL,
                CONSTRAINT name_unique UNIQUE (ChannelName)
            )""".format("pwitch_channel"))

        ## Logs messages from channels
        if "chat_log" in missing_tables:
            self.cursor.execute("""
                CREATE TABLE {} (
                ChannelId       INTEGER, 
                UserName        VARCHAR     NOT NULL,
                DateTime        DATETIME    NOT NULL,
                Message         VARCHAR     NOT NULL,
                FOREIGN KEY (ChannelId) REFERENCES pwitch_channel(ChannelId)
            )""".format("chat_log"))

        ## Monitors channel statistics i.e. viewer count over a stream.
        ## Logs statistics at user defined rate (self.log_rate).

        if "stream_stats" in missing_tables:
            self.cursor.execute("""
                CREATE TABLE {} (
                RecordId        INTEGER     PRIMARY KEY AUTOINCREMENT,
                ChannelId       INTEGER,
                DateTime        DATETIME    NOT NULL,   
                Viewers         INT         NOT NULL,
                StreamLive      BOOL        NOT NULL,
                Game            VARCHAR     NOT NULL,
                StreamStart     DATETIME    NOT NULL,
                TotalViewers    INT         NOT NULL,
                Followers       INT         NOT NULL,
                FOREIGN KEY (ChannelID) REFERENCES pwitch_channel(ChannelId)
            )""".format("stream_stats"))

    def log_channel(self,
                    channel_name,
                    is_bot_admin,
                    is_bot_logging,
                    pwitch_admin,
                    channel_table="pwitch_channel",
                   ):

        """
        channel_log

        Paramers:-
        :parm
        """
        try:
            self.cursor.execute("INSERT INTO {} (ChannelName, IsAdmin, IsLog, \
                PwitchAdmin) VALUES (?,?,?,?)".format(channel_table), 
                (channel_name, is_bot_admin, is_bot_logging, pwitch_admin))
            self.database.commit()

        except:
            ## logging module
            print("[log channel] Something broke")


    def add_channels(self, channels=None):
        """
        add_channel
        Add a twitch channel to the sqlite3 database.

        Parameters:-
        :param channels:        List of channels to be added to the pwitch databse.
                                Note: if channel=None: loads self.channels
        """

        if not channels:
            channels = self.channel_list

        if type(channels) != list:
            channels = [channels]

        for channel in channels:
            self.cursor.execute("""
                SELECT COUNT(ChannelName)
                FROM {}
                WHERE ChannelName = '{}'
                """.format("pwitch_channel", channel))

            if not self.cursor.fetchone()[0] == 1:
                self.log_channel(channel, "FALSE", "FALSE", "FALSE")

    def get_channel_id(self, channel_name):
        """
        get_channel_id
        Get channel identifier from channel database

        Parameters:-
        :param channel_name:     Channel name.
        """
        try:
            self.cursor.execute("""
                SELECT ChannelId FROM pwitch_channel \
                WHERE ChannelName=?""", (channel_name,))
            channel_id = self.cursor.fetchone()[0]
        except:
            channel_id = None
        return channel_id

class PwitchLogging(PwitchDatabase):
    ## Note: Don't run _create_table everytime new process is initiated
    def __init__(self,
                 db_path,
                 channel,
                 ):
        """
        PwitchChannelStats
        
        Pwitch's channel statistics database logging class
        """
        self.db_path = db_path
        self.log = open(parent_dir(db_path)+"/PwitchChannelStats.log", "w+")
        self.channel_list = channel

        ## Connect to database
        self.database = sqlite3.connect(self.db_path)
        self.cursor = self.database.cursor()

        ## Add channel to database / get channel_id
        self.add_channels()
        self.channel_id = self.get_channel_id(channel)

    def log_chat(self, 
            username,
            datetime,
            message,
            chat_table="chat_log",
            channel=None,
            ):
        """
        sql_insert

        Inserts chat messages into database table.

        Parameters:-
        :param username:    Message senders username.
        :param date:        Date message was sent.
        :param time:        Time message was sent.
        :param message:     Chat message.
        
        Note: date/time uses UTC, adjust accordingly.
        Note: All arguments must be of type string.
        """
        if channel==None:
            channel = self.channel_id
        try:
            self.cursor.execute("INSERT INTO {} VALUES (?,?,?,?)".format(
                chat_table), (channel, username, datetime, message))

            self.database.commit()
        except:
            ## Log
            self.log.write("{}|{}|{}|{}".format(channel, username, datetime,
                message))
            print("[log_chat] Something Broke...")



class PwitchStats(PwitchDatabase):
    def __init__(self,
                 db_path,
                 channels,
                 api_key,
                 update_rate=60,
                 process_queue=None,
                ):
        """
        PwitchStats

        Logs stream statistics into a sqlite3 database.
        Intended to be ran as a thread alongside Pwitch, but chan be ran
        independantly.

        Parameters:-
        :param db_path:         Path to sqlite3 database.
        :param channels:        List of Twitch channels to monitor.
        :param api_key:         Pwitch api key.
        :param update_rate:     Rate of logging (default: 60 seconds).
        """

        ## Note: May have to multiprocess/multithread this class to enable
        ## multiple API requests at once. Takes roughly 1s per channel :. needs
        ## multiple threads to scale to large number of channels.

        self.db_path = db_path
        self.channels = channels
        self.api_key = api_key
        self.update_rate = update_rate

        self.database = sqlite3.connect(db_path)
        self.cursor = self.database.cursor()

    def start(self):
        self.connected = True
        ## Check tables constructed / channels logged in database.
        ## self._check_database()
        self.add_channels(self.channels)
        channel_ids = self.pair_channelid_channelname(self.channels)
        self.main(channel_ids)

    def stop(self):
        self.connected = False

    def main(self, channel_ids):
        """
        main

        Logs statistics of specified Twitch channels into sqlite3 database
        table. Can be ran independantly of main Pwitch process.
        """
        while self.connected:
            start_time = time.time()
            while (time.time()-start_time < self.update_rate):
                try:
                    self.connected = self.process_queue.get_nowait()
                except:
                    time.sleep(0.2)
                self.log_channel_data(channel_ids)

            ## While loop implemented to catch server shutdown through mp queue.
            ## Requests channel data from twitch kraken service.
            #for channel in channel_ids:
            #    req="https://api.twitch.tv/kraken/streams/{}?client_id={}".format(
            #        channel[0], self.api_key)
            #    try:
            #        streamer_html = requests.get(req)
            #        raw_data = json.loads(streamer_html.text)
            #        data = self.parse_json(raw_data)
            #        if data == None:
            #            continue
            #        self.log_stream_stats(data, channel[1])
            #    except:
            #        pass

            #iteration_time = time.time() - start_time
            #time.sleep(self.update_rate - iteration_time)

    def log_channel_data(self, channels):
        for channel in channels:
            req="https://api.twitch.tv/kraken/streams/{}?client_id={}".format(
                channel[0], self.api_key)
            try:
                streamer_html = requests.get(req, timeout=5)
                raw_data = json.loads(streamer_html.text)
                data = self.parse_json(raw_data)
                if data == None:
                    continue
                self.log_stream_stats(data, channel[1])
            except:
                pass

    def pair_channelid_channelname(self,channels=None):
        """
        pair_channelid_channelname

        Returns list of tuples of passed channels
        Format - [(channel_name, channel_id)]
        """
        if not channels:
            channels = self.channels
        if type(channels) != list:
            channels = [channels]

        out_list = []
        for i in channels:
            out_list.append((i, self.get_channel_id(i)))

        return out_list

    def extend_channel_list(self, channels):
        """
        extend_channel_list

        Extends the self.irc_rooms variable for use in te get_statistics method.
        Allows additional channels to be added during thread runtime.

        parameters:-
        :param channels:        List of Twitch channels to add to monitor list.
        """
        pass

    def log_stream_stats(self,
                         #channel,
                         #viewers,
                         #stream_live,
                         #game,
                         #stream_start,
                         #total_viewers,
                         #total_followers,
                         #date_time,
                         data_dict,
                         channel_id,
                         table_name="stream_stats"
                        ):

        """
        log_stream_stats
        Logs stream statistics in sqlite3 database.

        Parameters:-
        :param channel:         Channel name.
        :param viewers:         Number of viewers currently watching stream.
        :param stream_live:     Stream currently live - BOOLEAN.
        :param total_viwers:    Total channel viewers.
        :param stream_start:    DATETIME when the stream started.
        :param game:            Game channel is currently playing.
        :param total_followers: Total number of people following channel.
        :param date_time:       The DATETIME when channel data was collected.
        :param table_name:      Table name -- Helper variable; contigent.
        """
        data = [x for x in data_dict.values()]
        data.insert(0, channel_id)

        try:
            self.cursor.execute("INSERT INTO {} (ChannelId, DateTime, Viewers,\
                StreamLive, Game, StreamStart, TotalViewers, \
                Followers) VALUES \
                (?,?,?,?,?,?,?,?)".format(table_name), data)

            self.database.commit()
        except:
            print("something broke")

    def parse_json(self, raw_data):
        """
        parse_json
        Scrapes wanted data from Twitch channel api request.

        Parameters:-
        :param raw_data:         Twitch API request data.
        """

        if raw_data["stream"] == None:
            return None

        adict = {}

        adict["datetime"] = get_datetime();
        adict["viewers"] = raw_data["stream"]["viewers"]
        adict["stream_live"] = raw_data["stream"]["stream_type"]
        adict["game"] = raw_data["stream"]["channel"]["game"]
        adict["stream_start"] = raw_data["stream"]["created_at"]
        adict["total_viewers"] = raw_data["stream"]["channel"]["views"]
        adict["total_followers"] = raw_data["stream"]["channel"]["followers"]

        return adict

if __name__ == "__main__":

    db_path = "memes_now.db"
    db_object = PwitchStats(db_path, ["dansgaming", "zfg1",
    "hyubsama","Borjoyze"],
            "cvlwzo59od73g9rbdmkjah896peib7")

    db_object.start()
