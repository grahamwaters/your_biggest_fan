# create a .gitignore file in the root directory of your project
# and add the following lines to it: data/, config/, .VSCode/
import os
import json
import pip
# create a config directory in the root directory of your project
# and add a config.json file to it
# add the following lines to the config.json file:
# {
#     "github_username": "your_github_username",
#     "github_password": "your_github_password",
#     "chrome_driver_path": "path_to_your_chrome_driver"
# }
# make sure to replace the values with your own
# you can get your chrome driver from here: https://chromedriver.chromium.org/downloads
# make sure to download the version that matches your chrome browser version
# you can find your chrome browser version by going to chrome://settings/help
# and clicking on "About Chrome"
# you can also find your chrome browser version by going to chrome://version
# and clicking on "Help" in the top right corner
# you can also find your chrome browser version by going to chrome://components

if not os.path.exists("config"):
    os.makedirs("config") # create a config directory in the root directory of your project

if not os.path.exists("config/config.json"):
    with open("config/config.json", "w") as f:
        f.write('{"github_username": "your_github_username", "github_password": "your_github_password", "chrome_driver_path": "path_to_your_chrome_driver"}')

#* Create a .gitignore file in the root directory of your project that contains the following lines:
# data/
# config/
#note: the line above is critical. It is to prevent your github username and password from being uploaded to github.
# .VSCode/

# create a .gitignore file in the root directory of your project
if not os.path.exists(".gitignore"):
    with open(".gitignore", "w") as f:
        f.write('data/\n')
        f.write('config/\n')
        f.write('.VSCode/\n')

# create a data directory in the root directory of your project
# and add a url_clicks.csv file to it
# add the following lines to the url_clicks.csv file:
# URL,Clicks
if not os.path.exists("data"):
    os.makedirs("data") # create a data directory in the root directory of your project
if not os.path.exists("data/url_clicks.csv"):
    with open("data/url_clicks.csv", "w") as f:
        f.write("URL,Clicks ")

# creating assets directory
if not os.path.exists("assets"):
    os.makedirs("assets") # create an assets directory in the root directory of your project
    # this is where your chrome driver will be stored

# creating src directory
if not os.path.exists("src"):
    os.makedirs("src") # create a src directory in the root directory of your project

def install(package):
    try:
        if hasattr(pip, 'main'):
            pip.main(['install', package])
        else:
            pip._internal.main(['install', package])
    except:
        print("Failed to install package: " + package)
        quit() # quit the program if the package fails to install

# install the following packages using pip:
# pip install selenium, pip install json, pip install datetime, pip install time, pip install random

install("selenium")
install("json")
install("datetime")
install("time")
install("random")
