

# Joining Property Data #


The Firebird framework is designed to help municipal fire departments:</br>
1. <a href="https://github.com/DSSG-Firebird/property-joins">Discover new properties for inspection</a><br>
2. <a href="https://github.com/DSSG-Firebird/risk-model">Prioritize those property inspections by their fire risk
</a><br>
3. <a href="https://github.com/DSSG-Firebird/interactive-map">Visualize property inspections on an interactive map
</a><br>

More information on the Firebird project can be found <a href="http://www.firebird.gatech.edu">here</a>.

- - - - 

This repository includes Python codes and data files for data collection, geocoding, fuzzy address matching, and joining. 

### All files and description 

| file name                          | description                                                                                                                              | used_by_code_file                                                                | used_by_code_file2                              | 
|---------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|-------------------------------------------------| 
| sample_addresses_for_geocoding.csv    | Sample file with addresses for google geocoding demo                                                                                     | address_to_xy_geocoding.py                                                       |                                                 | 
| sample_addresses_for_geocoding_xy.csv | Sample output file of google geocoding of code address_to_xy_geocoding.py                                                                | Output of address_to_xy_geocoding.py                                             |                                                 | 
| Blis_business_license.csv             | Original Business license data with coordinates and  empty columns for data joining with Fsaf, google, liquor license, PreK, and Daycare | Data_join_for_property_list.py                                                   |                                                 | 
| Fsaf_current_inspection.csv           | FSAF data with coordinates and empty columns for data joining with Blis, Google, PreK, DayCare, Liquor License                           | Data_join_for_property_list.py                                                   |                                                 | 
| Google_places.csv                     | Google places data collected by Google_Place_API_search.py for data joining with Fsaf, google, Blis, PreK, and Daycare                   | Data_join_for_property_list.py                                                   |                                                 | 
| Liquor_license_events_removed.csv     | Liquor license data with all events-license removed for data joining with with Fsaf, google, and Blis                                    | Data_join_for_property_list.py                                                   |                                                 | 
| PreK_programs_Jul2015.csv             | Pre K program list for data joining with Fsaf, Blis, and Google                                                                          | Data_join_for_property_list.py                                                   |                                                 | 
| Child_Care_Jul2015.csv                | Child Care / Day Care list for data joining with Fsaf, Blis, and Google                                                                  | Data_join_for_property_list.py                                                   |                                                 | 
| Atlanta_Grid_Coordinates.csv          | Atlanta Grid Coordinates with grid distance 210 meters for Google Places search                                                          | Google_Place_API_search.py                                                       |                                                 | 
| google_place_types.csv                | Google Places types that will be searched and included in the properties                                                                 | Google_Place_API_search.py                                                       |  Data_join_for_property_list.py                 | 
| google_places_sample.csv              | Google Places output sample file; if you change this file, please change the code based on columns                                       | Google_Place_API_search.py                                                       |                                                 | 
| Blis_business_license_joined.csv      | Business License data joined with Fsaf, google, liquor license, preK, and DayCare                                                        | Property_short_list_generator.py                                                 |  Property_long_list_generator.py                | 
| Fsaf_current_inspection_joined.csv    | FSAF data joined with Blis, Google, PreK, DayCare, and liquor icense                                                                     | Property_short_list_generator.py                                                 |  Property_long_list_generator.py                | 
| Google_places_joined.csv              | Google Places data joined with Blis, Fsaf, PreK, DayCare, and liquor icense                                                              | Property_short_list_generator.py                                                 |  Property_long_list_generator.py                | 
| Liquor_license_joined.csv             | Liquor license data joined with with Fsaf, google, and Blis                                                                              | Property_short_list_generator.py                                                 |  Property_long_list_generator.py                | 
| PreK_programs_Jul2015_joined.csv      | Pre K program list joined with Fsaf, Blis, and Google                                                                                    | Property_short_list_generator.py                                                 |  Property_long_list_generator.py                | 
| Child_Care_Jul2015_joined.csv         | Child Care / Day Care list joined with Fsaf, Blis, and Google                                                                            | Property_short_list_generator.py                                                 |  Property_long_list_generator.py                | 
| Property_list_sample.csv              | Property list output sample file                                                                                                         | Property_short_list_generator.py                                                 |  Property_long_list_generator.py                | 
| BLIS_SIC_Desc.csv                     | Business license sic types descriptions from City of Atlanta                                                                             | Property_short_list_generator.py                                                 |  Property_long_list_generator.py                | 
| sic_counts_desc.csv                   | SIC counts of inspections, fire, in_the_list_or_not (in_D1: 0 means not included; 1 means included)                                      | Property_short_list_generator.py                                                 |  Property_long_list_generator.py                | 
| AFRD_coords.csv                       | Coordinates of fire incidents for fire counts                                                                                            | Property_short_list_generator.py                                                 |  Property_long_list_generator.py                | 
| FSAF_Inspec2011_2015.csv              | All Fsaf inspecition from 2011 to 2015                                                                                                   | Property_short_list_generator.py                                                 |  Property_long_list_generator.py                | 
| BLIS_JOIN_COSTAR.csv                  | Blis id matched to Costar property id for joining the risk score to the list                                                             | Property_short_list_generator.py                                                 |  Property_long_list_generator.py                | 
| risk_scores_address.csv               | risk scores, address, property id for joining with the list                                                                              | Property_short_list_generator.py                                                 |  Property_long_list_generator.py                | 
| fsaf_address_validation_output.csv    | Fsaf validated address for address matching with Costar                                                                                  | Property_short_list_generator.py                                                 |  Property_long_list_generator.py                | 
| google_type_mapping.csv               | Googe types mapped to business SIC types                                                                                                 | Property_short_list_generator.py                                                 |                                                 | 
| Properties_list_short.csv             | Property list short list                                                                                                                 |  the difference with long list is only high probably business types are included | output file of Property_short_list_generator.py | 
| Properties_list_long.csv              | Property list long list                                                                                                                  |  the difference with long list is all possible business types are included       | output file of Property_long_list_generator.py  | 


More information can be found in the [code books](https://docs.google.com/spreadsheets/d/1d2xhMRfJApGkbJbriepnpVG9K9DGSXA8Hxo2LqQvIUE/edit?usp=sharing).

*Note: the real property information has been removed, but it is easy to find the structure of these data from the remaining files and code books.*
