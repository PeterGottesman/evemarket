#!/usr/bin/env python
import dbcon
from datetime import datetime

def format_percentage(dec):
    percentage = "{0:.2f}%".format(float(dec)*100)
    return percentage

def get_system_name(systemid):
    cursor, conn = dbcon.connect()
    cursor.execute("SELECT systemname FROM systems WHERE systemid=%d" % (systemid))
    name = cursor.fetchone()
    return name[0]

def get_station_name(stationid):
    cursor, conn = dbcon.connect()
    cursor.execute("SELECT stationname FROM stations WHERE stationid=%d" % (systemid))
    name = cursor.fetchone()
    return name[0]

def get_region_name(regionid):
    cursor, conn = dbcon.connect()
    cursor.execute("SELECT regionname FROM regions WHERE regionid=%d" % (regionid))
    name = cursor.fetchone()
    return name[0]

def get_type_name(typeid):
    cursor, conn = dbcon.connect()
    cursor.execute("SELECT typename FROM types WHERE typeid=%d" % (typeid))
    name = cursor.fetchone()
    if name is None:
        return "No Name Found: TypeID " + str(typeid) 
    return name[0]

def get_type_name_no_blueprint(typeid):
    cursor, conn = dbcon.connect()
    cursor.execute("SELECT typename FROM types WHERE typeid=%d NOT LIKE '%%Blueprint'" % (typeid))
    name = cursor.fetchone()
    if name is None:
        return None
    return name[0]

def get_price_station(typeid, stationid):
    prices = []
    cursor, conn = dbcon.connect()
    cursor.execute("SELECT MIN(price) FROM orders WHERE typeid=%d AND\
            stationid=%d AND bid=0" % (int(typeid), int(stationid)))
    prices.append(cursor.fetchone()[0])
    cursor.execute("SELECT MAX(price) FROM orders WHERE typeid=%d AND\
            stationid=%d AND bid=1" % (int(typeid), int(stationid)))
    prices.append(cursor.fetchone()[0])
    conn.close()
    return prices

def get_margin_station(typeid, stationid):
    prices = get_price_station(typeid, stationid)
    profit = prices[0] - prices[1]
    margin = profit/prices[0]
    return margin

def get_station_trades(stationid, min_margin=0.15):
    start = datetime.now()
    trades = {}
    stationid = long(stationid)

    cursor, conn = dbcon.connect()
    cursor.execute("SELECT DISTINCT typeid FROM orders WHERE stationid=%d AND bid = 0" % (stationid))
    types_sell = set(cursor.fetchall())
    cursor.execute("SELECT DISTINCT typeid FROM orders WHERE stationid=%d AND bid = 1" % (stationid))
    types_buy = set(cursor.fetchall())
    types = list(types_sell & types_buy) #Intersection
    types = [typeid[0] for typeid in types]
    for typeid in types:
        print types.index(typeid)
        name = get_type_name_no_blueprint(typeid)
        margin = get_margin_station(typeid, stationid)
        if margin is None or margin < min_margin or name is None:
            continue
        else:
            trades[name]=format_percentage(margin)
            #trades[typeid]=[format_percentage(margin)]
    print "Completed Request in " + str((datetime.now()-start).total_seconds) + " seconds"
    return trades
