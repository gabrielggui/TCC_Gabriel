from webscrapper.webscrapper import start_web_scrapping
from graficos.despesas import (
    despesa_por_mes_do_ano,
    TiposDeDespesa,
    despesa_acumulada_de_um_ano,
    despesa_acumulada_todos_os_anos,
    despesa_dos_12_meses_de_um_ano
)
import os

def selecionar_tipo_despesa():

    print("Escolha o tipo de despesa:")
    print("1. Visualizar apenas dados do tipo \"despesa\"")
    print("2. Visualizar apenas dados do tipo \"despesaOrcamentaria\"")
    print("3. Visualizar todos os dados")

    choiceTipoDespesa = input("Escolha uma opção (1/2/3): ")

    if choiceTipoDespesa == "1":
        return TiposDeDespesa.APENAS_DESPESA
    elif choiceTipoDespesa == "2":
        return TiposDeDespesa.APENAS_DESPESA_ORCAMENTARIA
    elif choiceTipoDespesa == "3":
        return TiposDeDespesa.TODAS_AS_DESPESAS
    else:
        return ''

def main():
    while True:
        print("Escolha uma opção:")
        print("1. Consultar despesas em um mês do ano")
        print("2. Consultar despesas de todos os meses do ano")
        print("3. Consultar despesas acumuladas de um ano")
        print("4. Consultar despesas acumuladas de todos os anos")
        print("--------------")
        print("5. Baixar arquivos .json do Portal da Transparência")
        print("6. Sair")

        choice = input("Escolha uma opção (1/2/3/4): ")

        if choice == "1":
            user_year = int(input("Digite o ano desejado: "))
            user_month = int(input("Digite o mês desejado (1 para Janeiro, 2 para Fevereiro, etc.): "))
            tipo_despesa = selecionar_tipo_despesa()

            despesa_por_mes_do_ano(user_year, user_month, tipo_despesa)
        elif choice == "2":
            user_year = int(input("Digite o ano desejado: "))
            tipo_despesa = selecionar_tipo_despesa()
            despesa_dos_12_meses_de_um_ano(user_year,tipo_despesa)
        elif choice == "3":
            user_year = int(input("Digite o ano desejado: "))
            tipo_despesa = selecionar_tipo_despesa()
            despesa_acumulada_de_um_ano(user_year,tipo_despesa)
        elif choice == "4":
            tipo_despesa = selecionar_tipo_despesa()
            despesa_acumulada_todos_os_anos(tipo_despesa)
        elif choice == "5":
            start_web_scrapping()
        elif choice == "6":
            print("Saindo do programa.")
            break
        else:
            print("Opção inválida!")
            break

        print()

if __name__ == "__main__":
    main()
