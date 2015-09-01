#!/usr/bin/env python
import sys
sys.path.append('../lib/')

import dbcon
import zlib
import arrow
# This can be replaced with the built-in json module, if desired.
import simplejson
import gevent
import signal
import zmq.green as zmq
from MySQLdb import Error
from MySQLdb import escape_string as escape
from datetime import datetime
from gevent.pool import Pool
from gevent import monkey; gevent.monkey.patch_all()

# The maximum number of greenlet workers in the greenlet pool. This is not one
# per processor, a decent machine can support hundreds or thousands of greenlets.
# I recommend setting this to the maximum number of connections your database
# backend can accept, if you must open one connection per save op.
MAX_NUM_POOL_WORKERS = 200
logfile = '../logs/logfile.txt'

def main():
    """
    The main flow of the application.
    """
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)

    # Connect to the first publicly available relay.
    subscriber.connect('tcp://relay-us-central-1.eve-emdr.com:8050')
    # Disable filtering.
    subscriber.setsockopt(zmq.SUBSCRIBE, "")

    # We use a greenlet pool to cap the number of workers at a reasonable level.
    greenlet_pool = Pool(size=MAX_NUM_POOL_WORKERS)

    print("Consumer daemon started, waiting for jobs...")
    print("Worker pool size: %d" % greenlet_pool.size)
    
    while True:
        # Since subscriber.recv() blocks when no messages are available,
        # this loop stays under control. If something is available and the
        # greenlet pool has greenlets available for use, work gets done.
        greenlet_pool.spawn(worker, subscriber.recv())

def worker(job_json):
    """
    For every incoming message, this worker function is called. Be extremely
    careful not to do anything CPU-intensive here, or you will see blocking.
    Sockets are async under gevent, so those are fair game.
    """
    market_json = zlib.decompress(job_json)
    market_data = simplejson.loads(market_json)

    try:
        resultType = market_data['resultType']
    except KeyError as e:
        log("Error getting result type")
        return

    cursor, conn = dbcon.connect()
    if resultType == 'orders':
        insert_sql = "INSERT INTO orders\
                (typeid, regionid, price, volremaining, orderrange, orderid, volentered,\
                minvolume, bid, issuedate, duration, stationid, solarsystemid) VALUES"
        values = "('%d', '%d', '%f', '%d', '%d', '%d', '%d', '%d', '%d', '%s', '%d', '%d', '%d')," 
        delete_sql = "DELETE FROM orders WHERE regionid = %d AND typeid = %d"

        try:
            for rowset in market_data['rowsets']:
                if len(rowset['rows']) <= 0:
                    continue
                try:
                    cursor.execute(delete_sql % (rowset['regionID'], rowset['typeID']))
                    conn.commit()
                except Error as e:
                    log("orders : " + delete_sql % (rowset['regionID'], rowset['typeID']))
                    log("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
                    conn.rollback()
                for row in rowset['rows']:
                    insert_sql += values % (rowset['typeID'], rowset['regionID'], row[0], row[1], row[2], row[3], row[4], row[5], row[6], arrow.get(row[7]).datetime.strftime('%Y-%m-%d %H:%M:%S'), row[8], row[9], row[10])
                try:
                    cursor.execute(insert_sql[:-1])
                    conn.commit()
                except:
                    log("Error inserting orders, rolling back")
                    log(simplejson.dumps(market_data, indent=4*' '))
                    conn.rollback()
        except KeyError as e:
            log("Error parsing order rowsets")
            conn.close()
            return
    elif resultType == 'history':
        insert_sql = "INSERT INTO history (typeid, regionid, issuedate, orders, low, high, average, quantity) VALUES"
        values = "('%d', '%d', '%s', '%d', '%d', '%d', '%d', '%d'),"
        delete_sql = "DELETE FROM history WHERE regionid = %d AND typeid = %d" 

        try:
            for rowset in market_data['rowsets']:
                try:
                    cursor.execute(delete_sql % (rowset['regionID'], rowset['typeID']))
                    conn.commit()
                except Error as e:
                    log("history : " + delete_sql % (rowset['regionID'], rowset['typeID']))
                    log("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
                    conn.rollback()
                for row in rowset['rows']:
                    insert_sql += values % (rowset['typeID'], rowset['regionID'], arrow.get(row[0]).datetime.strftime('%Y-%m-%d %H:%M:%S'), row[1], row[2], row[3], row[4], row[5])
                try:
                    cursor.execute(insert_sql[:-1])
                    conn.commit()
                except:
                    log("Error inserting history, rolling back")
                    log(simplejson.dumps(market_data, indent=4*' '))
                    conn.rollback()
        except KeyError as e:
            log("Error parsing history rowsets")
            conn.close()
            return
    conn.close()

def initlog():
    f = open(logfile, 'w')
    f.close()

def log(string):
    f = open(logfile, 'a')
    f.write(str(datetime.now()) + " : " + string + '\n')
    f.close()

def sigint_handler(signum, frame):
    print "Exiting"
    exit()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)
    initlog()
    main()

