import requests
from bs4 import BeautifulSoup
import os
from time import sleep
from tqdm import tqdm

# Headers for the HTTP request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}

# Read PMC IDs from the file
with open('PMCids.txt', 'r') as file:
    ids = file.readlines()

# Iterate over the PMC IDs
for u in tqdm(ids):
    pmc_id = u.strip()
    url = f'https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/'
    response = requests.get(url, headers=headers, timeout=10)
    sleep(10)  # Rate limiting
    
    if response.status_code == 200:
        try:
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            supple_tag = soup.find(class_='supplementary-materials')

            # Check if supplementary materials exist
            if supple_tag:
                # Create a folder for the current PMC ID
                cur_dir = os.getcwd()
                folder = os.path.join(cur_dir, 'Downloaded files', pmc_id)
                os.makedirs(folder, exist_ok=True)
                
                # Iterate over supplementary links and download files
                for supp in supple_tag.find_all('a'):
                    supple_link = 'https://pmc.ncbi.nlm.nih.gov' + supp['href']
                    file_name = os.path.basename(supple_link)
                    file_path = os.path.join(folder, file_name)
                    
                    supp_response = requests.get(supple_link, headers=headers)
                    if supp_response.status_code == 200:
                        with open(file_path, 'wb') as file:
                            file.write(supp_response.content)

                    # Log the supplementary file link
                    with open('data.csv', 'a') as log_file:
                        log_file.write(f"{pmc_id},{supple_link}\n")
            else:
                # Log if no supplementary file is available
                with open('data.csv', 'a') as log_file:
                    log_file.write(f"{pmc_id},No supplementary file found\n")
        except Exception as e:
            with open('data.csv', 'a') as log_file:
                log_file.write(f"{pmc_id},Error: {str(e)}\n")
    else:
        with open('data.csv', 'a') as log_file:
            log_file.write(f"{pmc_id},Failed to fetch page\n")
