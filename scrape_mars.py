
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from bs4 import BeautifulSoup
import requests
import pandas as pd
from selenium import webdriver as driver
import pymongo
import time

#conn = 'mongodb://localhost:27017'

# Pass connection to the pymongo instance.
#client = pymongo.MongoClient(conn)



# Connect to a database. Will create one if not already available.
#db = client.mars_app



def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    mars_facts = {}
    browser = init_browser()
    ### NASA Mars News
    # URL of page to be scraped
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    time.sleep(2)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    #getting the title and para
    title = soup.find('div', class_='content_title').find('a').text.strip()
    news_p = soup.find('div', class_='article_teaser_body').text
    mars_facts["recent"] = {"title": title, "description": news_p}

    ### Mars Facts
    factUrl = "http://space-facts.com/mars/"
    facts = pd.read_html(factUrl)
    facts_df = facts[0]
    facts_df.rename(columns={0:"Element", 1:"Value"}, inplace=True)
    #facts_df.set_index("Element", inplace=True)
    facts_html = facts_df.to_html()
    mars_facts["facts"] = {"table":facts_html}


    ### Mars Weather
    twtUrl = "https://twitter.com/marswxreport?lang=en"
    twtResp = requests.get(twtUrl)
    soup = BeautifulSoup(twtResp.text, 'lxml')
    twtdata = soup.find('p', class_='TweetTextSize TweetTextSize--normal js-tweet-text tweet-text')
    mars_weather = (twtdata.text.strip()).replace('\n', ' ')
    mars_facts["tweet"] = {"twt": mars_weather}



    ### JPL Mars Space Images - Featured Image
    featUrl = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(featUrl)
    time.sleep(2)
    browser.click_link_by_id('full_image')
    time.sleep(2)
    find_h=browser.find_by_css('img[class="fancybox-image"]')
    featured_image_url = find_h["src"]
    mars_facts["featuredimg"] = {"featimg": featured_image_url}


    ### Mars Hemispheres
    hemiUrl = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemiUrl)
    time.sleep(2)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.find_all('div', class_="description")[0:4]
    hemisphere_image_urls = []
    for div in divs:
        href = div.h3.text
        browser.click_link_by_partial_text(href)
        time.sleep(2)
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        dd = soup.find('a', target="_blank")['href']
        ah = soup.find('h2', class_="title").text
        hemisphere_image_urls.append({"title":ah, "img_url":dd})
        

        browser.visit(hemiUrl)
        time.sleep(2)
    mars_facts["Hemis"] = {"Hemispheres" : hemisphere_image_urls }

    return mars_facts
