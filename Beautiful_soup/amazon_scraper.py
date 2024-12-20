import requests
from bs4 import BeautifulSoup
import json

url = "https://partners.amazonaws.com/"

response = requests.get(url)
if response.status_code == 200:  
    print("Successfully fetched the webpage")
else:
    print("Failed to fetch the webpage")
    exit()

soup = BeautifulSoup(response.content, "html.parser")

fetch_partners = []

partners = soup.find_all("div") 

for i in partners:  
    # partner_tag = i.find("p", class_= "text-lg pt-35 pb-20")  
    # partner_name = partner_tag.get_text(strip=True) if i else "N/A"
    
    heading_tag = i.find(["h1", "h2", "h3", "h4","h5","h6"])  
    heading_content = heading_tag.get_text(strip=True) if heading_tag else "N/A"
    fetch_partners.append({
        # "Partner Name": partner_name, 
        "Heading" : heading_content
    })

output_json = json.dumps(fetch_partners, indent=2)

print(output_json)
