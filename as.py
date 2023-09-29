import streamlit as st
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

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

def currency_formatter(x, pos):
    return "R${:,.2f}".format(x)

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
    
def execução_despesas(tipo_de_dados, user_year):
    categories = set()
    values_by_category = {}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json') and tipo_de_dados.value in filename.lower()]

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

                            if movimento['tipoMovimento'] not in categories:
                               categories.add(movimento['tipoMovimento'])
                               values_by_category[movimento['tipoMovimento']] = value
                            else:
                                values_by_category[movimento['tipoMovimento']] += value

    sorted_categories = sorted(values_by_category.items(), key=lambda x: x[1], reverse=True)

    category_labels = [category[0] for category in sorted_categories]
    category_values = [category[1] for category in sorted_categories]

    if not values_by_category:
        st.warning("Não há valores em nenhuma das categorias para o ano especificado.")
    else:
        with plt.style.context("dark_background"):
            # Criar um gráfico de barras
            fig, ax = plt.subplots(figsize=(7.2, 7.2))
            bars = ax.bar(category_labels, category_values, color=plt.cm.winter(np.linspace(0, 1, len(category_labels))))

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

    #Gráfico
    ### TEAM ###
    row4_spacer1, row4_1, row4_spacer2 = st.columns((.2, 7.1, .2))

    st.sidebar.title('Análise')
    tipo_de_dados = st.sidebar.selectbox ("Qual o tipo de dados?", list(TiposDeDados.__members__.keys()), key = 'attribute_team')
    plot_x_per_team_type = st.sidebar.selectbox ("Qual medida estatística você quer analisar?", ["Mean","Absolute","Median","Maximum","Minimum"], key = 'measure_team')
    specific_team_colors = st.sidebar.checkbox("Use team specific color scheme")

    row5_1, row5_2, row5_3  = st.columns((1, 1,1))
    with row5_1:
        st.markdown("<h4 style='text-align: center;'>Execução das despesas</h4>", unsafe_allow_html=True) 
        tipo_enum = TiposDeDados.DESPESA if tipo_de_dados == TiposDeDados.DESPESA.name else TiposDeDados.RECEITA
        execução_despesas(tipo_enum,2022)   

    with row5_2:
        tipo_enum = TiposDeDados.DESPESA if tipo_de_dados == TiposDeDados.DESPESA.name else TiposDeDados.RECEITA
        
