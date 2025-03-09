from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
import time
import pandas as pd
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_directory, 'sas.csv')

# Chrome-driver setup
chrome_options = Options()
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
base_url = 'https://onlineshopping.flysas.com/nb-NO/alle-butikker/'

# Liste for å lagre data
data = []

# Start med første side og finn total antall sider
page_number = 1
url = f'{base_url}{page_number}'
driver.get(url)

# Vent til siden er lastet
time.sleep(3)

# Finn total antall sider ved å telle div-elementer i pagineringsseksjonen
try:
    pagination_elements = driver.find_elements(By.XPATH, '/html/body/div[1]/div/div[2]/main/div[3]/span/div')
    total_pages = len(pagination_elements) - 2  # Fjern tilbake og frem knappene
    print(f"Totalt antall sider: {total_pages}")
except Exception as e:
    print(f"Fant ikke sideinformasjons-elementene: {e}")
    total_pages = 1  # Hvis vi ikke finner sideinformasjons-elementene, antar vi at det bare er én side

# Gå gjennom alle sidene
for page_number in range(1, total_pages + 1):
    # Åpne riktig side
    url = f'{base_url}{page_number}'
    driver.get(url)
    
    # Vent til innholdet er lastet
    time.sleep(3)  # Juster ventetiden etter behov
    
    # Hent butikkene fra den aktuelle siden
    all_shops = driver.find_elements(By.XPATH, '//*[@id="allShops"]/div[1]/div')
    
    # Gå gjennom alle butikkene på denne siden
    for i, shop in enumerate(all_shops):
        # Hent butikkens navn
        shop_name = shop.find_element(By.XPATH, f'//*[@id="allShops"]/div[1]/div[{i+1}]/div[2]/div/p').text
        
        # Hent poengdataen for butikken (alle "span" i poengseksjonen)
        try:
            points_section = shop.find_elements(By.XPATH, f'//*[@id="allShops"]/div[1]/div[{i+1}]/div[2]/div/div[1]/span')
            points_data = []

            # Slå sammen poengdataene hvis det er flere "span" under en butikk
            for point in points_section:
                div_innhold = point.text
                if div_innhold.strip():  # Sjekk om den ikke er tom
                    points_data.append(div_innhold)
            
            # Hvis vi har flere poengdata for en butikk, slå sammen dem til én streng
            if len(points_data) == 2:
                all_points = f"{points_data[0]} {points_data[1]}"  # Slå sammen "10 poeng" og "per 100 kr."
            elif points_data:
                all_points = "; ".join(points_data)  # Hvis det er flere, samle dem med semikolon
            else:
                all_points = "Poengdata ikke funnet"

            data.append([shop_name, all_points, url])

        except Exception as e:
            print(f"Fant ikke poengdata for butikk {shop_name}: {e}")
            data.append([shop_name, "Poengdata ikke funnet", url])

data.sort()

# Lagre dataene til en CSV-fil
df = pd.DataFrame(data, columns=['Butikk', 'Bonus', 'Link'])
df.to_csv(csv_path, index=False)

# Lukk driveren
driver.quit()