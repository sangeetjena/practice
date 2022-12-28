import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# url of the page we want to scrape

class ChildScrapper:
    def get_all_child_paths(self,url):
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
        allpath = []
        for pair in pairs:
            print(pair.text)
            allpath.append(url + pair.text)
        return allpath