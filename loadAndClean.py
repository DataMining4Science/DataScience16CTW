import pandas as pd

def loadData():
	data = pd.read_csv('IPPS_2013.csv')
	return data

def str_to_num(s):
    """
    Return a float representing the dollar amount in string s
    String s is of the form '$xxxx.xx'
    """
    return float(s[1:])

def cleanData(data):
	data['Average Covered Charges Num'] = data['Average Covered Charges'].apply(str_to_num)
	data['Average Total Payments Num'] = data['Average Total Payments'].apply(str_to_num)
	data['Average Medicare Payments Num'] = data['Average Medicare Payments'].apply(str_to_num)
	data['DRG Code'] = data['DRG Definition'].apply(lambda x: int(x.split(" - ")[0]))
	geo_data = pd.read_csv('provider_geocodes_google.csv')
	data = data.merge(geo_data, how='left')

	return data

def loadAndClean():
	data = loadData()
	return cleanData(data)
