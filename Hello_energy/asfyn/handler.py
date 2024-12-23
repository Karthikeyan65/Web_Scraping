import calendar
import json
from datetime import datetime, timedelta
from typing import Any

# from common.aws_secrets_manager import get_secret
# from common.hello_energy_utils import load
# from common.teams import teams_error_handler_wrapper

from Hello_energy.asfyn.utils import extract, filter_data_by_date, get_access_token, transform


# @teams_error_handler_wrapper
def run(event: dict[str, Any], context: Any) -> None:

    CREDENTIALS = [
        {'username': 'data@hello-energy.com', 'password': 'w#YWet8Kstv8JfTB' }
    ]

    # he_parsers = get_secret("airflow/variables/he_parsers")
    # CREDENTIALS = json.loads(he_parsers["CREDENTIALS_DK_ASFYN"])
    asfyn_email = CREDENTIALS[0]["username"]
    asfyn_password = CREDENTIALS[0]["password"]

    access_token = get_access_token(asfyn_email, asfyn_password)

    extracted_data = extract_data(access_token, event)
    transformed_data = transform_data(extracted_data)
    # load(transformed_data)

    print(transformed_data)

def extract_data(access_token, event):
    try:
        if "start_date" in event and event["start_date"] and "end_date" in event and event["end_date"]:
            start_date = event["start_date"]
            end_date = event["end_date"]
        else:
            today = datetime.now()
            first_day_of_current_month = today.replace(day=1)
            for _ in range(2):
                first_day_of_current_month = (first_day_of_current_month - timedelta(days=1)).replace(day=1)
            first_day_of_month = first_day_of_current_month
            last_day_of_month = first_day_of_current_month.replace(
                day=calendar.monthrange(first_day_of_current_month.year, first_day_of_current_month.month)[1]
            )

            start_date = first_day_of_month.strftime("%Y-%m-%d")
            end_date = last_day_of_month.strftime("%Y-%m-%d")

        print("start_date", start_date)
        print("end_date", end_date)

        if "meter" in event and any(event["meter"]):
            meters = event["meter"]
            print("Meters:", meters)
        else:
            meters = []
            print("No meters specified")

        extracted_data = extract(access_token, start_date, end_date, meters)

        return filter_data_by_date(extracted_data, start_date, end_date)
    except Exception as e:
        print(f"Extract data error: {e}")
        raise


def transform_data(extracted_data):
    try:
        duration = "1D"
        unit = "GJ"
        parser = "Asfyn"
        group = "sum"
        transformed_data = transform(extracted_data, duration, unit, parser, group)

        return transformed_data
    except Exception as e:
        print(f"Transform data error: {e}")
        raise
