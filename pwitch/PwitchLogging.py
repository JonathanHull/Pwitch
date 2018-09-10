#!/usr/bin/env python3.6

"""
PwitchLogging

Library containing Pwitch logging functions.
Version: 0.1 (Alpha)

Current Support:-
    sqlite3
    postgreSQL (planned)
"""

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

        Connects/Creates to passed SQLite database.
        """
        try:
            if not os.path.isfile(self.db_path):
                self.database = sqlite3.connect(self.db_path)
                self.cursor = self.database.cursor()
                self._create_table()

            else:
                self.database = sqlite3.connect(self.logfile)
                self.cursor = self.database.cursor()
        except:
            ## Insert logging event here.
            print("Something Broke.")

    def sql_insert(self, 
            username,
            date,
            time,
            message,
            ):
        """
        sql_insert

        Inserts chat messages into database table.

        Parameters:-
        :param username:    Message senders username.
        :param date:        Date message was sent.
        :param time:        Time message was sent.
        :param message:     Chat message.

        Note: All arguments must be of type string.
        """

        a = "INSERT INTO {} VALUES ('{}','{}','{}','{}')".format(self.db_table,
                username, date, time, message)

        self.cursor.execute(a)
        self.database.commit()

    def _create_table(self):
        """
        _create_table

        Initialises database if not predefined.
        """

        self.cursor.execute('''CREATE TABLE {}
                               (username text   NOT NULL, 
                                date DATE       NOT NULL,
                                time TIME       NOT NULL, 
                                message text    NOT NULL
                                )'''.format(self.db_table))
