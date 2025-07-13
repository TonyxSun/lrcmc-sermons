
import requests
from bs4 import BeautifulSoup
import csv
import re
from urllib.parse import urljoin, urlparse
import time
import gc

# Disable SSL warnings for this specific case
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def get_soup(url, retries=3, delay=5):
    """Fetches a URL and returns a BeautifulSoup object with retries, handling encoding correctly."""
    for i in range(retries):
        try:
            with requests.get(url, verify=False, timeout=15, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                response.raise_for_status()
                # Use apparent_encoding to let requests guess the encoding.
                response.encoding = response.apparent_encoding
                # Pass the decoded text to BeautifulSoup
                return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    print(f"Failed to fetch {url} after {retries} retries.")
    return None

def scrape_links_from_soup(soup, url, writer):
    """Scrapes the media links from a given soup object and writes them to the csv."""
    if not soup:
        return

    print(f"Scraping {url}...")
    
    # Extract year and month from the URL
    match = re.search(r'/(\d{4})_(\d{2})/', url)
    year, month = (match.groups() if match else (None, None))

    # Find PowerPoint links
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)
        if any(ext in href.lower() for ext in ['.ppt', '.pptx']) or any(ext in text.lower() for ext in ['.ppt', '.pptx']):
            link = urljoin(url, href)
            writer.writerow({'page_name': url, 'year': year, 'date': month, 'link': link, 'file_name': text})

    # Find audio links
    for audio in soup.find_all('audio'):
        source = audio.find('source', src=True)
        if source and '.mp3' in source['src'].lower():
            link = urljoin(url, source['src'])
            writer.writerow({'page_name': url, 'year': year, 'date': month, 'link': link, 'file_name': ''})

    # Find YouTube embeds
    for iframe in soup.find_all('iframe', src=True):
        if 'youtube-nocookie.com/embed/' in iframe['src']:
            src = iframe['src']
            if src.startswith('//'):
                link = 'https' + src
            else:
                link = urljoin(url, src)
            writer.writerow({'page_name': url, 'year': year, 'date': month, 'link': link, 'file_name': ''})

def main():
    """Main function to crawl the site and scrape data."""
    base_url = 'https://lrcmc.ca/sunday-sermon/'
    
    with open('sermons.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['page_name', 'year', 'date', 'link', 'file_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        urls_to_visit = [base_url]
        visited_urls = set()

        while urls_to_visit:
            url = urls_to_visit.pop(0)
            if url in visited_urls:
                continue

            soup = get_soup(url)
            if not soup:
                continue
            
            visited_urls.add(url)
            scrape_links_from_soup(soup, url, writer)
            
            # Find sub-pages to scrape from the current page
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                if not href:
                    continue
                
                full_url = urljoin(url, href)
                
                # Check if the link is a subdirectory of the base url
                if full_url.startswith(base_url) and full_url != base_url and full_url.endswith('/'):
                    if full_url not in visited_urls:
                        urls_to_visit.append(full_url)

            del soup
            gc.collect()
            time.sleep(2) # Add a 2-second delay between requests

    print("Scraping complete. Data saved to sermons.csv")

if __name__ == '__main__':
    main()
