import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
import os

directory = '/home/gabriel/Área de Trabalho/TCC_Gabriel/Python/'

json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json') and 'despesa ' in filename.lower()]

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
                        category = registro['registro']['naturezaDespesa']['detalhamento']['denominacao']

                        if category not in categories:
                            categories.add(category)
                            values_by_category[category] = np.zeros(12)

                        values_by_category[category][month - 1] += value

sorted_categories = sorted(values_by_category.items(), key=lambda x: sum(x[1]), reverse=True)

top_categories = sorted_categories[:5]
other_categories = sorted_categories[5:]

other_values = np.zeros(12)
for category, values in other_categories:
    other_values += values

top_categories.append(("Outros", other_values))

category_labels = [category[0] for category in top_categories]
category_values = [category[1] for category in top_categories]

fig, ax = plt.subplots(figsize=(10, 6))

bar_height = 0.2
index = np.arange(len(months))

bars = []

for i, (label, values) in enumerate(top_categories):
    bar = ax.barh(index + i * bar_height, values, bar_height, label=label)
    bars.append(bar)

ax.set_ylabel('Mês')
ax.set_xlabel('Valor')
ax.set_title('Despesas Mensais por Categoria')
ax.set_yticks(index + bar_height * (len(top_categories) - 1) / 2)
ax.set_yticklabels(months)
ax.legend()

# formatar eixo "valor" em reais
def currency_formatter(x, pos):
    return "R${:,.2f}".format(x)

ax.xaxis.set_major_formatter(FuncFormatter(currency_formatter))

plt.tight_layout()
plt.show()
