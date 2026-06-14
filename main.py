import pandas as pd
import sys
from fpdf import FPDF
from fpdf.enums import XPos, YPos

def analisar_e_classificar(descricao):
    """
    O 'cérebro' do algoritmo. Ele lê a descrição do gasto e
    retorna a classificação contábil correta com base em palavras-chave.
    """
    texto = str(descricao).lower()
    
    if "programador" in texto:
        return "Custo Fixo"
    elif "comissão" in texto or "comissao" in texto:
        return "Despesa Variável"
    elif "estagiário" in texto or "estagiario" in texto:
        return "Despesa Fixa"
    elif "licenças" in texto or "licencas" in texto or "software" in texto:
        return "Custo Variável"
    elif "imposto" in texto or "iss" in texto:
        return "Despesa Variável"
    elif "pró-labore" in texto or "pro-labore" in texto or "lucas" in texto:
        return "Despesa Fixa"
    elif "internet" in texto:
        return "Custo Fixo"
    elif "material" in texto or "limpeza" in texto:
        return "Despesa Fixa"
    elif "plataforma" in texto or "automação" in texto or "automacao" in texto:
        return "Custo Fixo"
    else:
        return "Não Classificado"

def carregar_dados(caminho="Dados - Empresa Giga - Atualizados.xlsx"):
    """
    Lê a planilha atualizada e assegura que todos os dados do novo cenário estejam presentes.
    """
    try:
        df = pd.read_excel(caminho, header=0)
        
        descricao_col = df.columns[1]
        valor_col = df.columns[2]
        
        df_limpo = pd.DataFrame()
        df_limpo["descricao"] = df[descricao_col]
        df_limpo["valor"] = df[valor_col]
        
        df_limpo["valor"] = df_limpo["valor"].astype(str)
        df_limpo["valor"] = df_limpo["valor"].str.replace("R$", "", regex=False).str.replace(" por unidade", "", regex=False).str.strip()
        df_limpo["valor"] = df_limpo["valor"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
        df_limpo["valor"] = pd.to_numeric(df_limpo["valor"], errors="coerce").fillna(0)
        
        df_limpo["classificacao"] = df_limpo["descricao"].apply(analisar_e_classificar)
            
        dados_lista = df_limpo.to_dict(orient="records")

        # [SEGURANÇA] Verifica se a nova plataforma de 800 reais está no Excel lido.
        tem_plataforma = any("plataforma" in str(item["descricao"]).lower() for item in dados_lista)
        if not tem_plataforma:
            dados_lista.append({
                "descricao": "Plataforma de automação de chamados (Novo)",
                "valor": 800.00,
                "classificacao": analisar_e_classificar("plataforma")
            })
            
        return dados_lista
        
    except FileNotFoundError:
        print("\n[Aviso] Arquivo Excel atualizado não encontrado.")
        print("Carregando o banco de dados interno de emergência...\n")
        return [
            {"descricao": "Salário da equipe de programadores", "valor": 7000.00, "classificacao": "Custo Fixo"},
            {"descricao": "Comissão de 5% sobre o valor do serviço", "valor": 750.00, "classificacao": "Despesa Variável"},
            {"descricao": "Estagiário para o administrativo", "valor": 1200.00, "classificacao": "Despesa Fixa"},
            {"descricao": "Licenças de software de desenvolvimento", "valor": 800.00, "classificacao": "Custo Variável"},
            {"descricao": "Imposto sobre Serviços (ISS) de 10%", "valor": 1500.00, "classificacao": "Despesa Variável"},
            {"descricao": "Pró-labore do Lucas (Sócio-Administrador)", "valor": 3000.00, "classificacao": "Despesa Fixa"},
            {"descricao": "Conta de internet dedicada da empresa", "valor": 250.00, "classificacao": "Custo Fixo"},
            {"descricao": "Material de escritório e limpeza", "valor": 150.00, "classificacao": "Despesa Fixa"},
            {"descricao": "Plataforma de automação de chamados", "valor": 800.00, "classificacao": "Custo Fixo"}
        ]

def classificar_operacionalmente(contas):
    """
    Agrupa as contas puramente pelo seu comportamento: Fixos x Variáveis.
    """
    balanco = {
        "variaveis": [], 
        "fixos": []      
    }

    for conta in contas:
        classificacao = str(conta["classificacao"]).lower()

        if "variável" in classificacao or "variavel" in classificacao:
            balanco['variaveis'].append(conta)
        elif "fixo" in classificacao or "fixa" in classificacao:
            balanco['fixos'].append(conta)

    return balanco

def calcular_indicadores(balanco):
    """
    Função auxiliar para centralizar a matemática, garantindo que o terminal e o PDF usem exatamente os mesmos dados.
    """
    faturamento = 15000.00
    
    # Detalhamento por tipo (Custo vs Despesa)
    custos_fixos = sum(i["valor"] for i in balanco["fixos"] if "custo" in i["classificacao"].lower())
    despesas_fixas = sum(i["valor"] for i in balanco["fixos"] if "despesa" in i["classificacao"].lower())
    custos_variaveis = sum(i["valor"] for i in balanco["variaveis"] if "custo" in i["classificacao"].lower())
    despesas_variaveis = sum(i["valor"] for i in balanco["variaveis"] if "despesa" in i["classificacao"].lower())
    
    # Totais operacionais
    total_fixos = custos_fixos + despesas_fixas
    total_variaveis = custos_variaveis + despesas_variaveis
    gasto_total = total_fixos + total_variaveis

    # Indicadores Contábeis
    mc_valor = faturamento - total_variaveis
    mc_percentual = mc_valor / faturamento if faturamento > 0 else 0
    ponto_equilibrio = total_fixos / mc_percentual if mc_percentual > 0 else 0
    resultado_operacional = faturamento - gasto_total
    
    # Preço Alvo (Questão 4)
    novo_preco_alvo = 15300 / 0.85

    return {
        "faturamento": faturamento,
        "custos_fixos": custos_fixos,
        "despesas_fixas": despesas_fixas,
        "custos_variaveis": custos_variaveis,
        "despesas_variaveis": despesas_variaveis,
        "total_fixos": total_fixos,
        "total_variaveis": total_variaveis,
        "gasto_total": gasto_total,
        "mc_valor": mc_valor,
        "mc_percentual": mc_percentual,
        "ponto_equilibrio": ponto_equilibrio,
        "resultado_operacional": resultado_operacional,
        "novo_preco_alvo": novo_preco_alvo
    }

def exibir_relatorio_contabil(dados_brutos, balanco):
    """
    Exibe os resultados detalhados no terminal.
    """
    ind = calcular_indicadores(balanco)
    
    if ind["gasto_total"] == 0:
        print("\n[Erro Crítico] Nenhuma conta classificada. Verifique o arquivo Excel.")
        return

    print("-" * 75)
    print("RELATÓRIO CONTÁBIL ATUALIZADO - NOVO CENÁRIO DA GIGA".center(75))
    print("-" * 75)

    print("\n[ Resumo Financeiro Detalhado ]")
    print(f"Faturamento Base:         R$ {ind['faturamento']:,.2f}")
    print(f"Custo Fixo Total:         R$ {ind['custos_fixos']:,.2f}")
    print(f"Custo Variável Total:     R$ {ind['custos_variaveis']:,.2f}")
    print(f"Despesa Fixa Total:       R$ {ind['despesas_fixas']:,.2f}")
    print(f"Despesa Variável Total:   R$ {ind['despesas_variaveis']:,.2f}")
    print(f"-> Gasto Total do Mês:    R$ {ind['gasto_total']:,.2f}")
    
    print("\n[ Indicadores Gerenciais ]")
    print(f"Margem de Contribuição:   R$ {ind['mc_valor']:,.2f} ({ind['mc_percentual']*100:.2f}%)")

    print("\n" + "=" * 75)
    print("\n[ Questão 1 - Classificação e Reestruturação dos Gastos ]")
    print("Resposta: A nova plataforma de automação é classificada como 'Custo Fixo'.")
    print("\nDetalhamento dos totais agrupados para análise gerencial:")
    print(f" > Total de Gastos Fixos: R$ {ind['total_fixos']:,.2f}")
    print(f" > Total de Gastos Variáveis: R$ {ind['total_variaveis']:,.2f}")

    print("\n" + "-" * 75)
    print("\n[ Questão 2 - Novo Ponto de Equilíbrio Contábil ]")
    print(f"Fórmula: Gastos Fixos / Índice de Margem de Contribuição")
    print(f"Cálculo: {ind['total_fixos']:,.2f} / {ind['mc_percentual']:.4f}")
    print(f"Resposta: O novo Ponto de Equilíbrio Contábil (PEC) é de R$ {ind['ponto_equilibrio']:,.2f}.")

    print("\n" + "-" * 75)
    print("\n[ Questão 3 - Tomada de Decisão (Lucro ou Prejuízo) ]")
    if ind["resultado_operacional"] < 0:
        print(f"Resposta: PREJUÍZO. Mantendo o preço em R$ 15.000,00, a Giga opera com um prejuízo de R$ {abs(ind['resultado_operacional']):,.2f} por mês.")
    else:
        print(f"Resposta: LUCRO. A empresa tem um lucro de R$ {ind['resultado_operacional']:,.2f}.")

    print("\n" + "-" * 75)
    print("\n[ Questão 4 - Nova Precificação para Manter o Lucro Original ]")
    print("Contexto: O lucro no cenário antigo era de R$ 2.100,00.")
    print("Como as despesas variáveis (Imposto + Comissão) equivalem a 15% do faturamento, a nova receita deve cobrir isso de forma proporcional.")
    print(f"Resposta: Para garantir o exato mesmo lucro, o novo preço cobrado do cliente deverá ser de R$ {ind['novo_preco_alvo']:,.2f}.")
    print("\n" + "-" * 75 + "\n")

def gerar_pdf(dados_brutos, balanco):
    ind = calcular_indicadores(balanco)
    if ind["gasto_total"] == 0:
        print("\n[Erro Crítico] Não há dados para gerar o PDF.")
        return

    pdf = FPDF()
    pdf.add_page()
    
    # Define a largura útil de forma explícita
    largura_util = pdf.epw 
    
    # --- CABEÇALHO ---
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(largura_util, 10, text="RELATÓRIO CONTÁBIL ATUALIZADO", align="C")
    pdf.ln(12) # Força a descida do cursor para a próxima linha

    # --- RESUMO FINANCEIRO ---
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(largura_util, 8, text="Resumo Financeiro Detalhado:")
    pdf.ln(8)
    
    pdf.set_font("Helvetica", size=11)
    elementos_resumo = [
        ("Faturamento Base", ind['faturamento']), 
        ("Custo Fixo Total", ind['custos_fixos']),
        ("Custo Variável Total", ind['custos_variaveis']),
        ("Despesa Fixa Total", ind['despesas_fixas']),
        ("Despesa Variável Total", ind['despesas_variaveis'])
    ]
    
    for label, valor in elementos_resumo:
        pdf.cell(largura_util, 6, text=f"{label}: R$ {valor:,.2f}")
        pdf.ln(6) # Garante que a próxima linha financeira fique logo abaixo
    
    # Gasto Total em Negrito
    pdf.ln(2)
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(largura_util, 6, text=f"Gasto Total: R$ {ind['gasto_total']:,.2f}")
    pdf.ln(10)

    # --- CLASSIFICAÇÃO DOS GASTOS ---
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(largura_util, 8, text="Classificação dos Gastos:")
    pdf.ln(8)
    
    pdf.set_font("Helvetica", size=10)
    for i, item in enumerate(dados_brutos, start=1):
        texto = f"{i}. {item['descricao']} | R$ {item['valor']:.2f} | {item['classificacao']}"
        texto_seguro = texto.encode('latin-1', 'replace').decode('latin-1')
        
        # multi_cell calcula a altura sozinho, usamos o ln=YPos.NEXT para ele saltar
        pdf.multi_cell(largura_util, 6, text=texto_seguro, new_y=YPos.NEXT)
        pdf.ln(1) # Pequeno espaçamento entre um item e outro
        
    pdf.ln(8)

    # --- QUESTÕES ---
    questoes = [
        ("1", "Classificação e Reestruturação", f"A nova plataforma é Custo Fixo. Total Fixos: R$ {ind['total_fixos']:,.2f} | Total Variáveis: R$ {ind['total_variaveis']:,.2f}"),
        ("2", "Ponto de Equilíbrio", f"O novo Ponto de Equilíbrio Contábil é de R$ {ind['ponto_equilibrio']:,.2f}."),
        ("3", "Tomada de Decisão", "LUCRO." if ind["resultado_operacional"] >= 0 else f"PREJUÍZO. A empresa opera com um déficit de R$ {abs(ind['resultado_operacional']):,.2f}."),
        ("4", "Nova Precificação", f"Para manter o lucro original, o novo preço cobrado deverá ser R$ {ind['novo_preco_alvo']:,.2f}.")
    ]

    for q_num, titulo, texto in questoes:
        pdf.set_font("Helvetica", style="B", size=11)
        pdf.cell(largura_util, 6, text=f"[ Questão {q_num} - {titulo} ]")
        pdf.ln(6)
        
        pdf.set_font("Helvetica", size=10)
        texto_seguro_q = texto.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(largura_util, 5, text=texto_seguro_q, new_y=YPos.NEXT)
        pdf.ln(4) # Espaço entre blocos de perguntas

    # --- SALVAMENTO ---
    try:
        pdf.output("Relatorio_Financeiro_Giga.pdf")
        print("\n[Sucesso] PDF gerado na pasta raiz!")
    except Exception as e:
        print(f"\n[Erro] Erro ao salvar: {e}")
        
def menu():
    """
    Menu principal da aplicação.
    """
    dados_brutos = carregar_dados()
    balanco_operacional = classificar_operacionalmente(dados_brutos)

    while True:
        print("\n")
        print("MENU PRINCIPAL")
        print("1 - Mostrar Resultados do Novo Cenário")
        print("2 - Gerar Relatório em PDF")
        print("3 - Sair do Sistema")
        
        opcao = input("\nEscolha uma opção: ")

        if opcao == '1':
            exibir_relatorio_contabil(dados_brutos, balanco_operacional)
        elif opcao == '2':
            gerar_pdf(dados_brutos, balanco_operacional)
        elif opcao == '3':
            print("\nEncerrando o sistema.\n")
            sys.exit()
        else:
            print("\n[Erro] Opção inválida. Digite 1, 2 ou 3.\n")

if __name__ == "__main__":
    menu()