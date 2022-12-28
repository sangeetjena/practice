import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from  childScrapper import ChildScrapper
import time

# url of the page we want to scrape
url = "https://data.binance.vision/?prefix=data/spot/monthly/trades/"

# initiating the webdriver. Parameter includes the path of the webdriver.
driver = webdriver.Chrome('/usr/local/bin/chromedriver')
driver.get(url)

# this is just to ensure that the page is loaded
time.sleep(5)

html = driver.page_source

# this renders the JS code and stores all
# of the information in static HTML code.

# Now, we could simply apply bs4 to html variable
soup = BeautifulSoup(html, "html.parser")
all_divs = soup.find('tbody', {'id': 'listing'})
pairs = all_divs.find_all('a')

# printing top ten job profiles
count = 0
pairList=[]
for pair in pairs:
    #print(pair.text)
    new_path = url + pair.text
    count+=1
    pairList.append(pair.text)
    print("total pairs" + count.__str__())
    # childScrapper = ChildScrapper()
    # all_paths = childScrapper.get_all_child_paths(new_path)
    # print(all_paths)
print(pairList)