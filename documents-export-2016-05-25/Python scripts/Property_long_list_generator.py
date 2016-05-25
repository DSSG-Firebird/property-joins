##### code copyright July 2015 
##### written by  Xiang Cheng, with Oliver Haimson, Michael Madaio, and Wenwen Zhang
##### on behalf of Data Science for Social Good - Atlanta
##### for Atlanta Fire Rescue Department
##### contact: chengxiang.cn@gmail.com

## Program usage: generate a long property list using joined data sets
## The only difference is that more businesses are included here than short list



import numpy as np
import pandas as pd
import unicodedata

#### Input: Data Files ####
# input data files
blisfile = 'Blis_business_license_joined.csv'     # business license
fsaffile = 'Fsaf_current_inspection_joined.csv'     # fsaf
gpfile = 'Google_places_joined.csv'
lqfile = 'Liquor_license_joined.csv'
pkfile = 'PreK_programs_Jul2015_joined.csv'
dcfile = 'Child_Care_Jul2015_joined.csv'

sicfile = 'BLIS_SIC_Desc.csv'
sic_sel_file = 'sic_counts_desc.csv'
sic_desc_count_file = sic_sel_file
fire_file = "AFRD_coords.csv"
insp_file = "FSAF_Inspec2011_2015.csv"
blis_costar_file = "BLIS_JOIN_COSTAR.csv"
risk_file = 'risk_scores_address.csv'
cfile = risk_file
ffile = 'fsaf_address_validation_output.csv'
gtmfile = 'google_type_mapping.csv'
gtypefile = 'google_place_types.csv'

# output file name
d1samplefile = 'Property_list_sample.csv'
newd1file = 'Property_list_long.csv'


############## Data joining ###############
print "*************** Data Joining ****************"
print " It may take 2 ~ 10 minutes "

bldf = pd.read_csv(blisfile)
fsdf = pd.read_csv(fsaffile)
gpdf = pd.read_csv(gpfile)
lqdf = pd.read_csv(lqfile)
d1df = pd.read_csv(d1samplefile) 
pkdf = pd.read_csv(pkfile)
dcdf = pd.read_csv(dcfile)
d1dfi = d1df.copy(deep=True)
sicdf = pd.read_csv(sicfile)

tot_num = 0
ind_num = 0

print "Running FSAF..."
# 1. Fsaf
for i in range(fsdf.shape[0]):
    d1df = d1df.append(d1dfi, ignore_index=True)
    tot_num += 1
    ind_num += 1
    d1df['name'][tot_num] = fsdf['Legacy_ACCTNAME'][i].replace("\"",' ')
    d1df['fsaf_name'][tot_num] = fsdf['Legacy_ACCTNAME'][i].replace("\"",' ')
    d1df['address'][tot_num] = fsdf['Original Address'][i].replace("\"",' ')
    d1df['phone'][tot_num] = fsdf['Hansen_PHONE'][i]
    d1df['occup_type'][tot_num] = fsdf['Legacy_Occtype_DESCRIPTION'][i].replace("\"",' ')
    d1df['y'][tot_num] = fsdf['y'][i]
    d1df['x'][tot_num] = fsdf['x'][i]
    d1df['in_fsaf_yn'] = 1
    d1df['inspection_date'][tot_num] = fsdf['Legacy_INSPDATE'][i]
    d1df['issue_date'][tot_num] = fsdf['Legacy_ISSDATE'][i]
    d1df['fsaf_id'][tot_num] = fsdf['LEGACY_ACCTNO'][i]
    # blis info
    if fsdf['fs_in_bl_yn'][i]==1:
        d1df['b_sic_desc'][tot_num] = list(sicdf['sic_desc'][sicdf['sic']==fsdf['bl_sic'][i]])[0]
        d1df['b_sic'][tot_num] = fsdf['bl_sic'][i]
        d1df['b_id'][tot_num] = fsdf['bl_id'][i]
        d1df['blis_name'][tot_num] = fsdf['bl_name'][i].replace("\"",' ')
    # liquor license info
    if fsdf['fs_in_lq_yn'][i]==1:
        d1df['liq_id'][tot_num] = fsdf['lq_id'][i]
        d1df['liq_name'][tot_num] = fsdf['lq_name'][i].replace("\"",' ')
    # google info
    if fsdf['fs_in_g_yn'][i]==1:
        ind = np.where(gpdf['g_id']==fsdf['g_id'][i])[0][0]
        d1df['google_id'][tot_num] = gpdf['g_id'][ind]
        d1df['google_type'][tot_num] = gpdf['type'][ind].upper().replace("\"",' ')
        d1df['google_name'][tot_num] = gpdf['name'][ind].upper().replace("\"",' ')
        d1df['google_website'][tot_num] = gpdf['google_url'][ind]
        d1df['google_review_num'][tot_num] = gpdf['rating_num'][ind]
        d1df['google_rating'][tot_num] = gpdf['rating'][ind]
    else:
        d1df['google_review_num'][tot_num] = 0
        
    #### preK ####
    if fsdf['fs_in_pk_yn'][i]==1:
        d1df['preK_daycare'][tot_num] = "PreK"
        d1df['provider_no'][tot_num] = fsdf['pk_id'][i]
        d1df['pkdc_name'][tot_num] = fsdf['pk_name'][i]
    
    #### day care ####
    if fsdf['fs_in_dc_yn'][i]==1:
        d1df['preK_daycare'][tot_num] = "DayCare"
        d1df['provider_no'][tot_num] = fsdf['dc_id'][i]
        d1df['pkdc_name'][tot_num] = fsdf['dc_name'][i]


d1df.to_csv(newd1file, index=False, na_rep='NA')       
print '\tdone: %d added!' % (ind_num)

print "Running Liquor..."
# 2. Liquor
ind_num = 0
for i in range(lqdf.shape[0]):
    if(lqdf['lq_in_fs_yn'][i]==0):
        d1df = d1df.append(d1dfi, ignore_index=True)
        tot_num += 1
        ind_num += 1
        d1df['name'][tot_num] = str(lqdf['Legacy_DBA'][i]).replace("\"",' ')
        d1df['liq_name'][tot_num] = str(lqdf['Legacy_DBA'][i]).replace("\"",' ')
        d1df['address'][tot_num] = lqdf['AddressforTaxValidation'][i].replace("\"",' ')
        d1df['liq_id'][tot_num] = lqdf['GSU_IMPORT_ID'][i]
        d1df['in_fsaf_yn'][tot_num] = 0
        
        d1df['inspection_date'][tot_num] = None
        d1df['issue_date'][tot_num] = None
        
        if len(str(lqdf['Legacy_BUSINESS NUM'][i]))>5:
            d1df['phone'][tot_num] = lqdf['Legacy_BUSINESS NUM'][i]
        elif len(str(lqdf['Legacy_HOME NUM'][i]))>5:
            d1df['phone'][tot_num] = lqdf['Legacy_HOME NUM'][i]
        else:
            d1df['phone'][tot_num] = lqdf['Legacy_CELL NUM'][i]

        d1df['y'][tot_num] = lqdf['y'][i]
        d1df['x'][tot_num] = lqdf['x'][i]

        # blis info
        if lqdf['lq_in_bl_yn'][i]==1:
            d1df['b_sic_desc'][tot_num] = list(sicdf['sic_desc'][sicdf['sic']==lqdf['bl_sic'][i]])[0]
            d1df['b_sic'][tot_num] = lqdf['bl_sic'][i]
            d1df['b_id'][tot_num] = lqdf['bl_id'][i]
            d1df['blis_name'][tot_num] = lqdf['bl_name'][i].replace("\"",' ')

        # google info
        if lqdf['lq_in_g_yn'][i]==1:
            ind = np.where(gpdf['g_id']==lqdf['g_id'][i])[0][0]
            d1df['google_id'][tot_num] = gpdf['g_id'][ind]
            d1df['google_type'][tot_num] = gpdf['type'][ind].upper()
            d1df['google_name'][tot_num] = gpdf['name'][ind].upper().replace("\"",' ')
            d1df['google_website'][tot_num] = gpdf['google_url'][ind]
            d1df['google_review_num'][tot_num] = gpdf['rating_num'][ind]
            d1df['google_rating'][tot_num] = gpdf['rating'][ind]
        else:
            d1df['google_review_num'][tot_num] = 0
d1df.to_csv(newd1file, index=False, na_rep='NA') 
print '\tdone: %d added!' % (ind_num)
ind_num = 0



print "Running PreK..."
###### 2. PreK program #########
ind_num = 0
for i in range(pkdf.shape[0]):
    if(pkdf['pk_in_fs_yn'][i]==0):
        d1df = d1df.append(d1dfi, ignore_index=True)
        tot_num += 1
        ind_num += 1
        d1df['name'][tot_num] = str(pkdf['Location'][i]).replace("\"",' ')
        d1df['pkdc_name'][tot_num] = str(pkdf['Location'][i]).replace("\"",' ')
        d1df['address'][tot_num] = pkdf['Address'][i].replace("\"",' ')
        d1df['provider_no'][tot_num] = pkdf['Provider_Number'][i]
        d1df['in_fsaf_yn'][tot_num] = 0
        d1df['preK_daycare'][tot_num] = 'PreK'
        d1df['inspection_date'][tot_num] = None
        d1df['issue_date'][tot_num] = None
        d1df['preK_daycare'][tot_num] = "PreK"
        d1df['phone'][tot_num] = pkdf['Phone'][i]

        d1df['y'][tot_num] = pkdf['y'][i]
        d1df['x'][tot_num] = pkdf['x'][i]

        # blis info
        if pkdf['pk_in_b_yn'][i]==1:
            d1df['b_sic_desc'][tot_num] = list(sicdf['sic_desc'][sicdf['sic']==pkdf['b_sic'][i]])[0]
            d1df['b_sic'][tot_num] = pkdf['b_sic'][i]
            d1df['b_id'][tot_num] = pkdf['b_id'][i]
            d1df['blis_name'][tot_num] = pkdf['b_name'][i].replace("\"",' ')

        # google info
        if pkdf['pk_in_g_yn'][i]==1:
            ind = np.where(gpdf['g_id']==pkdf['g_id'][i])[0][0]
            d1df['google_id'][tot_num] = gpdf['g_id'][ind]
            d1df['google_type'][tot_num] = gpdf['type'][ind].upper()
            d1df['google_name'][tot_num] = gpdf['name'][ind].upper().replace("\"",' ')
            d1df['google_website'][tot_num] = gpdf['google_url'][ind]
            d1df['google_review_num'][tot_num] = gpdf['rating_num'][ind]
            d1df['google_rating'][tot_num] = gpdf['rating'][ind]
        else:
            d1df['google_review_num'][tot_num] = 0
d1df.to_csv(newd1file, index=False, na_rep='NA')
print '\tdone: %d added!' % (ind_num)
ind_num = 0




print "Running Day care..."
############## 2. Day Care / Child Care #########
ind_num = 0
for i in range(dcdf.shape[0]):
    if(dcdf['dc_in_fs_yn'][i]==0):
        d1df = d1df.append(d1dfi, ignore_index=True)
        tot_num += 1
        ind_num += 1
        d1df['name'][tot_num] = str(dcdf['Location'][i]).replace("\"",' ')
        d1df['pkdc_name'][tot_num] = str(dcdf['Location'][i]).replace("\"",' ')
        d1df['address'][tot_num] = dcdf['Address'][i].replace("\"",' ')
        d1df['provider_no'][tot_num] = dcdf['Provider_Number'][i]
        d1df['in_fsaf_yn'][tot_num] = 0
        d1df['preK_daycare'][tot_num] = "DayCare"
        d1df['inspection_date'][tot_num] = None
        d1df['issue_date'][tot_num] = None
        
        d1df['phone'][tot_num] = dcdf['Phone'][i]

        d1df['y'][tot_num] = dcdf['y'][i]
        d1df['x'][tot_num] = dcdf['x'][i]

        # blis info
        if dcdf['dc_in_b_yn'][i]==1:
            d1df['b_sic_desc'][tot_num] = list(sicdf['sic_desc'][sicdf['sic']==dcdf['b_sic'][i]])[0]
            d1df['b_sic'][tot_num] = dcdf['b_sic'][i]
            d1df['b_id'][tot_num] = dcdf['b_id'][i]
            d1df['blis_name'][tot_num] = dcdf['b_name'][i].replace("\"",' ')

        # google info
        if dcdf['dc_in_g_yn'][i]==1:
            ind = np.where(gpdf['g_id']==dcdf['g_id'][i])[0][0]
            d1df['google_id'][tot_num] = gpdf['g_id'][ind]
            d1df['google_type'][tot_num] = gpdf['type'][ind].upper()
            d1df['google_name'][tot_num] = gpdf['name'][ind].upper().replace("\"",' ')
            d1df['google_website'][tot_num] = gpdf['google_url'][ind]
            d1df['google_review_num'][tot_num] = gpdf['rating_num'][ind]
            d1df['google_rating'][tot_num] = gpdf['rating'][ind]
        else:
            d1df['google_review_num'][tot_num] = 0
d1df.to_csv(newd1file, index=False, na_rep='NA')
print '\tdone: %d added!' % (ind_num)
ind_num = 0



print "Running Business license..."
# 3. Blis
sicseldf = pd.read_csv(sic_sel_file)
mike_codes = [5992, 4212, 2511,7641, 4214, 4222, 7217, 2599, 5033, 2211, 1795, 5111, 3691, 3711, 3241, 5052, 8062]
codes = list(sicseldf['sic']) + mike_codes


for i in range(bldf.shape[0]):
    if(bldf['bl_in_fs_yn'][i]==0 and bldf['bl_in_lq_yn'][i]==0 and (bldf['sic'][i] in codes) and \
      bldf['y'][i]>(33.6511-0.005) and bldf['x'][i]>(-84.5576-0.005)and bldf['y'][i]<(33.8861+0.005) and bldf['x'][i]<(-84.2917+0.005)):
        d1df = d1df.append(d1dfi, ignore_index=True)
        tot_num += 1
        ind_num += 1
        d1df['name'][tot_num] = bldf['account_name'][i].replace("\"",' ')
        d1df['blis_name'][tot_num] = bldf['account_name'][i].replace("\"",' ')
        d1df['address'][tot_num] = bldf['address1'][i].replace("\"",' ')
        d1df['phone'][tot_num] = bldf['phone'][i]
        d1df['b_id'][tot_num] = bldf['license_no'][i]
        d1df['in_fsaf_yn'][tot_num] = 0
        d1df['b_sic_desc'][tot_num] = list(sicdf['sic_desc'][sicdf['sic']==bldf['sic'][i]])[0]
        d1df['b_sic'][tot_num] = bldf['sic'][i]
        d1df['y'][tot_num] = bldf['y'][i]
        d1df['x'][tot_num] = bldf['x'][i]
        
        d1df['inspection_date'][tot_num] = None
        d1df['issue_date'][tot_num] = None
        # google info
        if bldf['bl_in_g_yn'][i]==1:
            ind = np.where(gpdf['g_id']==bldf['g_id'][i])[0][0]
            d1df['google_id'][tot_num] = gpdf['g_id'][ind]
            d1df['google_type'][tot_num] = gpdf['type'][ind].upper().replace("\"",' ')
            d1df['google_name'][tot_num] = gpdf['name'][ind].upper().replace("\"",' ')
            d1df['google_website'][tot_num] = gpdf['google_url'][ind]
            d1df['google_review_num'][tot_num] = gpdf['rating_num'][ind]
            d1df['google_rating'][tot_num] = gpdf['rating'][ind]
        else:
            d1df['google_review_num'][tot_num] = 0
d1df.to_csv(newd1file, index=False, na_rep='NA') 
print '\tdone: %d added!' % (ind_num)
ind_num = 0


print "Running Google..."
# 4. google
gtypesdf = pd.read_csv(gtypefile)
gtypes = list(gtypesdf['type'][gtypesdf['search']>0])
for i in range(gpdf.shape[0]):
    if(gpdf['g_in_fs_yn'][i]==0 and gpdf['g_in_lq_yn'][i]==0 and (gpdf['g_in_bl_yn'][i]==0 or gpdf['bl_sic'][i] not in codes)  \
       and gpdf['type'][i] in gtypes):
        d1df = d1df.append(d1dfi, ignore_index=True)
        tot_num += 1
        ind_num += 1
        d1df['name'][tot_num] = gpdf['name'][i].replace("\"",' ')
        d1df['google_name'][tot_num] = gpdf['name'][i].upper().replace("\"", ' ')
        d1df['address'][tot_num] = gpdf['address'][i].replace("\"",' ')
        d1df['phone'][tot_num] = gpdf['phone'][i]
        d1df['in_fsaf_yn'][tot_num] = 0
        d1df['y'][tot_num] = gpdf['y'][i]
        d1df['x'][tot_num] = gpdf['x'][i]
        
        d1df['inspection_date'][tot_num] = None
        d1df['issue_date'][tot_num] = None

        # google info
        d1df['google_id'][tot_num] = gpdf['g_id'][i]
        d1df['google_type'][tot_num] = gpdf['type'][i].upper().replace("\"",' ')
        d1df['google_name'][tot_num] = gpdf['name'][i].upper().replace("\"", ' ')
        d1df['google_website'][tot_num] = gpdf['google_url'][i]
        d1df['google_review_num'][tot_num] = gpdf['rating_num'][i]
        d1df['google_rating'][tot_num] = gpdf['rating'][i]

d1df.to_csv(newd1file, index=False, na_rep='NA') 
print '\tdone: %d added!' % (ind_num)
ind_num = 0

# Count number of fires within 0.1 miles and the number of inspections
tolrange = 0.05
rangex = tolrange/110.574
rangey = tolrange/np.cos(-84.4/180)/111.320
afrddf = pd.read_csv(fire_file)
inspdf = pd.read_csv(insp_file)
for i in range(d1df.shape[0]):
    d1df['num_fire_50m'][i] = np.sum(np.logical_and(abs(d1df['y'][i]-afrddf['y'])<rangey, abs(d1df['x'][i]-afrddf['x'])<rangex))
    if d1df['in_fsaf_yn'][i] == 1:
        d1df['num_inspect_5years'][i] = len(np.unique(inspdf['INSPDATE'][inspdf['ACCTNO']==d1df['fsaf_id'][i]]))

d1df[1:].to_csv(newd1file, index=False, na_rep='NA')


######## Map costar to business / properties ############
blcodf = pd.read_csv(blis_costar_file)
rkdf = pd.read_csv(risk_file)
num = 0
for i in range(d1df.shape[0]):
    if d1df['b_id'][i]>0:
        frr = list(blcodf['COSTAR_PROPERTY_NO'][blcodf['blis_no'] == d1df['b_id'][i]])
        if len(frr)>0:
            d1df['costar_property_id'][i] = frr[0]
    if d1df['costar_property_id'][i]>0:
        frr = list(rkdf['fire_risk_rating'][rkdf['PropertyID'] == d1df['costar_property_id'][i]])
        if len(frr)>0:
            d1df['risk_rating'][i] = frr[0]
            d1df['risk_category'][i] = list(rkdf['risk_category'][rkdf['PropertyID'] == d1df['costar_property_id'][i]])[0]
            d1df['risk_raw_score'][i] = list(rkdf['raw_output'][rkdf['PropertyID'] == d1df['costar_property_id'][i]])[0]
            num += 1

d1df[1:].to_csv(newd1file, index=False, na_rep='NA')

### Join Fsaf with 
fdf = pd.read_csv(ffile)
for i in d1df.index:
    ind = fdf[['pid']][fdf['legacyNo']==d1df['fsaf_id'][i]].index
    if len(ind)>0:
        ind = list(ind)
        d1df['risk_raw_score'][i] = fdf['risk_raw_score'][ind[0]]
        d1df['risk_rating'][i] = fdf['risk_rating'][ind[0]]
        d1df['risk_category'][i] = fdf['risk_category'][ind[0]]
        d1df['costar_property_id'][i] = fdf['pid'][ind[0]]
        num += 1
# risk_raw_score	risk_rating	risk_category

## Join all the rest set
cdf = pd.read_csv(cfile, low_memory=False)
told = 8.0e-4
for i in d1df.index:
    if not (d1df['costar_property_id'][i]>0):
        ind = cdf[['x', 'y']][np.logical_and(abs(cdf['x']-d1df['x'][i])<told, abs(cdf['y']-d1df['y'][i])<told)].index
        if len(ind)>0:
            d1df['costar_property_id'] = cdf['PropertyID'][list(ind)[0]]
            d1df['risk_rating'][i] = cdf['fire_risk_rating'][list(ind)[0]]
            d1df['risk_category'][i] = cdf['risk_category'][list(ind)[0]]
            d1df['risk_raw_score'][i] = cdf['raw_output'][list(ind)[0]]
            num += 1
            
print "Risk Score Joined: %d!"% (num)

##################################################################


# Inspection pct and fire pct
siccdf = pd.read_csv(sic_desc_count_file)
for i in range(d1df.shape[0]):
    if d1df['b_id'][i]>0:
        frr = list((siccdf[['sic', 'PCT_inspected']][siccdf['sic']==d1df['b_sic'][i]]).index)
        if len(frr)>0:
            d1df['inspect_pct'][i] = siccdf['PCT_inspected'][frr[0]]
            d1df['fire_count_pct'][i] = siccdf['fire_pct'][frr[0]]

d1df[1:].to_csv(newd1file, index=False, na_rep='NA')
print "Inspection and fire PCT Joined!"

### NA ##
d1df['fsaf_id'][d1df['fsaf_id'] == -1] = None
d1df['b_id'][d1df['b_id'] == -1] = None
d1df['liq_id'][d1df['liq_id'] == -1] = None
d1df['costar_property_id'][d1df['costar_property_id'] == -1] = None
d1df['b_sic'][d1df['b_sic'] <= 0] = None
d1df[1:].to_csv(newd1file, index=False, na_rep='NA')

#################### Atlanta, GA, USA Remove###########################
print 'Formatting Google Addresses......'
for i in d1df.index:
    ad = (d1df['address'][i].replace(',', ' , ').split())
    if pd.notnull(d1df['google_id'][i]) and d1df['in_fsaf_yn'][i]==0 and ('States' in ad):
        if ('Atlanta' in ad):
            ad = " ".join(ad)
            ad = ad.replace(',', ' ').split()
            if ad.index('Atlanta')>0:
                d1df['address'][i] =  " ".join(ad[:len(ad)-ad[::-1].index('Atlanta')-1])
            else:
                d1df['address'][i] =  " ".join(ad[:-3])

        elif 'atlanta' in ad:
            ad = " ".join(ad)
            ad = ad.replace(',', ' ').split()
            d1df['address'][i] =  " ".join(ad[:len(ad)-ad[::-1].index('atlanta')-1])
        elif 'GA' in ad:
            ad = " ".join(ad)
            ad = ad.replace(',', ' ').split()
            d1df['address'][i] =  " ".join(ad[0:ad.index('GA')])
        elif ',' in ad:
            d1df['address'][i] =  " ".join(ad[0:ad.index(',')])
        
            


######################## Remove bad xy on Atlanta, GA###############################
badxy = [-84.3879824, 33.7489954]
seltf = [True] * d1df.shape[0]
num = 0
for i in d1df.index:
    if abs(d1df['x'][i] - badxy[0])<3e-6 and abs(d1df['y'][i] - badxy[1])<3e-6:
        seltf[i] = False
        num += 1
d1df = d1df[seltf]
print "%d removed because of Atlanta, GA xy!" % (num)
d1df[1:].to_csv(newd1file, index=False, na_rep='NA')
num = 0

########### Map one catagory and unicode#######
gtmdf = pd.read_csv(gtmfile)
ulist = 'name address occup_type	b_sic_desc	google_type	preK_daycare fsaf_name	blis_name	liq_name	google_name	pkdc_name	new_prop_type'
ulist = ulist.split()

for i in d1df.index:
    if d1df['in_fsaf_yn'][i] == 0:
        if pd.isnull(d1df['preK_daycare'][i]):

            if pd.notnull(d1df['b_sic_desc'][i]):
                d1df['new_prop_type'][i] = d1df['b_sic_desc'][i]
            elif pd.notnull(d1df['google_type'][i]):
                d1df['new_prop_type'][i] = list(gtmdf['mapping'][gtmdf['google_type'] == d1df['google_type'][i]])[0]
            elif pd.notnull(d1df['liq_id'][i]):
                d1df['new_prop_type'][i] = 'LIQUOR LICENSE'
                
        else:
            d1df['new_prop_type'][i] = d1df['preK_daycare'][i]
    
    ### unicode ####
    for colnm in ulist:
        if pd.notnull(d1df[colnm][i]):
            d1df[colnm][i] = unicodedata.normalize('NFKD', unicode( d1df[colnm][i], 'utf8')).encode('ascii','ignore')
   
d1df[1:].to_csv(newd1file, index=False, na_rep='NA')

