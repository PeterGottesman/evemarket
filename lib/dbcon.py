#!/usr/bin/env python

import MySQLdb

def connect():
    f.open('pass.txt', 'r')
    password = f.readline()
    f.close()
    conn = MySQLdb.connect("localhost", "root", password,"evemarket")
    cursor = conn.cursor()

    return cursor, conn
