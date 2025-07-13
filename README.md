
# Sermon Links Archive

This project contains a collection of links to sermons from the lrcmc.ca website. The links were gathered automatically by a script and are saved in the `sermons.csv` file.

## What's in the `sermons.csv` file?

The `sermons.csv` file is a spreadsheet that lists all the sermon media that was found. It includes the following information for each sermon:

- **page_name:** The web page where the sermon link was found.
- **year:** The year of the sermon.
- **date:** The month of the sermon.
- **link:** The direct link to the sermon file (e.g., a PowerPoint presentation, an audio file, or a YouTube video).
- **file_name:** The name of the sermon file, if available.

## How was this information collected?

The `scraper.py` script was used to automatically visit the lrcmc.ca website and collect all the sermon links. This script is what gathered the information and saved it into the `sermons.csv` file.
