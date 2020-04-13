#!/usr/bin/python

# Python default modules import

import os
import smtplib

# Webdriver imports

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
    driver_path = os.getenv('CHROMEDRIVERPATH') 
    browser_path = os.getenv('SELENIUM_BROWSER_PATH')
    driver = None

    if not(driver_path or browser_path):
        print("Error: WebDriver path or Browser Path not set!")
        return None

    webDriverOptions = Options()
    webDriverOptions.binary_location = browser_path
    webDriverOptions.add_argument('--headless')
    webDriverOptions.add_argument('--log-level=3')
    webDriverOptions.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(driver_path, options=webDriverOptions)
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

    if indexOfBuyingChoices > 0: 
        itemInfoList = itemInfoList[:indexOfBuyingChoices + 1]

    filterOut = ['Amazon\'s Choice', 'Best Seller', 'More Buying Choices']
    itemInfoList = list(filter(lambda x: x not in filterOut, itemInfoList))

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

def getEbayItem(item, webDriver):
    """Queries ebay's website for an item

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

    webDriver.get('https://www.ebay.com')
    searchBox = webDriver.find_element_by_id("gh-ac")
    searchBox.send_keys(item)
    searchBox.send_keys(Keys.RETURN)

    print(webDriver.title)

def format_item(itemInfo):
    """Formats iteminfo into a string

    Args: 
        itemInfo: Dictionary containing list of related items

    Return:
        strFormat: Formated string of relate items

    """
    strFormat = ''
    for key,value in itemInfo.items():
        strFormat += f'{key + 1}\n' 

        for itemKey, itemValue in value.items(): 
            strFormat += f'{itemKey} : {itemValue}\n'

        strFormat += '\n\n'
    
    return strFormat

def send_email(receiver, messageSub, messageBody):
    """Sends 

    Args:
        receiver: email of receiver
        messageBody: email body

    Return:
        None

    """

    SENDER_EMAIL = os.getenv('SENDER_EMAIL') 
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD') 

    if SENDER_EMAIL and SENDER_PASSWORD: # Checking that environment variables are set
        print('Sending Email....')
        with smtplib.SMTP('smtp-mail.outlook.com', 587) as smtp:
            # Encryption and login to outlook smtp-mail server

            smtp.starttls()
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)

            message = f"Subject: {messageSub} \n\n {messageBody}"
            smtp.sendmail('dominichenrywork@hotmail.com', receiver, message.encode('utf-8'))

    else:
       print("Email not sent! Set SENDER email environment variables")

if __name__ == "__main__":
    webDriver = getWebDriver()
    itemQuery = 'Samsung Remote UN49J5200AF'

    if webDriver != None: 
        print('Querying Amazon....')
        amazonQuery = getAmazonItem(itemQuery, webDriver) 
        print(amazonQuery)
        # formattedQuery = format_item(amazonQuery)
        # send_email('dominichenrywork@hotmail.com', itemQuery, formattedQuery)
        webDriver.close()

    print("Finished!")
