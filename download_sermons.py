import csv
import os
import requests
from urllib.parse import urlparse
import re

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

def main():
    """Main function to download sermons."""
    if not os.path.exists('sermons'):
        os.makedirs('sermons')

    with open('sermons.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            link = row.get('link', '').strip()
            if not link:
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
                # Try to get year and month from the page_name
                page_name = row.get('page_name', '').strip()
                if page_name:
                    match = re.search(r'/(\d{4})_(\d{2})/', page_name)
                    if match:
                        year = match.group(1)
                        month = match.group(2)

            if not year or not month:
                # Try to get year and month from the filename
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

            # Create directory structure
            directory = os.path.join('sermons', year, month)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Download file
            if 'dropbox.com' in link and ('?dl=1' in link or '?dl=' in link):
                if not file_name:
                    try:
                        file_name = os.path.basename(urlparse(link).path)
                    except Exception:
                        print(f"Could not determine filename for link: {link}")
                        continue
                
                # Sanitize filename
                file_name = "".join(c for c in file_name if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()
                
                # Add extension if missing
                if not any(file_name.endswith(ext) for ext in ['.mp3', '.pptx', '.ppt', '.pdf']):
                    if 'ppt' in file_name.lower():
                        file_name += '.pptx'
                    elif 'mp3' in file_name.lower():
                        file_name += '.mp3'


                local_filename = os.path.join(directory, file_name)
                download_file(link, local_filename)

if __name__ == '__main__':
    main()