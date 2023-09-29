import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.ticker import FuncFormatter
import os

directory = 'dados/'

def format_legend_label(label, max_line_length=50):
    # Função para formatar a legenda
    if len(label) > max_line_length:
        parts = label.split()
        formatted_label = ""
        line_length = 0
        for part in parts:
            if line_length + len(part) <= max_line_length:
                formatted_label += part + " "
                line_length += len(part) + 1
            else:
                formatted_label = formatted_label.rstrip()  # Remove espaços em branco à direita
                formatted_label += "\n" + part + " "
                line_length = len(part) + 1
        return formatted_label.rstrip()
    else:
        return label

def receita_acumulada_de_um_ano(user_year: int):
    categories = set()
    values_by_category = {}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json') and "receita" in filename.lower()]

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for movimento in registro['registro']['listMovimentos']:
                    if 'arrecadação' in movimento['tipoMovimento'].lower():
                        date = movimento['dataMovimento']
                        year = int(date.split('-')[0])

                        if year == user_year:
                            value = movimento['valorMovimento']
                            category = registro['registro']['naturezaReceita']['alinea']['denominacao']

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
    top_categories.append(("Demais receitas", other_values))

    category_labels = [category[0] for category in top_categories]
    category_values = [category[1] for category in top_categories]

    if not values_by_category:
        print("Não há valores em nenhuma das categorias para o ano especificado.")
    else:
        fig, ax = plt.subplots(figsize=(11, 6))

        bar_width = 0.5
        index = np.arange(len(category_labels))

        # Cores diferentes para cada barra
        colors = plt.cm.viridis(np.linspace(0, 1, len(category_labels)))

        bars = ax.bar(index, category_values, bar_width, color=colors)

        ax.set_xlabel('Categoria')
        ax.set_ylabel('Valor')
        ax.set_title(f'Receitas de {user_year} por Categoria (Top 10)')
        ax.set_xticks(index)
        ax.set_xticklabels([''] * len(category_labels))  # Configura as legendas do eixo x como vazio

        # Formatar o eixo "valor" em reais
        def currency_formatter(x, pos):
            return "R${:,.2f}".format(x)

        ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

        # Anotar as porcentagens nas barras
        total = sum(category_values)
        for i, v in enumerate(category_values):
            percentage = (v / total) * 100
            ax.annotate(f"{percentage:.1f}%", (i, v), ha='center', va='bottom')

        # Criar uma legenda separada
        legend_labels = [format_legend_label(f'{category[0]} (R$ {category[1]:,.2f})') for category in top_categories]
        plt.legend(bars, legend_labels, title='Categorias', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='large')

        plt.tight_layout()
        salvar_grafico(f'RecAcum_{user_year}.png')
        plt.show()

def receita_dos_12_meses_de_um_ano(user_year: int):

    categories = set()
    values_by_category = {month: {} for month in range(1, 13)}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json') and "receita" in filename.lower()]

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for movimento in registro['registro']['listMovimentos']:
                    if 'arrecadação' in movimento['tipoMovimento'].lower():
                        date = movimento['dataMovimento']
                        year, month, _ = map(int, date.split('-'))
                        
                        if year == user_year:
                            value = movimento['valorMovimento']
                            category = registro['registro']['naturezaReceita']['alinea']['denominacao']

                            if category not in categories:
                                categories.add(category)
                                for month_num in range(1, 13):
                                    values_by_category[month_num][category] = 0

                            values_by_category[month][category] += value

    # Organizar os valores em um formato adequado para o gráfico de barras empilhadas
    stacked_data = [[] for _ in range(12)]

    for month in range(1, 13):
        category_values = [(category, values_by_category[month][category]) for category in categories]
        category_values.sort(key=lambda x: x[1], reverse=True)

        top_categories = category_values[:9]
        other_value = sum([value for _, value in category_values[9:]])

        for i, category in enumerate(top_categories):
            stacked_data[month - 1].append(category[1])

        stacked_data[month - 1].append(other_value)

    month_labels = [f'Mês {month}' for month in range(1, 13)]
    category_labels = [category[0] for category in top_categories] + ['demais despesas']

    fig, ax = plt.subplots(figsize=(12, 8))

    bar_width = 0.7
    index = np.arange(len(month_labels))

    bars = []
    bottom = np.zeros(len(month_labels))

    for i, category in enumerate(category_labels):
        bar = ax.bar(index, [data[i] for data in stacked_data], bar_width, label=category, bottom=bottom)
        bars.append(bar)
        bottom += np.array([data[i] for data in stacked_data])

    ax.set_xlabel('Mês')
    ax.set_ylabel('Valor')
    ax.set_title(f'Despesas dos 12 meses de {user_year}')
    ax.set_xticks(index)
    ax.set_xticklabels(month_labels)
    ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1))

    def currency_formatter(x, pos):
        return "R${:,.2f}".format(x)

    ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

    plt.tight_layout()

    salvar_grafico(f'Receita12Meses_{user_year}.png')

    plt.show()

def salvar_grafico(nome_do_arquivo: str):

    output_directory = "img/"

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    output_file_path = os.path.join(output_directory, nome_do_arquivo)
    plt.savefig(output_file_path)

def lista_de_receitas(user_year: int):
    categories = set()
    values_by_category = {}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json') and "receita" in filename.lower()]
    tipo_movimento_list = []

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                    movimentos = registro.get("registro", {}).get("listMovimentos", [])
                    for movimento in movimentos:
                        tipo_movimento_list.append({"Tipo de Movimento": movimento.get("tipoMovimento")})

    # Criar DataFrame
    df = pd.DataFrame(tipo_movimento_list)

    # Exibir a tabela
    print(df)

lista_de_receitas(2023)