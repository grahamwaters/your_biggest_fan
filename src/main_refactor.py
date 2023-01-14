import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import json
import time

# Load config data
with open("config/config.json") as f:
    data = json.load(f)

# Initialize webdriver
options = webdriver.ChromeOptions()
options.add_argument("--disable-extensions")
options.add_argument('--disable-gpu')
options.add_argument("--no-sandbox")
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--remote-debugging-port=9222")
driver = webdriver.Chrome(executable_path=data["chrome_driver_path"], chrome_options=options)

# Go to login page
driver.get("https://www.github.com/login")


# find the password field and enter the password
password = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.ID, "password"))
)
password.send_keys(data["github_password"])

# wait for login
waiting = input("Press enter to continue")


# URL click counter
url_clicks = {}

# Click follow buttons
while True:
    # Skip if URL has been clicked too many times
    if driver.current_url in url_clicks:
        if url_clicks[driver.current_url] >= 5:
            continue
        else:
            url_clicks[driver.current_url] = 0

    # Find follow buttons
    follow_buttons = driver.find_elements(By.CSS_SELECTOR, "input.btn")
    follow_buttons = [button for button in follow_buttons if button.is_displayed() and button.is_enabled() and button.get_attribute("value") == "Follow" and button.location["y"] < driver.execute_script("return window.innerHeight")]

    # Click random follow button
    if follow_buttons:
        follow_buttons[random.randint(0, len(follow_buttons) - 1)].click()
        print(f"Follow button clicked at {datetime.now()} url: {driver.current_url}")
        time.sleep(random.randint(6, 10))

    # Break if loop has run too many times
    if url_clicks[driver.current_url] >= 30 or "This repository has no more watchers" in driver.page_source:
        break

# Close webdriver
driver.close()
