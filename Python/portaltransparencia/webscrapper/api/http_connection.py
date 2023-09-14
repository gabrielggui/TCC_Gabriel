import os
import requests

BASE_URL = "https://transparencia.e-publica.net/epublica-portal/rest/assu/api/v1/"

def save_to_json_file(url, file_name):
    file_name = file_name.replace("/", "")
    file_name = "dados/" + file_name

    # Verificar se o diretório existe e criar se não existir
    directory = os.path.dirname(file_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    try:
        response = requests.get(url)
        response.raise_for_status()

        with open(file_name, "w") as file:
            file.write(response.text)

        print(f"Arquivo {file_name} criado com sucesso.")
    except Exception as e:
        print(f"Falha ao criar o arquivo {file_name}")
        print(e)

def get_api_url(tipo, period_start, period_end):
    period_start_str = period_start.strftime("%m/%Y")
    period_end_str = period_end.strftime("%m/%Y")

    return f"{BASE_URL}{tipo}?periodo_inicial={period_start_str}&periodo_final={period_end_str}&codigo_unidade=2"
