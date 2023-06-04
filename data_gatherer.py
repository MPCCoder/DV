import requests
from bs4 import BeautifulSoup
import pandas as pd

# Base URL of the web page
base_url = "https://spacelaunchnow.me/launch/"

# Define the User-Agent header to simulate Chrome
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

# Loop through the pages and download each one
dfs = []
for page_number in range(1, 276):  # Download first 5 pages
    # Construct the URL for the current page
    url = f"{base_url}?page={page_number}"

    # Make a GET request to the URL
    response = requests.get(url, headers=headers)

    # Parse the HTML content of the response
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the table element in the HTML content
    table = soup.find("table")
    df = pd.read_html(str(table))[0]
    dfs.append(df)
    print(page_number)

# Concatenate the DataFrames into a single one
result = pd.concat(dfs)

# Print the result DataFrame
print(result)

# Save the result DataFrame to an Excel file
result.to_excel("output.xlsx", index=False)

# Print a message to confirm that the file was saved
print("Data saved to output.xlsx.")