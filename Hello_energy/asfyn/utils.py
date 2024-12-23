import time
from datetime import datetime

import requests
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.asfyn.dk/forside/"
TIME_ZONE = "Europe/Copenhagen"


def get_access_token(username, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-gpu", "--single-process"])
        page = browser.new_page()

        try:
            # Navigate to the base URL
            page.goto(BASE_URL)

            # Handle 'Accept cookies' modal
            accept_cookies = page.locator("#coi-banner-wrapper")
            if accept_cookies.is_visible():
                decline_button = page.locator("#declineButton")
                decline_button.click()
                print("Clicked 'Decline' button for cookies.")
            else:
                print("No 'Accept cookies' modal found.")

            time.sleep(2)

            # Click 'Sign in' button in the header
            signin_header_button = page.locator("#icon-navigation__size > li:nth-child(3) > button")
            signin_header_button.click()
            print("Clicked 'Sign in' button.")

            time.sleep(5)

            # Click 'Sign in with email' button
            page.click(".email-address")
            print("Clicked 'Sign in with email' button.")

            # Fill the login form
            username_field = page.locator("#input-email")
            username_field.fill(username)
            print("Entered username.")

            password_field = page.locator("#Password")
            password_field.fill(password)
            print("Entered password.")

            # Click the 'Log in' button
            login_button = page.locator("#login-form > div:nth-child(2) > form > div:nth-child(5) > button")
            login_button.click()
            print("Clicked 'Log in' button.")

            time.sleep(5)

            # Check for incorrect username or password
            error_message = page.locator("#login-form > div.alert.alert--danger")
            if error_message.is_visible():
                print("Incorrect username or password.")
                return None

            # Wait for login and retrieve cookies
            cookies = page.context.cookies()
            access_token = ""
            for c in cookies:
                if c["name"] == "sso_access_token":
                    access_token = c["value"]
                    break

            print("Access token retrieved:", access_token)
            return access_token
        finally:
            browser.close()


def _extract_date_components(date_obj):
    """
    Extracts various components such as year,
    quarter, month, week number, and day from a datetime object.

    Args:
    date_obj (datetime): A datetime object.

    Returns:
    dict: A dictionary containing the year,
    quarter, week number, month, and day.
    """
    year = date_obj.year
    month = date_obj.month
    day = date_obj.day

    # Calculating the quarter
    quarter = (month - 1) // 3 + 1

    # Calculating the week number
    week_number = date_obj.isocalendar()[1]

    return {
        "year": year,
        "quarter": quarter,
        "week": week_number,
        "month": month,
        "day": day,
    }


def get_consumption_data(headers, meter_info, year, quarter, week, month, day):
    customer_number = meter_info["customer_number"]
    meter = meter_info["meter"]
    installation = meter_info["installation"]
    url = f"https://efselfserviceapi.azurewebsites.net/api/consumptions/{customer_number}/134111/{meter}/{installation}/GJ/month"  # noqa E501

    params = {
        "year": year,
        "quarter": quarter,
        "week": week,
        "month": month,
        "day": day,
    }

    resp = requests.get(url, headers=headers, params=params)

    resp_data = resp.json()
    items = resp_data["items"]

    if items == []:
        print("No Data Available for the provided Date Range")
        return []

    extracted_data = []
    for item in items:
        day = int(item["label"])
        current_date = item["date"] + "+02:00"
        formatted_current_date = datetime.strptime(current_date, "%Y-%m-%dT%H:%M:%S%z")
        end = formatted_current_date.isoformat()

        value = item["value"]

        extracted_data.append({"end": end, "value": value})

    return extracted_data


def extract(access_token: str, start_date: str, end_date: str, meters: list[str]) -> dict[str, str]:
    headers = {
        "Authorization": "Bearer " + access_token,
        "Origin": "https://www.asfyn.dk",
        "Accept-Language": "da-DK",
    }

    customer_detail_response = requests.get(
        "https://efprofileservice.azurewebsites.net/api/customers/", headers=headers
    )

    if customer_detail_response.status_code == 200:
        customer_data = customer_detail_response.json()
        customer_number = customer_data[0]["customerNumber"]

        if customer_number:
            estates_data = requests.get(
                f"https://efselfserviceapi.azurewebsites.net/api/customers/{customer_number}/estates",
                headers=headers,
            )
            if estates_data.status_code == 200:
                estate_id = estates_data.json()[0]["id"]
                print("Estate id:", estate_id)

                product_params = {"isLarge": "false"}
                product_data = requests.get(
                    f"https://efselfserviceapi.azurewebsites.net/api/customers/{customer_number}/estates/{estate_id}/products",
                    headers=headers,
                    params=product_params,
                )
                products = product_data.json()

                meter_info = []
                print("Data Exteaction started....")
                for product in products:
                    if product["productName"] in ["Varme", "Vand"] and (not meters or product.get("meterId") in meters):

                        meter_params = {"meterId": product.get("meterId")}
                        print("meter_params", meter_params)
                        customer_meter_data = requests.get(
                            f"https://efselfserviceapi.azurewebsites.net/api/customers/{customer_number}/installations/{product['installationId']}/products",
                            headers=headers,
                            params=meter_params,
                        )
                        if customer_meter_data.status_code != 200:
                            print("No data fetched for meter", product.get("meterId"))
                        point = customer_meter_data.json()["customerMeterId"]
                        installation = product["installationId"]
                        meter = product.get("meterId")
                        data_object = {
                            "point": point,
                            "installation": installation,
                            "meter": meter,
                            "customer_number": customer_number,
                            "product_name": product["productName"],
                        }
                        meter_info.append(data_object)

                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

                extracted_data = []
                print("meter_info", meter_info)
                start_month = start_date_obj.month + start_date_obj.year * 12
                end_month = end_date_obj.month + end_date_obj.year * 12

                for month in range(start_month, end_month + 1):
                    year = month // 12
                    month_in_year = month % 12

                    if month_in_year == 0:
                        month_in_year = 12
                        year -= 1

                    first_day_of_month = datetime(year, month_in_year, 1)
                    date_components = _extract_date_components(first_day_of_month)

                    if not meter_info:
                        raise Exception("No data fetched for meters")
                    for meter in meter_info:
                        records = get_consumption_data(headers, meter, **date_components)
                        extracted_data.append(
                            {
                                "point": meter["point"],
                                "records": records,
                                "product_name": meter["product_name"],
                            }
                        )

                if not extracted_data:
                    raise Exception("No data found for the given parameters")
                print("Data Extraction completed....")
                return extracted_data


def transform(extracted_data, duration, unit, parser, group):

    transformed_data = []
    print("Data Transformation started....")
    for d in extracted_data:
        location_data = {
            "point": d["point"],
            "timezone": TIME_ZONE,
            "parser": parser,
            "group": group,
            "series": [],
        }
        for r in d["records"]:
            r["name"] = "thermal energy" if d["product_name"] == "Varme" else "water"
            r["unit"] = unit if d["product_name"] == "Varme" else "m3"
            r["duration"] = duration

            location_data["series"].append(r)

        transformed_data.append(location_data)
    print("Data Transformation completed....")
    return transformed_data


def filter_data_by_date(
    records: list[dict[str, str]], start_date_str: datetime, end_date_str: datetime
) -> list[dict[str, str]]:
    """
    Filters records based on a date range.

    Args:
        records (list of dict): A list of records, where each record is a dictionary containing an 'end' key with an ISO format date string.
        start_date_obj (datetime): The start date for the filtering range.
        end_date_obj (datetime): The end date for the filtering range.

    Returns:
        list of dict: A list of records that fall within the specified date range.
    """
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

    filtered_data = []

    for entry in records:
        filtered_records = []
        for record in entry["records"]:

            record_date = datetime.fromisoformat(record["end"]).date()
            if start_date <= record_date <= end_date:
                filtered_records.append(record)
        if filtered_records:
            filtered_data.append(
                {"point": entry["point"], "records": filtered_records, "product_name": entry["product_name"]}
            )

    return filtered_data
