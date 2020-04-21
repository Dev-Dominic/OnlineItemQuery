# Python default modules import

import os
import sys
import smtplib

# Webdriver imports

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

class BaseQueryDriver():
    """Base Class for a website item query driver

    Attributes:
        homepage: URL of home page that contains search bar
        searchBar: xpath of home page item query search bar
        item: Item to be queried

    """

    def __init__(self, homepage, searchBar, item):
        self.homepage = homepage
        self.searchBar = searchBar
        self.item = item

class AmazonQueryDriver(BaseQueryDriver):
    """Child class of BaseQueryDriver

    Queries amazon's website for a given item's details

    Attributes:
        BaseQueryDriver attributes
        None

    """

    def __init__(self, homepage, searchBar, item):
        BaseQueryDriver.__init__(self, homepage, searchBar, item)

