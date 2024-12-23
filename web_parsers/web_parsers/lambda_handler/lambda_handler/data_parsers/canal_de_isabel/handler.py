from typing import Any
from datetime import datetime, timedelta


# from common.hello_energy_utils import load
# from common.teams import teams_error_handler_wrapper
from data_parsers.canal_de_isabel.utils import extract, transform


# @teams_error_handler_wrapper
def run(event: dict[str, Any], context: Any) -> None:
    start_date_conf = event.get("start_date", None)
    end_date_conf = event.get("end_date", None)
    # print("hello")

    if start_date_conf:
        start_date = datetime.strptime(start_date_conf, "%Y-%m-%d")
    else:
        start_date = (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )

    if end_date_conf:
        end_date = datetime.strptime(end_date_conf, "%Y-%m-%d")
    else:
        end_date = start_date

    extracted_data = extract(start_date, end_date)
    transformed_data = transform(extracted_data)
    print(transformed_data)
    # load(transformed_data)
