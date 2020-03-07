#!/usr/bin/python3
from pandas_datareader import data
import matplotlib.pyplot as plt
import copy
from lib.rsi import *
from lib.cci import *
from lib.macd import *
from lib.atr import *
from lib.dmi import *
from lib.bollinger import *
from lib.WilliamsAlligator import *
from lib.StockData import *
from lib.DataOperations import *

# Get DATA from URL
# User pandas_reader.data.DataReader to load the desired data. As simple as that.
def GetData(code,begin,end):
    receivedData = data.DataReader(code, 'stooq', begin, end)

    if len(receivedData) == 0:
        print("No Stooq data for entry!")
        sys.exit(1)

    return receivedData

# Change volumeTotal to neg/pos value
def SetVolumeWithTrend(price,volumeTotal):
    # Assert condition
    if (price.size != volumeTotal.size):
        return

    lastPrice=price.values[-1]
    # We start from end because data from Stooq is reversed
    for i in reversed(range(1,len(price.values))):
        # If price drop then volumeTotal wih minus value
        if (lastPrice > price.values[i]):
            volumeTotal.values[i]=-volumeTotal.values[i]

        lastPrice=price.values[i]


# Calculate OBV index thanks to the volumeTotal
def SetOBV(volumeTotal):
    lastOBV=0
    obvTotal=copy.deepcopy(volumeTotal)

    for i in reversed(range(len(volumeTotal.values))):
        lastOBV+=volumeTotal.values[i]
        obvTotal.values[i] = lastOBV

    return obvTotal

"""
Typical Price
Source: https://en.wikipedia.org/wiki/Typical_price
Params: 
    data: pandas DataFrame
    high_col: the name of the HIGH values column
    low_col: the name of the LOW values column
    close_col: the name of the CLOSE values column
    
Returns:
    copy of 'data' DataFrame with 'typical_price' column added
"""
def typical_price(data, high_col = 'High', low_col = 'Low', close_col = 'Close'):
    
    data['typical_price'] = (data[high_col] + data[low_col] + data[close_col]) / 3

    return data
