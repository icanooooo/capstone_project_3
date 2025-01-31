from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime

import pandas as pd
import re

# Mesti pake selenium

def get_data_asetku(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Set the path to ChromeDriver (it is bundled with the Selenium WebDriver)
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    content_row_one = soup.find("div", class_="content-row-1")

    contents = content_row_one.find_all("div", class_="content-desc")

    header = []
    asetku_data = []

    for content in contents:
        name = content.find("div", class_="name")
        name = name.get_text(strip=True)

        header.append(name)

        content_data = content.find("div", class_="amount")
        content_data = content_data.get_text(strip=True)
        content_data = int(re.sub(r'\D', '', content_data))

        asetku_data.append(content_data)

    header.append("input_date")
    asetku_data.append(datetime.now())
        
    driver.quit()
        
    return header, asetku_data

def create_asetku_dataframe(data):
    header = ["total_fund_recipients",
              "total_cur_year_fund_recipients",
              "current_active_fund_recipients",
              "total_fund_providers",
              "total_cur_year_fund_providers",
              "current_active_fund_providers",
              "total_fund_accumulated",
              "total_cur_year_fund_accumulated",
              "current_active_fund_accumulated",
              "input_time_jkt"]
    
    df = pd.DataFrame([data], columns=header)

    return df