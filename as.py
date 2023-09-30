import streamlit as st
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import squarify

from matplotlib.ticker import FuncFormatter
from enum import Enum

class TiposDeDados(Enum):
    DESPESA = "despesa -"
    RECEITA = "receita -"

class MedidasEstatisticas(Enum):
    MEDIA = "despesa -"
    RECEITA = "receita -"

# Substitua 'directory' pelo caminho real do seu diretório
directory = 'dados/'
custom_colors = ['#e68728', '#0c5922', '#dd4477', '#6633cc', '#5981d3', '#334278']


def currency_formatter(x, pos):
    return "R${:,.2f}".format(x)

def format_legend_label(label, max_line_length=50):
    if len(label) > max_line_length:
        parts = label.split()
        formatted_label = ""
        line_length = 0
        for part in parts:
            if line_length + len(part) <= max_line_length:
                formatted_label += part + " "
                line_length += len(part) + 1
            else:
                formatted_label = formatted_label.rstrip()
                formatted_label += "\n" + part + " "
                line_length = len(part) + 1
        return formatted_label.rstrip()
    else:
        return label

def despesas_por_area(user_year):
    categories = set()
    values_by_category = {}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json' if user_year == 0 else f'{user_year}.json') and TiposDeDados.DESPESA.value in filename.lower()]

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for movimento in registro['registro']['listMovimentos']:
                    if ('Pagamento de empenho' == movimento['tipoMovimento'] or 'Pagamento de restos a pagar' == movimento['tipoMovimento']):
                        date = movimento['dataMovimento']
                        value = movimento['valorMovimento']

                        tipo_movimento = registro['registro']['despesa']['funcao']['denominacao']

                        if tipo_movimento not in categories:
                            categories.add(tipo_movimento)
                            values_by_category[tipo_movimento] = value
                        else:
                            values_by_category[tipo_movimento] += value

    sorted_categories = sorted(values_by_category.items(), key=lambda x: x[1], reverse=True)

    # Mostrar apenas as 10 maiores categorias e agrupar o restante em 'Outros'
    top_categories = sorted_categories[:5]
    other_categories = sorted_categories[5:]

    other_values = sum(category[1] for category in other_categories)
    top_categories.append(("Outros", other_values))

    category_labels = [format_legend_label(category[0]) for category in top_categories]
    category_values = [category[1] for category in top_categories]

    if not values_by_category:
        st.warning("Não há valores em nenhuma das categorias para o ano especificado.")
    else:
        with plt.style.context("dark_background"):

            # Criar um gráfico de treemap
            fig, ax = plt.subplots(figsize=(15, 5))
            squarify.plot(sizes=category_values, label=[f'{label}\n{currency_formatter(value, None)}\n({(value/sum(category_values)*100):.1f}%)' for label, value in zip(category_labels, category_values)], color=custom_colors, alpha=0.8)

            # Exibir o gráfico no Streamlit
            st.pyplot(fig)

def categorias_economicas(user_year):
    categories = set()
    values_by_category = {}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json' if user_year == 0 else f'{user_year}.json') and TiposDeDados.DESPESA.value in filename.lower()]

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for movimento in registro['registro']['listMovimentos']:
                    if ('Pagamento de empenho' == movimento['tipoMovimento'] or 'Pagamento de restos a pagar' == movimento['tipoMovimento']):
                        date = movimento['dataMovimento']
                        value = movimento['valorMovimento']

                        tipo_movimento = registro['registro']['naturezaDespesa']['categoriaEconomica']['denominacao']

                        if tipo_movimento not in categories:
                            categories.add(tipo_movimento)
                            values_by_category[tipo_movimento] = value
                        else:
                            values_by_category[tipo_movimento] += value

    sorted_categories = sorted(values_by_category.items(), key=lambda x: x[1], reverse=True)

    category_labels = [category[0] for category in sorted_categories]
    category_values = [category[1] for category in sorted_categories]

    if not values_by_category:
        st.warning("Não há valores em nenhuma das categorias para o ano especificado.")
    else:
        with plt.style.context("dark_background"):
            custom_colors = ['#dd3d77', '#3265FF', '#FFBF00']
            # Criar um gráfico de pizza
            fig, ax = plt.subplots(figsize=(7.2, 7.2))
            ax.pie(category_values, labels=[f'{label}\n{currency_formatter(value, None)}' for label, value in zip(category_labels, category_values)], autopct='%1.1f%%', startangle=90, colors=custom_colors)

            # Exibir o gráfico no Streamlit
            st.pyplot(fig)

def execução_restos_a_pagar(user_year):
    categories = set()
    values_by_category = {}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json' if user_year == 0 else f'{user_year}.json') and TiposDeDados.DESPESA.value in filename.lower()]

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for movimento in registro['registro']['listMovimentos']:
                    if (movimento['tipoMovimento'] == 'Pagamento de restos a pagar' 
                        or 'Cancelamento de restos a pagar' in movimento['tipoMovimento']):
                        date = movimento['dataMovimento']
                        year = int(date.split('-')[0])
                        
                        if year == user_year or user_year == 0:
                            value = movimento['valorMovimento']

                            if movimento['tipoMovimento'] == 'Pagamento de restos a pagar':
                                tipo_movimento = 'Valor pago'                             
                            elif 'Cancelamento de restos a pagar' in movimento['tipoMovimento']:
                                tipo_movimento = 'Valor cancelado'

                            if tipo_movimento not in categories:
                               categories.add(tipo_movimento)
                               values_by_category[tipo_movimento] = value
                            else:
                                values_by_category[tipo_movimento] += value

    sorted_categories = sorted(values_by_category.items(), key=lambda x: x[1], reverse=True)

    category_labels = [category[0] for category in sorted_categories]
    category_values = [category[1] for category in sorted_categories]

    if not values_by_category:
        st.warning("Não há valores em nenhuma das categorias para o ano especificado.")
    else:
        with plt.style.context("dark_background"):
            # Criar um gráfico de barras
            fig, ax = plt.subplots(figsize=(7.2, 7.2))
            bars = ax.bar(category_labels, category_values, color=custom_colors)

            ax.set_xlabel('Categoria')
            ax.set_ylabel('Valor')

            # Adicionar valores nas barras com formatação de moeda
            formatter = FuncFormatter(currency_formatter)
            ax.yaxis.set_major_formatter(formatter)

            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, yval + 500, currency_formatter(yval, None), ha='center', va='bottom', color='white')

            plt.tight_layout()

            # Exibir o gráfico no Streamlit
            st.pyplot(fig)

def execução_despesas(user_year):
    categories = set()
    values_by_category = {}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json' if user_year == 0 else f'{user_year}.json') and TiposDeDados.DESPESA.value in filename.lower()]

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for movimento in registro['registro']['listMovimentos']:
                    if (movimento['tipoMovimento'] == 'Emissão de empenho' 
                        or movimento['tipoMovimento'] == 'Liquidação de empenho'
                        or movimento['tipoMovimento'] == 'Pagamento de empenho'):
                        date = movimento['dataMovimento']
                        year = int(date.split('-')[0])
                        
                        if year == user_year or user_year == 0:
                            value = movimento['valorMovimento']

                            if movimento['tipoMovimento'] == 'Emissão de empenho':
                                tipo_movimento = 'Empenhado'                             
                            elif movimento['tipoMovimento'] == 'Liquidação de empenho':
                                tipo_movimento = 'Liquidado'                             
                            elif movimento['tipoMovimento'] == 'Pagamento de empenho':
                                tipo_movimento = 'Pago' 

                            if tipo_movimento not in categories:
                               categories.add(tipo_movimento)
                               values_by_category[tipo_movimento] = value
                            else:
                                values_by_category[tipo_movimento] += value

    sorted_categories = sorted(values_by_category.items(), key=lambda x: x[1], reverse=True)

    category_labels = [category[0] for category in sorted_categories]
    category_values = [category[1] for category in sorted_categories]

    if not values_by_category:
        st.warning("Não há valores em nenhuma das categorias para o ano especificado.")
    else:
        with plt.style.context("dark_background"):
            # Criar um gráfico de barras
            fig, ax = plt.subplots(figsize=(7.2, 7.2))
            bars = ax.bar(category_labels, category_values, color=custom_colors)

            ax.set_xlabel('Categoria')
            ax.set_ylabel('Valor')

            # Adicionar valores nas barras com formatação de moeda
            formatter = FuncFormatter(currency_formatter)
            ax.yaxis.set_major_formatter(formatter)

            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, yval + 500, currency_formatter(yval, None), ha='center', va='bottom', color='white')

            plt.tight_layout()

            # Exibir o gráfico no Streamlit
            st.pyplot(fig)

 
if __name__ == "__main__":
    st.set_page_config(page_title="Dados Abertos - Prefeitura de Assú/RN", layout="wide")

    st.warning("Observação: o conjunto de dados usado neste protótipo contém apenas dados entre janeiro de 2021 e setembro de 2023.")   

    #Título
    row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns((.1, 2.3, .1, .35, .1))
    with row0_1:
        st.title("Dados Abertos - Receitas e Despesas")
        st.subheader("Prefeitura de Assú/RN")
    with row0_2:
        st.text('')
        st.text('')
        st.image("Python/img/bandeira.png", use_column_width=True)

    st.markdown("---")

    st.markdown("<h2 style='text-align: center;'>Visão Geral</h2>", unsafe_allow_html=True) 

    #SIDEBAR
    row4_spacer1, row4_1, row4_spacer2 = st.columns((.2, 7.1, .2))

    st.sidebar.title('Análise')
    tipo_de_dados = st.sidebar.selectbox ("Qual o tipo de dados?", list(TiposDeDados.__members__.keys()), key = 'attribute_team')
    ano = st.sidebar.selectbox ("Qual ano você quer analisar?", ["Todos", 2023, 2022, 2021], key = 'measure_team')
    specific_team_colors = st.sidebar.checkbox("Use team specific color scheme")

    #SEC1
    row5_1, row5_2, row5_3= st.columns((1, 1, 1))
    with row5_1:
        st.markdown("<h5 style='text-align: center;'>Execução das despesas no ano</h5>", unsafe_allow_html=True)   

    with row5_2:
        st.markdown("<h5 style='text-align: center;'>Despesas por categoria econômica</h5>", unsafe_allow_html=True) 
        
    with row5_3:
        st.markdown("<h5 style='text-align: center;'>Execução dos compromissos de anos anteriores (restos a pagar)</h5>", unsafe_allow_html=True) 
        
    row5_1_1, row5_2_1, row5_3_1 = st.columns((1, 1, 1))
    with row5_1_1:
        tipo_enum = TiposDeDados.DESPESA if tipo_de_dados == TiposDeDados.DESPESA.name else TiposDeDados.RECEITA
        execução_despesas(0 if ano == "Todos" else ano)   

    with row5_2_1:
        tipo_enum = TiposDeDados.DESPESA if tipo_de_dados == TiposDeDados.DESPESA.name else TiposDeDados.RECEITA
        categorias_economicas(0 if ano == "Todos" else ano)

    with row5_3_1:
        tipo_enum = TiposDeDados.DESPESA if tipo_de_dados == TiposDeDados.DESPESA.name else TiposDeDados.RECEITA
        execução_restos_a_pagar(0 if ano == "Todos" else ano)

    st.markdown("---")

    #SEC2
    st.markdown("<h2 style='text-align: center;'>Pagamento de despesas por área de atuação (função)</h2>", unsafe_allow_html=True) 

    despesas_por_area(0 if ano == "Todos" else ano)

    st.markdown("---")

    st.markdown("<h2 style='text-align: center;'>Execução da despesa por área de atuação (função)</h2>", unsafe_allow_html=True) 