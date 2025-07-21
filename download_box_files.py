import csv
import os
import requests
from urllib.parse import urlparse
import re
from bs4 import BeautifulSoup

def download_file(url, local_filename):
    """Downloads a file from a URL to a local path."""
    if os.path.exists(local_filename):
        print(f"File already exists: {local_filename}")
        return
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Downloaded: {local_filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")

def get_box_download_link(url):
    """Gets the direct download link from a Box.com page."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # This is a common pattern for Box.com download buttons, but it might not always work.
        download_button = soup.find('a', {'class': 'btn-primary'})
        if download_button and download_button.has_attr('href'):
            return download_button['href']
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
    except Exception as e:
        print(f"Error parsing {url}: {e}")
    return None

def main():
    """Main function to download sermons from Box.com."""
    with open('sermons.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            link = row.get('link', '').strip()
            if not link or ('box.com' not in link and 'box.net' not in link):
                continue

            year = row.get('year', '').strip()
            month = row.get('date', '').strip()
            file_name = row.get('file_name', '').strip()

            if not file_name:
                try:
                    file_name = os.path.basename(urlparse(link).path)
                except Exception:
                    pass

            if not year or not month:
                page_name = row.get('page_name', '').strip()
                if page_name:
                    match = re.search(r'/(\d{4})_(\d{2})/', page_name)
                    if match:
                        year = match.group(1)
                        month = match.group(2)

            if not year or not month:
                if file_name:
                    match = re.search(r'(\d{4})_(\d{2})', file_name)
                    if not match:
                        match = re.search(r'(\d{4})-(\d{2})', file_name)
                    if match:
                        year = match.group(1)
                        month = match.group(2)

            if not year or not month:
                print(f"Could not determine year/month for link: {link}")
                continue

            directory = os.path.join('sermons', year, month)
            if not os.path.exists(directory):
                os.makedirs(directory)

            download_link = get_box_download_link(link)
            if download_link:
                local_filename = os.path.join(directory, file_name)
                download_file(download_link, local_filename)
            else:
                print(f"Could not find download link for: {link}")

if __name__ == '__main__':
    main()