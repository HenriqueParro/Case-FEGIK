import streamlit as st
import pandas as pd
import os
import plotly.express as px
from PIL import Image



# Diretório onde estão os CSVs
CAMINHO_ANALISES = "./analises"

# Prefixos dos arquivos de análise
TIPOS_ANALISE = {
    "Ativos por Tipo": "analise_ativos_tipo",
    "Direitos por Valor": "analise_direitos_valor",
    "Distribuição vs Lucro": "analise_distribuicao_vs_lucro",
    "Imóveis para Venda": "analise_imoveis_para_venda",
    "Informações Qualitativas": "analise_informacoes_qualitativas",
    "Liquidez": "analise_liquidez",
    "Movimentação de Imóveis": "analise_movimentacao_imoveis",
    "Rentabilidade Média": "analise_rentabilidade_media",
    "Vacância": "analise_vacancia"
}

# Intervalo de anos gerados na análise
ANOS = list(range(2016, 2026))  # de 2016 a 2025

# Interface Streamlit
st.set_page_config(page_title="Dashboard FIIs", layout="wide")

# Estilo customizado
st.markdown(



    """
    <style>
    
      /* ======== Cores Gerais ======== */

    body {
        background-color: #1E304B;
        color: #FFFFFF;
    }
    .stApp {
        background-color: #1E304B;
        color: #FFFFFF;
    }
    
    /* Fundo geral e textos */
    body, .stApp {
        background-color: #0F2239;
        color: #FFFFFF;
    }

    h1, h2, h3, h4, h5, h6, .stMarkdown {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    label, .css-145kmo2 {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] button {
        color: #B7C4E1;
        border-color: #0F2239; 
        font-weight: bold;
    }

    .stTabs [aria-selected="true"] {
        color: #FFFFFF;
        border-bottom: 3px solid #7D7824;
    }

    /* ======== Sidebar com fundo branco ======== */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        color: #0F2239;
        border-right: 2px solid #676a24;
    }


    /* Textos da sidebar */
   
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #0F2239 !important;
        font-weight: 500;
        margin-bottom: 10px;
        background-color: transparent !important;
}
    
    section[data-testid="stSidebar"] h1 {
    color: #FFFFFF !important;
    font-weight: 700;
    background-color: #676a24;
    padding: 6px 10px;
    border-radius: 6px;
    display: inline-block;
    margin-bottom: 10px;
}

    /* Texto do slogan em azul-claro */
    .slogan {
        color: #B7C4E1 !important;
        font-weight: 400;
    }

    /* Destaque para "OLHOS NO FUTURO" */
    .destaque {
        color: #7D7824 !important;
        font-weight: bold;
    }

        [data-testid="collapsedControl"] {
        opacity: 1 !important;
        visibility: visible !important;
        pointer-events: auto !important;
        transition: opacity 0.3s ease-in-out;
        z-index: 1000 !important;
    }

    [data-testid="collapsedControl"] svg {
        opacity: 1 !important;
        visibility: visible !important;
        color: white !important;
        transition: opacity 0.3s ease, color 0.3s ease;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# Caminho absoluto ou relativo da imagem
caminho_logo = os.path.join("resources", "fegik_investimentos_logo.jpg")



# Barra lateral
with st.sidebar:
    st.title("📊 Dashboard FIIs")
    st.markdown("## 👁️‍🗨️ OLHOS NO FUTURO")
    st.markdown(
        "<span style='color:#B7C4E1'>Responsabilidade e transparência com dados</span>",
        unsafe_allow_html=True
    )

    st.markdown("<hr style='border-color:#1E304B'>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.image(Image.open(caminho_logo), use_container_width=True)





# Cria abas para cada tipo de análise
abas = st.tabs(TIPOS_ANALISE.keys())

# Preenche cada aba
for aba, (titulo, prefixo) in zip(abas, TIPOS_ANALISE.items()):
    with aba:
        st.subheader(f"📁 {titulo}")
        ano = st.selectbox(f"Ano da análise ({titulo})", ANOS, key=prefixo)

        caminho = os.path.join(CAMINHO_ANALISES, f"{prefixo}_{ano}.csv")

        try:
            df = pd.read_csv(caminho)
            st.dataframe(df, use_container_width=True)

            # Tentativa de plotar gráfico automaticamente
            colunas_numericas = df.select_dtypes(include="number").columns
            colunas_categoricas = df.select_dtypes(include="object").columns

            if len(colunas_numericas) >= 1 and len(colunas_categoricas) >= 1:
                fig = px.bar(
                    df,
                    x=colunas_categoricas[0],
                    y=colunas_numericas[0],
                    title=f"{colunas_numericas[0]} por {colunas_categoricas[0]}",
                    color_discrete_sequence=["#7D7824"]
                )
                fig.update_layout(
                    plot_bgcolor='#0F2239',
                    paper_bgcolor='#0F2239',
                    font_color='#FFFFFF',
                    title_font_color='#B7C4E1'
                )
                st.plotly_chart(fig, use_container_width=True)
        except FileNotFoundError:
            st.error(f"Arquivo `{prefixo}_{ano}.csv` não encontrado.")
        except Exception as e:
            st.error(f"Erro ao carregar: {e}")

