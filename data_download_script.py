import requests
import os
import time

# Base URL for the SEC EDGAR full index
base_url = 'https://www.sec.gov/Archives/edgar/full-index/'

# Function to download the file, now includes headers parameter
def download_file(url, path, headers):
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

# Prompt for start and end year
start_year = int(input("Enter the start year (YYYY): "))
end_year = int(input("Enter the end year (YYYY): "))
save_dir = input('Please Input Path to Your Directory to Download Files:')

#checking for the existence of the directory, if not, then will create new one with the name
if not os.path.exists(save_dir):
    os.makedirs(save_dir, exist_ok=True)

# Add your user-agent string here
headers = {'User-Agent': 'addyour@email.com'}

# Iterate over each year and quarter within the specified range
for year in range(start_year, end_year + 1):
    for quarter in ['QTR1', 'QTR2', 'QTR3', 'QTR4']:
        file_url = f"{base_url}{year}/{quarter}/company.idx"
        save_path = os.path.join(save_dir, f"{year}_{quarter}_company.idx")

        print(f"Attempting to download {file_url}...")

        # Make the download attempt
        try:
            download_file(file_url, save_path, headers)
            print(f"Successfully downloaded {file_url}")
        except Exception as e:
            print(f"Failed to download {file_url}. Error: {e}")

        # Respect the SEC's rate limiting
        time.sleep(1)  # Sleep for 1 second to avoid hitting rate limit

print("All requested files have been attempted to download.")
