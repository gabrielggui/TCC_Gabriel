import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
import os

# diretório dos arquivos .json
directory = '/'

# listar todos os arquivos .json
json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json') and 'despesa' in filename.lower()]

print("Escolha uma opção:")
print("1. Analisar todos os anos")
print("2. Analisar um ano específico")

user_choice = input("Digite o número da opção escolhida: ")

years_to_analyze = set()

if user_choice == '2':
    specific_year = int(input("Digite o ano específico que deseja analisar: "))
    years_to_analyze.add(specific_year)

elif user_choice == '1':
    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for movimento in registro['registro']['listMovimentos']:
                    if 'pagamento' in movimento['tipoMovimento'].lower():
                        date = movimento['dataMovimento']
                        year = int(date.split('-')[0])
                        years_to_analyze.add(year)
else:
    print("Opção inválida. Saindo do programa.")
    exit()

categories = set()
months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
values_by_category = {}

for json_file in json_files:
    with open(os.path.join(directory, json_file), 'r') as file:
        data = json.load(file)
        for registro in data['registros']:
            for movimento in registro['registro']['listMovimentos']:
                if 'pagamento' in movimento['tipoMovimento'].lower():
                    date = movimento['dataMovimento']
                    year = int(date.split('-')[0])
                    if year in years_to_analyze:
                        month = int(date.split('-')[1])
                        value = movimento['valorMovimento']
                        category = registro['registro']['naturezaDespesa']['elemento']['denominacao']

                        if category not in categories:
                            categories.add(category)
                            values_by_category[category] = np.zeros(12)

                        values_by_category[category][month - 1] += value

category_values = list(values_by_category.values())

# criar gráfico
fig, ax = plt.subplots(figsize=(10, 6))
for i in range(len(category_values)):
    ax.bar(months, category_values[i], label=list(categories)[i], bottom=np.sum(category_values[:i], axis=0))

ax.set_xlabel('Mês')
ax.set_ylabel('Valor')
ax.set_title('Despesas Mensais por Categoria')
ax.legend(loc='upper right', bbox_to_anchor=(1.5, 1))

# formatar eixo "valor" em reais
def currency_formatter(x, pos):
    return "R${:,.2f}".format(x)

ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

plt.tight_layout()
plt.xticks(rotation=45)
plt.show()
