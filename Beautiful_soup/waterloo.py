import requests
from bs4 import BeautifulSoup

# Base URL
url = "https://www.wrps.on.ca/Modules/NewsIncidents/Search.aspx"

# Parameters for the GET request
params = {
    "feedId": "73a5e2dc-45fb-425f-96b9-d575355f7d4d",
    "keyword": "",
    "date": "12/18/2024",  # Your desired date
    "page": 1              # Desired page number
}

# Headers to mimic a browser request (important to avoid blocks)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
}

# Send an HTTP GET request with params and headers
response = requests.get(url, params=params, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract data from the response (modify based on the page structure)
    # For example: Find all news articles or incidents in specific tags or classes
    articles = soup.find_all("div", class_="news-item")  # Replace with actual HTML structure
    
    if articles:
        print("Data found:")
        for idx, article in enumerate(articles, 1):
            # Example: Extracting title and date
            title = article.find("h3").get_text(strip=True) if article.find("h3") else "No title"
            date = article.find("span", class_="news-date").get_text(strip=True) if article.find("span", class_="news-date") else "No date"
            
            print(f"{idx}. {title} - {date}")
    else:
        print("No articles found for the given parameters.")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
