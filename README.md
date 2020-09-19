# Online Item Query

Queries for a specific item on Amazon and Ebay and returns result via email.

## External Dependencies

- Selenium

- chromedriver

- Valid chromium based webbrowser

## Setup

### Linux/Mac OS

Creation of virtual environment and installation of dependencies.

```bash

$ python -m venv venv

$ source venv/bin/activate

$ pip install -r requirements.txt

```

### Windows
Creating and entering virutal environment

```bash

$ python -m venv venv

$ venv\Scripts\activate

$ pip install -r requirements.txt

```

### Environment variables

- SENDER_EMAIL: email to be used to send query responses

- SENDER_PASSWORD: SENDER_EMAIL password

- CHROMEDRIVERPATH: path to chromedriver

- SELENIUM_BROWSER_PATH: path to chromium based browser

**Note:** Ensure that the versions for the chromium based browser matches your chromedriver
