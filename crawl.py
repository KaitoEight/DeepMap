from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)

BASE_URL = "https://batdongsan.com.vn/cho-thue-can-ho-chung-cu-thu-duc"

def clean_price(price_text):
    if not price_text:
        return None
    
    # extract number (VD: 12 triệu -> 12)
    match = re.search(r'(\d+[,.]?\d*)', price_text)
    if match:
        return float(match.group(1).replace(",", "."))
    return None

def get_text_safe(parent, selectors):
    for sel in selectors:
        try:
            el = parent.find_element(By.CSS_SELECTOR, sel)
            text = el.text.strip()
            if text:
                return text
        except:
            continue
    return ""

def crawl_page(page=1):
    url = f"{BASE_URL}/p{page}"
    driver.get(url)

    cards = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".re__card-info-content"))
    )

    print(f"\n📄 Page {page} - Found:", len(cards))

    results = []

    for card in cards:
        title = get_text_safe(card, [
            ".pr-title",
            ".re__card-title span",
            "h3"
        ])

        price = get_text_safe(card, [
            ".re__card-config-price"
        ])

        area = get_text_safe(card, [
            ".re__card-config-area"
        ])

        location = get_text_safe(card, [
            ".re__card-location span"
        ])

        desc = get_text_safe(card, [
            ".re__card-description"
        ])

        # 🚫 skip record rỗng
        if not title or not price:
            continue

        data = {
            "title": title,
            "price_text": price,
            "price_million": clean_price(price),
            "area": area,
            "location": location,
            "description": desc
        }

        results.append(data)

        print(f"✔ {title} | {price}")

    return results


# ========================
# MAIN
# ========================

all_data = []

for page in range(1, 4):  # crawl 3 pages trước
    data = crawl_page(page)
    all_data.extend(data)
    time.sleep(2)

driver.quit()

print("\nTOTAL:", len(all_data))