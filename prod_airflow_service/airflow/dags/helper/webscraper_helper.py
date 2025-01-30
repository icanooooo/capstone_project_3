from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

# Mesti pake selenium

def get_data_asetku(url, geckodriver):
    options = Options()
    options.add_argument("--headless")
    service = Service(geckodriver)

    driver = webdriver.Firefox(service=service, options=options)

    driver.get(url)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    divs = soup.find_all("div", class_="content-row-1")

    for div in divs:
        print(div)