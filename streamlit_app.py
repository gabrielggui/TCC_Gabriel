from time import strptime
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter
import locale
import numpy as np
import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px
from datetime import datetime
from enum import Enum

class TiposDeDados(Enum):
    DESPESA = "despesa -"
    RECEITA = "receita -"

class CategoriasDespesa(Enum):
    OUTROS_SERVICOS_TERCEIROS = "Outros Serviços de Terceiros - Pessoa Jurídica"
    MATERIAL_DE_CONSUMO = "Material de Consumo"

# Substitua 'directory' pelo caminho real do seu diretório
directory = 'dados/'
custom_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#e68728', '#0c5922', '#dd4477', '#6633cc', '#5981d3', '#334278']


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
    
def formatar_moeda(valor):
    return locale.currency(valor, grouping=True)
    
def categorias_economicas_receita(user_year):
    categories = set()
    values_by_category = {}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json' if user_year == 0 else f'{user_year}.json') and TiposDeDados.RECEITA.value in filename.lower()]

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for movimento in registro['registro']['listMovimentos']:
                    if ('Arrecadação de receita' == movimento['tipoMovimento']):
                        value = movimento['valorMovimento']

                        tipo_movimento = registro['registro']['naturezaReceita']['categoriaEconomica']['denominacao']

                        if tipo_movimento not in categories:
                            categories.add(tipo_movimento)
                            values_by_category[tipo_movimento] = value
                        else:
                            values_by_category[tipo_movimento] += value
    # Criar um DataFrame do pandas
    df = pd.DataFrame(list(values_by_category.items()), columns=['Categoria', 'Valor'])
    # Formatar os valores para reais
    df['Valor Formatado'] = df['Valor'].apply(formatar_moeda)
    # Criar gráfico de barras horizontais usando Plotly
    fig = px.bar(df, x='Valor', y='Categoria', orientation='h', text='Valor Formatado')
    fig.update_traces(marker_color=custom_colors)

    # Exibir gráfico
    st.plotly_chart(fig, use_container_width=True)


def receitas_por_especie(user_year):
    categories = set()
    values_by_category = {}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json' if user_year == 0 else f'{user_year}.json') and TiposDeDados.RECEITA.value in filename.lower()]

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for movimento in registro['registro']['listMovimentos']:
                    if ('Arrecadação de receita' == movimento['tipoMovimento']):
                        value = movimento['valorMovimento']

                        tipo_movimento = registro['registro']['naturezaReceita']['especie']['denominacao']

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

    category_labels = [f'{label}<br>{formatar_moeda(value)}<br>({(value/sum(category_values)*100):.1f}%)' for label, value in zip(category_labels, category_values)]

    df = pd.DataFrame(list(zip(category_labels, category_values)), columns =['category_labels', 'category_values'])

    if not values_by_category:
        st.warning("Não há valores em nenhuma das categorias para o ano especificado.")
    else:
        # Criar um gráfico de treemap
        fig = px.treemap(df, path=['category_labels'], values='category_values', color_discrete_sequence=custom_colors)
        fig.update_layout(font=dict(size=19))
        
        st.plotly_chart(fig, use_container_width=True)

def receita_12meses(user_year: int):
    categories = set()
    values_by_category = {month: {} for month in range(1, 13)}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json' if user_year == 0 else f'{user_year}.json') and TiposDeDados.RECEITA.value in filename.lower()]

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for movimento in registro['registro']['listMovimentos']:
                    if ('Arrecadação de receita' == movimento['tipoMovimento']):
                        date = movimento['dataMovimento']
                        year, month, _ = map(int, date.split('-'))
                        
                        if year == user_year:
                            value = movimento['valorMovimento']
                            category = registro['registro']['naturezaReceita']['especie']['denominacao']

                            if category not in categories:
                                categories.add(category)
                                for month_num in range(1, 13):
                                    values_by_category[month_num][category] = 0
    
                            values_by_category[month][category] += value
    data = []
    for month, category_values in values_by_category.items():
        for category, value in category_values.items():
            data.append({
                'Mês': month,
                'Categoria': category,
                'Valor': value
            })

    # Crie o DataFrame
    df = pd.DataFrame(data)
    df = df.sort_values(by='Valor', ascending=False)

    # Criar um gráfico de barras empilhadas com Plotly Express
    fig = px.bar(df, x='Mês', y='Valor', color='Categoria',
                labels={'Valor': 'Valor', 'Categoria': 'Categoria'})

    # Adicione um rótulo informativo ao eixo Y
    fig.update_yaxes(title_text='Valor (R$)')

    # Formatando o texto que aparece ao passar o mouse sobre as barras
    fig.update_traces(hovertemplate='R$ %{y:,.2f}')

    total_por_categoria = df['Valor'].sum()


    st.markdown(f'<h6 style=\'text-align: center;\'>Valor total: {locale.currency(total_por_categoria, grouping=True)}</h6>', unsafe_allow_html=True) 
    # Exiba o gráfico no Streamlit

    # Formatando o eixo x como moeda em reais
    fig.update_layout(yaxis_tickformat='$,.2f')
    st.plotly_chart(fig, use_container_width=True)

def boxplot_despesa_dos_12_meses_de_um_ano(user_year: int, categoria_despesa):
    categories = set()
    values_by_category = {month: {} for month in range(1, 13)}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json' if user_year == 0 else f'{user_year}.json') and TiposDeDados.DESPESA.value in filename.lower()]

    top_expenses = []  # Lista para armazenar as 100 maiores despesas

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for empenho_item in registro['registro']['listEmpenhoItens']:
                    emissao = registro['registro']['empenho']['emissao']
                    year, month, _ = map(int, emissao.split('-'))

                    category = registro['registro']['naturezaDespesa']['elemento']['denominacao']

                    if ((year == user_year or user_year == 0) and category == categoria_despesa):
                        value = empenho_item['quantidade'] * empenho_item['valorUnitario']

                        if value != 0:
                            if category not in categories:
                                categories.add(category)
                                for month_num in range(1, 13):
                                    values_by_category[month_num][category] = []

                            values_by_category[month][category].append(value)

                                # Adicionar à lista de despesas para tabela
                            top_expenses.append({
                                'Categoria': category,
                                'Denominação do Empenho': empenho_item['denominacao'],
                                'Emissão': datetime.strptime(emissao, "%Y-%m-%d").strftime("%d/%m/%Y"),
                                'Quantidade': empenho_item['quantidade'],
                                'Valor unitário': empenho_item['valorUnitario'],
                                'Valor total': value
                            })

    # Organizar os valores em um formato adequado para o gráfico de box plot
    data = {
        'Mês': [],
        'Categoria': [],
        'Valor': []
    }

    for month in range(1, 13):
        for category, values in values_by_category[month].items():
            for value in values:
                data['Mês'].append(month)
                data['Categoria'].append(category)
                data['Valor'].append(value)

    df = pd.DataFrame(data)

    # Criar um gráfico de box plot com Plotly Express
    fig = px.box(df, x='Mês', y='Valor', color='Categoria',
                 labels={'Valor': 'Valor', 'Mês': 'Mês', 'Categoria': 'Categoria'},
                 height=700,log_y=True)

    fig.update_traces(hovertemplate='R$ %{y:,.2f}')
    fig.update_layout(yaxis_tickformat="R$,2f")
    fig.update_yaxes(type="log", tickvals=[1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7], ticktext=["R$10,00", "R$100,00", "R$1.000,00", "R$10.000,00", "R$100.000,00", "R$1.000.000,00", "R$10.000.000,00"])

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<h2 style='text-align: center;'>Maiores despesas empenhadas no período</h2>", unsafe_allow_html=True) 
    st.markdown("<h6 style='text-align: center;'>As 50 (vinte) maiores despesas empenhadas no período</h6>", unsafe_allow_html=True) 
    # Exibir a tabela com as 100 maiores despesas
    if top_expenses:
        top_expenses_df = pd.DataFrame(top_expenses)
        top_expenses_df = top_expenses_df.sort_values(by='Valor total', ascending=False).head(50)

        # Formatar valores como reais na tabela
        formatted_df = top_expenses_df.copy()
        formatted_df['Valor total'] = formatted_df['Valor total'].apply(formatar_moeda)
        formatted_df['Valor unitário'] = formatted_df['Valor unitário'].apply(formatar_moeda)
        formatted_df['Quantidade'] = formatted_df['Quantidade'].apply(lambda x: f'{x:.2f}')

        st.table(formatted_df)
    else:
        st.warning("Não há despesas para o ano especificado.")


def despesa_12meses(user_year: int):
    categories = set()
    values_by_category = {month: {} for month in range(1, 13)}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json' if user_year == 0 else f'{user_year}.json') and TiposDeDados.DESPESA.value in filename.lower()]

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for movimento in registro['registro']['listMovimentos']:
                    if ('Pagamento de empenho' == movimento['tipoMovimento'] or 'Pagamento de restos a pagar' == movimento['tipoMovimento']):
                        date = movimento['dataMovimento']
                        year, month, _ = map(int, date.split('-'))
                        
                        if year == user_year:
                            value = movimento['valorMovimento']
                            category = registro['registro']['naturezaDespesa']['elemento']['denominacao']

                            if category not in categories:
                                categories.add(category)
                                for month_num in range(1, 13):
                                    values_by_category[month_num][category] = 0
    
                            values_by_category[month][category] += value
    data = []
    for month, category_values in values_by_category.items():
        for category, value in category_values.items():
            data.append({
                'Mês': month,
                'Categoria': category,
                'Valor': value
            })

    # Crie o DataFrame
    df = pd.DataFrame(data)
    df = df.sort_values(by='Valor', ascending=False)

    # Criar um gráfico de barras empilhadas com Plotly Express
    fig = px.bar(df, x='Mês', y='Valor', color='Categoria',
                labels={'Valor': 'Valor', 'Categoria': 'Categoria'})

    # Adicione um rótulo informativo ao eixo Y
    fig.update_yaxes(title_text='Valor (R$)')

    # Formatando o texto que aparece ao passar o mouse sobre as barras
    fig.update_traces(hovertemplate='R$ %{y:,.2f}')

    total_por_categoria = df['Valor'].sum()


    st.markdown(f'<h6 style=\'text-align: center;\'>Valor total: {locale.currency(total_por_categoria, grouping=True)}</h6>', unsafe_allow_html=True) 
    # Exiba o gráfico no Streamlit

    # Formatando o eixo x como moeda em reais
    fig.update_layout(yaxis_tickformat='$,.2f')
    st.plotly_chart(fig, use_container_width=True)

def despesas_por_grupo(user_year):
    categories = set()
    values_by_category = {}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json' if user_year == 0 else f'{user_year}.json') and TiposDeDados.DESPESA.value in filename.lower()]

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for movimento in registro['registro']['listMovimentos']:
                    if ('Pagamento de empenho' == movimento['tipoMovimento'] or 'Pagamento de restos a pagar' == movimento['tipoMovimento']):
                        value = movimento['valorMovimento']

                        tipo_movimento = registro['registro']['naturezaDespesa']['grupo']['denominacao']

                        if tipo_movimento not in categories:
                            categories.add(tipo_movimento)
                            values_by_category[tipo_movimento] = value
                        else:
                            values_by_category[tipo_movimento] += value

    sorted_categories = sorted(values_by_category.items(), key=lambda x: x[1], reverse=True)

    # Mostrar apenas as 10 maiores categorias e agrupar o restante em 'Outros'
    top_categories = sorted_categories[:3]
    other_categories = sorted_categories[3:]

    other_values = sum(category[1] for category in other_categories)
    top_categories.append(("Outros", other_values))

    category_labels = [format_legend_label(category[0]) for category in top_categories]
    category_values = [category[1] for category in top_categories]

    category_labels = [f'{label}<br>{formatar_moeda(value)}<br>({(value/sum(category_values)*100):.1f}%)' for label, value in zip(category_labels, category_values)]

    df = pd.DataFrame(list(zip(category_labels, category_values)), columns =['category_labels', 'category_values'])

    if not values_by_category:
        st.warning("Não há valores em nenhuma das categorias para o ano especificado.")
    else:
        # Criar um gráfico de treemap
        fig = px.treemap(df, path=['category_labels'], values='category_values', color_discrete_sequence=custom_colors)
        fig.update_layout(font=dict(size=17))
        
        st.plotly_chart(fig, use_container_width=True)

def despesas_por_secretaria(user_year):
    categories = set()
    values_by_category = {}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json' if user_year == 0 else f'{user_year}.json') and TiposDeDados.DESPESA.value in filename.lower()]

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for movimento in registro['registro']['listMovimentos']:
                    if ('Pagamento de empenho' == movimento['tipoMovimento'] or 'Pagamento de restos a pagar' == movimento['tipoMovimento']):
                        value = movimento['valorMovimento']

                        tipo_movimento = registro['registro']['unidadeOrcamentaria']['denominacao']

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

    category_labels = [f'{label}<br>{formatar_moeda(value)}<br>({(value/sum(category_values)*100):.1f}%)' for label, value in zip(category_labels, category_values)]

    df = pd.DataFrame(list(zip(category_labels, category_values)), columns =['category_labels', 'category_values'])

    if not values_by_category:
        st.warning("Não há valores em nenhuma das categorias para o ano especificado.")
    else:
        # Criar um gráfico de treemap
        fig = px.treemap(df, path=['category_labels'], values='category_values', color_discrete_sequence=custom_colors)
        fig.update_layout(font=dict(size=17))
        
        st.plotly_chart(fig, use_container_width=True)

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

    category_labels = [f'{label}<br>{formatar_moeda(value)}<br>({(value/sum(category_values)*100):.1f}%)' for label, value in zip(category_labels, category_values)]

    df = pd.DataFrame(list(zip(category_labels, category_values)), columns =['category_labels', 'category_values'])

    if not values_by_category:
        st.warning("Não há valores em nenhuma das categorias para o ano especificado.")
    else:
        # Criar um gráfico de treemap
        fig = px.treemap(df, path=['category_labels'], values='category_values', color_discrete_sequence=custom_colors)
        fig.update_layout(font=dict(size=17))
        
        st.plotly_chart(fig, use_container_width=True)


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
        # Create a pie chart using Plotly
        fig = px.pie(
            names=category_labels,
            values=category_values,
            labels={'value': 'Valor'},
            title=f'Despesas por categoria econômica',
            color_discrete_sequence=custom_colors,
            hole=0.4,
        )
        fig.update_traces(hovertemplate='R$ %{value:,.2f}')
        # Exibir o gráfico no Streamlit
        st.plotly_chart(fig, use_container_width=True)

def execucao_restos_a_pagar(user_year):
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
        # Criar um gráfico de barras responsivo usando Plotly Express
        fig = px.bar(
            x=category_labels,
            y=category_values,
            title=f'Execução dos compromissos de anos anteriores (restos a pagar)',
            labels={'y': 'Valor', 'x': 'Categoria'},
            text=category_values,
        )

        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside', hovertemplate='R$ %{y:,.2f}', marker_color=custom_colors)

        fig.update_layout(yaxis_tickformat="R$,2f")

        st.plotly_chart(fig, use_container_width=True)

def execucao_despesas(user_year):
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

        fig = px.bar(
            x=category_labels,
            y=category_values,
            title=f'Execução das despesas',
            labels={'y': 'Valor', 'x': 'Categoria'},
            text=category_values,
        )

        fig.update_traces(texttemplate='%{text:.2s}', hovertemplate='R$ %{y:,.2f}', textposition='outside')

        fig.update_traces(marker_color=custom_colors)

        fig.update_layout(yaxis_tickformat="R$,2f")
        
        # Tornar o gráfico responsivo com altura e largura relativas
        st.plotly_chart(fig, use_container_width=True)


 
if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    
    st.set_page_config(page_title="Dados Abertos - Prefeitura de Assú/RN", layout="wide")

    st.warning("Observação: o conjunto de dados usado neste protótipo contém apenas dados entre janeiro de 2021 e dezembro de 2022.")   

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

    #SIDEBAR
    row4_spacer1, row4_1, row4_spacer2 = st.columns((.2, 7.1, .2))

    st.sidebar.title('Análise')
    tipo_de_dados = st.sidebar.selectbox ("Qual o tipo de dados?", list(TiposDeDados.__members__.keys()), key = 'attribute')
    ano = st.sidebar.selectbox ("Qual ano você quer analisar?", [2023 ,2022, 2021], key = 'measure_team')

    if tipo_de_dados == "DESPESA":

        st.markdown("<h2 style='text-align: center;'>Visão Geral</h2>", unsafe_allow_html=True) 
        #SEC1
        row5_1_1, row5_2_1, row5_3_1 = st.columns((1, 1, 1))
        with row5_1_1:
            execucao_despesas(ano)   

        with row5_2_1:
            categorias_economicas(ano)

        with row5_3_1:
            st.markdown("<center>", unsafe_allow_html=True)
            execucao_restos_a_pagar(ano)

        st.markdown("---")

        st.markdown("<h2 style='text-align: center;'>Pagamento de despesas por mês do ano</h2>", unsafe_allow_html=True) 
        despesa_12meses(ano)

        st.markdown("---")

        #SEC2
        st.markdown("<h2 style='text-align: center;'>Pagamento de despesas por área de atuação (função)</h2>", unsafe_allow_html=True) 

        despesas_por_area(ano)

        st.markdown("---")

        st.markdown("<h2 style='text-align: center;'>Pagamento de despesas por secretaria</h2>", unsafe_allow_html=True)
        
        despesas_por_secretaria(ano) 

        st.markdown("---")

        st.markdown("<h2 style='text-align: center;'>Pagamento de despesas por grupo de despesa</h2>", unsafe_allow_html=True)
        
        despesas_por_grupo(ano) 

        st.markdown("---")

        st.markdown("<h2 style='text-align: center;'>Despesas empenhadas (box plot)</h2>", unsafe_allow_html=True)
        categoria_despesa = st.selectbox("Qual categoria de despesa?", list([categoria.value for categoria in CategoriasDespesa]), key = 'seletor_boxplot')
        boxplot_despesa_dos_12_meses_de_um_ano(ano, categoria_despesa)
    elif tipo_de_dados == "RECEITA":

        st.markdown("<h2 style='text-align: center;'>Arrecadação por mês do ano</h2>", unsafe_allow_html=True) 
        receita_12meses(ano) 

        st.markdown("---")
        st.markdown("<h2 style='text-align: center;'>Arrecadação anual (por espécie)</h2>", unsafe_allow_html=True)
        receitas_por_especie(ano)
        st.markdown("---")
        st.markdown("<h2 style='text-align: center;'>Arrecadação anual (por categoria econômica)</h2>", unsafe_allow_html=True)
        categorias_economicas_receita(ano)