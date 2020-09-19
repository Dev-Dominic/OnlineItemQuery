#!/usr/bin/python

# Python default modules import

import os
import sys
import smtplib

# Webdriver imports

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

RESULTS_LIMIT = 5 # Results retrieved per website
LABELS = ['title', 'price', 'URL']

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
    # webDriverOptions.add_argument('--no-sandbox')
    # webDriverOptions.add_argument('--remote-debugging-port=9222')
    # webDriverOptions.add_argument('--disable-dev-shm-usage')
    # webDriverOptions.add_argument('--log-level=3')
    # webDriverOptions.add_argument('start-maximized')
    # webDriverOptions.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(driver_path, options=webDriverOptions)
    # driver = webdriver.Chrome(driver_path)
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
        # Index to delete irrelevant information

        indexOfBuyingChoices = itemInfoList.index('More Buying Choices')

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

    # resultXpath      : Using xpath to get each resulting element
    # resultLinkXpath  : Using xpath to get each resulting element URL link

    resultXpath = '//div[@data-index="{}"]'
    resultLinkXpath = '//div[@data-index="{}"]//span[@data-component-type="s-product-image"]//a[1]'

    index, itemIndex = 0,1
    while index < RESULTS_LIMIT:

        # Goes to next item if issue finding item via xpath
        try:
            searchResults = webDriver.find_element_by_xpath(resultXpath.format(itemIndex)).text
            searchURL = webDriver.find_element_by_xpath(resultLinkXpath.format(itemIndex))
        except:
            itemIndex += 1
            continue

        resultValue = amazonItemStrip(searchResults) + [searchURL.get_attribute('href')]

        if len(resultValue) != 3:
            itemIndex += 1
            continue

        results[index] = dict(zip(LABELS,resultValue))
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

    results = {}

    itemTitle = webDriver.find_elements_by_class_name('s-item__title')
    itemPrice = webDriver.find_elements_by_class_name('s-item__price')
    itemURL = webDriver.find_elements_by_xpath('//div[@class="s-item__image"]/a')

    for i in range(RESULTS_LIMIT):

        # Extracts an item's title, price and URL
        # Creates item dictionary that is added to results dictionary

        resultValue = [itemTitle[i].text, itemPrice[i].text, itemURL[i].get_attribute('href')]
        results[i] = dict(zip(LABELS,resultValue))

    return results


def email_format(*itemInfo):
    """Formats iteminfo into a string

    Args:
        itemInfo: an array of arguments from different websites
        that is tuple format formatted as a dictionary containing list of related items

        ('name of website', 'dictionary of related items')

    Return:
        strFormat: Formated string of relate items

    """
    strFormat = ''

    for websiteQuery in itemInfo:
        strFormat += f'{websiteQuery[0]}\n'

        for key,value in websiteQuery[1].items():
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

            message = f"Subject: {messageSub} \n\n {messageBody} \n\n Powered by Dev-Dominic"
            smtp.sendmail('dominichenrywork@hotmail.com', receiver, message.encode('utf-8'))

    else:
       print("Email not sent! Set SENDER email environment variables")

if __name__ == "__main__":
    # Retrieve commandline arguments:
    # $ python app.py <query-item> <receiver-email>

    itemQuery, receiver_email = sys.argv[1], sys.argv[2]


    webDriver = getWebDriver() # webDriver init

    if webDriver != None:

        ## Querying each website

        print('Querying Amazon....')
        amazonQuery = getAmazonItem(itemQuery, webDriver)

        print('Querying Ebay....')
        ebayQuery = getEbayItem(itemQuery, webDriver)

        # Formatting information for email

        strFormat = email_format(('Amazon', amazonQuery), ('Ebay',ebayQuery))

        send_email(receiver_email, itemQuery, strFormat)
        webDriver.close()

    print("Finished!")
