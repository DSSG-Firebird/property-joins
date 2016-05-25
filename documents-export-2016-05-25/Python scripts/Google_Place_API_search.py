##### code copyright July 2015 
##### written by  Xiang Cheng, with Oliver Haimson, Michael Madaio, and Wenwen Zhang
##### on behalf of Data Science for Social Good - Atlanta
##### for Atlanta Fire Rescue Department
##### contact: chengxiang.cn@gmail.com

### Program usage: Search for Google Places using Google Places API

# Input: Names of files
coord_file = "Atlanta_Grid_Coordinates.csv"   # Atlanta Grid coordiantes 
type_file = 'google_place_types.csv'          # Google types to search
input_file = 'google_places_sample.csv'       # sampel output file; if you change the file, change the code too based on the columns
output_file = "Google_places.csv"             # output file name

API_KEY = '----PASTE YOUR GOOGLE PLACES API KEY HERE----'     # Your Google_Places_API key;

########### Google Places Searching    ############
import numpy as np
import pandas as pd
from googleplaces import GooglePlaces, types, lang
import googleplaces
import csv
import time

if API_KEY=='':
    print "Error: API_KEY not given!"
    print "Please add the Google Place API Key in the code: API_KEY=''!"
    exit()

google_places = GooglePlaces(API_KEY)
coord_file = "Atlanta_Grid_Coordinates.csv"
type_file = 'google_place_types.csv'
input_file = 'google_places_sample.csv'
output_file = "Google_places.csv"
cur_num = 0

cddf = pd.read_csv(coord_file)
gpdf = pd.read_csv(input_file)
tpdf = pd.read_csv(type_file)
gpdfi = gpdf.copy(deep=True)
curtp = 0
placenum = 0

print "Google Place Search Running for all types....."
print " *** It may take 12 hours or more to run *** "
for ti in range(tpdf.shape[0]):
    if ti >= curtp and tpdf['search'][ti]==1:
        tp = tpdf['type'][ti]
        print "Runing: ", tp, "......"
        for cdi in range(cddf.shape[0]):
            try:
                time.sleep(0.03)
                query_result = google_places.nearby_search(lat_lng={'lat': cddf['y'][cdi], 'lng': cddf['x'][cdi]}, radius=220., types=[tp])
            except:
                print '  Error Happend for google_places.nearby_search()...'
                print "  Try again 10s later:", cddf['y'][cdi],':', cddf['x'][cdi]
                time.sleep(10.1)
                query_result = google_places.nearby_search(lat_lng={'lat': cddf['y'][cdi], 'lng': cddf['x'][cdi]}, radius=220., types=[tp])

            if len(query_result.places)>0:
                if (cdi%400)==0:
                    print "\t%-6s: %.2f Completed (overall:%.2f)..." % (tp, 1.0*cdi/4300.0, 1.0*ti/(cddf.shape[0]+2))
                #print "%s:%d:%d; " % (tp, cdi, len(query_result.places)),
                exg = query_result.places
                for place in query_result.places:
                    place.get_details()
                    if sum(place.place_id == gpdf['g_id'])<1:
                        gpdf = gpdf.append(gpdfi, ignore_index=True)
                        placenum += 1
                        gpdf['g_id'][placenum] = place.place_id
                        gpdf['name'][placenum] = place.name.encode('UTF-8', 'ignore')
                        try:
                            gpdf['rating_num'][placenum] = place.details['user_ratings_total']
                        except KeyError:
                            x=None
                            #print '0 revs;',
                        try:
                            gpdf['closed'][placenum] = place.details['permanently_closed']
                            print "\nClosed:",  place.name
                        except:
                            gpdf['closed'][placenum] = -1
                        try:
                            gpdf['closed'][placenum] = place.permanently_closed
                            print "\nClosed:",  place.name
                        except:
                            gpdf['closed'][placenum] = -1
                        try:
                            gpdf['zip_code'][placenum] = places.details['address_components'][5]['short_name']
                        except:
                            gpdf['zip_code'][placenum] = 0
                        gpdf['address'][placenum] = place.formatted_address.encode('UTF-8', 'ignore')
                        gpdf['y'][placenum] = place.geo_location['lat']
                        gpdf['x'][placenum] = place.geo_location['lng']
                        gpdf['rating'][placenum] = place.rating
                        gpdf['phone'][placenum] = place.local_phone_number
                        gpdf['website'][placenum] = place.website 
                        gpdf['google_url'][placenum] = place.url
                        gpdf['type'][placenum] = place.details['types'][0]
                        gpdf['type_all'][placenum] = ','.join(place.details['types'])
        curtp += 1
        gpdf[1:].to_csv(output_file)

# output to csv file

