import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from zipfile import ZipFile
import pandas as pd
import numpy as np
from functools import reduce


# ======================
# VARIÁVEL DE CAMINHO
# ======================
CAMINHO = "./dados_fiis"  # você pode alterar para o diretório desejado
RESULTADO_ANALISES = "./analises"

anos = [2016, 2017, 2018,2019,2020,2021,2022,2023,2024,2025]  # ajustar conforme necessário

# Cria a pasta se não existir
os.makedirs(CAMINHO, exist_ok=True)
os.makedirs(RESULTADO_ANALISES, exist_ok=True)

# ======================
# URL do índice da CVM
# ======================
URL_BASE = "https://dados.cvm.gov.br/dados/FII/DOC/INF_TRIMESTRAL/DADOS/"


def listar_links_zip():
    """Retorna todos os links para arquivos .zip da página da CVM"""
    response = requests.get(URL_BASE)
    soup = BeautifulSoup(response.text, "html.parser")
    links = [URL_BASE + a['href'] for a in soup.find_all('a') if a['href'].endswith('.zip')]
    return links


def baixar_arquivo(link):
    """Baixa o arquivo se ele ainda não existir"""
    nome_arquivo = link.split('/')[-1]
    caminho_completo = os.path.join(CAMINHO, nome_arquivo)

    if os.path.exists(caminho_completo):
        print(f"Já existe: {nome_arquivo}")
        return caminho_completo

    print(f"Baixando: {nome_arquivo}")
    response = requests.get(link, stream=True)

    with open(caminho_completo, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return caminho_completo


def descompactar_arquivo(caminho_zip):
    """Descompacta o .zip se ainda não estiver descompactado"""
    with ZipFile(caminho_zip, 'r') as zip_ref:
        zip_ref.extractall(CAMINHO)


# --------------------------
# CONFIGURAÇÕES
# --------------------------

# ===============================
# FUNCAO: Carregar DataFrames dinamicamente com suporte a varios anos
# ===============================
def carregar_dfs(ano, base_dir=CAMINHO):
    arquivos = [f for f in os.listdir(base_dir) if f.endswith('.csv') and f'_{ano}' in f]
    dfs = {}
    for f in arquivos:
        nome_base = f.replace(".csv", "")
        caminho = os.path.join(base_dir, f)
        dfs[nome_base] = pd.read_csv(caminho, sep=';', encoding='ISO-8859-1')
    return dfs

def get_df(dfs, nome_base, ano):
    return dfs.get(f"{nome_base}_{ano}")
# FUNCAO: Fazer todos os merges
# ===============================
def realizar_merges(dfs, ano):
    merges = {}

    merges['rentab_merge'] = get_df(dfs, 'inf_trimestral_fii_rentabilidade_efetiva', ano).merge(
        get_df(dfs, 'inf_trimestral_fii_geral', ano), on=['CNPJ_Fundo', 'Data_Referencia', 'Versao'], how='left')

    merges['imovel_merge'] = get_df(dfs, 'inf_trimestral_fii_imovel', ano) \
        .merge(get_df(dfs, 'inf_trimestral_fii_imovel_desempenho', ano), on=['CNPJ_Fundo', 'Data_Referencia', 'Versao', 'Classe'], how='left') \
        .merge(get_df(dfs, 'inf_trimestral_fii_imovel_renda_acabado_inquilino', ano), on=['CNPJ_Fundo', 'Data_Referencia', 'Versao', 'Nome_Imovel'], how='left')

    merges['resultado_merge'] = get_df(dfs, 'inf_trimestral_fii_resultado_contabil_financeiro', ano).merge(
        get_df(dfs, 'inf_trimestral_fii_geral', ano), on=['CNPJ_Fundo', 'Data_Referencia', 'Versao'], how='left')

    merges['ativos_merge'] = get_df(dfs, 'inf_trimestral_fii_ativo', ano) \
        .merge(get_df(dfs, 'inf_trimestral_fii_ativo_garantia_rentabilidade', ano), on=['CNPJ_Fundo', 'Data_Referencia', 'Versao', 'Nome_Ativo'], how='left') \
        .merge(get_df(dfs, 'inf_trimestral_fii_geral', ano), on=['CNPJ_Fundo', 'Data_Referencia', 'Versao'], how='left')

    merges['complemento_merge'] = get_df(dfs, 'inf_trimestral_fii_geral', ano).merge(
        get_df(dfs, 'inf_trimestral_fii_complemento', ano), on=['CNPJ_Fundo', 'Data_Referencia', 'Versao'], how='left')

    merges['imoveis_historico'] = get_df(dfs, 'inf_trimestral_fii_imovel', ano) \
        .merge(get_df(dfs, 'inf_trimestral_fii_aquisicao_imovel', ano), on=['CNPJ_Fundo', 'Nome_Imovel'], how='left') \
        .merge(get_df(dfs, 'inf_trimestral_fii_alienacao_imovel', ano), on=['CNPJ_Fundo', 'Nome_Imovel'], how='left')

    merges['terrenos_historico'] = get_df(dfs, 'inf_trimestral_fii_terreno', ano) \
        .merge(get_df(dfs, 'inf_trimestral_fii_aquisicao_terreno', ano), on=['CNPJ_Fundo', 'Endereco'], how='left') \
        .merge(get_df(dfs, 'inf_trimestral_fii_alienacao_terreno', ano), on=['CNPJ_Fundo', 'Endereco'], how='left')

    merges['direitos_merge'] = get_df(dfs, 'inf_trimestral_fii_geral', ano).merge(
        get_df(dfs, 'inf_trimestral_fii_direito', ano), on=['CNPJ_Fundo', 'Data_Referencia', 'Versao'], how='left')

    merges['contratos_merge'] = get_df(dfs, 'inf_trimestral_fii_imovel', ano).merge(
        get_df(dfs, 'inf_trimestral_fii_imovel_renda_acabado_contrato', ano),
        left_on=['CNPJ_Fundo', 'Nome_Imovel'], right_on=['CNPJ_Fundo', 'Nome_Endereco_Imovel'], how='left')

    return merges





def padronizar_colunas_dfs(dfs):

    mapeamentos = {
        'CNPJ_Fundo_Classe': 'CNPJ_Fundo',
        'Data_Referencia_Classe': 'Data_Referencia',
        'Versao_Classe': 'Versao',
        'CNPJ_Classe': 'CNPJ_Fundo',
        'CNPJ': 'CNPJ_Fundo',
        'Data': 'Data_Referencia',
        'Nome_Fundo_Classe': 'Nome_Fundo'
    }

    for nome_df, df in dfs.items():
        novas_colunas = {
            col: mapeamentos[col]
            for col in df.columns
            if col in mapeamentos
        }
        dfs[nome_df] = df.rename(columns=novas_colunas)

    return dfs


# ===============================
# FUNCAO: Gerar analises principais
# ===============================
def limpar_dataframe(df, colunas_obrigatorias=None, arredondar=True, casas_decimais=2):
    df = df.copy()
    if colunas_obrigatorias:
        df = df.dropna(subset=colunas_obrigatorias)
    if arredondar:
        for col in df.select_dtypes(include='number').columns:
            df.loc[:, col] = df[col].round(casas_decimais)
    return df.reset_index(drop=True)

def gerar_analises(merges):
    analises = {}

    # Rentabilidade média por fundo
    analises['rentabilidade_media'] = merges['rentab_merge'].groupby('Nome_Fundo')[
        'Percentual_Rentabilidade_Efetiva_Mes'
    ].mean().reset_index()

    # Vacância e inadimplência média por imóvel
    analises['vacancia'] = merges['imovel_merge'].groupby('Nome_Imovel')[
        ['Percentual_Vacancia', 'Percentual_Inadimplencia']
    ].mean().reset_index()

    # Distribuição de rendimento em relação ao lucro
    resultado = merges['resultado_merge'].copy()
    resultado['%Distribuido'] = 100 * resultado['Rendimentos_Declarados'] / resultado['Lucro_Contabil']
    analises['distribuicao_vs_lucro'] = resultado[
        ['CNPJ_Fundo', 'Nome_Fundo', 'Lucro_Contabil', 'Rendimentos_Declarados', '%Distribuido']
    ]

    # Tipo de ativos por fundo
    analises['ativos_tipo'] = merges['ativos_merge'].groupby(['Nome_Fundo', 'Tipo'])[
        'Valor'
    ].sum().reset_index()

    # Liquidez disponível
    analises['liquidez'] = merges['complemento_merge'][
        ['Nome_Fundo', 'Ativo_Liquidez_Valor_Disponibilidades']
    ].dropna()

    # Direitos com valor
    analises['direitos_valor'] = merges['direitos_merge'][
        merges['direitos_merge']['Valor'].notna()
    ][['Nome_Fundo', 'Nome_Ativo', 'Valor']]

    # Imóveis alienados com área

    df_mov = merges['imoveis_historico'].copy()
    # Substitui datas inválidas por NaN
    df_mov['Data_Alienacao'] = df_mov['Data_Alienacao'].replace('1899-12-31', np.nan)
    # Converte a data em datetime (caso ainda não seja)
    df_mov['Data_Alienacao'] = pd.to_datetime(df_mov['Data_Alienacao'], errors='coerce')
    # Filtra imóveis que foram alienados
    df_mov = df_mov[df_mov['Data_Alienacao'].notna()]
    # Aplica limpeza final
    analises['movimentacao_imoveis'] = limpar_dataframe(df_mov)




    # Imóveis para venda
    df_imoveis = merges['imoveis_historico'].copy()

    # Normaliza a coluna Classe
    df_imoveis['Classe'] = df_imoveis['Classe'].str.lower().str.strip()

    # Filtra imóveis para venda
    imoveis_para_venda = df_imoveis[
        df_imoveis['Classe'].str.contains("imóveis para venda", na=False)
    ]

    # colunas_para_remover = [
    #     col for col in imoveis_para_venda.columns
    #     if any(sufixo in col for sufixo in ['_x', '_y']) or col in [
    #         'Versao', 'Versao_x', 'Versao_y',
    #         'Data_Referencia_x', 'Data_Referencia_y', 'Data_Referencia',
    #         'Outras_Caracteristicas_Relevantes_x', 'Outras_Caracteristicas_Relevantes_y',
    #         'Endereco_x', 'Endereco_y', 'Endereco'
    #     ]
    # ]
    #
    # imoveis_para_venda.drop(columns=colunas_para_remover, inplace=True, errors='ignore')

    analises['imoveis_para_venda'] = limpar_dataframe(
        imoveis_para_venda,
        colunas_obrigatorias=['Classe']
    )



    # Custos totais do exercício (Despesas)
    if 'Despesas_Exercicio' in merges['resultado_merge'].columns:
        analises['custos'] = limpar_dataframe(
            merges['resultado_merge'][['Nome_Fundo', 'Despesas_Exercicio']],
            colunas_obrigatorias=['Despesas_Exercicio']
        )

    # Informações qualitativas: Mercado e Público-Alvo
    colunas_qualitativas = ['Nome_Fundo', 'Publico_Alvo', 'Mercado']
    colunas_existentes = [col for col in colunas_qualitativas if col in merges['complemento_merge'].columns]

    analises['informacoes_qualitativas'] = limpar_dataframe(
        merges['complemento_merge'][colunas_existentes].drop_duplicates()
    )

    # Limpeza e arredondamento
    for chave, df in analises.items():
        if chave == 'distribuicao_vs_lucro':
            analises[chave] = limpar_dataframe(df, colunas_obrigatorias=['%Distribuido', 'Lucro_Contabil'])
        elif chave == 'ativos_tipo':
            analises[chave] = limpar_dataframe(df, colunas_obrigatorias=['Valor'])
        elif chave == 'liquidez':
            analises[chave] = limpar_dataframe(df, colunas_obrigatorias=['Ativo_Liquidez_Valor_Disponibilidades'])
        else:
            analises[chave] = limpar_dataframe(df)



    return analises


# ======================
# Execução Principal
# ======================
if __name__ == "__main__":

    links = listar_links_zip()
    for link in tqdm(links):
        zip_path = baixar_arquivo(link)
        descompactar_arquivo(zip_path)

    for ano in anos:
        print(f"\n=== Processando ano {ano} ===")
        dfs = carregar_dfs(ano, CAMINHO)
        dfs = padronizar_colunas_dfs(dfs)
       
        if not dfs:
            print(f"Nenhum dado encontrado para {ano}. Pulando...")
            continue
        try:

            merges = realizar_merges(dfs,ano)
            analises = gerar_analises(merges)
            for nome, df in analises.items():
                df.to_csv(f"{RESULTADO_ANALISES}/analise_{nome}_{ano}.csv", index=False)
        except Exception as e:
            print(f"Erro ao processar ano {ano}: {e}")

    print("\nTodas as análises foram exportadas com sucesso!")




