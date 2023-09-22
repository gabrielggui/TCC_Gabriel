from datetime import datetime, timedelta
from webscrapper.api.http_connection import save_to_json_file, get_api_url
from webscrapper.utils.file_utils import get_file_name

TYPES = ["receita", "despesa", "despesaOrcamentaria"]

def start_web_scrapping():
    for tipo in TYPES:
        start = datetime(datetime.now().year - 5, 1, 1)
        end = datetime.now()

        while start < end:
            period_start = start
            period_end = start + timedelta(days=364) #365 - 1

            if period_end > end:
                period_end = end

            period = f"{period_start.month} a {period_end.month} - {period_start.year}"
            file_name = get_file_name(tipo, period)

            api_url = get_api_url(tipo, period_start, period_end)

            print(f"inicio: {period_start}\nfim: {period_end}\n{api_url}")

            save_to_json_file(api_url, file_name)

            start = datetime(period_start.year + 1, 1, 1)
