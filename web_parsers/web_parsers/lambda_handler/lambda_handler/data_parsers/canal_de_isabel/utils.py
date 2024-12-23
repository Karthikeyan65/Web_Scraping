import json
import re
from datetime import datetime
from io import BytesIO
from typing import Any
# import chompjs
from bs4 import BeautifulSoup

import pandas as pd
import pytz
import requests
from playwright.sync_api import Page, sync_playwright, Request, Route
from playwright_recaptcha import recaptchav2

from common.aws_secrets_manager import get_secret

BASE_URL = "https://oficinavirtual.canaldeisabelsegunda.es"
PARSER = "Canal de Isabel"
GROUP = "sum"
TIME_ZONE = "Europe/Madrid"
DURATION = "1H"
NAME = "water"
UNIT = "dm3"


def _convert_to_madrid_time(date_str: str) -> str:
    date_obj = datetime.strptime(date_str, "%d/%m/%Y %H")
    berlin_timezone = pytz.timezone(TIME_ZONE)

    return berlin_timezone.localize(date_obj).isoformat()


raw_html_container = []


def extract_data(
    start_date: str,
    end_date: str,
    username: str,
    password: str,
) -> list[str]:

    def wait_for_all_xhr(page: Page) -> None:
        try:
            with page.expect_event("requestfinished"):
                with page.expect_event("requestfailed"):
                    pass
        except:
            pass

    with sync_playwright() as p:

        chromium = p.chromium
        browser = chromium.launch(headless=True, args=["--disable-gpu", "--single-process"])
        context = browser.new_context()
        page = context.new_page()

        page.goto(f"{BASE_URL}")
        page.wait_for_load_state("networkidle")
        try:
            accept_button = page.locator('button[id="CybotCookiebotDialogBodyButtonDecline"]')
            accept_button.click()
        except Exception as e:
            print("No button to accept cookies.")
            print(str(e))

        print("Attempting login.")
        enterBttn = page.locator('button[class="btn btn-blue"][id="btnEntrar"]')
        enterBttn.click()

        empresaBttn = page.locator('label[for="radioEmpresaLoginDesktop"]')
        empresaBttn.click()

        page.select_option("#tipoDocumento", "NIE")

        page.locator('input[id="numeroDocumento"]').fill(username)
        page.locator('input[type="password"]').fill(password)
        loginbttn = page.locator('button[id="btLogin"]')
        loginbttn.click()

        # with recaptchav2.SyncSolver(page) as solver:
        #     token = solver.solve_recaptcha(wait=True)

        wait_for_all_xhr(page)

        print("Login Completed.")

        page.goto(f"{BASE_URL}/group/ovir/consumo", timeout=120000)

        contract_divs = page.locator('div[class="btn-filter-wrapper"]')
        point = ""
        count = contract_divs.count()
        for i in range(count):
            text = contract_divs.nth(i).text_content()
            if "Contador" in text:
                point = re.sub(r"Contador|\s+", "", text)        
        print(point)
        print("class is loading...")


        wait_for_all_xhr(page)

        filter_button = page.locator('button[id="activarFiltro"]').nth(0).click()

        page.select_option("#selectPeriodicidad", "Horaria")

        page.locator('input[id="fechaDesde1"]').fill(start_date)
        page.locator('input[id="fechaHasta1"]').fill(end_date)

        filter_data_button = page.locator('button[id="btnFiltrar1"]')

        global raw_html_container
        raw_html_container = []

        page.route("**", lambda route, request: handle_route(route, request))

        filter_data_button.click()
        while True:
            wait_for_all_xhr(page)
            if raw_html_container:
                # Parse the raw HTML content using Beautiful Soup
                soup = BeautifulSoup(raw_html_container[0], 'html.parser')

                # Find the script tag containing the JavaScript data
                script_tag = soup.find('script', text=lambda t: t and 'dataJsonConsumo' in t)

                if script_tag:
                    # Extract the JavaScript content from the script tag
                    script_content = script_tag.string

                    # Extract JSON data from the JavaScript variable
                    json_data = script_content.split("dataJsonConsumo = ")[-1].split(";\n")[0]

                    # Parse JSON data
                    data = json.loads(json_data)

                    # Return parsed content
                    return {"content": data["rows"], "point": point}

            # Return empty response if no data found
            return {"content": [], "point": point}


def handle_route(route: Route, request: Request) -> None:
    if "/group/ovir/consumo?p_p_id" in request.url and request.method == "POST" and request.post_data:
        global raw_html_container
        url = request.url
        headers = {key: value for key, value in request.headers.items()}
        cookies = headers.get("Cookie", "")
        form_data = request.post_data

        response = requests.post(url, data=form_data, headers=headers, cookies=cookies)
        raw_html_container.append(response.text)

        route.abort()
    else:
        route.continue_()


def transform(extracted_data: list[dict]) -> list[dict[str, str]]:

    transformed_data = []

    for data in extracted_data:
        point = data["point"]
        records = []
        for entry in data["content"]:
            c = entry["c"]
            date_str = c[0]["v"].strip()
            value = c[1]["v"]

            if len(date_str) > 6 and date_str[0].isalpha():
                currDate = date_str[2:12]
                date_str = currDate + " " + date_str[13:15]
            else:
                date_str = currDate + " " + date_str[:-1]

            date_time = _convert_to_madrid_time(date_str)
            records.append({"end": date_time, "value": value, "duration": DURATION, "name": NAME, "unit": UNIT})

        transformed_data.append(
            [{"point": point, "timezone": TIME_ZONE, "parser": PARSER, "group": GROUP, "series": records}]
        )

    return transformed_data


def extract(start_date: str, end_date: str) -> list[dict[str, Any]]:
    # he_parsers = get_secret("airflow/variables/he_parsers")
    # creds = json.loads(he_parsers["CREDENTIALS_ES_CANAL_DE_ISABEL"])
    creds = [{"username": "Y4191133H", "password": "Limehome2023!"}]

    print(f"Start date: {start_date}")
    print(f"End date: {end_date}")

    extracted_data = []

    for cred in creds:
        extracted_data.append(extract_data(start_date, end_date, cred["username"], cred["password"]))

    return extracted_data
