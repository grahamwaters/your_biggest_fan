```python
def scrape_for_users(driver):
    current_page = driver.current_url
    suffixes = ["watchers", "stargazers"]
    urls = [current_page + "/" + suffix for suffix in suffixes]
    for url in urls:
        try:
            page_html = requests.get(url).text
            soup = BeautifulSoup(page_html, "html.parser")
            users = soup.find_all("a", class_=re.compile("user"))
            with open("data/users.json", "w") as f:
                json.dump([user.text for user in users], f)
        except Exception as e:
            print("Error: ", e)
```