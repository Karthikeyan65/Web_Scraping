from playwright.sync_api import sync_playwright
from urllib.parse import parse_qs, urlparse
from datetime import datetime, timedelta
import requests
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


start_date = "2024-12-22"
end_date = "2024-12-22"

url = "https://builtrix.auth.eu-central-1.amazoncognito.com/login?client_id=3vbut4lt2ts1ae7dv8m9kuo4f3&response_type=token&scope=email+openid+phone&redirect_uri=https%3A%2F%2Fexample.com%2Fcallback"
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=70)
    page = browser.new_page()
    page.goto(url)
    print("Page loaded successfully...")
    page.locator('input#signInFormUsername').nth(1).fill('data@hello-energy.com')
    page.locator('input#signInFormPassword').nth(1).fill('d&|UN+PX]3X8')
    button = page.locator('input[type = submit]').nth(1).click()

    page.wait_for_url("**/*", timeout=1200000)
    final_link = page.url
    print(final_link)
    print("Login Successfully...") 
    browser.close()

    # Seperate the ID_token in the 
    fragment = urlparse(final_link).fragment
    params = parse_qs(fragment)
    id_token = params.get("id_token", [None])[0]
    print("ID_TOKEN:", id_token)

    def split_date(start_date: str, end_date: str, max_day: int = 31 ) -> list[tuple[str, str]]:
        format = "%Y-%m-%d"
        start = datetime.strptime(start_date, format)
        end = datetime.strptime(end_date, format)

        available = []

        curr_start = start
        while curr_start < end:
            curr_end = min(curr_start + timedelta(days = max_day - 1), end)
            available.append((curr_start.strftime(format), curr_end.strftime(format)))
            curr_start = curr_end + timedelta(days=1)
        print("**************************")
        print("Format",available)
            # return available
    # result = split_date('2024-12-01', '2024-12-31')
    # print(result)

    def consumption_data(auth_token: str, start_date: str, end_date: str, customers: list) -> dict:
        api_url = "https://api.builtrix.tech/get-consumption-data"
        headers = {"auth-token": f"Bearer {auth_token}"}
        consolidated_data = {}

        date_chunks = split_date(start_date, end_date)

        for customer in customers:
            cpe_number, nif = customer.get("cpe_number"), customer.get("nif")
            if not cpe_number or not nif:
                continue

            customer_data = {"cpe_number": cpe_number, "data": []}

            for chunk_start, chunk_end in date_chunks:
                params = {"start_date": chunk_start, "end_date": chunk_end, "cpe_number": cpe_number, "nif": nif}
                try:
                    response = requests.get(api_url, headers=headers, params=params).json()
                    if response.get("statusCode") == 200:
                        customer_data["data"].extend(response["body"].get("data", []))
                    elif response.get("statusCode") == 404:
                        break
                    else:
                        raise Exception(response.get("body", "Unknown error"))
                except Exception as e:
                    break

            if customer_data["data"]:
                consolidated_data[cpe_number] = customer_data

        return consolidated_data or {"error": "No data retrieved."}

