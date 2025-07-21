import csv
import os
import re
from urllib.parse import urlparse

def get_file_icon(link, file_name):
    """Returns an icon based on the file type."""
    if "youtube.com" in link or "youtu.be" in link:
        return '<i class="fab fa-youtube"></i>'
    if "box.com" in link or "box.net" in link:
        return '<i class="fas fa-archive"></i>'
    
    ext = os.path.splitext(file_name)[1].lower()
    if ext in ['.ppt', '.pptx']:
        return '<i class="fas fa-file-powerpoint"></i>'
    if ext == '.mp3':
        return '<i class="fas fa-file-audio"></i>'
    if ext == '.pdf':
        return '<i class="fas fa-file-pdf"></i>'
    return '<i class="fas fa-file"></i>'

def generate_html():
    """Generates an aesthetically pleasing HTML file from the sermons.csv data."""
    with open('sermons.csv', 'r') as f:
        reader = csv.DictReader(f)
        sermons_by_year = {}
        for row in reader:
            year = row.get('year', '').strip()
            if not year:
                page_name = row.get('page_name', '').strip()
                if page_name:
                    match = re.search(r'/(\d{4})_(\d{2})/', page_name)
                    if match:
                        year = match.group(1)
            if not year:
                file_name = row.get('file_name', '').strip()
                if file_name:
                    match = re.search(r'(\d{4})_(\d{2})', file_name)
                    if not match:
                        match = re.search(r'(\d{4})-(\d{2})', file_name)
                    if match:
                        year = match.group(1)

            if year:
                if year not in sermons_by_year:
                    sermons_by_year[year] = []
                sermons_by_year[year].append(row)

    with open('index.html', 'w') as f:
        f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LRCMC Sermon Archive</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Lato', sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4;
            color: #333;
        }
        .container {
            max-width: 900px;
            margin: auto;
            background: #fff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #e2e2e2;
            padding-bottom: 20px;
        }
        header h1 {
            margin: 0;
            color: #2c3e50;
        }
        header p {
            margin: 5px 0 0;
            color: #7f8c8d;
        }
        details {
            margin-bottom: 10px;
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        summary {
            padding: 15px;
            font-weight: bold;
            cursor: pointer;
            background-color: #ecf0f1;
            outline: none;
            font-size: 1.1em;
        }
        details[open] summary {
            background-color: #bdc3c7;
            color: #2c3e50;
        }
        .month-content {
            padding: 10px 20px;
        }
        .sermon {
            display: flex;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        .sermon:last-child {
            border-bottom: none;
        }
        .sermon i {
            margin-right: 15px;
            color: #3498db;
            width: 20px;
            text-align: center;
        }
        .sermon a {
            text-decoration: none;
            color: #2980b9;
            font-weight: 500;
        }
        .sermon a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>LRCMC Sermon Archive</h1>
            <p>A browsable archive of sermons from the London Richmond Chinese Mennonite Church.</p>
        </header>
""")
        for year in sorted(sermons_by_year.keys(), reverse=True):
            f.write(f'<details><summary>Year {year}</summary>')
            
            sermons_by_month = {}
            for sermon in sermons_by_year[year]:
                month_num = "00"
                page_name = sermon.get('page_name', '').strip()
                if page_name:
                    match = re.search(r'/(\d{4})_(\d{2})/', page_name)
                    if match: month_num = match.group(2)
                if month_num == "00":
                    file_name = sermon.get('file_name', '').strip()
                    if file_name:
                        match = re.search(r'(\d{4})_(\d{2})', file_name) or re.search(r'(\d{4})-(\d{2})', file_name)
                        if match: month_num = match.group(2)
                if sermon.get('date'):
                    month_num = sermon.get('date').strip()

                if month_num not in sermons_by_month:
                    sermons_by_month[month_num] = []
                sermons_by_month[month_num].append(sermon)

            for month_num in sorted(sermons_by_month.keys()):
                month_name = f"Month {month_num}"
                f.write(f'<div class="month-content"><details><summary>{month_name}</summary>')
                for sermon in sermons_by_month[month_num]:
                    link = sermon.get('link', '').strip()
                    file_name = sermon.get('file_name', '').strip()
                    if not file_name:
                        try:
                            file_name = os.path.basename(urlparse(link).path)
                        except Exception:
                            file_name = link
                    
                    icon = get_file_icon(link, file_name)
                    
                    f.write('<div class="sermon">')
                    if 'dropbox.com' in link:
                        local_path = os.path.join('sermons', year, month_num, file_name)
                        f.write(f'{icon}<a href="{local_path}">{file_name}</a>')
                    else:
                        f.write(f'{icon}<a href="{link}" target="_blank">{file_name}</a>')
                    f.write('</div>')
                f.write('</details></div>')
            f.write('</details>')
        f.write("""
    </div>
</body>
</html>
""")

if __name__ == '__main__':
    generate_html()