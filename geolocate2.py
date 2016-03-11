import requests
import pandas as pd
import time
from geopy.geocoders import GoogleV3
from geopy.geocoders import Bing
from numpy import mean

google_maps_api_key = ''
bing_maps_api_key = ''

#This function takes in a locator and a string and attempts to return the latitude and Longitude.
def geocode(locator, gc_str):
    try:
        location = locator.geocode(gc_str, exactly_one=True)
        return location.latitude,location.longitude
    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
    	print e
        return None

#Takes in a panda series and and a locator. It combines the appropriate columns into a string to be geocoded
def geocode_address(locator, series):
    """
    Return the Location of the provider in the given Series using the address
    """
    cols = ['Provider Street Address', 'Provider City', 'Provider State', 'Provider Zip Code']
    address_str = ', '.join(str(series[col]) for col in cols)
    location = geocode(locator, address_str)
    return location


if __name__ == '__main__':
    cols = ['Provider Id', 'Provider Street Address', 'Provider City',
            'Provider State', 'Provider Zip Code', 'Provider Name']
    data = pd.read_csv('IPPS_2013.csv')[cols]
    data.drop_duplicates(inplace=True)

    # Load and join existing geocode data
    try:
        geo_data = pd.read_csv('provider_geocodes_google.csv')
        data = data.merge(geo_data, how='left')
    except IOError:
        data['Latitude'] = None
        data['Longitude'] = None

    new_locator = GoogleV3(api_key=google_maps_api_key)

    i = 0
    n = 4000 #number of series to try and geolocate from the file
    failsList = []
    print 'unknownsLeft: ', data.Latitude.isnull().sum()
    for index,row in data[data.Latitude.isnull()].iterrows():
        if i >= n:
            break
        #save the start time to ensure we don't violate rate limiting by the api provider
        start = time.time()
        location = geocode_address(new_locator, row)
        if location is not None:
            data.loc[index, 'Latitude'] = location[0]
            data.loc[index, 'Longitude'] = location[1]
        else:
            failsList.append(row['Provider Id'])
            print row['Provider Id'], 'failed'
        i += 1
        end = time.time()
        #sleep if going to fast (aka likley to exceed rate limit)
        remain = start + .1 - end
        if remain > 0:
            time.sleep(remain)
    print "fails: ",failsList
    print len(failsList), 'fails out of', i

    #save results
    data[['Provider Id', 'Latitude', 'Longitude']].sort_values('Provider Id').to_csv('provider_geocodes_google.csv', index=False)
