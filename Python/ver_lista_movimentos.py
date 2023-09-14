import json
import os

directory = '/home/gabriel/Área de Trabalho/TCC_Gabriel/Python/'

json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json') and 'despesa ' in filename.lower()]

user_year = int(input("Digite o ano desejado: "))
user_month = int(input("Digite o mês desejado (1 para Janeiro, 2 para Fevereiro, etc.): "))

# Criar um conjunto para armazenar os tipos de movimento únicos
tipos_movimento = set()

for json_file in json_files:
    with open(os.path.join(directory, json_file), 'r') as file:
        data = json.load(file)
        for registro in data['registros']:
            for movimento in registro['registro']['listMovimentos']:
                if 'pagamento' in movimento['tipoMovimento'].lower():
                    date = movimento['dataMovimento']
                    year = int(date.split('-')[0])
                    month = int(date.split('-')[1])
                    
                    if year == user_year and month == user_month:
                        tipo_movimento = movimento['tipoMovimento']
                        tipos_movimento.add(tipo_movimento)

# Exibir os tipos de movimento únicos
print("Tipos de Movimento Únicos:")
for tipo in tipos_movimento:
    print(tipo)
