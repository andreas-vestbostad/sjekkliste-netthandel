from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_directory, 'studentkortet.csv')

# Chrome-driver setup
chrome_options = Options()
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
url = 'https://studentkortet.no/rabatter'
driver.get(url)

# Vent til at elementene er lastet
time.sleep(2)

# Finn alle "li"-elementene som inneholder butikkene
list_items = driver.find_elements(By.XPATH, '//*[@id="main"]/section[3]/div/div/ul/li')

# Liste for å lagre data
data = []

# Gå gjennom hvert element og hent relevant informasjon
for i, item in enumerate(list_items):
    try:
        # Hent butikkens navn fra "alt"-teksten til bildet
        shop_name = item.find_element(By.XPATH, f'//*[@id="main"]/section[3]/div/div/ul/li[{i+1}]/div/div/a/img').get_attribute('alt').split(' ')[0]
        
        # Hent tilbudet fra den relevante "div"-en
        offer = item.find_element(By.XPATH, f'//*[@id="main"]/section[3]/div/div/ul/li[{i+1}]/div/a/div').text
        
        # Hent lenken til tilbudet
        link = item.find_element(By.XPATH, f'//*[@id="main"]/section[3]/div/div/ul/li[{i+1}]/div/a').get_attribute('href')
        
        # Legg til informasjonen i listen
        data.append([shop_name, offer, link])
    except Exception as e:
        print(f"Fant ikke element på indeks {i+1}: {e}")
        data.append(["Ikke funnet", "Ikke funnet", "Ikke funnet"])

# Sorter dataene (kan være nyttig for alfabetisk rekkefølge på butikkene)
data.sort()

# Lagre dataene i en CSV-fil
df = pd.DataFrame(data, columns=['Butikk', 'Bonus', 'Link'])
df.to_csv(csv_path, index=False)

# Lukk driveren
driver.quit()