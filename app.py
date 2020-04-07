#!/usr/bin/python

import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

noRESULTS = 5 # Results retrieved per website

def getWebDriver():
    """Setups up google webdriver

    Webdriver contains headless option(does not run a physical window),
    as well as suppresses commandline log messages that are not critical. 

    Args:
        None

    Return:
        driver: Returns a google webdriver object or none if chromedriver path is not set

    """
    chromeDrivePath = os.getenv('CHROMEDRIVERPATH') 
    driver = None

    if chromeDrivePath == None:
        print("Error: ChromeDriver path not set!")
        return None

    chromeOptions = Options()
    chromeOptions.add_argument('--headless')
    chromeOptions.add_argument('--log-level=3')
    chromeOptions.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(chromeDrivePath, options=chromeOptions)

    return driver

def amazonItemStrip(itemInfo):
    """Strips unnecesarry item info

    Strips item info such as:
        - Amazon's Choice
        - 'Best Seller'
        - 'More Buying Choices'
        - All information after 'More Buying Choices'
        - Review Count
        - Numbers without dollar amounts

    Args:
        itemInfo: string containing item information

    Return: 
        stripedInfo: list containg only relvant item info

    """
   
    itemInfoList = itemInfo.split('\n') 
    indexOfBuyingChoices = 0 

    if 'More Buying Choices' in itemInfoList:
        indexOfBuyingChoices = itemInfoList.index('More Buying Choices') # Index to delete irrelevant information

    filterOut = ['Amazon\'s Choice', 'Best Seller', 'More Buying Choices']
    itemInfoList = list(filter(lambda x: not x in filterOut, itemInfoList))[indexOfBuyingChoices:]

    stripedInfo = [itemInfoList[0]] + list(filter(lambda x: x.startswith('$'), itemInfoList))

    if len(stripedInfo) > 2:
        stripedInfo = stripedInfo[0:2]

    return stripedInfo

def getAmazonItem(item, webDriver):
    """Queries amanzon's website for an item

    Args:
        item: Name of item to query 
        webDriver: selenium google webdriver object

    Return: 
        Dict mapping search results index with each 
        result's information.

       results:  
       {
            '0' : 
            {
                'title' : 'Vagabond, Vol. 1 (VIZBIG Edition)',
                'price' : $10
                'URL'   : <amazon resource url>
            },
            '1' : 
            {
                'title' : 'Vagabond, Vol. 2 (VIZBIG Edition)',
                'price' : $10
                'URL'   : <amazon resource url>
            } 
        }

    """

    webDriver.get('https://www.amazon.com')
    searchBox = webDriver.find_element_by_id("twotabsearchtextbox")
    searchBox.send_keys(item)
    searchBox.send_keys(Keys.RETURN)

    results = {}
    resultsSubLabels = ['title', 'price', 'URL']

    # resultXpath      : Using xpath to get each resulting element 
    # resultLinkXpath  : Using xpath to get each resulting element URL link

    resultXpath = '//div[@data-index="{}"]' 
    resultLinkXpath = '//div[@data-index="{}"]//span[@data-component-type="s-product-image"]//a[1]'
    
    index, itemIndex = 0,0
    while index < noRESULTS:
        searchResults = webDriver.find_element_by_xpath(resultXpath.format(itemIndex)).text
        searchURL = webDriver.find_element_by_xpath(resultLinkXpath.format(itemIndex))

        resultValue = amazonItemStrip(searchResults) + [searchURL.get_attribute('href')]

        if len(resultValue) != 3:
            itemIndex += 1
            continue

        results[index] = dict(zip(resultsSubLabels,resultValue))
        index += 1
        itemIndex += 1

    return results

# driver.get('https://ebay.com')

if __name__ == "__main__":
    webDriver = getWebDriver()

    if webDriver != None: 
        amazonQuery = getAmazonItem('nike shoes', webDriver) 


    print(amazonQuery)
    webDriver.close()
    print("Finished!")

