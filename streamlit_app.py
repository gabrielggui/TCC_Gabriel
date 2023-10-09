import locale
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

directory = 'dados/'
despesa_categories = set()
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
    df = pd.DataFrame(list(values_by_category.items()), columns=['Categoria', 'Valor'])
    df['Valor Formatado'] = df['Valor'].apply(formatar_moeda)
    fig = px.bar(df, x='Valor', y='Categoria', orientation='h', text='Valor Formatado')
    fig.update_traces(marker_color=custom_colors)

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
        fig = px.treemap(df, path=['category_labels'], values='category_values', color_discrete_sequence=custom_colors)
        fig.update_layout(font=dict(size=18))
        
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

    df = pd.DataFrame(data)
    df = df.sort_values(by='Valor', ascending=False)

    fig = px.bar(df, x='Mês', y='Valor', color='Categoria',
                labels={'Valor': 'Valor', 'Categoria': 'Espécie'})

    fig.update_yaxes(title_text='Valor (R$)')
    fig.update_traces(hovertemplate='R$ %{y:,.2f}')
    total_por_categoria = df['Valor'].sum()

    fig.update_layout(yaxis_tickformat='$,.2f')

    # Adiciona o valor total acima de cada barra
    for month_num in range(1, 13):
        total_por_mes = df[df['Mês'] == month_num]['Valor'].sum()
        fig.add_annotation(
            x=month_num,
            y=total_por_mes,
            text=f'          {locale.currency(total_por_mes, grouping=True)}',
            arrowhead=0,
            arrowcolor="black",
            arrowwidth=1,
            arrowsize=1,
            font=dict(size=9),
            yshift=5
        )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f'<h4 style=\'text-align: center;\'>Total de receitas no ano: {locale.currency(total_por_categoria, grouping=True)}</h4>', unsafe_allow_html=True) 

def dados_estatisticos_mes(user_year: int, user_month: int, categoria_despesa: str):
    categories = set()
    values_by_category = {month: {} for month in range(1, 13)}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json' if user_year == 0 else f'{user_year}.json') and TiposDeDados.DESPESA.value in filename.lower()]

    top_expenses = []

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for empenho_item in registro['registro']['listEmpenhoItens']:
                    emissao = registro['registro']['empenho']['emissao']
                    year, month, _ = map(int, emissao.split('-'))

                    category = registro['registro']['naturezaDespesa']['elemento']['denominacao']

                    if (year == user_year and (month == user_month or user_month == 0) and (categoria_despesa == category or categoria_despesa == "Todos")):
                        value = empenho_item['quantidade'] * empenho_item['valorUnitario']

                        if value != 0:
                            if category not in categories:
                                categories.add(category)
                                for month_num in range(1, 13):
                                    values_by_category[month_num][category] = []

                            values_by_category[month][category].append(value)

                            top_expenses.append({
                                'Valor total': value
                            })
    
    # Calcular e exibir estatísticas
    valores_totais = pd.DataFrame(top_expenses)

    if 'Valor total' in valores_totais.columns:
        valores_totais = valores_totais.get('Valor total', 0).apply(lambda x: float(x))
        media = valores_totais.mean()
        mediana = valores_totais.median()
        desvio_padrao = valores_totais.std()
            
        print("Estatísticas:")
        print(f"Média: {formatar_moeda(media)}")
        print(f"Mediana: {formatar_moeda(mediana)}")
        print(f"Desvio Padrão: {desvio_padrao}")
        print(f'Coeficiente de Variação: {(desvio_padrao / media) * 100:.2f}%') 

def maiores_despesas_ano(user_year: int, user_month: int, categoria_despesa: str, numero_resultados: int):
    categories = set()
    values_by_category = {month: {} for month in range(1, 13)}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json' if user_year == 0 else f'{user_year}.json') and TiposDeDados.DESPESA.value in filename.lower()]

    top_expenses = []

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for empenho_item in registro['registro']['listEmpenhoItens']:
                    emissao = registro['registro']['empenho']['emissao']
                    year, month, _ = map(int, emissao.split('-'))

                    category = registro['registro']['naturezaDespesa']['elemento']['denominacao']

                    if (year == user_year and (month == user_month or user_month == 0) and (categoria_despesa == category or categoria_despesa == "Todos")):
                        value = empenho_item['quantidade'] * empenho_item['valorUnitario']

                        if value != 0:
                            if category not in categories:
                                categories.add(category)
                                for month_num in range(1, 13):
                                    values_by_category[month_num][category] = []

                            values_by_category[month][category].append(value)

                            top_expenses.append({
                                'Categoria': category,
                                'Denominação do Empenho': empenho_item['denominacao'],
                                'Emissão': datetime.strptime(emissao, "%Y-%m-%d").strftime("%d/%m/%Y"),
                                'Quantidade': empenho_item['quantidade'],
                                'Unidade de Medida': empenho_item['unidadeMedida']['sigla'],
                                'Valor unitário': empenho_item['valorUnitario'],
                                'Valor total': value
                            })
    
    # Calcular e exibir estatísticas
    valores_totais = pd.DataFrame(top_expenses)

    if 'Valor total' in valores_totais.columns:
        valores_totais = valores_totais.get('Valor total', 0).apply(lambda x: float(x))
        media = valores_totais.mean()
        mediana = valores_totais.median()
        desvio_padrao = valores_totais.std()

        row1, row2, row3, row4 = st.columns((1, 1, 1, 1))
        with row1:
            st.markdown("<h6 style='text-align: center;'>Média:</h6>", unsafe_allow_html=True) 
            st.markdown(f'<center>{formatar_moeda(media)}</center>', unsafe_allow_html=True)
        with row2:
            st.markdown("<h6 style='text-align: center;'>Mediana:</h6>", unsafe_allow_html=True)
            st.markdown(f'<center>{formatar_moeda(mediana)}</center>', unsafe_allow_html=True)
        with row3:
            st.markdown("<h6 style='text-align: center;'>Desvio padrão:</h6>", unsafe_allow_html=True)
            st.markdown(f'<center>{formatar_moeda(desvio_padrao)}</center>', unsafe_allow_html=True)
        with row4: 
            st.markdown("<h6 style='text-align: center;'>Coeficiente de variação:</h6>", unsafe_allow_html=True)
            coeficiente_variacao = (desvio_padrao / media) * 100
            st.markdown(f'<center>{coeficiente_variacao:.2f}%</center>', unsafe_allow_html=True)        

    if top_expenses:
        top_expenses_df = pd.DataFrame(top_expenses)
        top_expenses_df = top_expenses_df.sort_values(by='Valor total', ascending=False).head(numero_resultados)

        formatted_df = top_expenses_df.copy()
        formatted_df['Valor total'] = formatted_df['Valor total'].apply(formatar_moeda)
        formatted_df['Valor unitário'] = formatted_df['Valor unitário'].apply(formatar_moeda)
        formatted_df['Quantidade'] = formatted_df['Quantidade'].apply(lambda x: f'{x:.2f}')

        st.table(formatted_df)
    else:
        st.warning("Não há despesas para o período especificado.")

def load_despesa_categories(user_year: int):
    categories = set()
    values_by_category = {month: {} for month in range(1, 13)}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith('.json' if user_year == 0 else f'{user_year}.json') and TiposDeDados.DESPESA.value in filename.lower()]

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for empenho_item in registro['registro']['listEmpenhoItens']:
                    emissao = registro['registro']['empenho']['emissao']
                    year, month, _ = map(int, emissao.split('-'))

                    category = registro['registro']['naturezaDespesa']['elemento']['denominacao']

                    if year == user_year:
                        value = empenho_item['quantidade'] * empenho_item['valorUnitario']

                        if value != 0:
                            if category not in categories:
                                categories.add(category)
                                despesa_categories.add(category)
                                for month_num in range(1, 13):
                                    values_by_category[month_num][category] = []

                            values_by_category[month][category].append(value)

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

    df = pd.DataFrame(data)
    df = df.sort_values(by='Valor', ascending=False)

    fig = px.bar(df, x='Mês', y='Valor', color='Categoria',
                labels={'Valor': 'Valor', 'Categoria': 'Elemento de despesa'})

    fig.update_yaxes(title_text='Valor (R$)')
    fig.update_traces(hovertemplate='R$ %{y:,.2f}')
    total_por_categoria = df['Valor'].sum()

    fig.update_layout(yaxis_tickformat='$,.2f')

    # Adiciona o valor total acima de cada barra
    for month_num in range(1, 13):
        total_por_mes = df[df['Mês'] == month_num]['Valor'].sum()
        fig.add_annotation(
            x=month_num,
            y=total_por_mes,
            text=f'          {locale.currency(total_por_mes, grouping=True)}',
            arrowhead=2,
            arrowcolor="black",
            arrowwidth=2,
            arrowsize=1,
            font=dict(size=9),
            yshift=5
        )
    fig.update_layout(yaxis_tickformat='$,.2f')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f'<h4 style=\'text-align: center;\'>Total de despesas pagas no ano: {locale.currency(total_por_categoria, grouping=True)}</h4>', unsafe_allow_html=True) 


def despesas_por_elemento(user_year):
    categories = set()
    values_by_category = {}

    json_files = [filename for filename in os.listdir(directory) if filename.endswith(f'{user_year}.json') and TiposDeDados.DESPESA.value in filename.lower()]

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r') as file:
            data = json.load(file)
            for registro in data['registros']:
                for movimento in registro['registro']['listMovimentos']:
                    if ('Pagamento de empenho' == movimento['tipoMovimento'] or 'Pagamento de restos a pagar' == movimento['tipoMovimento']):
                        value = movimento['valorMovimento']

                        tipo_movimento = registro['registro']['naturezaDespesa']['elemento']['denominacao']

                        if tipo_movimento not in categories:
                            categories.add(tipo_movimento)
                            values_by_category[tipo_movimento] = value
                        else:
                            values_by_category[tipo_movimento] += value

    sorted_categories = sorted(values_by_category.items(), key=lambda x: x[1], reverse=True)

    top_categories = sorted_categories[:10]
    other_categories = sorted_categories[10:]

    other_values = sum(category[1] for category in other_categories)
    top_categories.append(("Outros", other_values))

    category_labels = [format_legend_label(category[0]) for category in top_categories]
    category_values = [category[1] for category in top_categories]

    category_labels = [f'{label}<br>{formatar_moeda(value)}<br>({(value/sum(category_values)*100):.1f}%)' for label, value in zip(category_labels, category_values)]

    df = pd.DataFrame(list(zip(category_labels, category_values)), columns =['category_labels', 'category_values'])

    if not values_by_category:
        st.warning("Não há valores em nenhuma das categorias para o ano especificado.")
    else:
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
        fig = px.pie(
            names=category_labels,
            values=category_values,
            labels={'value': 'Valor'},
            title=f'Pagamento de despesas por categoria econômica',
            color_discrete_sequence=custom_colors,
            hole=0.4,
        )
        fig.update_traces(hovertemplate='R$ %{value:,.2f}')
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
        fig = px.bar(
            x=category_labels,
            y=category_values,
            title=f'Execução dos compromissos de anos anteriores (restos a pagar)',
            labels={'y': 'Valor', 'x': 'Categoria'},
            text=category_values,
        )

        fig.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside', hovertemplate='R$ %{y:,.2f}', marker_color=custom_colors)

        fig.update_layout(yaxis_tickformat="$,.2f")

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

        fig.update_traces(texttemplate='R$ %{text:,.2f}', hovertemplate='R$ %{y:,.2f}', textposition='outside')
        fig.update_traces(marker_color=custom_colors)
        fig.update_layout(yaxis_tickformat="$,.2f")
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
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

    #Sidebar
    st.sidebar.title('Configurações')

    tipo_de_dados = st.sidebar.selectbox("Qual o tipo de dados?", list(TiposDeDados.__members__.keys()), key = 'tipo_dados')
    
    ano_exercicio = st.sidebar.selectbox("Qual ano você quer analisar?", [2023 ,2022, 2021], key = 'ano_exercicio')

    load_despesa_categories(ano_exercicio)

    if tipo_de_dados == "DESPESA":
                
        #SEC1
        st.markdown("<h2 style='text-align: center;'>Visão Geral</h2>", unsafe_allow_html=True) 

        row1_1_1, row1_2_1, row1_3_1 = st.columns((1, 1, 1))
        with row1_1_1:
            execucao_despesas(ano_exercicio)   
        with row1_2_1:
            categorias_economicas(ano_exercicio)
        with row1_3_1:
            execucao_restos_a_pagar(ano_exercicio)

        st.markdown("---")

        #SEC2
        st.markdown("<h2 style='text-align: center;'>Pagamento de despesas por mês do ano</h2>", unsafe_allow_html=True)
        st.markdown(f'<h6 style=\'text-align: center;\'>(Clique duas vezes em uma categoria para selecioná-la)</h6>', unsafe_allow_html=True)  
        despesa_12meses(ano_exercicio)

        st.markdown("---")

        #SEC3
        st.markdown("<h2 style='text-align: center;'>Pagamento de despesas no ano por área de atuação (função)</h2>", unsafe_allow_html=True) 

        despesas_por_area(ano_exercicio)

        st.markdown("---")

        #SEC4
        st.markdown("<h2 style='text-align: center;'>Pagamento de despesas no ano por elemento de despesa</h2>", unsafe_allow_html=True)
        
        despesas_por_elemento(ano_exercicio) 

        st.markdown("---")

        #SEC5
        st.markdown("<h2 style='text-align: center;'>Pagamento de despesas no ano por secretaria</h2>", unsafe_allow_html=True)
        
        despesas_por_secretaria(ano_exercicio) 

        st.markdown("---")

        #SEC6
        st.markdown("<h2 style='text-align: center;'>Maiores despesas empenhadas</h2>", unsafe_allow_html=True) 
        
        row6_1, row6_2, row6_3 = st.columns((1, 1, 1))
        with row6_1:
            categoria_despesa = st.selectbox("Qual categoria de despesa?", ["Todos"] + list([categoria for categoria in despesa_categories]), key = 'seletor_boxplot')        
        with row6_2:
            mes = st.selectbox("Qual o mês?", ['Todos', 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1], key = 'month')           
        with row6_3:
            tamanho_resultados = st.selectbox("Número de resultados", [10, 50, 100], key = 'results')        

        maiores_despesas_ano(ano_exercicio, 0 if mes == 'Todos' else mes, categoria_despesa, tamanho_resultados)

        dados_estatisticos_mes(ano_exercicio, 0 if mes == 'Todos' else mes, categoria_despesa)

    elif tipo_de_dados == "RECEITA":

        st.markdown("<h2 style='text-align: center;'>Arrecadação por mês do ano</h2>", unsafe_allow_html=True) 
        receita_12meses(ano_exercicio) 

        st.markdown("---")
        st.markdown("<h2 style='text-align: center;'>Arrecadação anual (por espécie)</h2>", unsafe_allow_html=True)
        receitas_por_especie(ano_exercicio)
        st.markdown("---")
        st.markdown("<h2 style='text-align: center;'>Arrecadação anual (por categoria econômica)</h2>", unsafe_allow_html=True)
        categorias_economicas_receita(ano_exercicio)
    