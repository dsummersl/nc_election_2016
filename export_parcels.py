from arcgis import downloader, utils
import geopandas as gpd
import pandas as pd

print('Load shape data')
durham = gpd.GeoDataFrame.from_file("data/durham.shp")

print('Load lots')
lots = {}
for precinct in durham['PREC_ID'].unique():
    bounds = durham[durham.PREC_ID == precinct].bounds
    all_lots_url_template = "http://gisweb2.durhamnc.gov/arcgis/rest/services/PublicWorks/PublicWorks/MapServer/89/query?f=json&geometry={},{},{},{}&returnGeometry=true&outFields=*&outSR=4326&inSR=4326"
    lots[precinct] = downloader.get_shp(all_lots_url_template, 'data/all_lots-{}'.format(precinct), bounds)

print('Cleanup lots')
all_lots = pd.concat(lots.values())
# b/c of rectangular arcgis regions, there will be some dups, delete:
all_lots = all_lots.drop_duplicates(['PARCEL_ID'])
all_lots['lat_long'] = all_lots.centroid
all_lots['lat'] = all_lots['lat_long'].map(lambda ll: ll.y)
all_lots['long'] = all_lots['lat_long'].map(lambda ll: ll.x)
utils.create_address_fields(all_lots, 'SITE_ADDRE')

print('Load voters')
voters = pd.read_csv('data/ncvoter32.txt', sep=None)
voters_in_county = voters[voters.county_desc == "DURHAM"]
# cut out 'removed' voters
voters_in_county = voters[voters.voter_status_desc != "REMOVED"]
utils.create_address_fields(voters_in_county, 'res_street_address')

print('Create common address column')
voters_in_county['clean_number_address'] = voters_in_county['clean_street_number'] + ' ' + voters_in_county['clean_full_street']
all_lots['clean_number_address'] = all_lots['clean_street_number'] + ' ' + all_lots['clean_full_street']

print('Merge')
merged_lots = all_lots.merge(voters_in_county, on='clean_number_address', how='outer')

print('Save')

# Include both lot and voter address - b/c voters not matched to a lot will have
# an address that may be useful for finding apartments.
merged_lots[[
    'PARCEL_ID', 'voter_reg_num', 'clean_number_address',
    'clean_full_street_x', 'clean_full_street_y', 'precinct_desc',
    'clean_address_x', 'clean_address_y', 'lat', 'long', 'first_name', 'middle_name', 'last_name',
    'birth_age', 'voter_status_desc', 'party_cd'
]].to_csv('data/durham_parcels.csv', index=False)
