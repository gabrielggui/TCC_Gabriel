from graficos.despesas import (
    despesa_por_mes_do_ano,
    TiposDeDespesa,
    despesa_acumulada_por_ano,
    despesa_acumulada_todos_os_anos,
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
        print("1. Consultar despesa em um mês do ano")
        print("2. Consultar despesa acumulada de todos os meses em um ano")
        print("3. Consultar despesa acumulada de todos os anos")
        print("4. Sair")

        choice = input("Escolha uma opção (1/2/3/4): ")

        if choice == "1":
            user_year = int(input("Digite o ano desejado: "))
            user_month = int(input("Digite o mês desejado (1 para Janeiro, 2 para Fevereiro, etc.): "))
            tipo_despesa = selecionar_tipo_despesa()

            despesa_por_mes_do_ano(user_year, user_month, tipo_despesa)
        elif choice == "2":
            user_year = int(input("Digite o ano desejado: "))
            despesa_acumulada_por_ano(user_year)
        elif choice == "3":
            despesa_acumulada_todos_os_anos()
        elif choice == "4":
            print("Saindo do programa.")
            break
        else:
            print("Opção inválida!")
            break

        print()

if __name__ == "__main__":
    main()
