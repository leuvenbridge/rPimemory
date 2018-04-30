

import sqlite3


def create_connection(dbFile):
    ## connection to sql database
    conn = sqlite3.connect(dbFile)
    return conn


def create_table(conn, create_table_sql):
    ## create a table from the create_table_sql statement
    curs = conn.cursor()
    curs.execute(create_table_sql)


def create_database(dbPath):
    ## create database and tables for session, log and data

    sql_create_recording_table = ''' CREATE TABLE IF NOT EXISTS recordingTable (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    boxmac INTEGER NOT NULL,
                                    monkey INTEGER NOT NULL,
                                    task INTEGER NOT NULL,
                                    timestart REAL NOT NULL
                                ); '''

    sql_create_log_table = ''' CREATE TABLE IF NOT EXISTS logTable (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    recording INTEGER NOT NULL,
                                    boxmac INTEGER NOT NULL,
                                    timesession REAL NOT NULL,
                                    type INTEGER NOT NULL,
                                    value INTEGER NOT NULL,
                                        FOREIGN KEY (recording,boxmac) REFERENCES recordingTable(id,boxmac)
                                ); '''

    sql_create_data_table = ''' CREATE TABLE IF NOT EXISTS dataTable (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        recording INTEGER NOT NULL,
                                        boxmac INTEGER NOT NULL,
                                        timesession REAL NOT NULL,
                                        lambda REAL NOT NULL,
                                        tau REAL NOT NULL,
                                        pup REAL NOT NULL,
                                        pdown REA NOT NULL,
                                        avail INTEGER NOT NULL,
                                        click INTEGER NOT NULL,
                                        timeout INTEGER NOT NULL,
                                            FOREIGN KEY (recording,boxmac) REFERENCES recordingTable(id,boxmac)
                                    ); '''


    ## create a database connection
    conn = create_connection(dbPath)

    ## create tables
    create_table(conn, sql_create_recording_table)
    create_table(conn, sql_create_log_table)
    create_table(conn, sql_create_data_table)
    return conn
