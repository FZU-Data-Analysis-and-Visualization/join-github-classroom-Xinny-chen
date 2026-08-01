# -*- coding: utf-8 -*-
import sys
import os
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Fix windows terminal encode
sys.stdout.reconfigure(encoding="utf-8")
os.environ["PYTHONIOENCODING"] = "utf-8"

# Config
city = "fuzhou"
max_count = 200
wait_sec = 2

# Chrome config
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
wait = WebDriverWait(driver, 10)

# Define variable at top
house_list = []
page = 1

print("Start crawling second-hand house data of {}, target quantity: {} items".format(city, max_count))

# Crawl loop
while len(house_list) < max_count:
    url = "https://{}.anjuke.com/sale/p{}-y1/?from=fangjia".format(city, page)
    print("Crawling page {}: {}".format(page, url))
    driver.get(url)

    try:
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "property")))
    except Exception:
        print("Page load timeout or no house data exists")
        break

    house_cards = driver.find_elements(By.CLASS_NAME, "property")
    if not house_cards:
        print("No more house data, exit loop")
        break

    for card in house_cards:
        if len(house_list) >= max_count:
            break
        try:
            title = card.find_element(By.CLASS_NAME, "property-content-title-name").text.strip()
            room_info = card.find_element(By.CLASS_NAME, "property-content-info").text.strip()
            floor_year = card.find_element(By.CLASS_NAME, "property-content-info-extra").text.strip()
            address = card.find_element(By.CLASS_NAME, "property-content-info-comm-address").text.strip()
            total_price = card.find_element(By.CLASS_NAME, "property-price-total").text.strip()
            unit_price = card.find_element(By.CLASS_NAME, "property-price-average").text.strip()
            district = address.split(" ")[0] if " " in address else "Unknown"

            house_list.append({
                "District": district,
                "Title": title,
                "RoomInfo": room_info,
                "FloorAndYear": floor_year,
                "FullAddress": address,
                "TotalPrice": total_price,
                "UnitPrice": unit_price
            })
        except Exception:
            continue

    page += 1
    time.sleep(wait_sec)

# Close browser
driver.quit()

# Save excel
df = pd.DataFrame(house_list)
output_path = "SecondHandHouseData.xlsx"
df.to_excel(output_path, index=False, encoding="utf-8-sig")

print("Crawl finished! Total {} records saved to {}".format(len(house_list), output_path))

# Add statistics sheet only when data exists
if not df.empty:
    print("\n===== District House Count Statistics =====")
    district_count = df["District"].value_counts()
    print(district_count)

    with pd.ExcelWriter(output_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        district_count.to_excel(writer, sheet_name="DistrictStats", header=["HouseCount"])
    print("\nDistrictStats sheet has been added to excel file successfully.")
else:
    print("Warning: No house data crawled, skip statistics sheet")