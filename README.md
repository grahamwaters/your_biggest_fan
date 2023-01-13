# your_biggest_fan
A friendly background bot to follow you across the internet and just press those follow buttons every couple minutes.

# Setup
1. Clone this repo
2. Run the `setup.py` script to setup the folders and initial config file. This will also install the required dependencies.
3. Edit the `config.json` file to your liking.
   1. Include your GitHub username and password in this file if you are trying to set up auto-login.
   2. Else -> You will have to manually login to GitHub every time you run the script.
4. Run the `main.py` script to start the background bot, then just browse the pages on Github that interest you and the bot will follow you around and press the follow buttons for you every so often to indicate to those users that you are interested in their work. It's that simple.

# Background Runner

## Route 1. Painful - An actual window running in the background
The background runner opens a headless window that mirrors the first one you open. This is so that the bot can run in the background and not interfere with your normal browsing. The background runner will also automatically close when you close the first window.
Here are the things that the background runner will support:
- [x] Auto-login (captcha is a challenge here)
- [ ] etc.

## Route 2. Simple if it works - Requests running based on user's current page and visible links.
This option would watch for certain links (specifically links like "141 watching" or "https://github.com/microsoft/SynapseML/graphs/contributors" and request the html of the resulting pages. This would provide the user with a list of pages, and their subsequent HTML files. Why do we want these? Great question.
The pages have users that you could connect with and chances are, if you're looking at `OpenCV` because you're interested in computer vision, the other people that are ... stanning `OpenCV` are probably interested in computer vision too. So, you could follow them and they could follow you back. This is a great way to build a network of people that are interested in the same things as you.

# TODO
- [ ] Add a background runner that will run in the background and not interfere with your normal browsing.
- [ ] Add a background runner that will watch for certain links (specifically links like "141 watching" and the longer ones.
- [ ] Create a list of strings to watch for in urls on the page and add those to the config file.

# Layout of a Repository
Places we want to look to find users that share our interests:
1. The "Watchers" tab (people that are watching the repo) - These are likely to be active coders that are interested in the repo.
2. The "Contributors" tab (people that have contributed to the repo) - These ARE active coders that are interested in the repo and have worked on it.
3. The "Stargazers" tab (people that starred the repo) - People that may be just like you... watching the repo and interested in it.

## an example:
*https://github.com/microsoft/SynapseML/stargazers*

The pages we want are:
1. https://github.com/microsoft/SynapseML/watchers
   1. https://github.com/microsoft/SynapseML/watchers?page=2 (and so on)
2. https://github.com/microsoft/SynapseML/network/members
   1. on this page you can find the users that created forks
      1.  at the css selector: #network > div > div:nth-child(3) > a:nth-child(3)
      2.  or by looking for urls on the page that lead to profiles (links with just https://github.com/ + some_username_suffix like `iamausername`)
3. https://github.com/microsoft/SynapseML/stargazers
   1. https://github.com/microsoft/SynapseML/stargazers?page=2 (and so on)
