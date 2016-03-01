from geopy.geocoders import Nominatim
from geopy.geocoders import GeoNames
import pandas as pd
from numpy import mean

def geocode(locator, gc_str):
    try:
        locations = locator.geocode(gc_str, exactly_one=False)
        # Check the range of responses (either a list of Locations or None*)
        # If it's less than a threshold, use the mean latitude and longitude
        # If not, return None
        # *None will raise an exception and cause None to be returned
        thresh = 0.005
        lats = [l.latitude for l in locations]
        lons = [l.longitude for l in locations]
        if (max(lats) - min(lats) < thresh) and (max(lons) - min(lons) < thresh):
            return mean(lats), mean(lons)
        else:
            return None
    except KeyboardInterrupt:
        exit(0)
    except:
        return None

def geocode_address(locator, series):
    """
    Return the Location of the provider in the given Series using the address
    """
    cols = ['Provider Street Address', 'Provider City', 'Provider State', 'Provider Zip Code']
    # Try first with everthing
    address_str = ', '.join(str(series[col]) for col in cols)
    location = geocode(locator, address_str)
    # If it fails, try taking off the ZIP code
    if location is None:
        address_str = ' '.join(str(series[col]) for col in cols[:-1])
        location = geocode(locator, address_str)
    return location

def geocode_name(locator, series):
    """
    Return the Location of the provider in the given Series using the name
    """
    cols = ['Provider Name', 'Provider City', 'Provider State']
    name_str = ', '.join(str(series[col]) for col in cols)
    return geocode(locator, name_str)

if __name__ == '__main__':
    # Load IPPS data
    cols = ['Provider Id', 'Provider Street Address', 'Provider City',
            'Provider State', 'Provider Zip Code', 'Provider Name']
    data = pd.read_csv('IPPS_2013.csv')[cols]
    data.drop_duplicates(inplace=True)

    # Load and join existing geocode data
    try:
        geo_data = pd.read_csv('provider_geocodes.csv')
        data = data.merge(geo_data, how='left')
    except IOError:
        data['Latitude'] = None
        data['Longitude'] = None

    # Randomize data so we don't get stuck on the same ones failing
    data = data.sample(frac=1).reset_index(drop=True)

    # Create locators
    address_locator = Nominatim(country_bias='United States')
    name_locator = GeoNames(username='jkingery', country_bias='United States')

    n = 1000
    i = 0
    fails = 0
    # Go through any rows with null Latitude (and thus Longitude) values
    for index,row in data[data.Latitude.isnull()].iterrows():
        if i >= n:
            break
        # Try by address first, then by name if that fails
        location = geocode_address(address_locator, row) or geocode_name(name_locator, row)
        if location is not None:
            data.loc[index, 'Latitude'] = location[0]
            data.loc[index, 'Longitude'] = location[1]
        else:
            fails += 1
            print row['Provider Id'], 'failed'
        i += 1
    print fails, 'fails out of', n

    data[['Provider Id', 'Latitude', 'Longitude']].sort_values('Provider Id').to_csv('provider_geocodes.csv', index=False)
