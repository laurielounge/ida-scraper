import requests
from bs4 import BeautifulSoup

# URL of the page you want to scrape
url = "https://au.vushstimulation.com/"

# Request the page content
response = requests.get(url)

# Parse the content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Extract the main <title> tag
main_title = soup.find('title')
main_title_text = main_title.get_text() if main_title else None

# Count the main title (if it exists)
title_count = 1 if main_title else 0

# Extract meta tags with OpenGraph and Twitter titles
og_title = soup.find('meta', property='og:title')
twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})

# Check if the titles are different from the main title to avoid double-counting
if og_title and og_title['content'] != main_title_text:
    title_count += 1
if twitter_title and twitter_title['content'] != main_title_text:
    title_count += 1

# Now, let's print the details
print(f"Main Title: {main_title_text}")
print(f"OpenGraph Title: {og_title['content'] if og_title else 'None'}")
print(f"Twitter Title: {twitter_title['content'] if twitter_title else 'None'}")
print(f"Title Count: {title_count}")

# Optional: Debug by checking all elements with the "title" tag and the <meta> tags
all_titles = soup.find_all('title')
meta_titles = soup.find_all('meta', attrs={'property': 'og:title'})
meta_titles += soup.find_all('meta', attrs={'name': 'twitter:title'})
print(f"\nAll relevant titles (main + meta): {len(all_titles) + len(meta_titles)}")
