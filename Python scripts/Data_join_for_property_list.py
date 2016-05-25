##### code copyright July 2015 
##### written by  Xiang Cheng, with Oliver Haimson, Michael Madaio, and Wenwen Zhang
##### on behalf of Data Science for Social Good - Atlanta
##### for Atlanta Fire Rescue Department
##### contact: chengxiang.cn@gmail.com

### Program usage: Join 6 data sets pair by pair

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import tzinfo, timedelta, datetime
import time
from collections import Counter
import json
import urllib
from fuzzywuzzy import fuzz
from googleplaces import GooglePlaces, types, lang
import googleplaces
import re

#### Input: data files ####

# data files
blisfile = 'Blis_business_license.csv'     # business license
fsaffile = 'Fsaf_current_inspection.csv'     # fsaf
gpfile = 'Google_places.csv'
lqfile = 'Liquor_license_events_removed.csv'
pkfile = 'PreK_programs_Jul2015.csv'
dcfile = 'Child_Care_Jul2015.csv'
g_type_file = "google_place_types.csv"


# name of joined data files
newblis = 'Blis_business_license_joined.csv'     # business license
newfsaf = 'Fsaf_current_inspection_joined.csv'     # fsaf
newgp = 'Google_places_joined.csv'
newlq = 'Liquor_license_joined.csv'
newpk = 'PreK_programs_Jul2015_joined.csv'
newdc = 'Child_Care_Jul2015_joined.csv'


################# Data joining #######################
print "*********** Data is joining *************"
print "\tIt may take 3~10 minutes"
fsdf = pd.read_csv(fsaffile, low_memory=False)
fsdf = fsdf.drop_duplicates(cols=['LEGACY_ACCTNO', 'Original Address'])
fsdf = fsdf.reset_index(drop=True)

gpdf = pd.read_csv(gpfile, low_memory=False)
bldf = pd.read_csv(blisfile, low_memory=False)

lqdf = pd.read_csv(lqfile, low_memory=False)
lqdf = lqdf.drop_duplicates(cols=['Legacy_DBA', 'AddressforTaxValidation'])
lqdf = lqdf.reset_index(drop=True)

dcdf = pd.read_csv(dcfile, low_memory=False)
pkdf = pd.read_csv(pkfile, low_memory=False)

# 0 Google data preprocessing
    # 0.1. Primay types: select items with their primary type in the selected list
gtypedf = pd.read_csv(g_type_file)
gtypes = list(gtypedf['type'][gtypedf['search']>0])
try:
    gtypes.remove('doctor') # remove doctor type because redundence with hospital
except:
    pass
selected_places = [tp in gtypes for tp in gpdf['type']] # keep only selected types (primary)

    # 0.2. Dentist: select only dental office but not individual dentist
tempdf = gpdf[gpdf['type']=='dentist']
temp_true_index = list(tempdf[['name', 'address']][tempdf['rating_num']>7].drop_duplicates(cols=['name']).index)
for ind in tempdf.index:
    tpli = re.sub('[&#$@]', ' ', re.sub('[!\'./]', '', tempdf.loc[ind,'name'].upper())).split()
    if (('DDS' not in tpli) and ('DMD' not in tpli) and ('DR' not in tpli) and ('PHD' not in tpli)) or ('PC' in tpli):
        temp_true_index += [ind]
    selected_places[ind] = False    # all dentist are intialized to be false
tempdf = tempdf.loc[temp_true_index, ['name', 'rating_num', 'address']].drop_duplicates(cols=['name']).drop_duplicates(cols=['address'])
for ind in tempdf.index:
    selected_places[ind] = True     # only selected ones are changed to True

    # 0.3.  Veterinary Care: select offices but not individual DVM
tempdf = gpdf[gpdf['type']=='veterinary_care']
temp_true_index = list(tempdf[['name', 'address']][tempdf['rating_num']>3].drop_duplicates(cols=['name']).index)
for ind in tempdf.index:
    tpli = re.sub('[&#$@]', ' ', re.sub('[!\'./]', '', tempdf.loc[ind,'name'].upper())).split()
    if ('DVM' not in tpli):
        temp_true_index += [ind]
    selected_places[ind] = False    # all dentist are intialized to be false
tempdf = tempdf.loc[temp_true_index, ['name', 'rating_num', 'address']].sort('rating_num', ascending=False)
tempdf = tempdf.drop_duplicates(cols=['name']).drop_duplicates(cols=['address'])
for ind in tempdf.index:
    selected_places[ind] = True     # only selected ones are changed to True
    



 
 
 # 0.4. for all other types, 
# bakery, book_stores, department_store, library, shopping_mall, place_of_worship, school, grocery_or_supermarket
othertypes = 'bakery, book_stores, hospital, lodging, furniture_store, department_store, library, shopping_mall, place_of_worship, school, grocery_or_supermarket'
othertypes = othertypes.replace(',', ' ').split()

for tp in othertypes:
    tempdf = gpdf[gpdf['type'] == tp]
    # keep all places having more than 5 reviewss
    temp_true_index = list(tempdf[['name', 'address']][tempdf['rating_num']>5].drop_duplicates(cols=['name', 'address']).index)
    for ind in tempdf.index:
        tpli = re.sub('[&#$@]', ' ', re.sub('[!\'./]', '', tempdf.loc[ind,'name'].upper())).split()
        if ind not in temp_true_index:
            temp_true_index += [ind]
        selected_places[ind] = False    # all dentist are intialized to be false
    tempdf = tempdf.loc[temp_true_index, ['name', 'rating_num', 'address']].sort('rating_num', ascending=False)
    #drop the places with the same address
    tempdf = tempdf.drop_duplicates(cols=['name']).drop_duplicates(cols=['address'])
    for ind in tempdf.index:
        selected_places[ind] = True     # only selected ones are changed to True


# 0.3. Bad address: remove bad addresses, such as Atlanta, GA, United States and outside Atlanta
                    # university buildings have multiple labs/depts will be only kept one
for i in gpdf.index:
    if gpdf['type'][i]=='university':
        selected_places[i] = False
        
    if len((gpdf['address'][i]).split()) < 7:
        selected_places[i] = False
        
    if abs(gpdf['y'][i]-33.7)>0.3 or abs(gpdf['x'][i]+84.4)>0.3:
        selected_places[i] = False


gpdf = gpdf[selected_places].reset_index(drop=True)



####### 1. join fsaf and google palces based on near_by_xy and names ######
foundnum = 0
# first small xy (0.0001) join
toldist = 0.0001
print "fsaf...google..."
for i in range(gpdf.shape[0]):
    names = fsdf['Legacy_ACCTNAME'][np.logical_and(abs(gpdf['y'][i] - fsdf['y'])<toldist, abs(gpdf['x'][i] - fsdf['x'])<toldist)]
    if len(names)>0:
        ind = list(names.index)
        scores = [fuzz.token_set_ratio(gpdf['name'][i], namei) for namei in names]
        max_ind = np.argmax(scores)
        dfind = ind[max_ind]
        if scores[max_ind]<80.:
            if scores[max_ind]>70:
                x=None
                #print '\tLOW SCORE: %d; %-6s; %s(g):%s(f)' % (scores[max_ind], gpdf['g_id'][i], gpdf['name'][i], fsdf['Legacy_ACCTNAME'][dfind])
        else:
            foundnum += 1
            gpdf['g_in_fs_yn'][i] = 1
            gpdf['fs_name'][i] = fsdf['Legacy_ACCTNAME'][dfind]
            gpdf['fs_id'][i] = fsdf['LEGACY_ACCTNO'][dfind]
            fsdf['fs_in_g_yn'][dfind] = 1
            fsdf['g_name'][dfind] = gpdf['name'][i]
            fsdf['g_id'][dfind] = gpdf['g_id'][i]
            fsdf['g_type'][dfind] = gpdf['type'][i]
            #print "Found:%d %d; %-6s; %s(g):%s(f)" % (foundnum, scores[max_ind], gpdf['g_id'][i],  gpdf['name'][i], fsdf['Legacy_ACCTNAME'][dfind])
print "\n************ Searching More  ***************\n"

toldist = 0.008
for i in range(gpdf.shape[0]):
    names = fsdf['Legacy_ACCTNAME'][np.logical_and(abs(gpdf['y'][i] - fsdf['y'])<toldist, abs(gpdf['x'][i] - fsdf['x'])<toldist)]
    if len(names)>0 and gpdf['g_in_fs_yn'][i]== 0:
        ind = list(names.index)
        scores = [fuzz.token_set_ratio(gpdf['name'][i], namei) for namei in names]
        max_ind = np.argmax(scores)
        dfind = ind[max_ind]
        if scores[max_ind]<86.:
            if scores[max_ind]>80:
                x=None
                #print '\tLOW SCORE: %d; %-6s; %s(g):%s(f)' % (scores[max_ind], gpdf['g_id'][i], gpdf['name'][i], fsdf['Legacy_ACCTNAME'][dfind])
        else:
            foundnum += 1
            gpdf['g_in_fs_yn'][i] = 1
            gpdf['fs_name'][i] = fsdf['Legacy_ACCTNAME'][dfind]
            gpdf['fs_id'][i] = fsdf['LEGACY_ACCTNO'][dfind]
            fsdf['fs_in_g_yn'][dfind] = 1
            fsdf['g_name'][dfind] = gpdf['name'][i]
            fsdf['g_id'][dfind] = gpdf['g_id'][i]
            #print "*Found:%d %d; %-6s; %s(g):%s(f)" % (foundnum, scores[max_ind], gpdf['g_id'][i],gpdf['name'][i], fsdf['Legacy_ACCTNAME'][dfind])

# output to csv files
fsdf.to_csv(newfsaf, index=False, na_rep='NA')
gpdf.to_csv(newgp, index=False, na_rep='NA')




####### 2. join fsaf and liquor license places based on near_by_xy and names ######
print "fsaf...liquor license..."
foundnum = 0
# first small xy (0.0001) join
toldist = 0.0001
for i in range(lqdf.shape[0]):
    names = fsdf['Legacy_ACCTNAME'][np.logical_and(abs(lqdf['y'][i] - fsdf['y'])<toldist, abs(lqdf['x'][i] - fsdf['x'])<toldist)]
    if len(names)>0:
        ind = list(names.index)
        scores = [fuzz.token_set_ratio(lqdf['Legacy_DBA'][i], namei) for namei in names]
        max_ind = np.argmax(scores)
        dfind = ind[max_ind]
        if scores[max_ind]<80.:
            if scores[max_ind]>70:
                x=None
                #print '\tLOW SCORE: %d; %-6d; %s(g):%s(f)' % (scores[max_ind], lqdf['GSU_IMPORT_ID'][i], lqdf['Legacy_DBA'][i], fsdf['Legacy_ACCTNAME'][dfind])
        else:
            foundnum += 1
            lqdf['lq_in_fs_yn'][i] = 1
            lqdf['fs_name'][i] = fsdf['Legacy_ACCTNAME'][dfind]
            lqdf['fs_id'][i] = fsdf['LEGACY_ACCTNO'][dfind]
            fsdf['fs_in_lq_yn'][dfind] = 1
            fsdf['lq_name'][dfind] = lqdf['Legacy_DBA'][i]
            fsdf['lq_id'][dfind] = lqdf['GSU_IMPORT_ID'][i]
            #print "Found:%d %d; %-6s; %s(g):%s(f)" % (foundnum, scores[max_ind], lqdf['GSU_IMPORT_ID'][i],  lqdf['Legacy_DBA'][i], fsdf['Legacy_ACCTNAME'][dfind])

print "\n************ Searching More  ***************\n"
toldist = 0.008
for i in range(lqdf.shape[0]):
    names = fsdf['Legacy_ACCTNAME'][np.logical_and(abs(lqdf['y'][i] - fsdf['y'])<toldist, abs(lqdf['x'][i] - fsdf['x'])<toldist)]
    if len(names)>0 and lqdf['lq_in_fs_yn'][i]==0:
        ind = list(names.index)
        scores = [fuzz.token_set_ratio(lqdf['Legacy_DBA'][i], namei) for namei in names]
        max_ind = np.argmax(scores)
        dfind = ind[max_ind]
        if scores[max_ind]<86.:
            if scores[max_ind]>75:
                x=None
                #print '\tLOW SCORE: %d; %-6d; %s(l):%s(f)' % (scores[max_ind], lqdf['GSU_IMPORT_ID'][i], lqdf['Legacy_DBA'][i], fsdf['Legacy_ACCTNAME'][dfind])
        else:
            foundnum += 1
            lqdf['lq_in_fs_yn'][i] = 1
            lqdf['fs_name'][i] = fsdf['Legacy_ACCTNAME'][dfind]
            lqdf['fs_id'][i] = fsdf['LEGACY_ACCTNO'][dfind]
            fsdf['fs_in_lq_yn'][dfind] = 1
            fsdf['lq_name'][dfind] = lqdf['Legacy_DBA'][i]
            fsdf['lq_id'][dfind] = lqdf['GSU_IMPORT_ID'][i]
            #print "*Found:%d %d; %-6s; %s(l):%s(f)" % (foundnum, scores[max_ind], lqdf['GSU_IMPORT_ID'][i],  lqdf['Legacy_DBA'][i], fsdf['Legacy_ACCTNAME'][dfind])

# Output to csv
lqdf.to_csv(newlq, index=False, na_rep='NA')
fsdf.to_csv(newfsaf, index=False, na_rep='NA')




####### 3. join fsaf and blis based on near_by_xy and names ######
print "fsaf...business license..."
foundnum = 0
# first small xy (0.0001) join
toldist = 0.0001
for i in range(bldf.shape[0]):
    names = fsdf['Legacy_ACCTNAME'][np.logical_and(abs(bldf['y'][i] - fsdf['y'])<toldist, abs(bldf['x'][i] - fsdf['x'])<toldist)]
    if len(names)>0:
        ind = list(names.index)
        scores = [fuzz.token_set_ratio(bldf['account_name'][i], namei) for namei in names]
        max_ind = np.argmax(scores)
        dfind = ind[max_ind]
        if scores[max_ind]<80.:
            if scores[max_ind]>70:
                x=None
                #print '\tLOW SCORE: %d; %-6d; %s(g):%s(f)' % (scores[max_ind], bldf['license_no'][i], bldf['account_name'][i], fsdf['Legacy_ACCTNAME'][dfind])
        else:
            foundnum += 1
            bldf['bl_in_fs_yn'][i] = 1
            bldf['fs_name'][i] = fsdf['Legacy_ACCTNAME'][dfind]
            bldf['fs_id'][i] = fsdf['LEGACY_ACCTNO'][dfind]
            fsdf['fs_in_bl_yn'][dfind] = 1
            fsdf['bl_name'][dfind] = bldf['account_name'][i]
            fsdf['bl_id'][dfind] = bldf['license_no'][i]
            fsdf['bl_sic'][dfind] = bldf['sic'][i]
            #print "Found:%d %d; %-6s; %s(g):%s(f)" % (foundnum, scores[max_ind], bldf['license_no'][i], bldf['account_name'][i], fsdf['Legacy_ACCTNAME'][dfind])

print "\n************ Searching More  ***************\n"
toldist = 0.008
for i in range(bldf.shape[0]):
    names = fsdf['Legacy_ACCTNAME'][np.logical_and(abs(bldf['y'][i] - fsdf['y'])<toldist, abs(bldf['x'][i] - fsdf['x'])<toldist)]
    if len(names)>0 and bldf['bl_in_fs_yn'][i]==0:
        ind = list(names.index)
        scores = [fuzz.token_set_ratio(bldf['account_name'][i], namei) for namei in names]
        max_ind = np.argmax(scores)
        dfind = ind[max_ind]
        if scores[max_ind]<90.:
            if scores[max_ind]>80:
                x=None
                #print '\tLOW SCORE: %d; %-6d; %s(b):%s(f)' % (scores[max_ind], bldf['license_no'][i], bldf['account_name'][i], fsdf['Legacy_ACCTNAME'][dfind])
        else:
            foundnum += 1
            bldf['bl_in_fs_yn'][i] = 1
            bldf['fs_name'][i] = fsdf['Legacy_ACCTNAME'][dfind]
            bldf['fs_id'][i] = fsdf['LEGACY_ACCTNO'][dfind]
            fsdf['fs_in_bl_yn'][dfind] = 1
            fsdf['bl_name'][dfind] = bldf['account_name'][i]
            fsdf['bl_id'][dfind] = bldf['license_no'][i]
            fsdf['bl_sic'][dfind] = bldf['sic'][i]
            #print "*Found:%d %d; %-6s; %s(b):%s(f)" % (foundnum, scores[max_ind], bldf['license_no'][i], bldf['account_name'][i], fsdf['Legacy_ACCTNAME'][dfind])

# Output to csv
bldf.to_csv(newblis, index=False, na_rep='NA')
fsdf.to_csv(newfsaf, index=False, na_rep='NA')



####### 4. join blis and google based on xy and names #######
print "business license...google..."
foundnum = 0
toldist=0.0001
for i in range(gpdf.shape[0]):
    names = bldf['account_name'][np.logical_and(abs(bldf['y'] - gpdf['y'][i])<toldist, abs(bldf['x'] - gpdf['x'][i])<toldist)]
    if len(names)>0:
        ind = list(names.index)
        scores = [fuzz.token_set_ratio(gpdf['name'][i], namei) for namei in names]
        max_ind = np.argmax(scores)
        dfind = ind[max_ind]
        if scores[max_ind]<80.:
            if scores[max_ind]>70:
                x=None
                #print '\tLOW SCORE: %d; %-6s; %s(g):%s(b)' % (scores[max_ind], gpdf['g_id'][i], gpdf['name'][i], bldf['account_name'][dfind])
        else:
            foundnum += 1
            gpdf['g_in_bl_yn'][i] = 1
            gpdf['bl_name'][i] = bldf['account_name'][dfind]
            gpdf['bl_id'][i] = bldf['license_no'][dfind]
            gpdf['bl_sic'][i] = bldf['sic'][dfind]
            bldf['bl_in_g_yn'][dfind] = 1
            bldf['g_name'][dfind] = gpdf['name'][i]
            bldf['g_id'][dfind] = gpdf['g_id'][i]
            #print "Found:%d %d; %-6s; %s(g):%s(fb" % (foundnum, scores[max_ind], gpdf['g_id'][i], gpdf['name'][i], bldf['account_name'][dfind])

print "\n************ Searching More  ***************\n"
toldist=0.008
for i in range(gpdf.shape[0]):
    names = bldf['account_name'][np.logical_and(abs(bldf['y'] - gpdf['y'][i])<toldist, abs(bldf['x'] - gpdf['x'][i])<toldist)]
    if len(names)>0 and gpdf['g_in_bl_yn'][i]==0:
        ind = list(names.index)
        scores = [fuzz.token_set_ratio(gpdf['name'][i], namei) for namei in names]
        max_ind = np.argmax(scores)
        dfind = ind[max_ind]
        if scores[max_ind]<90.:
            if scores[max_ind]>80:
                x=None
                #print '\tLOW SCORE: %d; %-6s; %s(g):%s(b)' % (scores[max_ind], gpdf['g_id'][i], gpdf['name'][i], bldf['account_name'][dfind])
        else:
            foundnum += 1
            gpdf['g_in_bl_yn'][i] = 1
            gpdf['bl_name'][i] = bldf['account_name'][dfind]
            gpdf['bl_id'][i] = bldf['license_no'][dfind]
            gpdf['bl_sic'][i] = bldf['sic'][dfind]
            bldf['bl_in_g_yn'][dfind] = 1
            bldf['g_name'][dfind] = gpdf['name'][i]
            bldf['g_id'][dfind] = gpdf['g_id'][i]
            #print "*Found:%d %d; %-6s; %s(g):%s(fb" % (foundnum, scores[max_ind], gpdf['g_id'][i], gpdf['name'][i], bldf['account_name'][dfind])
            
            
# output to csv file
bldf.to_csv(newblis, index=False, na_rep='NA')
gpdf.to_csv(newgp, index=False, na_rep='NA')




####### 5. join blis and liquor license based on xy and names #######
print "business license...liquor..."
foundnum = 0
toldist=0.0001
for i in range(lqdf.shape[0]):
    names = bldf['account_name'][np.logical_and(abs(bldf['y'] - lqdf['y'][i])<toldist, abs(bldf['x'] - lqdf['x'][i])<toldist)]
    if len(names)>0:
        ind = list(names.index)
        scores = [fuzz.token_set_ratio(lqdf['Legacy_DBA'][i], namei) for namei in names]
        max_ind = np.argmax(scores)
        dfind = ind[max_ind]
        if scores[max_ind]<80.:
            if scores[max_ind]>70:
                x=None
                #print '\tLOW SCORE: %d; %-6s; %s(l):%s(b)' % (scores[max_ind], lqdf['GSU_IMPORT_ID'][i], lqdf['Legacy_DBA'][i], bldf['account_name'][dfind])
        else:
            foundnum += 1
            lqdf['lq_in_bl_yn'][i] = 1
            lqdf['bl_name'][i] = bldf['account_name'][dfind]
            lqdf['bl_id'][i] = bldf['license_no'][dfind]
            lqdf['bl_sic'][i] = bldf['sic'][dfind]
            bldf['bl_in_lq_yn'][dfind] = 1
            bldf['lq_name'][dfind] = lqdf['Legacy_DBA'][i]
            bldf['lq_id'][dfind] = lqdf['GSU_IMPORT_ID'][i]
            #print "*Found:%d %d; %-6s; %s(g):%s(fb" % (foundnum, scores[max_ind], lqdf['GSU_IMPORT_ID'][i], lqdf['Legacy_DBA'][i], bldf['account_name'][dfind])

print "\n************ Searching More  ***************\n"
toldist=0.008
for i in range(lqdf.shape[0]):
    names = bldf['account_name'][np.logical_and(abs(bldf['y'] - lqdf['y'][i])<toldist, abs(bldf['x'] - lqdf['x'][i])<toldist)]
    if len(names)>0 and lqdf['lq_in_bl_yn'][i]==0:
        ind = list(names.index)
        scores = [fuzz.token_set_ratio(lqdf['Legacy_DBA'][i], namei) for namei in names]
        max_ind = np.argmax(scores)
        dfind = ind[max_ind]
        if scores[max_ind]<90.:
            if scores[max_ind]>80:
                x=None
                #print '\tLOW SCORE: %d; %-6s; %s(l):%s(b)' % (scores[max_ind], lqdf['GSU_IMPORT_ID'][i], lqdf['Legacy_DBA'][i], bldf['account_name'][dfind])
        else:
            foundnum += 1
            lqdf['lq_in_bl_yn'][i] = 1
            lqdf['bl_name'][i] = bldf['account_name'][dfind]
            lqdf['bl_id'][i] = bldf['license_no'][dfind]
            lqdf['bl_sic'][i] = bldf['sic'][dfind]
            bldf['bl_in_lq_yn'][dfind] = 1
            bldf['lq_name'][dfind] = lqdf['Legacy_DBA'][i]
            bldf['lq_id'][dfind] = lqdf['GSU_IMPORT_ID'][i]
            #print "*Found:%d %d; %-6s; %s(g):%s(fb" % (foundnum, scores[max_ind], lqdf['GSU_IMPORT_ID'][i], lqdf['Legacy_DBA'][i], bldf['account_name'][dfind])

# output to csv file
bldf.to_csv(newblis, index=False, na_rep='NA')
lqdf.to_csv(newlq, index=False, na_rep='NA')



####### 6. join liquor license and google places ######
print "liquor...google..."
foundnum = 0
toldist=0.0001
for i in range(gpdf.shape[0]):
    names = lqdf['Legacy_DBA'][np.logical_and(abs(lqdf['y'] - gpdf['y'][i])<toldist, abs(lqdf['x'] - gpdf['x'][i])<toldist)]
    if len(names)>0:
        ind = list(names.index)
        scores = [fuzz.token_set_ratio(gpdf['name'][i], namei) for namei in names]
        max_ind = np.argmax(scores)
        dfind = ind[max_ind]
        if scores[max_ind]<80.:
            if scores[max_ind]>70:
                x=None
                #print '\tLOW SCORE: %d; %-6s; %s(g):%s(l)' % (scores[max_ind], gpdf['g_id'][i], gpdf['name'][i],lqdf['Legacy_DBA'][dfind])
        else:
            foundnum += 1
            gpdf['g_in_lq_yn'][i] = 1
            gpdf['lq_name'][i] = lqdf['Legacy_DBA'][dfind]
            gpdf['lq_id'][i] = lqdf['GSU_IMPORT_ID'][dfind]
            lqdf['lq_in_g_yn'][dfind] = 1
            lqdf['g_name'][dfind] = gpdf['name'][i]
            lqdf['g_id'][dfind] = gpdf['g_id'][i]
            #print "Found:%d %d; %-6s; %s(g):%s(fb" % (foundnum, scores[max_ind], gpdf['g_id'][i], gpdf['name'][i], lqdf['Legacy_DBA'][dfind])

print "\n************ Searching More  ***************\n"
toldist=0.008
for i in range(gpdf.shape[0]):
    names = lqdf['Legacy_DBA'][np.logical_and(abs(lqdf['y'] - gpdf['y'][i])<toldist, abs(lqdf['x'] - gpdf['x'][i])<toldist)]
    if len(names)>0 and gpdf['g_in_lq_yn'][i]==0:
        ind = list(names.index)
        scores = [fuzz.token_set_ratio(gpdf['name'][i], namei) for namei in names]
        max_ind = np.argmax(scores)
        dfind = ind[max_ind]
        if scores[max_ind]<80.:
            if scores[max_ind]>70:
                x=None
                #print '\tLOW SCORE: %d; %-6s; %s(g):%s(l)' % (scores[max_ind], gpdf['g_id'][i], gpdf['name'][i],lqdf['Legacy_DBA'][dfind])
        else:
            foundnum += 1
            gpdf['g_in_lq_yn'][i] = 1
            gpdf['lq_name'][i] = lqdf['Legacy_DBA'][dfind]
            gpdf['lq_id'][i] = lqdf['GSU_IMPORT_ID'][dfind]
            lqdf['lq_in_g_yn'][dfind] = 1
            lqdf['g_name'][dfind] = gpdf['name'][i]
            lqdf['g_id'][dfind] = gpdf['g_id'][i]
            #print "*Found:%d %d; %-6s; %s(g):%s(fb" % (foundnum, scores[max_ind], gpdf['g_id'][i], gpdf['name'][i], lqdf['Legacy_DBA'][dfind])


####### new1. join fsaf and pre-K based on near_by_xy and names ######
foundnum = 0
# first small xy (0.0001) join
toldist = 0.001
print "fsaf...preK..."
for i in range(pkdf.shape[0]):
    names = fsdf['Legacy_ACCTNAME'][np.logical_and(abs(pkdf['y'][i] - fsdf['y'])<toldist, abs(pkdf['x'][i] - fsdf['x'])<toldist)]
    if len(names)>0:
        ind = list(names.index)
        scores = [fuzz.token_set_ratio(pkdf['Location'][i], namei) for namei in names]
        max_ind = np.argmax(scores)
        dfind = ind[max_ind]
        if scores[max_ind]<80.:
            if scores[max_ind]>70:
                x=None
                #print '\tLOW SCORE: %d; %-6s; %s(g):%s(f)' % (scores[max_ind], gpdf['g_id'][i], gpdf['name'][i], fsdf['Legacy_ACCTNAME'][dfind])
        else:
            foundnum += 1
            pkdf['pk_in_fs_yn'][i] = 1
            pkdf['fs_id'][i] = fsdf['LEGACY_ACCTNO'][dfind]
            fsdf['fs_in_pk_yn'][dfind] = 1
            fsdf['pk_id'][dfind] = pkdf['Provider_Number'][i]
            fsdf['pk_name'][dfind] = pkdf['Location'][i]
            print foundnum, ': ', fsdf['Legacy_ACCTNAME'][dfind], ':', pkdf['Location'][i]

            #print "Found:%d %d; %-6s; %s(g):%s(f)" % (foundnum, scores[max_ind], gpdf['g_id'][i],  gpdf['name'][i], fsdf['Legacy_ACCTNAME'][dfind])

####### new2. join blis and pre-K based on near_by_xy and names ######
foundnum = 0
# first small xy (0.0001) join
toldist = 0.001
print "blis...preK..."
for i in range(pkdf.shape[0]):
    names = bldf['account_name'][np.logical_and(abs(pkdf['y'][i] - bldf['y'])<toldist, abs(pkdf['x'][i] - bldf['x'])<toldist)]
    if len(names)>0:
        ind = list(names.index)
        scores = [fuzz.token_set_ratio(pkdf['Location'][i], namei) for namei in names]
        max_ind = np.argmax(scores)
        dfind = ind[max_ind]
        if scores[max_ind]<80.:
            if scores[max_ind]>70:
                x=None
                #print '\tLOW SCORE: %d; %-6s; %s(g):%s(f)' % (scores[max_ind], gpdf['g_id'][i], gpdf['name'][i], fsdf['Legacy_ACCTNAME'][dfind])
        else:
            foundnum += 1
            pkdf['pk_in_b_yn'][i] = 1
            pkdf['b_id'][i] = bldf['license_no'][dfind]
            pkdf['b_name'][i] = bldf['account_name'][dfind]
            pkdf['b_sic'][i] = bldf['sic'][dfind]
            bldf['bl_in_pk_yn'][dfind] = 1
            bldf['pk_id'][dfind] = pkdf['Provider_Number'][i]
            print foundnum, ': ', bldf['account_name'][dfind], ':', pkdf['Location'][i]
            

            
####### new3. join google and pre-K based on near_by_xy and names ######
foundnum = 0
# first small xy (0.0001) join
toldist = 0.001
print "google...preK..."
for i in range(pkdf.shape[0]):
    names = gpdf['name'][np.logical_and(abs(pkdf['y'][i] - gpdf['y'])<toldist, abs(pkdf['x'][i] - gpdf['x'])<toldist)]
    if len(names)>0:
        ind = list(names.index)
        scores = [fuzz.token_set_ratio(pkdf['Location'][i], namei) for namei in names]
        max_ind = np.argmax(scores)
        dfind = ind[max_ind]
        if scores[max_ind]<80.:
            if scores[max_ind]>70:
                x=None
                #print '\tLOW SCORE: %d; %-6s; %s(g):%s(f)' % (scores[max_ind], gpdf['g_id'][i], gpdf['name'][i], fsdf['Legacy_ACCTNAME'][dfind])
        else:
            foundnum += 1
            pkdf['pk_in_g_yn'][i] = 1
            pkdf['g_id'][i] = gpdf['g_id'][dfind]
            pkdf['g_name'][i] = gpdf['name'][dfind]
            pkdf['g_type'][i] = gpdf['type'][dfind]
            gpdf['g_in_pk_yn'][dfind] = 1
            gpdf['pk_id'][dfind] = pkdf['Provider_Number'][i]
            print foundnum, ': ', gpdf['name'][dfind], ':', pkdf['Location'][i]


####### new4. join fsaf and day care based on near_by_xy and names ######
foundnum = 0
# first small xy (0.0001) join
toldist = 0.001
print "fsaf...day care..."
for i in range(dcdf.shape[0]):
    names = fsdf['Legacy_ACCTNAME'][np.logical_and(abs(dcdf['y'][i] - fsdf['y'])<toldist, abs(dcdf['x'][i] - fsdf['x'])<toldist)]
    if len(names)>0:
        ind = list(names.index)
        scores = [fuzz.token_set_ratio(dcdf['Location'][i], namei) for namei in names]
        max_ind = np.argmax(scores)
        dfind = ind[max_ind]
        if scores[max_ind]<80.:
            if scores[max_ind]>70:
                x=None
                #print '\tLOW SCORE: %d; %-6s; %s(g):%s(f)' % (scores[max_ind], gpdf['g_id'][i], gpdf['name'][i], fsdf['Legacy_ACCTNAME'][dfind])
        else:
            foundnum += 1
            dcdf['dc_in_fs_yn'][i] = 1
            dcdf['fs_id'][i] = fsdf['LEGACY_ACCTNO'][dfind]
            fsdf['fs_in_dc_yn'][dfind] = 1
            fsdf['dc_id'][dfind] = dcdf['Provider_Number'][i]
            fsdf['dc_name'][dfind] = dcdf['Location'][i]
            print foundnum, ': ', fsdf['Legacy_ACCTNAME'][dfind], ':', dcdf['Location'][i]

            #print "Found:%d %d; %-6s; %s(g):%s(f)" % (foundnum, scores[max_ind], gpdf['g_id'][i],  gpdf['name'][i], fsdf['Legacy_ACCTNAME'][dfind])

####### new5. join blis and day care based on near_by_xy and names ######
foundnum = 0
# first small xy (0.0001) join
toldist = 0.001
print "blis...day care..."
for i in range(dcdf.shape[0]):
    names = bldf['account_name'][np.logical_and(abs(dcdf['y'][i] - bldf['y'])<toldist, abs(dcdf['x'][i] - bldf['x'])<toldist)]
    if len(names)>0:
        ind = list(names.index)
        scores = [fuzz.token_set_ratio(dcdf['Location'][i], namei) for namei in names]
        max_ind = np.argmax(scores)
        dfind = ind[max_ind]
        if scores[max_ind]<80.:
            if scores[max_ind]>70:
                x=None
                #print '\tLOW SCORE: %d; %-6s; %s(g):%s(f)' % (scores[max_ind], gpdf['g_id'][i], gpdf['name'][i], fsdf['Legacy_ACCTNAME'][dfind])
        else:
            foundnum += 1
            dcdf['dc_in_b_yn'][i] = 1
            dcdf['b_id'][i] = bldf['license_no'][dfind]
            dcdf['b_name'][i] = bldf['account_name'][dfind]
            dcdf['b_sic'][i] = bldf['sic'][dfind]
            bldf['bl_in_dc_yn'][dfind] = 1
            bldf['dc_id'][dfind] = dcdf['Provider_Number'][i]
            print foundnum, ': ', bldf['account_name'][dfind], ':', dcdf['Location'][i]
            

            
####### new6. join google and day care based on near_by_xy and names ######
foundnum = 0
# first small xy (0.0001) join
toldist = 0.001
print "google...preK..."
for i in range(dcdf.shape[0]):
    names = gpdf['name'][np.logical_and(abs(dcdf['y'][i] - gpdf['y'])<toldist, abs(dcdf['x'][i] - gpdf['x'])<toldist)]
    if len(names)>0:
        ind = list(names.index)
        scores = [fuzz.token_set_ratio(dcdf['Location'][i], namei) for namei in names]
        max_ind = np.argmax(scores)
        dfind = ind[max_ind]
        if scores[max_ind]<80.:
            if scores[max_ind]>70:
                x=None
                #print '\tLOW SCORE: %d; %-6s; %s(g):%s(f)' % (scores[max_ind], gpdf['g_id'][i], gpdf['name'][i], fsdf['Legacy_ACCTNAME'][dfind])
        else:
            foundnum += 1
            dcdf['dc_in_g_yn'][i] = 1
            dcdf['g_id'][i] = gpdf['g_id'][dfind]
            dcdf['g_name'][i] = gpdf['name'][dfind]
            dcdf['g_type'][i] = gpdf['type'][dfind]
            gpdf['g_in_dc_yn'][dfind] = 1
            gpdf['dc_id'][dfind] = dcdf['Provider_Number'][i]
            print foundnum, ': ', gpdf['name'][dfind], ':', dcdf['Location'][i]



fsdf.to_csv(newfsaf, index=False, na_rep="NA")
gpdf.to_csv(newgp, index=False, na_rep="NA")
bldf.to_csv(newblis, index=False, na_rep="NA")
lqdf.to_csv(newlq, index=False, na_rep="NA")
pkdf.to_csv(newpk, index=False, na_rep="NA")
dcdf.to_csv(newdc, index=False, na_rep="NA")
