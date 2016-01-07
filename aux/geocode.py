import urllib2
import json
import pandas as pd
from model import util

def get_address_component(result, name, key='short_name'):
    c = [c[key] for c in result['address_components'] if name in c['types']]
    if len(c) > 0:
        return c[0]
    else:
        return None

def geocode(test_ids, address, city, url): #'https://maps.googleapis.com/'
    response = urllib2.urlopen(url + '/maps/api/geocode/json?address=' + urllib2.quote((address + ' , ' + city + ' IL').decode('ascii', 'ignore')))
    result = json.load(response)['results'][0]

    # make sure result is in Chicago!
    if get_address_component(result, 'locality').upper() != 'CHICAGO' or \
            get_address_component(result, 'administrative_area_level_1') != 'IL':
        print 'not in chicago'
        return
    
    num = get_address_component(result, 'street_number')
    route =  get_address_component(result, 'route')
    
    if num == None or route == None:
        print 'None'
        return
    #address2 = (num + ' ' + route).upper()
    loc = result['geometry']['location']
    
    #print address + ',' + num + ',' + route + ',' + str(loc['lat']) + ',' + str(loc['lng'])
    
    connection = engine.connect()
    
    sql = 'insert into aux.geocode2 (address,num,route,lat,lng) ' \
        'values (\'{address}\',\'{num}\',\'{route}\',{lat},{lng})'.format(address=address,num=num,route=route,lat=loc['lat'],lng=loc['lng'])
            
    connection.execute(sql)
    """
    result = connection.execute('select id from aux.addresses where address = \'{address}\''.format(address=address)).first()
    if result != None:
        id = result['id']
        
        print 'Address exists: ' + str(id)
    else:
        sql = 'insert into aux.addresses (address, geom, source) ' \
        + 'values (\'{address}\', st_makepoint({lat}, {lng}), \'{source}\') returning id' \
        .format(address=address, city=city, lat=loc['lat'], lng=loc['lng'], source='dstk')

        result = connection.execute(sql).first()
        if result != None:
            id = result['id']
            print 'Inserted address: ' + str(id)
        else:
            id = None
            print 'Not found.'
            
    if id != None:
        for test_id in test_ids:
            sql = 'insert into aux.test_addresses (test_id,address_id,method) ' \
                'values ({test_id}, {address_id}, \'{method}\')'.format(test_id=test_id, address_id=id,method='dstk')
            
            connection.execute(sql)
    """
    connection.close()

def get_engine():
    global engine
    engine = util.create_engine()

get_engine()

rows = pd.read_sql(
    'select array_agg(id), t.address,city from input.tests t left join aux.test_addresses ta on t.id = ta.test_id where ta.test_id is null '
    'and t.cleaned_address is null and city=\'CHICAGO\' group by t.address, city', 
    engine)

def geocode_row(row):
    try:
        geocode(row[0], row[1], row[2])
    except:
        print row
    

from multiprocessing import Pool

import time
start_time = time.time()

p = Pool(processes=50, initializer=get_engine)
p.map(geocode_row, rows.values)
#print 'address,num,route,lat,lng'
#print("--- %s seconds ---" % str(time.time() - start_time))
#for row in rows.values:
    #print row
#    geocode_row(row)
#print("--- %s seconds ---" % str(time.time() - start_time))