import requests
from bs4 import BeautifulSoup
import json

url = "https://partners.amazonaws.com/"

# Send GET request
response = requests.get(url)
if response.status_code == 200:  
    print("Successfully fetched the webpage")
else:
    print("Failed to fetch the webpage")
    exit()

# Parse the content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

fetch_partners = []

# Inspect and find the appropriate tags containing partner data
partners = soup.find_all("div")  # Example class name; replace with the real one

# Loop through found elements to extract partner names
for i in partners:  
    # partner_tag = i.find("p", class_= "text-lg pt-35 pb-20")  
    # partner_name = partner_tag.get_text(strip=True) if i else "N/A"
    
    heading_tag = i.find(["h5"])  
    heading_content = heading_tag.get_text(strip=True) if heading_tag else "N/A"
    fetch_partners.append({
        # "Partner Name": partner_name, 
        "Heading" : heading_content
    })

# Convert extracted data to JSON format
output_json = json.dumps(fetch_partners, indent=2)

# Print the JSON output
print(output_json)
