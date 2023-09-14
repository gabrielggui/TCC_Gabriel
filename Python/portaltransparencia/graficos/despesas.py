import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
from enum import Enum
import os

directory = '/home/gabriel/Área de Trabalho/TCC_Gabriel/Python/'

class TiposDeDespesa(Enum):
    APENAS_DESPESA = "despesa "
    APENAS_DESPESA_ORCAMENTARIA = "despesaOrcamentaria "
    TODAS_AS_DESPESAS = "despesa"
    
def despesa_por_mes_do_ano(user_year: int, user_month: int):
    categories = set()
    values_by_category = {}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json') and TiposDeDespesa.APENAS_DESPESA.value in filename.lower()]

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
                            value = movimento['valorMovimento']
                            category = registro['registro']['naturezaDespesa']['detalhamento']['denominacao']

                            if category not in categories:
                                categories.add(category)
                                values_by_category[category] = value
                            else:
                                values_by_category[category] += value

    sorted_categories = sorted(values_by_category.items(), key=lambda x: x[1], reverse=True)

    # Mostrar apenas as 10 maiores categorias e agrupar o restante em 'Outros'
    top_categories = sorted_categories[:10]
    other_categories = sorted_categories[10:]

    other_values = sum(category[1] for category in other_categories)
    top_categories.append(("demais despesas", other_values))

    category_labels = [category[0] for category in top_categories]
    category_values = [category[1] for category in top_categories]

    if not values_by_category:
        print("Não há valores em nenhuma das categorias para o ano e mês especificados.")
    else:
        fig, ax = plt.subplots(figsize=(10, 6))

        bar_width = 0.5
        index = np.arange(len(category_labels))

        # Cores diferentes para cada barra
        colors = plt.cm.viridis(np.linspace(0, 1, len(category_labels)))

        bars = ax.bar(index, category_values, bar_width, color=colors)

        ax.set_xlabel('Categoria')
        ax.set_ylabel('Valor')
        ax.set_title(f'Despesas de {user_month}/{user_year} por Categoria (Top 10)')
        ax.set_xticks(index)
        ax.set_xticklabels([''] * len(category_labels))  # Configura as legendas do eixo x como vazio

        # Formatar o eixo "valor" em reais
        def currency_formatter(x, pos):
            return "R${:,.2f}".format(x)

        ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

        # Criar uma legenda separada
        legend_labels = [f'{category[0]} (R$ {category[1]:,.2f})' for category in top_categories]
        plt.legend(bars, legend_labels, title='Categorias', bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.tight_layout()
        plt.show()

def despesa_acumulada_por_ano(user_year: int):
    categories = set()
    values_by_category = {}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json') and TiposDeDespesa.APENAS_DESPESA.value in filename.lower()]

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for movimento in registro['registro']['listMovimentos']:
                    if 'pagamento' in movimento['tipoMovimento'].lower():
                        date = movimento['dataMovimento']
                        year = int(date.split('-')[0])
                        
                        if year == user_year:
                            value = movimento['valorMovimento']
                            category = registro['registro']['naturezaDespesa']['detalhamento']['denominacao']

                            if category not in categories:
                                categories.add(category)
                                values_by_category[category] = value
                            else:
                                values_by_category[category] += value

    sorted_categories = sorted(values_by_category.items(), key=lambda x: x[1], reverse=True)

    # Mostrar apenas as 10 maiores categorias e agrupar o restante em 'Outros'
    top_categories = sorted_categories[:10]
    other_categories = sorted_categories[10:]

    other_values = sum(category[1] for category in other_categories)
    top_categories.append(("demais despesas", other_values))

    category_labels = [category[0] for category in top_categories]
    category_values = [category[1] for category in top_categories]

    if not values_by_category:
        print("Não há valores em nenhuma das categorias para o ano especificado.")
    else:
        fig, ax = plt.subplots(figsize=(10, 6))

        bar_width = 0.5
        index = np.arange(len(category_labels))

        # Cores diferentes para cada barra
        colors = plt.cm.viridis(np.linspace(0, 1, len(category_labels)))

        bars = ax.bar(index, category_values, bar_width, color=colors)

        ax.set_xlabel('Categoria')
        ax.set_ylabel('Valor')
        ax.set_title(f'Despesas de {user_year} por Categoria (Top 10)')
        ax.set_xticks(index)
        ax.set_xticklabels([''] * len(category_labels))  # Configura as legendas do eixo x como vazio

        # Formatar o eixo "valor" em reais
        def currency_formatter(x, pos):
            return "R${:,.2f}".format(x)

        ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

        # Criar uma legenda separada
        legend_labels = [f'{category[0]} (R$ {category[1]:,.2f})' for category in top_categories]
        plt.legend(bars, legend_labels, title='Categorias', bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.tight_layout()
        plt.show()

