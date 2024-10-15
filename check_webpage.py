import requests
from bs4 import BeautifulSoup

# URL of the page you want to scrape
# url = "https://au.vushstimulation.com/products/bound-nipple-clamps-rubber-caps-rose-gold-metal-with-linking-chain-set-of-2"
url = "https://au.vushstimulation.com/products/femme-funn-unda"

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

# Extract <h1> tags
h1_tags = soup.find_all('h1')
h1_texts = [h1.get_text().strip() for h1 in h1_tags]

# Extract the meta description
meta_description = soup.find('meta', attrs={'name': 'description'})
meta_description_content = meta_description['content'] if meta_description else None

# Now, let's print the details
print(f"Main Title: {main_title_text}")
print(f"OpenGraph Title: {og_title['content'] if og_title else 'None'}")
print(f"Twitter Title: {twitter_title['content'] if twitter_title else 'None'}")
print(f"Title Count: {title_count}")

# Print the h1 tags
print(f"\nH1 Tags ({len(h1_tags)} found):")
for i, h1_text in enumerate(h1_texts, 1):
    print(f"H1-{i}: {h1_text}")

# Print the meta description
print(f"\nMeta Description: {meta_description_content}")

# Optional: Debug by checking all elements with the "title" tag and the <meta> tags
all_titles = soup.find_all('title')
meta_titles = soup.find_all('meta', attrs={'property': 'og:title'})
meta_titles += soup.find_all('meta', attrs={'name': 'twitter:title'})
print(f"\nAll relevant titles (main + meta): {len(all_titles) + len(meta_titles)}")
