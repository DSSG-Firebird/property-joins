##### code copyright July 2015 
##### written by  Xiang Cheng, with Oliver Haimson, Michael Madaio, and Wenwen Zhang
##### on behalf of Data Science for Social Good - Atlanta
##### for Atlanta Fire Rescue Department
##### contact: chengxiang.cn@gmail.com
import numpy as np
import pandas as pd
from googleplaces import GooglePlaces, types, lang
import googleplaces
import time

# Program usage: Geocode addresses to coordiantes (lattitude and longitude) 
# Input: csv file name
# Output: a new csvfile "address2xy.csv"

# input:
filename = 'sample_addresses_for_geocoding.csv'   # file name to geocode
address_col_name = 'address'        # column name of the address
API_KEY = ''                        # Your Google Geocode API key
newfilename = filename[:-4] + '_xy.csv' # new file name

##########################  Geocoding  #################################
print "Geocoding ....... "
print "Please make sure the column name of addresses is %s !" % (address_col_name)
print "Make sure city and state is included in the addresses!"

df = pd.read_csv(filename, low_memory=False)

google_places = GooglePlaces(API_KEY)
xy = np.zeros((df.shape[0],2))

for i in df.index:
  
      address = df[address_col_name][i]  
      # if city and state not included, add " + 'City, State' "
      # i.e. the new code the the line above will be: address = df[address_col_name][i]  + "City, State"
      
      try:
        latlng = googleplaces.geocode_location(address, sensor=False) # geocode
      except:
        print "Google returned an error; we will retry in 20 seconds" 
        time.sleep(20.123)  # if there is an error, stop for 29.123 seconds and try again
        latlng = googleplaces.geocode_location(address, sensor=False) # geocode

      xy[i, 1] = latlng['lng']
      xy[i, 0] = latlng['lat']
      print  ' %-3d geocoded: %s : %-.6f, %-.6f' % (i, address, latlng['lat'], latlng['lng'])
      time.sleep(0.1592578357)
      # stop for 0.1592578357 seconds; otherwise google will return error
df['lat'] = xy[:,0]
df['lng'] = xy[:,1]

##### output data to a file #####
df.to_csv(newfilename, index=False, na_rep="NA")
print "Done! Data with lat and lng is saved as \"%s\"" % newfilename

