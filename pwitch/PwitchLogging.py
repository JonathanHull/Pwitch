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

import sqlite3
import os.path

class PwitchLogging:
    def __init__(self,
                 db_path,
                 db_table,
                 ):
        """
        PwitchLogging

        Pwitch's database logging module.

        Parameters:-
        :param db_path:     Path to database.
        :param db_table:    IRC Chatroom logging table i.e. chatroom name.

        Usage: variable = PwitchLogging(db_path, db_table)
               variable.sql_insert("username, "date", "time", "message")

        """

        self.db_path = db_path
        self.db_table = db_table
        self._connect()

    def _connect(self):
        """
        PwitchLogging.connect()

        Creates/Connects to database file.
        Checks for existance of database table and creates if needed.
        """

        self.database = sqlite3.connect(self.db_path)
        self.cursor = self.database.cursor()

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
            date,
            time,
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
            self.cursor.execute("INSERT INTO {} VALUES (?,?,?,?)".format(
                self.db_table), (username, date, time, message))
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

        Initialises database if not predefined.
        """

        self.cursor.execute("""
           CREATE TABLE {} (
           USERNAME text   NOT NULL, 
           DATE DATE       NOT NULL,
           TIME TIME       NOT NULL, 
           MESSAGE text    NOT NULL
           )""".format(self.db_table))
