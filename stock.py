import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import numpy as np
import urllib.request
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import wordpress_xmlrpc
from wordpress_xmlrpc.methods import media, posts

dataPage = 'https://money.cnn.com/data/hotstocks/'  # Define Web Page
page = urllib.request.urlopen(dataPage)  # Obtain HTML Document

soup = BeautifulSoup(page, 'html.parser')  # Parse w/ BeautifulSoup

stock = [] # Create Blank Array to Store Stock Symbols
userIn = str(input('Enter Stock Symbol or Scrape: ')).lower()  # Ask User to Chart Single Stock or Scrape Market Movers

if userIn == 'scrape':  # Scrape Market Movers
    for td in soup.find_all('a', attrs={'class': re.compile('wsod_symbol')}): # Find Tag w/ Attr <a class = wsod_symbol>
        cleanText = td.get_text()  # Remove HTML Tags From Each Found Result
        if not cleanText.isspace():
            stock.append(cleanText)  # Add Stock Symbol to Array

    stock = list(set(stock[3:]))  # Remove Duplicate Values / First 3 Values (DOW/NASDAQ/SP500)
else:
    stock = [userIn.upper()]  # Set User Inputted Stock

end = datetime.now()  # Set Current Date as End Date
start = end - timedelta(weeks=52*5)  # Set Start Date
avgTwenty = 20
avgFifty = 50
avgTwoHund = 200


for i in range(len(stock)):  # Get Data / Create Images for Each Stock Chart
    f = web.DataReader(stock[i], 'iex', start, end)  # Gather data using IEX
    f.index = pd.to_datetime(f.index)  # Convert Index to Date
    # print(f) # Print Full Data
    
    maTwenty = []  # Define Array for 20 Day MA Data
    maFifty = []  # Define Array for 50 Day MA Data
    maTwoHund = []  # Define Array for 200 Day MA Data
    
    for j in range(len(f.close.values)):  # Compute 20 Day MA
        if j >= avgTwenty:
            maTwenty.append(sum(f.close.values[j - avgTwenty:j])/avgTwenty)
            
    for j in range(len(f.close.values)):  # Compute 50 Day MA
        if j >= avgFifty:
            maFifty.append(sum(f.close.values[j - avgFifty:j])/avgFifty)
            
    for j in range(len(f.close.values)):  # Compute 200 Day MA
        if j >= avgTwoHund:
            maTwoHund.append(sum(f.close.values[j - avgTwoHund:j])/avgTwoHund)

    bbStDev = []  # Define Array for Standard Deviation
    uBB = []  # Define Array for Upper Bollinger Band
    lBB = []  # Define Array for Lower Bolling Band
            
    for j in range(len(f.close.values)):  # Compute Bollinger Bands
        if j >= avgTwenty:
            uBB.append(maTwenty[j - avgTwenty] + 2 * np.std(f.close.values[j - avgTwenty:j]))
            lBB.append(maTwenty[j - avgTwenty] - 2 * np.std(f.close.values[j - avgTwenty:j]))


#### CALCULATE RSI VALUES
#### ADD INDICATION WHEN RSI <40 AND STOCK PRICE NEAR LOWER BB
            
    if str(f.index[len(f.index)-1])[:10] == str(end)[:10]: # Plot if Data is Recent
        plt.figure(stock[i], figsize = [18, 12])  # Create Figure w/ Stock Symbol as Title
        # plt.ion() # Turn on Interactive Mode
        
        plt.bar(f.index, f.volume.values / 1000000, color='lightgray') # Plot Bar for Volume
        plt.ylabel('Volume (Million)')  # Label Y-Axis
        
        plt.twinx() # Create Second Axis
        plt.plot(f.index, f.close.values, label = stock[i], color = 'black')  # Plot Close Price Data
        plt.plot(f.index[20:], maTwenty, label = '20MA', color = 'magenta', linewidth = 1.0)  # Plot 20MA
        plt.plot(f.index[50:], maFifty, label = '50MA', color = 'lime', linewidth = 1.0)  # Plot 50MA
        plt.plot(f.index[200:], maTwoHund, label = '200MA', color = 'blue', linewidth = 1.0)  # Plot 200MA
        plt.plot(f.index[20:], uBB, color = 'peachpuff', linewidth = 1.0, linestyle = '--')  # Plot Upper Band
        plt.plot(f.index[20:], lBB, color = 'peachpuff', linewidth = 1.0, linestyle = '--')  # Plot Lower Band
        plt.fill_between(f.index[20:], uBB, lBB, color = 'oldlace')
        
        plt.title(stock[i] + ' from ' + str(f.index[0])[:10] + ' to ' + str(f.index[len(f.index)-1])[:10])  # Show Title
        plt.legend()  # Show Legend (Stock Symbol)
        plt.grid(True)  # Turn on Grid
        plt.ylabel('Price (USD)')  # Label Y-Axis
        plt.xlabel('Date')  # Label X-Axis

#       plt.show()
        plt.savefig(str(stock[i]) + '.png', bbox_inches='tight', format = 'png', dpi = 200)  # Save as STOCK.PNG
        
    else: # Print Last Updated Price if Not Recent
        print('Closing Prices Last Updated: ' + str(f.index[len(f.index)-1]))
        quit()  # Quit if Prices Aren't Updated

wpUser = str(input('Enter WordPress Username: ')).lower()  # Input WordPress Username
wpPW = str(input('Enter WordPress Password: '))  # Input WordPress Password
wpURL = 'https://bspt82221685.wordpress.com/xmlrpc.php'  # WordPress URL (XMLRPC)

wp = wordpress_xmlrpc.Client(wpURL, wpUser, wpPW) # Login to WordPress
wpPost = wordpress_xmlrpc.WordPressPost()  # Create New Post
wpMM = str(datetime.now().strftime('%m'))  # MM
wpDD = str(datetime.now().strftime('%d'))  # DD
wpYYYY = str(datetime.now().strftime('%Y'))  # YYYY
wpPost.title = 'Stock Market Movers: ' + wpMM + '/' + wpDD + '/' + wpYYYY  # Add Title
htmlIMG = []

for i in range(len(stock)):  # Upload Charts to WordPress
    imgName = 'https://bspt82221685.files.wordpress.com/' + wpYYYY + '/' + wpMM + '/' + str(stock[i]).lower() + '.png'
    htmlIMG.append('<figure class="wp-block-image"><a href="' + imgName +
                   '"><img src="' + imgName + '" alt=""/></a></figure>')  # Add HTML Tags to Figure
    data = {'name' : str(stock[i]).lower() + '.png', 'type' : 'image/png', }
    with open(str(stock[i]) + '.png', 'rb') as img:  # Open File
        data['bits'] = wordpress_xmlrpc.xmlrpc_client.Binary(img.read())
    wp.call(media.UploadFile(data))  # Upload File

postAll = ''
for s in htmlIMG:  # Take All HTML and Place Into Single String
    postAll += s + ' '

wpPost.content = postAll  # Add Images to Post Content
wpPost.post_status = 'publish'  # Set Post as Publish
wp.call(posts.NewPost(wpPost))  # Post Content
