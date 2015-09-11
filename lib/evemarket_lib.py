#!/usr/bin/env python
import dbcon
from datetime import datetime

def format_percentage(dec):
    percentage = "{0:.2f}%".format(float(dec)*100)
    return percentage 

def format_number(num):
    return "{0:,}".format(num)

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

def get_region(stationid):
    cursor, conn = dbcon.connect()
    cursor.execute("SELECT regionid FROM systems WHERE systemid=(SELECT systemid FROM stations WHERE stationid=%d)" % (stationid))
    return cursor.fetchone()[0]

def get_type_name(typeid):
    cursor, conn = dbcon.connect()
    cursor.execute("SELECT typename FROM types WHERE typeid=%d" % (typeid))
    name = cursor.fetchone()
    if name is None:
        return "No Name Found: TypeID " + str(typeid) 
    return name[0]

def get_type_name_no_blueprint(typeid):
    cursor, conn = dbcon.connect()
    cursor.execute("SELECT typename FROM types WHERE typeid=%d AND typename NOT LIKE '%%Blueprint'" % (typeid))
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

def get_avg_station_quantity(typeid, regionid):
    #return None
    cursor, conn = dbcon.connect()
    cursor.execute("SELECT AVG(quantity) FROM history WHERE typeid=%d AND regionid=%d" % (typeid, regionid))
    return cursor.fetchone()[0]

def get_margin_station(typeid, stationid):
    prices = get_price_station(typeid, stationid)
    profit = prices[0] - prices[1]
    margin = profit/prices[0]
    return margin

def get_margin_values(prices):
    profit = prices[0] - prices[1]
    margin = profit/prices[0]
    return margin

def get_station_trades(stationid, min_margin=0.15):
    start = datetime.now()
    trades = {}
    stationid = long(stationid)

    cursor, conn = dbcon.connect()
    #cursor.execute("SELECT DISTINCT typeid FROM orders WHERE stationid=%d AND bid = 0" % (stationid))
    cursor.execute("SELECT typeid, price FROM (SELECT * FROM orders WHERE stationid=%d\
            AND bid=0 ORDER BY typeid, price asc) price GROUP BY typeid" % (stationid))
    types_sell = dict(cursor.fetchall())
    #cursor.execute("SELECT DISTINCT typeid FROM orders WHERE stationid=%d AND bid = 1" % (stationid))
    cursor.execute("SELECT typeid, price FROM (SELECT * FROM orders WHERE stationid=%d\
            AND bid=1 ORDER BY typeid, price desc) price GROUP BY typeid" % (stationid))
    types_buy = dict(cursor.fetchall())
    typeids = [key for key in types_sell if key in types_buy]
    
    #print [key for key in types_sell]
    #types = dict((key, value) for key, value in types_sell if key in types_buy)
    for typeid in typeids:
    #types = [typeid[0] for typeid in types]
    #for typeid in types:
        name = get_type_name_no_blueprint(typeid)
        margin = get_margin_values([types_sell[typeid], types_buy[typeid]])
        quantity = get_avg_station_quantity(typeid, get_region(stationid))
        if margin is None or margin < min_margin or name is None:
            continue
        else:
            trades[name]=[typeid, format_percentage(margin), quantity]
            #trades[typeid]=[format_percentage(margin)]
    return trades
