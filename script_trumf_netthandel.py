from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_directory, 'trumf.csv')


# Chrome-driver setup
chrome_options = Options()
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
url = 'https://trumfnetthandel.no/kategori' 
driver.get(url)

# Vent til den første delen av innholdet er lastet
WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[3]/div/div/div[2]')))

# Rull ned på siden til alle elementene er lastet
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Finn alle "a"-tagger i ønsket div
a_tags = driver.find_elements(By.XPATH, '/html/body/div[3]/div[3]/div/div/div[2]//a')

# Liste for å lagre data
data = []

# Gå gjennom hver "a"-tag og hent href, data-name, og innhold fra den spesifikke div'en
for i, a_tag in enumerate(a_tags):
    href = a_tag.get_attribute('href')
    data_name = a_tag.get_attribute('data-name')
    
    try:
        div_innhold = driver.find_element(By.XPATH, f'//*[@id="CategoryResults"]/a[{i+1}]/div/div[1]/div').text
        value = float(div_innhold[:-2].replace(",", ".").strip())
        points = round(value * 13.5)
        div_innhold = div_innhold + f" ({points} poeng per 100kr)"

        data.append([data_name, div_innhold, href])

    except Exception as e:
        print(f"Fant ikke element på indeks {i+1}: {e}")
        data.append([data_name, "Ikke funnet", href])

data.sort()

df = pd.DataFrame(data, columns=['Butikk', 'Bonus', 'Link'])
df.to_csv(csv_path, index=False)

# Lukk driveren
driver.quit()