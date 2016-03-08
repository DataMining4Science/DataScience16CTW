import pandas as pd
import numpy as np

def loadData():
	data = pd.read_csv('IPPS_2013.csv')
	return data

def get_series_ids(x):
    '''Function returns a pandas series consisting of ids, 
       corresponding to objects in input pandas series x
       Example: 
       get_series_ids(pd.Series(['a','a','b','b','c'])) 
       returns Series([0,0,1,1,2], dtype=int)'''

    values = np.unique(x)
    values2nums = dict(zip(values,range(len(values))))
    return x.replace(values2nums)

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
	data['Provider HRR Num'] = get_series_ids(data['Provider HRR'])
	geo_data = pd.read_csv('provider_geocodes_google.csv')
	data = data.merge(geo_data, how='left')

	return data

def loadAndClean():
	data = loadData()
	return cleanData(data)
