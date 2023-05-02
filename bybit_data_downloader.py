# Ryuryu's Bybit Historical Data Downloader 
# (Production Mode 6973)
# -------------------------------------
# (c) 2022 Ryan Hayabusa 
# Github: https://github.com/ryu878 
# Web: https://aadresearch.xyz/
# Discord: ryuryu#4087
# -------------------------------------
# pip install beautifulsoup4
# pip install requests

import urllib.request
import os
import re
import gzip
import time
import requests
from bs4 import BeautifulSoup


ver = '1.2:02/05/23'

# Define the base URL
base_url = 'https://public.bybit.com/trading/'

# Select the start date
start_date = '2023-01-01'

# Set the list of coins
coins = ['BTCUSDT', 'ETHUSDT']

# Create a function to download the files
def download_file(url, local_path):
    with urllib.request.urlopen(url) as response, open(local_path, 'wb') as out_file:
        data = response.read()
        out_file.write(data)

# Create a function to check if a file exists
def file_exists(local_path):
    return os.path.exists(local_path)

# Make a GET request to the base URL and parse the HTML
response = requests.get(base_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all the links on the page
links = soup.find_all('a')

# Loop through all the links
for link in links:
    # Get the href attribute of the link
    href = link.get('href')
    # Check if the href attribute is a directory
    if href.endswith('/'):
        # Get the directory name
        dir_name = href[:-1]
        # Check if the directory name is in the coins list
        if dir_name not in coins:
            continue
        # Create the directory locally if it doesn't exist
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        # Make a GET request to the directory URL and parse the HTML
        dir_url = base_url + href
        dir_response = requests.get(dir_url)
        dir_soup = BeautifulSoup(dir_response.text, 'html.parser')
        # Find all the CSV files in the directory
        csv_links = dir_soup.find_all(href=re.compile('.csv.gz$'))
        # Loop through all the CSV files
        for csv_link in csv_links:
            # Get the CSV file name
            csv_name = csv_link.text
            # Extract the date from the CSV file name
            csv_date = re.findall(r'\d{4}-\d{2}-\d{2}', csv_name)[0]
            # Check if the file is from or after the selected start date
            if csv_date >= start_date:
                # Construct the full URL of the CSV file
                csv_url = dir_url + csv_name
                # Construct the local path of the extracted file
                extracted_path = os.path.join(dir_name, csv_name[:-3])
                # Check if the extracted file exists locally
                if file_exists(extracted_path):
                    print('Skipping download of', csv_name, '- extracted file already exists.')
                else:
                    # Construct the local path of the archive file
                    archive_path = os.path.join(dir_name, csv_name)
                    # Download the archive file if it doesn't exist locally
                    if not file_exists(archive_path):
                        download_file(csv_url, archive_path)
                        print('Downloaded:', archive_path)
                        time.sleep(0.1)
                    # Check if the file is a gzip archive
                    if csv_name.endswith('.gz'):
                        # Open the gzip archive and extract the contents
                        with gzip.open(archive_path, 'rb') as f_in:
                            with open(extracted_path, 'wb') as f_out:
                                f_out.write(f_in.read())
                                print('Extracted:', extracted_path)
                        # Remove the archive file
                        os.remove(archive_path)
                        print('Removed:', archive_path)
                    else:
                        # Rename the file to remove the .csv extension
                        os.rename(archive_path, extracted_path)
                        print('Renamed:', archive_path, 'to', extracted_path)

            else:
                # Skip the file
                print('Skipping download of', csv_name, '- date is before start date.')
