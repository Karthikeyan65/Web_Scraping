import json
from datetime import datetime, timedelta
from typing import Any

# from common.aws_secrets_manager import get_secret
# from common.hello_energy_utils import load
# from common.teams import teams_error_handler_wrapper
from data_parsers.Vattenfall_SE.utils import extract


# @teams_error_handler_wrapper
def run(event: dict[str, Any], context: Any) -> None:
    print(event)
    extracted_data = extract_data(event)
    if extracted_data:
        transformed_data = transform(extracted_data)
        # load(transformed_data)
        print(transformed_data)


def extract_data(event: dict[str, Any]):
    try:
        if "start_date" in event and event["start_date"] and "end_date" in event and event["end_date"]:
                start_date = event["start_date"]
                end_date = event["end_date"]
        else:
            start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
            end_date = start_date

        

        print("Start Date:", start_date)
        print("End Date:", end_date)

        if "meter" in event and event["meter"]:
            meters = event["meter"]
        else:
            meters = []

        # he_parsers = get_secret("airflow/variables/he_parsers")
        # CREDENTIALS = json.loads(he_parsers["CREDENTIALS_SE_VATTENFALL_HEAT"])

        CREDENTIALS = [
    {
        "username": "jonas.karlsson@newsec.se",
        "password": "Sommar2022*"
    }
]

        all_extracted_data = []
        
        for credentials in CREDENTIALS:
            username = credentials["username"]
            password = credentials["password"]
        
            try:
                user_data = extract(username, password, start_date, end_date)
                if "error" in user_data:
                    raise ValueError(user_data["error"])
                all_extracted_data.append(user_data)
            except Exception as e:
                error_message = f"Error for user {username}: {str(e)}"
                print(error_message)
                continue
            
            print(f"Extracting data for user: {username}")  
            
        if all_extracted_data:
            return all_extracted_data
        else:
            raise ValueError("No data extracted for this date range")
    except Exception as e:
        print(f"Extract process error: {e}")




def transform(extracted_data):
    try:
        flattened_data = [entry for sublist in extracted_data for entry in sublist]
        if not flattened_data:
            raise ValueError("Transformed data is empty")
        return flattened_data
    except Exception as e:
        print(f"Transform data error: {e}")
        raise