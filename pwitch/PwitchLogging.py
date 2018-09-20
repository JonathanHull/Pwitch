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

import sqlite3
import os.path
from .PwitchUtils import parent_dir

class PwitchLogging:
    def __init__(self,
                 ircRoom,
                 db_path,
                 db_table,
                 ):
        """
        PwitchLogging

        Pwitch's chat logging database class.

        Parameters:-
        :param db_path:     Path to database.
        :param db_table:    IRC Chatroom logging table i.e. chatroom name.

        Usage: variable = PwitchLogging(db_path, db_table)
               variable.sql_insert("username, "date", "time", "message")

        """
        
        self.ircRoom = ircRoom
        self.log = parent_dir(parent_dir(__file__))
        self.db_path = db_path
        self.db_table = db_table
        self._checkDatabase()

    def _checkDatabase(self, *databases):
        """
        _checkDatabase

        Creates/Connects to database file.
        Checks for existance of database table and creates if needed.
        """

        self.database = sqlite3.connect(self.db_path)
        self.cursor = self.database.cursor()

        ## Checks if table exists in database.

        self.cursor.execute("""
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type='table'
            AND name = '{}'
            """.format(self.db_table))

        if not self.cursor.fetchone()[0] == 1:
            self._create_table()

    def sql_insert(self, 
            username,
            datetime,
            message):
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

        try:
            self.cursor.execute("INSERT INTO {} VALUES (?,?,?)".format(
                self.db_table), (username, datetime, message))
            self.database.commit()
        except:
            print("Something Broke...")


    def sql_read(self,
            username,
            date=None):

        """
        sql_read

        Queries sql database for messages from specific user.

        Parameters:-
        :param username:    Username to query database.
        :param date:        Optional parameter to search within specific data.
        :param time:        Optional paramater to search within specific time.

        Usage: object.sql_read("USERNAME")
        """

        return None

    def _create_table(self):
        """
        _create_table

        Initialises Pwitch chat logging database if not predefined.
        """

        self.cursor.execute("""
           CREATE TABLE {} (
           USERNAME text   NOT NULL, 
           DATE DATE       NOT NULL,
           TIME TIME       NOT NULL, 
           MESSAGE text    NOT NULL
           )""".format(self.db_table))


class PwitchChannelStats(PwitchLogging):
    ## Note: Don't run _create_table everytime new process is initiated
    def __init__(self,
                 db_path,
                 ircRoom,
                 ):
        """
        PwitchChannelStats
        
        Pwitch's channel statistics database logging class
        """
        self.db_path = db_path
        self.log = open(parent_dir(db_path)+"/PwitchChannelStats.log", "w+")
        self.ircRoom = ircRoom
        #self.log_rate = log_rate
        self._checkDatabase()
        self.channel_in_database()

        self.channel_id = self.get_channel_id(ircRoom)

    def _checkDatabase(self, *table_list):
        """
        _checkDatabase

        Creates/Connects to database file.
        Checks for existance of database table and creates if needed.
        """

        self.database = sqlite3.connect(self.db_path)
        self.cursor = self.database.cursor()

        ## Checks if table exists in database.

        tableNames = ["stream_stats","pwitch_channel", "chat_log"]

        for i in tableNames:
            self.cursor.execute("""
                SELECT COUNT(*)
                FROM sqlite_master
                WHERE type='table'
                AND name = '{}'
                """.format(i))

            if not self.cursor.fetchone()[0] == 1:
                self._create_tables()

    def channel_in_database(self, ircRoom=None):
        """
        channel_in_database

        Checks whether the passed channel/list of channels have been defined
        within the sqlite3 database; and inserts them with the default metadata
        if not.

        Parameter(s):-
        :param ircRoom:         Channel/List of channels to define.
        """

        if not ircRoom:
            ircRoom = self.ircRoom

        if type(ircRoom) != type(list):
            ircRoom = [ircRoom]

        for channel in ircRoom:
            self.cursor.execute("""
                SELECT COUNT(ChannelName)
                FROM {}
                WHERE ChannelName = '{}'
                """.format("pwitch_channel", self.ircRoom))

            if not self.cursor.fetchone()[0] == 1:
                self.log_channel(channel, "FALSE", "FALSE", "FALSE")


    def _create_tables(self):
        """
        _create_table

        Initialises Pwitch Channel Statistics logging database if not
        predefined.
        """

        ## Could check to see whether each table exists independantly incase
        ## user accidentally removed one (only for chat_log, stream_stats).

        ## Records static channel properties
        self.cursor.execute("""
            CREATE TABLE {} (
            ChannelId       INTEGER     PRIMARY KEY AUTOINCREMENT,
            ChannelName     VARCHAR     NOT NULL,
            IsAdmin         BOOL        NOT NULL,
            IsLog           BOOL        NOT NULL,
            PwitchAdmin     BOOL        NOT NULL,
            CONSTRAINT name_unique UNIQUE (ChannelName)
        )""".format("pwitch_channel"))

        ## Logs messages from ircRoom
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

    def update_channel_tables(self):
        """
        update_channel_tables
        Updates the static channel data. This should be ran every 24 hours or
        when a chat command indicates change.
        """

        ## Write function in Pwitch.py which
        pass


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

    def log_stream_stats(self,
                         channel,
                         viewers,
                         stream_live,
                         game,
                         stream_start,
                         total_viewers,
                         total_followers,
                         date_time,
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

        channel_id = self.get_channel_id(channel)
        if not channel_id:
            ## Log; this shouldn't happen.
            ## Create channel id.
            pass

        try:
            self.cursor.execute("INSERT INTO {} (ChannelId, DateTime, Viewers,\
                StreamLive, Game, StreamStart, TotalViewers, \
                Followers) VALUES (?,?,?,?,?,?,?,?)".format(table_name),
                (channel_id, date_time, viewers, stream_live, game, 
                    stream_start, total_viewers, total_followers))
            self.database.commit()
        except:
            print("something broke")


class PwitchStats(PwitchChannelStats):
    def __init__(self,
                 db_path,
                 channels,
                 update_rate,
                ):
        """
        PwitchStats

        Logs stream statistics into a sqlite3 database.
        Intended to be ran as a thread alongside Pwitch, but chan be ran
        independantly.

        Parameters:-
        :param db_path:         Path to sqlite3 database.
        :param channels:        List of Twitch channels to monitor.
        :param update_rate:     Rate of logging (default: 60 seconds).
        """
        import requests
        import time

        self.db_path = db_path
        self.update_rate = update_rate
        self._check_database()

        self.check_table

    def start(self):
        self.connected = True

    def get_statistics(self):

        while self.connected:
            start_time = time.time()
            for irc_room in self.irc_rooms:
                req="https://api.twitch.tv/kraken/streams/{}?client_id={}".format(
                    irc_room, client_id)
                data = self.parse_json(req)

                #self.log_stream_stats(


            iteration_time = time.time() - start_time
            time.sleep(self.update_rate - iteration_time)

    def parse_json(self, request):
        """
        parse_json
        Scrapes wanted data from Twitch channel api request.

        Parameters:-
        :param request:         Twitch API request data.
        """
        adict = {}

        adict["datetime"]
        adict["viewers"] = request["stream"]["viewers"]
        adict["stream_live"] = request["stream"]["stream_type"]
        adict["game"] = request["stream"]["channel"]["game"]
        adict["stream_start"] = request["stream"]["created_at"]
        adict["total_viewers"] = request["stream"]["channel"]["viewers"]
        adict["total_followers"] = request["stream"]["channel"]["followers"]

        return adict





def get_date_time():
    pass
                          


if __name__ == "__main__":
    import datetime
    db_path = "test.db"
    db_object = PwitchChannelStats("test.db")

    dt = datetime.datetime.utcnow()
    date = ",".join(str(i) for i in dt.timetuple()[:3])
    time = ":".join(str(i) for i in dt.timetuple()[3:6])
    datetime = "M".join([date,time])

    db_object.log_channel("Steelwlng", "TRUE", "TRUE", "TRUE")
    db_object.log_channel("meme", "TRUE", "TRUE", "TRUE")
    db_object.log_channel("hihi", "TRUE", "TRUE", "TRUE")
    
    db_object.log_stream_stats("Steelwlng",
            200,"TRUE","test", "2018-10-10M7:00:00",
            3000,3000,"2018-10-10M8:00:00")
