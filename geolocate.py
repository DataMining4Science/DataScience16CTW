from geopy.geocoders import Nominatim
from geopy.geocoders import GeoNames
import pandas as pd

def geocode(locator, gc_str):
    try:
        return locator.geocode(gc_str, exactly_one=True)
    except:
        return None

def geocode_address(locator, series):
    """
    Return the Location of the provider in the given Series using the address
    """
    cols = ['Provider Street Address', 'Provider City', 'Provider State', 'Provider Zip Code']
    # Try first with everthing
    address_str = ' '.join(str(series[col]) for col in cols)
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
    name_str = series['Provider Name']
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
            data.loc[index, 'Latitude'] = location.latitude
            data.loc[index, 'Longitude'] = location.longitude
        else:
            fails += 1
            print row['Provider Id'], 'failed'
        i += 1
    print fails, 'fails out of', n

    data[['Provider Id', 'Latitude', 'Longitude']].sort_values('Provider Id').to_csv('provider_geocodes.csv', index=False)
