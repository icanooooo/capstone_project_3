from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from datetime import datetime

import pandas as pd
import re

# Mesti pake selenium

def get_data_asetku(url, geckodriver):
    class AsetkuData:
        def __init__(self):
            self.data = []
        def append_data(self, value):
            self.data.append(value)

    asetkuObject = AsetkuData()

    options = Options()
    options.add_argument("--headless")
    service = Service(geckodriver)

    driver = webdriver.Firefox(service=service, options=options)

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