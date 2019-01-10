import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import numpy as np
import urllib.request
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

dataPage = 'https://money.cnn.com/data/hotstocks/' # Define Web Page
page = urllib.request.urlopen(dataPage) # Obtain HTML Document

soup = BeautifulSoup(page, 'html.parser') # Parse w/ BeautifulSoup

stock = [] # Create Blank Array to Store Stock Symbols

for td in soup.find_all('a', attrs={'class': re.compile('wsod_symbol')}): # Find HTML Tag w/ Attribute (e.g. <a class = wsod_symbol>)
    cleanText = td.get_text() # Remove HTML Tags From Each Found Result
    if not cleanText.isspace():
        stock.append(cleanText) # Add Stock Symbol to Array

stock = list(set(stock[3:])) # Remove Duplicate Values / First 3 Values (DOW/NASDAQ/SP500)

##stock = ['AMZN'] # Define Stock Symbol Array

end = datetime.now() # Set Current Date as End Date
start = end - timedelta(weeks=52*5) # Set Start Date
avgTwenty = 20
avgFifty = 50
avgTwoHund = 200


for i in range(len(stock)):
    f = web.DataReader(stock[i], 'iex', start, end) # Gather data using IEX
    f.index = pd.to_datetime(f.index) # Convert Index to Date
##    print(f) # Print Full Data
    
    maTwenty = [] # Define Array for 20 Day MA Data
    maFifty = [] # Define Array for 50 Day MA Data
    maTwoHund = [] # Define Array for 200 Day MA Data
    
    for j in range(len(f.close.values)): # Compute 20 Day MA
        if j >= avgTwenty:
            maTwenty.append(sum(f.close.values[j - avgTwenty:j])/avgTwenty)
            
    for j in range(len(f.close.values)): # Compute 50 Day MA
        if j >= avgFifty:
            maFifty.append(sum(f.close.values[j - avgFifty:j])/avgFifty)
            
    for j in range(len(f.close.values)): # Compute 200 Day MA
        if j >= avgTwoHund:
            maTwoHund.append(sum(f.close.values[j - avgTwoHund:j])/avgTwoHund)

    bbStDev = [] # Define Array for Standard Deviation
    uBB = [] # Define Array for Upper Bollinger Band
    lBB = [] # Define Array for Lower Bolling Band
            
    for j in range(len(f.close.values)): # Compute Bollinger Bands
        if j >= avgTwenty:
            uBB.append(maTwenty[j - avgTwenty] + 2 * np.std(f.close.values[j - avgTwenty:j]))
            lBB.append(maTwenty[j - avgTwenty] - 2 * np.std(f.close.values[j - avgTwenty:j]))
            
    plt.figure(stock[i]) # Create Figure w/ Stock Symbol as Title
    plt.ion() # Turn on Interactive Mode
    
    plt.bar(f.index, f.volume.values / 1000000, color='lightgray') # Plot Bar for Volume
    plt.ylabel('Volume (Million)') # Label Y-Axis
    
    plt.twinx() # Create Second Axis
    plt.plot(f.index, f.close.values, label = stock[i], color = 'black') # Plot Close Price Data
    plt.plot(f.index[20:], maTwenty, label = '20MA', color = 'magenta', linewidth = 1.0) # Plot 20MA
    plt.plot(f.index[50:], maFifty, label = '50MA', color = 'lime', linewidth = 1.0) # Plot 50MA
    plt.plot(f.index[200:], maTwoHund, label = '200MA', color = 'blue', linewidth = 1.0) # Plot 200MA
    plt.plot(f.index[20:], uBB, color = 'peachpuff', linewidth = 1.0, linestyle = '--') # Plot Upper Band
    plt.plot(f.index[20:], lBB, color = 'peachpuff', linewidth = 1.0, linestyle = '--') # Plot Lower Band
    plt.fill_between(f.index[20:], uBB, lBB, color = 'oldlace')
    
    plt.title(stock[i] + ' from ' + str(f.index[0])[:10] + ' to ' + str(f.index[len(f.index)-1])[:10]) # Display Title
    plt.legend() # Show Legend (Stock Symbol)
    plt.grid(True) # Turn on Gridlines
    plt.ylabel('Price (USD)') # Label Y-Axis
    plt.xlabel('Date') # Label X-Axis

    plt.show()

##    plt.figure('Bollinger Band ' + stock[i]) # Create Figure
##    plt.ion() # Turn on Interactive Mode
##
##    plt.plot(f.index, f.close.values, label = stock[i], color = 'blue', linewidth = 1.0) # Plot Close Price
##    plt.plot(f.index[20:], uBB, color = 'green', linewidth = 1.0) # Plot Upper Band
##    plt.plot(f.index[20:], lBB, color = 'red', linewidth = 1.0) # Plot Lower Band
##    plt.plot(f.index[20:], maTwenty, label = '20MA', color = 'magenta', linewidth = 1.0, linestyle = '--') # Plot 20MA
##
##    plt.title(stock[i] + ' Bolling Bands')
##    plt.ylabel('Price (USD)') # Label Y-Axis
##    plt.xlabel('Date') # Label X-Axis
##    plt.legend() # Show Legend
##    plt.grid(True) # Turn on Grid

##    plt.show()
