# 📊 Case FEGIK - Análise de Fundos Imobiliários (FIIs)

Este projeto realiza a análise de Fundos Imobiliários (FIIs) a partir dos dados trimestrais divulgados pela CVM. Ele é dividido em duas partes:

- `main.py`: coleta, trata e analisa os dados com pandas, gerando arquivos `.csv` com os resultados.
- `bi.py`: visualiza as análises por meio de um dashboard interativo com Streamlit.

## 🔧 Como rodar

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute a análise e geração dos dados:

```bash
python main.py
```

Rode o dashboard de Business Intelligence:

```bash
streamlit run bi.py
```

O dashboard será aberto automaticamente no navegador (normalmente em `http://localhost:8501`).

## 🗂️ Arquivos gerados

O script `main.py` gera arquivos `.csv` com as seguintes análises (uma por ano):

- `analise_ativos_tipo_{ano}.csv`
- `analise_direitos_valor_{ano}.csv`
- `analise_distribuicao_vs_lucro_{ano}.csv`
- `analise_imoveis_para_venda_{ano}.csv`
- `analise_informacoes_qualitativas_{ano}.csv`
- `analise_liquidez_{ano}.csv`
- `analise_movimentacao_imoveis_{ano}.csv`
- `analise_rentabilidade_media_{ano}.csv`
- `analise_vacancia_{ano}.csv`

Esses arquivos ficam na pasta `./analises`.

## 📁 Estrutura

```
├── main.py                      # Coleta, trata e analisa os dados
├── bi.py                        # Dashboard interativo (Streamlit)
├── analises/                    # Arquivos CSV de análise por ano
├── resources/
│   └── fegik_investimentos_logo.jpg
├── requirements.txt             # Bibliotecas necessárias
└── README.md
```

## 💻 Tecnologias utilizadas

- Python
- pandas
- plotly
- Streamlit
- Pillow (para carregamento de imagem)

## 👨‍💻 Autor

Desenvolvido por Henrique Parro para o Case FEGIK.
