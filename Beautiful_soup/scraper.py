import requests
from bs4 import BeautifulSoup
import json

url = "https://meyicloud.com/"

response = requests.get(url)
if response.status_code == 200:  
    print("Successfully fetched the webpage")
else:
    print("Failed to fetch the webpage")
    exit()

soup = BeautifulSoup(response.content, "html.parser")

fetch_data = []

quotes_divs = soup.find_all("div", class_="text-wrapper")

for i in quotes_divs:  
    paragraph_tag = i.find("p", class_= "text-lg pt-35 pb-20")  
    paragraph_content = paragraph_tag.get_text(strip=True) if paragraph_tag else "N/A"
    
    heading_tag = i.find(["h1", "h2", "h3", "h4", "h5", "h6"])  
    heading_content = heading_tag.get_text(strip=True) if heading_tag else "N/A"
    
    
    fetch_data.append({
        "Paragraph": paragraph_content,
        "Heading": heading_content
    })

output_json = json.dumps(fetch_data, indent=2)

print(output_json)

