from bs4 import BeautifulSoup
import requests


def main():
    response = requests.get('https://www.meyicloud.com')

    # print(soup.prettify())
     
    soup = BeautifulSoup(response.content, 'html.parser')
    specific_element = soup.find(class_="text-lg pt-35 pb-20")  
    if specific_element:
        print(specific_element.get_text())  
    else:
        print("Element with the specified ID not found.")
  
main()



