import random
import re
import json
import time
import os
import datetime
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
from ratelimit import limits, sleep_and_retry
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import requests
url_clicks = {}
with open("data/url_clicks.csv", "w") as csv_file:
    csv_file.write("URL,Clicks\n")
with open("config/config.json") as f:
    data = json.load(f)
options = webdriver.ChromeOptions()
options.add_argument("--disable-extensions")
options.add_argument('--disable-gpu')
options.add_argument("--no-sandbox")
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--remote-debugging-port=9222")
driver = webdriver.Chrome(
    executable_path=data["chrome_driver_path"], chrome_options=options
)
driver.get("https://www.github.com/login")
time.sleep(10)
@sleep_and_retry
def click_follow_buttons(driver):
    """
    click_follow_buttons
    _extended_summary_
    :param driver: _description_
    :type driver: _type_
    :param data: the data from the config file, contains the good pages to scrape
    :type data: _type_
    :return: _description_
    :rtype: _type_
    """
    while_counter = 0
    url_clicks = {}
    while True and while_counter < 40:
        try:
            if driver.current_url in url_clicks:
                if url_clicks[driver.current_url] >= 5:
                    continue
                else:
                    url_clicks[driver.current_url] = 0
            follow_buttons = driver.find_elements(By.CSS_SELECTOR, "input.btn")
            follow_buttons = [button for button in follow_buttons if button.is_displayed() and button.is_enabled() and button.get_attribute("value") == "Follow" and button.location["y"] < driver.execute_script("return window.innerHeight")]
            if follow_buttons:
                follow_buttons[random.randint(0, len(follow_buttons) - 1)].click()
                print(f"Follow button clicked at {datetime.now()} url: {driver.current_url}")
                time.sleep(random.randint(6, 10))
            while_counter += 1
            if url_clicks[driver.current_url] >= 30:
                break
            if while_counter > 30:
                break
            else:
                while_counter += 1
            if "This repository has no more watchers" in driver.page_source:
                break
            if while_counter > 20:
                break
        except Exception as e:
            print(e)
            continue
        while_counter += 1
@sleep_and_retry
def scrape_for_users(driver):
    """
    scrape_for_users - takes a driver and scrapes the current page for users that are interested in the same things as you are and saves them to a json file in the data folder.
    :param driver: _description_
    :type driver: _type_
    """
    current_page = driver.current_url
    prev_url = None
    if "people" in current_page:
        current_page = current_page.replace("/people", "")
    driver.get(current_page + "/repositories")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    repos = soup.find_all("a", {"itemprop": "name codeRepository"})
    repos = [repo["href"] for repo in repos]
    viable_urls = []
    for repo in repos:
        repo = 'https://github.com' + repo
        driver.get(repo)
        time.sleep(5)
        current_page = driver.current_url
        suffixes = ["watchers", "stargazers", "people"]
        base = current_page + "/"
        urls = [base + suffix for suffix in suffixes]
        for url in urls:
            try:
                print(url)
                baseurl = url
                time.sleep(random.randint(1, 5))
                for suffix_page in range(1, 11):
                    count = 0
                    time.sleep(random.randint(1, 10))
                    if suffix_page % 5 == 0:
                        time.sleep(10)
                    if "This repository has no more watchers" in driver.page_source:
                        break
                    url = baseurl + "?page=" + str(suffix_page)
                    driver.get(url)
                    if driver.current_url == prev_url:
                        break
                    try:
                        page_html = requests.get(url).text
                    except Exception as e:
                        print("Error getting the page html: ", e)
                    try:
                        with open("data/page.html", "w") as f:
                            f.write(page_html)
                    except Exception as e:
                        print("Error saving the page html: ", e)
                    soup = BeautifulSoup(page_html, "html.parser")
                    users = soup.find_all("a", {"class": "Link--primary"})
                    users = [user.text for user in users]
                    if not os.path.exists("data/users_dict.json"):
                        users_dict = {}
                    else:
                        with open("data/users_dict.json", "r") as f:
                            users_dict = json.load(f)
                    user_pattern = 'data-hovercard-type="user" data-hovercard-url="/users/'
                    users = []
                    if soup is not None:
                        for line in soup:
                            if user_pattern in line:
                                viable_urls.append(str(driver.current_url))
                                pattern_index = line.index(user_pattern)
                                hovercard_index = line.index("/hovercard")
                                username = line[pattern_index + len(user_pattern):hovercard_index]
                                users.append(username)
                        users_dict.update({current_page: users})
                        with open("data/users_dict.json", "w") as f:
                            json.dump(users_dict, f)
                        click_follow_buttons(driver)
                        prev_url = driver.current_url
                        if url == driver.current_url:
                            count += 1
                            if count == 5:
                                break
            except Exception as e:
                print("Error scraping the page: ", e)
        try:
            os.remove("data/page.html")
        except Exception as e:
            print("Error removing the page html: ", e)
green_light = input("Press enter to start following people on GitHub:\nNote: This indicates that you are logged in and ready for every 'follow' button to be potentially clicked. ")
driver.get("https://github.com/orgs/google/people")
print(
    "Following you now! Go crazy, but make sure to stay on GitHub until we develop this for more general use."
)
time.sleep(5)
beta_testing_background_runner = True
while True:
    if driver.current_url in url_clicks:
        if url_clicks[driver.current_url] >= 5:
            continue
        else:
            url_clicks[driver.current_url] = 0
    good_pages = data["good_pages"]
    if not beta_testing_background_runner:
        if not any(good_page in driver.current_url for good_page in good_pages):
            continue
    follow_buttons = []
    try:
        follow_buttons = driver.find_elements(
            By.CSS_SELECTOR, r"input.btn"
        )
        follow_buttons = [
            button
            for button in follow_buttons
            if button.is_displayed()
            and button.is_enabled()
            and button.get_attribute("value") == "Follow"
            and button.location["y"]
            < driver.execute_script("return window.innerHeight")
        ]
        follow_buttons[random.randint(0, len(follow_buttons) - 1)].click()
        print(f"Follow button clicked at {datetime.now()} url: {driver.current_url}")
        follow_buttons = soup.find_all("button", string="Follow")
        for button in follow_buttons:
            print(button)
        time.sleep(random.randint(6, 10))
    except ValueError as e:
        scrape_for_users(driver)
        pass
    except Exception as e:
        scrape_for_users(driver)
        pass
    if re.search("yahoo", driver.current_url):
        break
driver.close()
