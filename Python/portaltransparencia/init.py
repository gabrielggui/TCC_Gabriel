from graficos.despesas import despesa_por_mes_do_ano, TiposDeDespesa, despesa_acumulada_por_ano
import os

user_year = int(input("Digite o ano desejado: "))
user_month = int(input("Digite o mês desejado (1 para Janeiro, 2 para Fevereiro, etc.): "))

despesa_acumulada_por_ano(user_year)