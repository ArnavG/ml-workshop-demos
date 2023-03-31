#!/usr/bin/env python
# coding: utf-8

# # Web Crawling in Selenium
# ### By Arnav Gurudatt
# 
# 
# **The first thing you're going to want to do is make sure your Chrome is up to date. THIS IS SUPER IMPORTANT. If your browser is not up to date, Selenium will not work. Close your browser and update it at this stage if it is not already up to date.**

# ![Go to Chrome settings and find the About Chrome section in the sidebar](chromeupdate.png)
# 
# Go to Chrome settings and find the About Chrome section in the sidebar

# # Downloading ChromeDriver for Selenium
# 
# Selenium makes use of a web driver that mimics user-generated actions on a browser. This includes clicking on web pages, opening a new tab, and selecting HTML elements. You're going to want to download the ChromeDriver that **matches the current Chrome version that you are using as well as your device.** Link here: [https://chromedriver.chromium.org/downloads].

# ![Head to the website and download the correct version](chromedriverdownload.png)
# 
# Head to the website and download the correct version: https://chromedriver.chromium.org/downloads
# 
# Call it 'chromedriver'.

# Now some standard package installation stuff. Feel free to just run the next couple cells.

# In[1]:


pip install selenium


# In[2]:


import numpy as np
import pandas as pd
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# # 1. Some Stonks Data!
# 
# For this demo, let's try to get some data on a couple of equities. In this data set, we'll be dealing with [Exchange-Traded Funds](https://en.wikipedia.org/wiki/Exchange-traded_fund) (ETFs) and [Mutual Funds](https://en.wikipedia.org/wiki/Mutual_fund). ETFs hold a variety of assets, including stocks, bonds, currencies, futures contracts, and sometimes even commodities like gold. Mutual Funds are very similar in that they pool money from investors to purchase securities, but Mutual Funds are are bought and sold from the issuer based on their price at the end of the day, while ETFs are traded from other owners throughout the day on stock exchanges. Let's see how a couple of equities have been performing of late using the website [Morningstar](https://www.morningstar.com/), a financial services company which tracks securities data.

# In[3]:


# Let's start by importing our dataset.

df = pd.read_csv('demo_stock_data.csv', index_col=0) # Helps to save the CSV file to the same directory where the notebook file is located. If not, include the filepath in the code
df


# Let's take a look at the data Morningstar has on our first ETF, with ticker [SPY](https://www.morningstar.com/etfs/arcx/spy/performance).

# ![Go to Chrome settings and find the About Chrome section in the sidebar](spy_demo.png)
# 
# Say we want Monthly and Year-to-Date (YTD) updates on SPY's Total Return % (Price). How can we go about obtaining this data directly from the website?
# 
# Easy! Let's try using the built-in scraper from pandas!

# In[4]:


url = "https://www.morningstar.com/etfs/arcx/spy/performance"
test_morningstar_data = pd.read_html(url) # This will error, don't be scared
test_morningstar_data


# Well, crap. That's not good.
# 
# As you might find, pandas' built-in function that reads html pages can be super valuable for web pages with easy-to-read, tabular data. Basketball Reference is a good example of this. Let's get [Stephen Curry's stats](https://www.basketball-reference.com/players/c/curryst01.html):

# In[5]:


bball_url = "https://www.basketball-reference.com/players/c/curryst01.html"
bball_data = pd.read_html(bball_url)[1] # Stephen Curry's player stats
bball_data


# For more complex, dynamic web pages, though, pandas will not be enough. As you'll see from the error we received trying to read Morninstar's web page, pandas could not find any HTML tables to generate a data frame.
# 
# Thankfully, we have selenium!

# # 2. Scraping Stonks in Selenium
# 
# As mentioned earlier, Selenium will mimic user actions on a Chrome web page: clicking, opening new URLs, etc.
# 
# To get started with Selenium, we will first need to find the file path to the ChromeDriver we downloaded earlier. This will open a separate Chrome window where Selenium will run.

# In[6]:


PATH = "/Users/arnavgurudatt/chromedriver" # Change this file path to match the chromedriver location on your device!
driver = webdriver.Chrome(PATH)


# As you may have noticed, the Chrome WebDriver would have opened an entirely new Chrome window! That's where the action happens. You can actually see what goes on in that window as your web scraper runs. It's usually a good idea to monitor it to check for errors or stoppages.
# 
# Now comes the magic – let's write a function that can scrape the Monthly and YTD values from morningstar.

# In[7]:


# Let's start by creating a couple of lists to store our data. We'll add these to the dataframe later.

one_mo_vals = [] # List for Monthly returns
ytd_vals = [] # List for YTD returns


# One thing that's very important in web scraping is URL manipulation. We're trying to scrape data for multiple index funds across several different web pages. This seems like a complicated task if we can't scrape everything all at once from the same web page.
# 
# However, let's take a look at Morningstar's URL patterns for various equities:
# 
# * **SPY**: [https://www.morningstar.com/etfs/arcx/spy/performance](https://www.morningstar.com/etfs/arcx/spy/performance)
# * **VFIAX**: [https://www.morningstar.com/funds/xnas/vfiax/performance](https://www.morningstar.com/funds/xnas/vfiax/performance)
# * **VOO**: [https://www.morningstar.com/etfs/arcx/voo/performance](https://www.morningstar.com/etfs/arcx/voo/performance)

# You should notice two main patterns. First, there are two types of equities in the data set, which are represented in the url as either ```etfs``` or ```funds```. Second, the URLs for different equities really only vary by their ticker symbol: ```spy```, ```vfiax```, and ```voo```.
# 
# We can exploit this fact for some simple URL string manipulation.

# In[8]:


# Let's get the names of all the ticker symbols from our data frame

df_tickers = df[["Ticker"]].Ticker.values.tolist()
df_tickers


# Now, all we need to do is iterate through this list as we visit each URL using Selenium! Let's write the code for our function, then call it on each of our ticker symbols in ```df_tickers```.
# 
# Also, there's a lot of comments here, but don't be scared, they're there to help you. Read them so you have an idea of what's going on. The actual code is pretty simple and doesn't take up too many lines, but if you want to understand what each line means, the comments cover the syntax. Or, maybe you just want to rip the code for your own project and just replace the names with whatever you need. That's fine, too.

# In[9]:


def scraper(ticker_name): # Our function, called scraper, takes the name of the ticker as its parameter
    
    # Morningstar uses a search query where you can find the information on any ticker at the top. This is our URL.
    url = "https://www.morningstar.com/search/us-securities?query=" + str(ticker_name).lower()
    driver.get(url) # Call get() on the URL so that the Chrome WebDriver visits the website

    # WTF is this scary witch spell string???
    # It's called an XPATH, and each element in HTML has a unique one. Make use of inspect element to find it.
    # Believe it or not, it's one of the easiest ways to scrape information. Think of it like a file path on
    # your computer (e.g. Desktop/SAAS/RP/rp_project.py) except the file directs to an HTML element on a web page
    link = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div/div[2]/div[3]/main/div/div/div[1]/section/div[1]/a')
    # We generate the URL we want to click and store it in link. link.click() mimics a user clicking the link
    link.click()
    
    # If you don't have stable connection or selenium is bugging out, it will take a while to open the web page
    # This doesn't stop Python from reading the rest of the commands though – this can cause errors.
    # The implicitly_wait() method allows the web page to take its time loading for a little before execution
    # It's generally bad practice to use implicitly_wait(). You should use WebDriverWait
    # There's also an explicitly_wait() method but it's much more complicated so this is a hacky solution
    driver.implicitly_wait(5)
    
    
    # There's still one problem we haven't handled yet: is the equity an ETF or a FUND?
    # It's easier to do this using driver.current_url and string manipulation, but it's not working for me ;-;
    # e.g. https://www.morningstar.com/etfs/arcx/spy/quote
    # current_url = driver.current_url # driver has a current_url attribute to retrieve this info
    # print(current_url)
    # is_etf = "etfs" in current_url # is_etf will be True if the current_url has "etfs" in it, False otherwise
    # is_fund = "funds" in current_url # is_fund will be True if the current_url has "funds" in it, False otherwise

    # Since that's not working, we'll just use try/except

    try: 
        # We need to get to the PERFORMANCE tab. This is why knowing whether the equity is an ETF vs. FUND is important.
        # ETFs all have the same XPATH for the PERFORMANCE tab. Let's save the XPATH.
        # Selenium Webdriver has a "By" class that allows us to select web elements by Class Name, ID, XPATH, and more.
        performance = driver.find_element(By.XPATH, '//*[@id="etf__tab-performance"]/a/span')
        performance.click() # Click the tab
        driver.implicitly_wait(5) # Wait for the page to load
        
        # By default, the Trailing Returns data is stored by Day End. But we want Month End data.
        # Month End appears to be a button. Let's get its XPATH.
        monthly_button = driver.find_element(By.XPATH, '//*[@id="monthly"]')
        #monthly_button = driver.find_element_by_xpath('//*[@id="monthly"]')
        monthly_button.click() # Click the button
        driver.implicitly_wait(5) # Wait for page to load
        
        # Now the final step is to copy the XPATH of the elements we want and extract the text 
        # Note the use of .text at the end – this gets the specific text string and not the web element itself
        one_mo = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div/div[2]/div[3]/div/div[2]/main/div/div/div[1]/section/sal-components/div/sal-components-funds-performance/div/div[1]/div/div/div/div[2]/div[1]/section[2]/div/div/div/div/div[2]/div[1]/div/table/tbody/tr[1]/td[2]').text
        ytd = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div/div[2]/div[3]/div/div[2]/main/div/div/div[1]/section/sal-components/div/sal-components-funds-performance/div/div[1]/div/div/div/div[2]/div[1]/section[2]/div/div/div/div/div[2]/div[1]/div/table/tbody/tr[1]/td[5]').text
    except:
        # If it's not an ETF, it's a FUND. Same business here as before
        
        performance = driver.find_element(By.XPATH,'//*[@id="performance"]/a/span')
        performance.click()
        driver.implicitly_wait(5)
        
        monthly_button = driver.find_element(By.XPATH, '//*[@id="monthly"]')
        monthly_button.click()
        driver.implicitly_wait(5)
        
        one_mo = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div[3]/div/div[2]/main/div/div/div[1]/section/sal-components/div/sal-components-funds-performance/div/div[1]/div/div/div/div[2]/div[1]/section[2]/div/div/div/div/div[2]/div[1]/div/table/tbody/tr[1]/td[2]').text
        ytd = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div[3]/div/div[2]/main/div/div/div[1]/section/sal-components/div/sal-components-funds-performance/div/div[1]/div/div/div/div[2]/div[1]/section[2]/div/div/div/div/div[2]/div[1]/div/table/tbody/tr[1]/td[5]').text

    # Now, append the Monthly and YTD variables to their respective lists
    one_mo_vals.append(one_mo)
    ytd_vals.append(ytd)


# In[10]:


# Now let's iterate through the list of tickers and get the Monthly and YTD Trailing Returns for each one
# You can actually watch the Chrome window scrape through each one!
# This could take a couple minutes, though, since Selenium is literally mimicking user actions to do this.
# Granted, it's still a lot faster than a human going to each page and copy-pasting!

for ticker in df_tickers:
    scraper(ticker)


# In[11]:


one_mo_vals


# In[12]:


ytd_vals


# In[13]:


# Now we just add these lists to our df, and we're done!

df.insert(4, "Monthly", one_mo_vals)
df.insert(5, "YTD", ytd_vals)
df


# In[14]:


df.to_csv('updated_stonksdata.csv', index=False, encoding='utf-8')


# In[ ]:




