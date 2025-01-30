from helper.webscraper_helper import get_data_asetku, create_asetku_dataframe

a, b = get_data_asetku('https://www.asetku.co.id/', "/snap/bin/geckodriver")

df = create_asetku_dataframe(b)

print(df)