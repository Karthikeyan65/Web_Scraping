from playwright.sync_api import sync_playwright
from urllib.parse import parse_qs, urlparse
from datetime import datetime, timedelta
from typing import Any

import requests
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


start_date = "2024-12-22"
end_date = "2024-12-22"

def validate(events):
    try:
        if "start_date" in events and "end_date" in events:
            start_date_str = events["start_date"]
            end_date_str = events["end_date"]
            format = "%Y-%m-%d"

            start_date = datetime.strptime(start_date_str, format)
            end_date = datetime.strptime(end_date_str, format)

            if start_date >= end_date:
                return{"Error": "start_date must be less"}
            print("Validated start_date and the end_date:",start_date_str, end_date_str)
            return {"start_date": start_date_str, "end_date": end_date_str}
        else:
            print("Start date or end date are not provided. So it take the default values will be used...")
    except ValueError as vee:
       return {"error": f"Date validation error: {vee}"}
    except Exception as e:
       return {"error": f"unexpected error in the date validation:{e}"}

def id(username, paassword):
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
    


    def extract_data(username: str, password: str, start_date: str,end_date: str, customers: list) -> dict[str]:
        print("Data Extraction is Started...")

        auth_token = id(username, password)

        extract_data = consumption_data(auth_token, start_date, end_date, customers)

        return extract_data
    

def data(raw: dict[str, Any],parser: str,group: str,duration: str,timezone: str,) -> list[dict[str, Any]]:

    transformed_date = []

    for entry_cpe in raw.values():
        cpe_number = entry_cpe.get("cpe_number")
        unit = entry_cpe.get("unit_Parameter", "kwh")
        consumption = entry_cpe.get("Consumption_Production", "consumption").lower()
        name = "active power production" if consumption == "production" else "active power"

        # cpe_series = {
        #     "end": point.get("timestamp"),
        # }

        # for point in entry_cpe.get(data, []):
