from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import os

def scroll_down(driver):
    """Ruller ned på siden for å laste inn flere gavekort."""
    driver.execute_script("window.scrollBy(0, 500);")
    time.sleep(2)  # Gir tid til at flere elementer lastes inn

# Sett opp lagringsplass for CSV
current_directory = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_directory, 'zupergift.csv')

# Sett opp Chrome-driver
chrome_options = Options()
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--headless")  # Headless for raskere scraping

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
url = 'https://zupergift.com/no/alle-gavekort'
driver.get(url)

# Vent til innholdet lastes
time.sleep(5)

data = []

# Finn alle gavekortene
gift_cards = driver.find_elements(By.CLASS_NAME, 'ProductList_itemInner__05f4267a')
print(f"Antall gavekort funnet før scrolling: {len(gift_cards)}")

for i, card in enumerate(gift_cards, start=1):
    if i % 4 == 0:  # Scroll etter hvert 4. gavekort
        scroll_down(driver)
    
    try:
        # Hent navn på gavekortet
        name_element = card.find_element(By.CLASS_NAME, 'styles_name__18dea1a2')
        name = name_element.text.strip() if name_element else "Ikke funnet"
        
        # Hent bonus-informasjonen (pris)
        bonus_element = card.find_element(By.CLASS_NAME, 'styles_price__18dea1a2')
        bonus = bonus_element.text.strip() if bonus_element else "Ikke funnet"
        
        # Fast link for alle gavekort
        link = "https://www.saseurobonusshop.com/no/zupergift"
        
        print(f"Gavekort {i}: {name} - {bonus}")  # Debugging
        
        data.append([name, bonus, link])
    except Exception as e:
        print(f"Feil ved gavekort {i}: {e}")
        data.append(["Ikke funnet", "Ikke funnet", "Ikke funnet"])

# Sorter dataene alfabetisk
data.sort()

# Lagre til CSV
df = pd.DataFrame(data, columns=['Butikk', 'Bonus', 'Link'])
df.to_csv(csv_path, index=False)

# Lukk driveren
driver.quit()
