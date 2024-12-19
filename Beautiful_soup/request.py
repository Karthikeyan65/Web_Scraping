import requests
url = "https://www.hindustantimes.com/ht-img/img/2024/08/22/550x309/Vijay_1724323776656_1724323777017.jpg"

headers = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
response = requests.get(url = url, headers= headers)

img = response.content

f = open("Vijay_1724323776656_1724323777017.jpg", "wb")
f.write(img)