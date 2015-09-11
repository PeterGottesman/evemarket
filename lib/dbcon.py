#!/usr/bin/env python

import MySQLdb

def connect():
    f = open('../lib/pass.txt', 'r')
    password = f.readline().rstrip('\n')
    f.close()
    conn = MySQLdb.connect("localhost", "root", password,"evemarket")
    cursor = conn.cursor()

    return cursor, conn
