#Grabs book data from Amazon for acquisitions lists
# importing libraries
from bs4 import BeautifulSoup
from time import sleep
from random import randint
import requests
import random
import pandas as pd
import re
from collections import OrderedDict

#Define empty dictionary for later
dict = {}
dict['title'] = []
dict['author'] = []
dict['price'] = []
dict['publication'] = []
dict['isbn'] = []
dict['year'] = []
dict['pubname'] = []

#A bunch of user agent data to rotate between to hopefully evade bot detection
headers_list = [
# Firefox 77 Mac
{
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"Accept-Language": "en-US,en;q=0.5",
"Referer": "https://www.google.com/",
"DNT": "1",
"Connection": "keep-alive",
"Upgrade-Insecure-Requests": "1"
},
# Firefox 77 Windows
{
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"Accept-Language": "en-US,en;q=0.5",
"Accept-Encoding": "gzip, deflate, br",
"Referer": "https://www.google.com/",
"DNT": "1",
"Connection": "keep-alive",
"Upgrade-Insecure-Requests": "1"
},
# Chrome 83 Mac
{
"Connection": "keep-alive",
"DNT": "1",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
"Sec-Fetch-Site": "none",
"Sec-Fetch-Mode": "navigate",
"Sec-Fetch-Dest": "document",
"Referer": "https://www.google.com/",
"Accept-Encoding": "gzip, deflate, br",
"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
},
# Chrome 83 Windows 
{
"Connection": "keep-alive",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
"Sec-Fetch-Site": "same-origin",
"Sec-Fetch-Mode": "navigate",
"Sec-Fetch-User": "?1",
"Sec-Fetch-Dest": "document",
"Referer": "https://www.google.com/",
"Accept-Encoding": "gzip, deflate, br",
"Accept-Language": "en-US,en;q=0.9"
}
]
ordered_headers_list = []
for headers in headers_list:
    h = OrderedDict()
for header,value in headers.items():
    h[header]=value
    ordered_headers_list.append(h)


#Asks for input and output filenames
inputname = input('URL Input Filename without extension (Max 50 URLS): ')
newFile = input('Save output data as: ')

#Pulls in URL file:
URLs = open(inputname + '.txt').readlines()
#Check that they pulled in properly
print(URLs)

#Loop to run the URLs through Soup and put their info in the Dictionary
for i, url in enumerate(URLs, 0):
    sleep(randint(5,100))    

    url = URLs[i]        
    #Pick a random browser headers
    headers = random.choice(headers_list)
    #Create a request session
    r = requests.Session()
    r.headers = headers
    webpage = r.get(url)
    
    # Creating the Soup Object containing all data
    soup = BeautifulSoup(webpage.content, "lxml")
    # retrieving title
    try:
        # Outer Tag Object
        title = soup.find("span", attrs={"id": 'productTitle'})
        # Inner NavigableString Object
        title_value = title.string
        # Title as a string value
        title_string = title_value.strip().replace(',', '')
    except AttributeError:
        title_string = "NA"
    
    #removes extra parenteses from title
    titlesub1 = re.sub(r'\(manga\)|\(Light Novel\)|\(novel\)', '', title_string)
    titlefix = re.sub(r'\((.*?)\)', '', titlesub1)
    print("Title = ", titlefix)
    
    # retrieving author
    try:
        author = soup.find("a", attrs={'class': 'contributorNameID'}).contents
        authorString = author[0].getText()            
    except AttributeError:
        author2 = soup.find("span", attrs={'class': 'author'})
        name2 = author2.findAll("a")
        authorString = name2[0].getText()
    print("Author = ", authorString)

    # retrieving price
    try:
        price = soup.find("span", attrs={'class': 'a-size-base a-color-price a-color-price'}).string.strip().replace(',', '')
    # we are omitting unnecessary spaces and commas form our string
    except AttributeError:
        price = "NA"
    print("Price = ", price)

    # finding all li tags in ul and printing the text within it
    data1 = soup.find("div", attrs={'id': 'detailBullets_feature_div'})
    info = data1.findAll("span")
    pub = info[2].getText()
    isbn= info[14].getText()
    print("Publication = ", pub)
    print("ISBN = ", isbn)

    # Append these to dictionary
    dict['title'].append(titlefix) 
    dict['author'].append(authorString)
    dict['price'].append(price)
    dict['publication'].append(pub)
    dict['isbn'].append(isbn)
    
    #Grab just the publisher's name for a separate column
    pubsearch = re.compile(r'[^\(]*')
    pubtemp = pubsearch.search(pub)
    pubname = pubtemp.group()
    pubclean = re.sub(r';[^.]+', '', pubname)
    print("Publisher = ", pubclean)
    dict['pubname'].append(pubclean)
    
    #Grab just the year part for a separate column
    yearsearch = re.compile(r'\d\d\d\d')
    yeartemp = yearsearch.search(pub)
    year= yeartemp.group()
    print("Year = ", year)
    dict['year'].append(year)

#Makes Dataframe
df = pd.DataFrame(dict)

#Removes dash from ISBN
df['isbn'] = df['isbn'].str.replace("-","")

#Drops extra column and reorders them to the right order
df.drop(columns= ['publication'], inplace=True)
df = df[['title', 'author', 'year', 'pubname', 'isbn', 'price']]
df.columns = df.columns.str.strip()
df.head()

#Saves to Excel
df.to_excel(newFile + '.xlsx')