# ## Route 2. Simple if it works - Requests running based on user's current page and visible links.
# This option would watch for certain links (specifically links like "141 watching" or "https://github.com/microsoft/SynapseML/graphs/contributors" and request the html of the resulting pages. This would provide the user with a list of pages, and their subsequent HTML files. Why do we want these? Great question.
# The pages have users that you could connect with and chances are, if you're looking at `OpenCV` because you're interested in computer vision, the other people that are ... stanning `OpenCV` are probably interested in computer vision too. So, you could follow them and they could follow you back. This is a great way to build a network of people that are interested in the same things as you.

# # TODO
# - [ ] Add a background runner that will run in the background and not interfere with your normal browsing.
# - [ ] Add a background runner that will watch for certain links (specifically links like "141 watching" and the longer ones.
# - [ ] Create a list of strings to watch for in urls on the page and add those to the config file.

# # Layout of a Repository
# Places we want to look to find users that share our interests:
# 1. The "Watchers" tab (people that are watching the repo) - These are likely to be active coders that are interested in the repo.
# 2. The "Contributors" tab (people that have contributed to the repo) - These ARE active coders that are interested in the repo and have worked on it.
# 3. The "Stargazers" tab (people that starred the repo) - People that may be just like you... watching the repo and interested in it.

# ## an example:
# *https://github.com/microsoft/SynapseML/stargazers*

# The pages we want are:
# 1. https://github.com/microsoft/SynapseML/watchers
#    1. https://github.com/microsoft/SynapseML/watchers?page=2 (and so on)
# 2. https://github.com/microsoft/SynapseML/network/members
#    1. on this page you can find the users that created forks
#       1.  at the css selector: #network > div > div:nth-child(3) > a:nth-child(3)
#       2.  or by looking for urls on the page that lead to profiles (links with just https://github.com/ + some_username_suffix like `iamausername`)
# 3. https://github.com/microsoft/SynapseML/stargazers
#    1. https://github.com/microsoft/SynapseML/stargazers?page=2 (and so on)

import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os

from main import driver




def scrape_for_users(driver):
    """
    scrape_for_users - takes a driver and scrapes the current page for users that are interested in the same things as you are and saves them to a json file in the data folder.
    :param driver: _description_
    :type driver: _type_
    """
    current_page = driver.current_url

    # Get the links from the current page
    links = driver.find_elements_by_tag_name("a")

    # Now find the links that fit the criteria listed above in the layout of a repository section
    # 1. The "Watchers" tab (people that are watching the repo) - These are likely to be active coders that are interested in the repo.
    # 2. The "Contributors" tab (people that have contributed to the repo) - These ARE active coders that are interested in the repo and have worked on it.
    # 3. The "Stargazers" tab (people that starred the repo) - People that may be just like you... watching the repo and interested in it.

    watcher_pages = []
    contributor_pages = []
    stargazer_pages = []

    for link in links:
        href = link.get_attribute("href")
        if href is not None:
            if "watchers" in href:
                watcher_pages.append(href)
            elif "contributors" in href: #todo - this is not technically accurate, see the examples above. Needs to be worked out.
                contributor_pages.append(href)
            elif "stargazers" in href:
                stargazer_pages.append(href)


    # Now we have a list of pages that we want to scrape for users.
    # Tier one users are those that have contributed to the repo, they should be the first ones we look at.
    # Tier two users are those that are watching the repo, they should be the second ones we look at.
    # Tier three users are those that have starred the repo, they should be the third ones we look at.

    # Now we need to scrape the pages for users.
    # We will use the same method as in route1.py

    # get each page's html (one at a time) save the file to the data folder and then scrape the page for users.
    # then once we have all the users, we can save them to a file and then we can use them to follow them.
    # we can remove the html file now. We don't need it anymore.

    # follow these directions and write the code
    # 1. get the html of the page
    # 2. save the html to a file in the data folder
    # 3. scrape the html for users
    # 4. save the users to the dictionary (json) in the data folder
    # 5. remove the html file

    # step 1
    try:
        page_html = requests.get(current_page).text
    except Exception as e:
        print("Error getting the page html: ", e)

    # step 2
    try:
        with open("data/page.html", "w") as f:
            f.write(page_html)
    except Exception as e:
        print("Error saving the page html: ", e)

    # step 3 & 4
    soup = BeautifulSoup(page_html, "html.parser")

    # if the users_dict does not already exist in the data folder then make it
    if not os.path.exists("data/users_dict.json"):
        users_dict = {}
        with open("data/users_dict.json", "w") as f:
            json.dump(users_dict, f)
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
                pattern_index = line.index(user_pattern)
                hovercard_index = line.index("/hovercard")
                username = line[pattern_index + len(user_pattern):hovercard_index]
                users.append(username) # add the username to the list of users
        # update the dictionary of users with the new users and save it back to the csv file
        users_dict.update({current_page: users}) # we can extract each user from the list and add them to the dictionary later
        with open("data/users_dict.json", "w") as f:
            json.dump(users_dict, f)

    # step 5
    try:
        os.remove("data/page.html")
    except Exception as e:
        print("Error removing the page html: ", e)
