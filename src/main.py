# taken from another repository
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
# options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument("--no-sandbox")
options.add_argument("start-maximized")
options.add_argument("disable-infobars")  # <--- Note the option
options.add_argument("--disable-dev-shm-usage")  # <--- Note the option
options.add_argument("--remote-debugging-port=9222")  # <--- Note the port
# options.add_argument(f'user-data-dir={data["chrome_driver_path"]}') # <--- Note the f-string

driver = webdriver.Chrome(
    executable_path=data["chrome_driver_path"], chrome_options=options
)
driver.get("https://www.github.com/login")

#* Functions
@sleep_and_retry
def click_follow_buttons_v2(driver):
    """
    This function clicks the follow buttons on the page. It will click a random follow button on the page and then sleep for a random amount of time between 6 and 10 seconds. It will do this until it has clicked 30 buttons or until it has reached the bottom of the page. It will also stop if it has clicked 5 buttons on the same page.

    :param driver: _description_
    :type driver: _type_
    :param data: the data from the config file, contains the good pages to scrape
    :type data: _type_
    :return: _description_
    :rtype: _type_
    """
    while_counter = 0
    try:
        while while_counter < 40:
            follow_buttons = driver.find_elements(By.CSS_SELECTOR, "input.btn")
            follow_buttons = [button for button in follow_buttons if button.is_displayed() and button.is_enabled() and button.get_attribute("value") == "Follow" and button.location["y"] < driver.execute_script("return window.innerHeight")]
            if follow_buttons:
                follow_buttons[random.randint(0, len(follow_buttons) - 1)].click()
                print(f"Follow button clicked at {datetime.now()} url: {driver.current_url}")
                time.sleep(random.randint(6, 10))
            while_counter += 1
            if while_counter > 30:
                break
            if "This repository has no more watchers" in driver.page_source:
                break
            if while_counter > 20:
                break
    except Exception as e:
        print(e)

@sleep_and_retry
def scrape_for_users(driver):
    """
    scrape_for_users - takes a driver and scrapes the current page for users that are interested in the same things as you are and saves them to a json file in the data folder.
    :param driver: _description_
    :type driver: _type_
    """
    current_page = driver.current_url
    prev_url = None
    #^ We want to request several pages from github and scrape them for users that are interested in the same things as you are.
    #^ i.e. https://github.com/microsoft/rnx-kit
    # * first scrape - https://github.com/microsoft/rnx-kit/watchers
    # & second scrape - https://github.com/microsoft/rnx-kit/contributors
    # ! third scrape - https://github.com/microsoft/rnx-kit/stargazers

    if "people" in current_page:
        current_page = current_page.replace("/people", "")

    url_now = current_page # init
    # go to the repositories page for the company (user)
    if "repositories" in current_page:
        driver.get(current_page)
        time.sleep(5)
    else:
        print("not on the repositories page?")
        # extract the name of the company
        company_name = current_page.split("/")[-1] # i.e. microsoft
        # go to the repositories page for the company (user)
        url_now = "https://github.com/orgs/" + company_name + "/repositories"
        driver.get(url_now)
        time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    repos = soup.find_all("a", {"itemprop": "name codeRepository"})
    # get the links for the repositories
    repos = [repo["href"] for repo in repos]

    viable_urls = [] # the urls that we will scrape
    for repo in repos:
        repo = 'https://github.com' + repo
        driver.get(repo) # go to the repo
        # wait till the page loads using EC (expected conditions)
        time.sleep(5) #todo make this dynamic
        current_page = driver.current_url
        suffixes = ["watchers", "stargazers", "people"]
        base = current_page + "/"
        urls = [base + suffix for suffix in suffixes]

        #^ We want to scrape the pages for users that are interested in the same things as you are.
        for url in urls:
            try:
                print(url)
                # the suffix_page is the page that we are scraping i.e. ?page=2
                # get the first ten pages
                baseurl = url
                time.sleep(random.randint(1, 5))
                for suffix_page in range(1, 11):
                    count = 0

                    time.sleep(random.randint(1, 10))
                    # randomly sleep 10 seconds every 5 pages
                    if suffix_page % 5 == 0:
                        time.sleep(10)
                    # if the page content contains the text "This repository has no more watchers." then break
                    if "This repository has no more watchers" in driver.page_source:
                        break
                    url = baseurl + "?page=" + str(suffix_page)
                    #https://github.com/jakevdp/sklearn_tutorial/watchers?page=2
                    # navigate to the page
                    driver.get(url)
                    # wait till the page loads
                    #driver.implicitly_wait(10)
                    if driver.current_url == prev_url:
                        break
                    #*** ---- Button Clicks ---- ***#

                    #!click_follow_buttons(driver, data) # click the follow buttons
                    #note: could just save the url if the page has a "follow" button and go through those urls later in the while loop below. This would save time and clicks.
                    # save the url if the page has a "follow" button


                    #**** ---- Scrape the page for users ---- ****#
                    #^ Get the html of the page
                    try:
                        page_html = requests.get(url).text
                    except Exception as e:
                        print("Error getting the page html: ", e)

                    #^ Save the html to a file in the data folder
                    try:
                        with open("data/page.html", "w") as f:
                            f.write(page_html)
                    except Exception as e:
                        print("Error saving the page html: ", e)

                    #^ Scrape the html for users

                    soup = BeautifulSoup(page_html, "html.parser")
                    users = soup.find_all("a", {"class": "Link--primary"})
                    users = [user.text for user in users]

                    #^ Save the users to the dictionary (json) in the data folder
                    # if the users_dict does not already exist in the data folder then make it
                    if not os.path.exists("data/users_dict.json"):
                        users_dict = {}
                    else:
                        with open("data/users_dict.json", "r") as f:
                            users_dict = json.load(f)

                    # get the users from the page
                    # f4 Link--primary
                    # the usernames are between these:
                    # - data-hovercard-type="user" data-hovercard-url="/users/
                    # and
                    # - /hovercard"
                    # i.e. data-hovercard-type="user" data-hovercard-url="/users/username/hovercard"
                    user_pattern = 'data-hovercard-type="user" data-hovercard-url="/users/'
                    users = [] # will hold the usernames
                    if soup is not None:
                        # look for the pattern
                        for line in soup:
                            if user_pattern in line:
                                # get the username from the line
                                # the username is between the pattern and the /hovercard"
                                # i.e. data-hovercard-type="user" data-hovercard-url="/users/username/hovercard"
                                # so we need to get the index of the pattern and the index of the /hovercard"
                                # then we can slice the line to get the username
                                # save the url
                                viable_urls.append(str(driver.current_url))
                                pattern_index = line.index(user_pattern)
                                hovercard_index = line.index("/hovercard")
                                username = line[pattern_index + len(user_pattern):hovercard_index]
                                users.append(username) # add the username to the list of users
                        # update the dictionary of users with the new users and save it back to the csv file
                        users_dict.update({current_page: users}) # we can extract each user from the list and add them to the dictionary later
                        with open("data/users_dict.json", "w") as f:
                            json.dump(users_dict, f)
                        click_follow_buttons_v2(driver)
                        # if th url has not changed for five iterations then break
                        prev_url = driver.current_url
                        if url == driver.current_url:
                            count += 1
                            if count == 5:
                                break
            except Exception as e:
                print("Error scraping the page: ", e)
        # step 5
        try:
            os.remove("data/page.html")
        except Exception as e:
            print("Error removing the page html: ", e)

#* Main Section
# find the password field and enter the password
password = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.ID, "password"))
)
password.send_keys(data["github_password"])
# wait ten seconds for the follow buttons to load
time.sleep(random.randint(5,10))
try:
    # find the username field and enter it
    password = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "login_field"))
    )
    password.send_keys(data["github_username"])
    # find the login button and click it
    login_button = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "commit"))
    )
    login_button.click()
except Exception as e:
    print("Error finding the username field: ", e)

    green_light = input("Press enter to start following people on GitHub:\nNote: This indicates that you are logged in and ready for every 'follow' button to be potentially clicked. ")

# go to IBM people page
# driver.get("https://github.com/orgs/IBM/people")
# then https://github.com/homedepot/repositories

#driver.get("https://github.com/facebook")
#todo - https://github.com/microsoft
driver.get("https://github.com/linkedin")

print(
    "Following you now! Go crazy, but make sure to stay on GitHub until we develop this for more general use."
)
time.sleep(5)  # wait five seconds for the page to load

beta_testing_background_runner = True

while True:
    if driver.current_url in url_clicks: # if the url is in the dictionary
        if url_clicks[driver.current_url] >= 5: # if the url has been clicked 5 times
            continue # skip to the next iteration of the loop
        else:
            url_clicks[driver.current_url] = 0
    #* load good_pages from config
    good_pages = data["good_pages"] # these are strings indicating a page that is scrapable for follow buttons
    # only follow if the url contains a match from the good_pages list in the url (if not in beta testing)
    if not beta_testing_background_runner:
        if not any(good_page in driver.current_url for good_page in good_pages): # if the current url does not contain any of the good pages
            # time.sleep(3)
            continue  # skip to the next iteration of the loop
    follow_buttons = []  # init
    try:
        # Find the buttons
        follow_buttons = driver.find_elements(
            By.CSS_SELECTOR, r"input.btn"
        )  # [5].click()
        # now find the buttons that are displayed and interactable (not hidden) & also not 'Unfollow' buttons. Also, check that the button is in view currently (not scrolled off the page)
        follow_buttons = [
            button
            for button in follow_buttons
            if button.is_displayed()
            and button.is_enabled()
            and button.get_attribute("value") == "Follow"
            and button.location["y"]
            < driver.execute_script("return window.innerHeight")
        ]
        # now click one of the visible buttons
        follow_buttons[random.randint(0, len(follow_buttons) - 1)].click()
        print(f"Follow button clicked at {datetime.now()} url: {driver.current_url}")
        # wait a random amount of time between 4 and 10 seconds
        time.sleep(random.randint(4, 10))
    except ValueError as e:
        scrape_for_users(driver) # scrape the page for users links. this value error means the follow buttons list is empty and we should just skip to the next iteration of the loop
    except Exception as e:
        scrape_for_users(driver) # scrape the page for users links
    if re.search("yahoo", driver.current_url):
        break

driver.close()
