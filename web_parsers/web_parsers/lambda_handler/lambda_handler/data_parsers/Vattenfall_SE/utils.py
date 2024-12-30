import tempfile
import time
from datetime import datetime

import openpyxl
from playwright.sync_api import Page, sync_playwright

months = {
    "January": "januari",
    "February": "februari",
    "March": "mars",
    "April": "april",
    "May": "maj",
    "June": "juni",
    "July": "juli",
    "August": "augusti",
    "September": "september",
    "October": "oktober",
    "November": "november",
    "December": "december",
}


def login(page, username: str, password: str) -> None:
    """
    Logs into the Vattenfall Heat Business Portal with the provided credentials.

    Parameters:
    page (Page): The Playwright Page object used for browser interactions.
    username (str): The username for login.
    password (str): The password for login.

    Returns:
    None
    """
    login_url = "https://heatbusinessportal.vattenfall.se/Account/SignIn"
    page.goto(login_url)
    time.sleep(7)
    print(f"Logging in with username: {username}")
    page.fill("input#username", username)
    page.fill("input#password", password)
    page.click('button[type="submit"]')
    time.sleep(2)
    print("Login successful.")
    page.keyboard.press("Escape")
    time.sleep(5)


def get_point(page) -> str:
    """
    Retrieves the point value (Anläggnings-ID) from the given page.

    Parameters:
    page (Page): The Playwright Page object from which to retrieve the point value.

    Returns:
    str: The extracted point value.
    """
    try:
        accept_button = page.locator('button[class="ds-text ds-border ds-rounded-[20px] ds-px ds-py-xs"]')
        accept_button.click()
    except Exception as e:
        print("No button to accept cookies.")
        print(str(e))
    # time.sleep(10)
    # page.click("a.close", timeout=5000)
    # time.sleep(2)
    # page.click('a[routerlink="contract"]')
    # time.sleep(5)
    # point_full = page.text_content('//p[contains(text(), "Anläggnings-ID")]/following-sibling::p')
    # point = "".join(filter(str.isdigit, point_full))
    # return point

    # Code Modification
    # page.click("a[class=""]", timeout=5000)
    locator = page.locator('a.ds-hbp-menu-item[href="/report/consumption"]').nth(1)

    locator.scroll_into_view_if_needed()

    locator.click(force=True)

    print("Anchor tag clicked successfully.")




def set_dates(page, start_date: datetime, end_date: datetime) -> None:
    """
    Sets the start and end dates for data extraction on the given page.

    Parameters:
    page (Page): The Playwright Page object on which to set the dates.
    start_date (datetime): The start date to be set.
    end_date (datetime): The end date to be set.

    Returns:
    None
    """
    # time.sleep(5)
    # page.click("li.ng-star-inserted > a:nth-child(1)")
    # page.click("mat-button-toggle#mat-button-toggle-4")

    # Code Modification

    page.click('button[class = "ds-group ds-flex ds-justify-center ds-w-[62px] ds-min-h-[44px] ds-text-center ds-items-center md:ds-pl-xs md:ds-ml-xs md:ds-w-[40px]"]')
    print("DropDown button click successfully")

    page.click('label[for = "HOUR"]')
    print("Hour Click successfully")
    
    #Start Date
    # today_date = datetime.today().strftime('%Y-%m-%d')
    # print(f"Today's Date: {today_date}")

    # page.click()
    # page.fill('input#ui-input-14', today_date) 
    max_date = "2024-12-30"
    today_date = min(datetime.today(), datetime.strptime(max_date, '%Y-%m-%d')).strftime('%Y-%m-%d')
    page.locator('input#ui-input-8').fill(today_date)


    # entered_value = page.input_value('input#ui-input-8')
    # entered_value.wait_for(timeout=10000)
    # print(f"Entered Date: {entered_value}")


    # Start date
    # page.click('button[class = "ds-group ds-flex ds-justify-center ds-w-[62px] ds-min-h-[44px] ds-text-center ds-items-center md:ds-pl-xs md:ds-ml-xs md:ds-w-[40px]"]')
    # time.sleep(2)
    # page.click('//*[@id="mat-datepicker-0"]/custom-month-header/div/div/button[1]')
    # time.sleep(1)
    # page.click(f'input[pattern="{start_date.year}"]')
    # time.sleep(1)
    # page.click(f'button[aria-label="{months[month]} {start_date.year}"]')
    # time.sleep(1)
    # page.click(f'button[aria-label="{start_date.day} {months[month]} {start_date.year}"]')
    # time.sleep(1)

    # page.locator('input[data-testid="input"]').nth(0) 

    # today = datetime.strftime('2023-12-01', '%Y-%m-%d') 

    # # input_field.fill(today) 

    # print(f"Entered date: {today}")


    # End date
    # end_date = datetime.fromisoformat(end_date)
    # print("end_date", end_date)
    # month = start_date.strftime("%B")
    # page.click('input[placeholder="Slutdatum"]')
    # time.sleep(1)
    # page.click('//*[@id="mat-datepicker-1"]/custom-month-header/div/div/button[1]')
    # time.sleep(1)
    # page.click(f'button[aria-label="{end_date.year}"]')
    # time.sleep(1)
    # page.click(f'button[aria-label="{months[month]} {end_date.year}"]')
    # time.sleep(1)
    # page.click(f'button[aria-label="{end_date.day} {months[month]} {end_date.year}"]')
    # time.sleep(1)


def export_data(page: Page) -> str:
    """
    Initiates the data export process on the given page and handles the file download.

    Parameters:
    page (Page): The Playwright Page object on which to perform the export actions.

    Returns:
    str: The file path to the downloaded Excel file.
    """
    #Entry Button
    button = page.locator('button[data-track-as="5"]').nth(1)
    button.scroll_into_view_if_needed()
    button.wait_for(state="visible", timeout=5000)  
    button.click()
    print("Button clicked successfully!")

    #Another Button
    button2 = page.locator('button[class = "ds-button ds-tiny ds-no-arrow !ds-min-w-[130px] ds-pr-xs ds-pl"]').nth(1)
    button2.scroll_into_view_if_needed()
    button2.wait_for(state="visible", timeout=5000) 
    button2.click()
    print("successfully click")


    with tempfile.TemporaryDirectory() as temp_dir:
        download_path = "/tmp/consumption.xlsx"

        def handle_download(download):
            try:
                download.save_as(download_path)
                print(f"File saved successfully to: {download_path}")
            except Exception as e:
                print(f"Error saving file: {str(e)}")

        page.on("download", handle_download)


            # Ensure the button is visible
   


        # time.sleep(3)

        # page.click(
        #     'div.button-block button.mat-focus-indicator.mat-raised-button.mat-button-base.mat-secondary:has-text("Ladda ner")'
        # )
        # time.sleep(7)
        # print("File downloaded Successfully")
        return download_path


def read_file_and_transform(path: str, point: str) -> list[dict]:
    """
    Reads an Excel file and transforms the data into a structured format.

    Parameters:
    path (str): The file path to the Excel file.
    point (str): The point value to be included in the transformed data.

    Returns:
    list[dict]: A list of dictionaries containing the transformed data.
    """
    print("Starting transformation process...")
    wb = openpyxl.load_workbook(path)
    ws = wb[wb.sheetnames[0]]
    row_data = []
    data = []
    series = []
    for cells in ws.iter_rows():
        row_data.append([str(cell.value) if isinstance(cell.value, datetime) else cell.value for cell in cells])
    filtered_row_data = [row for row in row_data[2:] if any(cell is not None for cell in row)]
    if not filtered_row_data:
        return {'error':"No data found in this date"}
    for val in filtered_row_data:
        if val[0] and val[1] is not None:
            dt = datetime.strptime(str(val[5]), "%Y-%m-%d %H:%M:%S")
            value = float(val[6]) * 3600
            formatted_value = round(value, 2)
        series.append(
            {
                "duration": "1H",
                "end": f"{dt.isoformat()}+01:00",
                "value": formatted_value,
                "name": "thermal energy",
                "unit": "MJ",
            }
        )
    data.append(
        {
            "point": point,
            "timezone": "Europe/Stockholm",
            "series": series,
            "parser": "Vattenfall_Heat_SE",
            "group": "sum",
        }
    )
    print("Transformation process completed.")
    return data


def extract(username: str, password: str, start_date: datetime, end_date: datetime) -> list[dict]:
    """
    Extracts consumption data for the specified meters within the given date range.

    Parameters:
    username (str): The username for login.
    password (str): The password for login.
    start_date (datetime): The start date for data extraction.
    end_date (datetime): The end date for data extraction.
    meters (list[str]): A list of meter IDs for which data is to be extracted.

    Returns:
    list[dict]: A list of dictionaries containing the extracted data.
    """
    path = "/tmp/consumption.xlsx"
    print("Starting extraction process...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=["--disable-gpu", "--single-process", "--incognito"])
            context = browser.new_context()
            page = context.new_page()
            login(page, username, password)
            point = get_point(page)
            set_dates(page, start_date, end_date)
            export_data(page)
            page.wait_for_timeout(5000)

            browser.close()

        data = read_file_and_transform(path, point)
        if "error" in data:
            return data
        print(f"Successfully extracted the values.")
        return data
    except Exception as e:
        print(f"An error occurred during the extraction process: {e}")
        return []
