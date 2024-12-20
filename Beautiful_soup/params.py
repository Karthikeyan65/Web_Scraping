import requests
from bs4 import BeautifulSoup

url = "https://www.wrps.on.ca/Modules/NewsIncidents/Search.aspx"

params = {
    "feedId": "73a5e2dc-45fb-425f-96b9-d575355f7d4d",
    "keyword": "",
    "date": "12/18/2024",
    "page": 1
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
}

response = requests.get(url, params=params, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("div", class_="newsItem")

    if articles:
        print("Data is found...")
        for idx, article in enumerate(articles, 1):  
            
            title_tag = article.find(["h1", "h2", "h3", "h4", "h5", "h6"])
            title = title_tag.get_text(strip=True) if title_tag else "N/A"

            
            date_tag = article.find("span", class_="newsItem_PostedDate")  
            date = date_tag.get_text(strip=True) if date_tag else "N/A"

            print(f"{idx}. {title} - {date}")
    else:
        print("No articles found.")

else:
    print(f"Failed to fetch the data. Status code: {response.status_code}")
