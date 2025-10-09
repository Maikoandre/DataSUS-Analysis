# Projeto de Análise de Dados do DataSUS (SIH)

Este projeto foca na Análise Exploratória de Dados (EDA) de internações hospitalares do Sistema de Informações Hospitalares (SIH) do DataSUS. O objetivo é processar, analisar e extrair insights a partir dos microdados de Autorização de Internação Hospitalar (AIH).

O projeto é composto por duas partes principais:
1.  **Análise Exploratória (`notebooks/sih_analysis.ipynb`):** Um notebook Jupyter que detalha o processo de coleta, limpeza, pré-processamento e análise exploratória dos dados brutos (em formato `.csv`).
2.  **Dashboard Interativo (`app.py`):** Uma aplicação Streamlit que carrega dados pré-processados (em formato `.parquet`) e apresenta os principais indicadores e visualizações focados nas internações do estado da Bahia (BA).

## 📊 Principais Análises

O dashboard interativo (`app.py`) foca nos dados da Bahia e apresenta as seguintes métricas e visualizações:

### Visão Geral (Bahia)
* Total de Internações
* Custo Total e Custo Médio por Internação
* Percentual e Total de Óbitos

### Análise Demográfica
* Distribuição de internações por Sexo
* Distribuição por Faixa Etária
* Distribuição por Raça/Cor

### Análise Clínica e Operacional
* Tempo Médio de Permanência por Faixa Etária
* Distribuição das internações por Capítulo do CID-10 (Diagnóstico Principal)

### Análise Geográfica e Hospitalar
* Top 10 Municípios (local do estabelecimento) com maior número de internações.
* Top 10 Hospitais (por CNES) com:
    * Maior Número de Internações
    * Maior Taxa de Mortalidade (com filtro de N mínimo de internações)
    * Maior Tempo Médio de Permanência
    * Maior Proporção de Internações em UTI

## 🗂️ Estrutura do Projeto

* `app.py`: Aplicação principal do Dashboard Streamlit.
* `notebooks/sih_analysis.ipynb`: Notebook Jupyter com a análise exploratória (EDA) completa.
* `data/`: Diretório onde os dados devem ser armazenados.
* `LICENSE`: Licença do projeto.
* `.gitignore`: Arquivo de configuração do Git.

## 🛠️ Tecnologias Utilizadas

* **Python**
* **Streamlit**: Para o dashboard interativo.
* **Pandas**: Para manipulação e análise dos dados.
* **Jupyter Lab/Notebook**: Para a análise exploratória.
* **Plotly**: Para visualizações interativas (usado no notebook).
* **Seaborn & Matplotlib**: Para visualizações estáticas (usado no `app.py`).
* **PyArrow**: Para leitura de arquivos `.parquet`.

## 🏁 Como Executar

Siga estas instruções para configurar e executar o projeto localmente.

### 1. Pré-requisitos

É necessário ter o Python 3.x e o `pip` instalados.

### 2. Instalação

1.  Clone o repositório:
    ```bash
    git clone https://github.com/Maikoandre/DataSUS-Analysis.git
    cd DataSUS-Analysis
    ```

2.  (Recomendado) Crie e ative um ambiente virtual:
    ```bash
    python -m venv venv
    # Linux/macOS
    source venv/bin/activate
    # Windows
    .\venv\Scripts\activate
    ```

3.  Instale as dependências:
    ```bash
    pip install streamlit pandas matplotlib seaborn plotly pyarrow
    ```

### 3. Obtenção dos Dados

Este repositório não armazena os arquivos de dados. Você deve baixá-los manualmente e colocá-los em um diretório chamado `datasets/` na raiz do projeto.

Os arquivos necessários são:
* **Dados do SIH (AIH Reduzida):**
    * Para o **Notebook (`sih_analysis.ipynb`)**: Requer o arquivo `RD202401.csv` (ou o mês/ano de sua escolha) do [portal DataSUS](https://datasus.saude.gov.br/transferencia-de-arquivos/).
    * Para o **Dashboard (`app.py`)**: Requer o arquivo `RD202401.parquet`. O `app.py` espera este formato; você pode converter o `.csv` para `.parquet` para otimizar o carregamento.
* **Dados Auxiliares:**
    * `municipios.csv`: Arquivo de municípios brasileiros (provavelmente do IBGE).
    * `cnes_estabelecimentos.csv`: Arquivo de Cadastro Nacional de Estabelecimentos de Saúde (CNES), disponível no [portal DataSUS](https://datasus.saude.gov.br/transferencia-de-arquivos/).

### 4. Executando a Análise (Notebook)

1.  Inicie o Jupyter Lab:
    ```bash
    jupyter lab
    ```
2.  Abra o arquivo `notebooks/sih_analysis.ipynb` e execute as células.

### 5. Executando o Dashboard (Streamlit)

1.  Execute o `app.py` no seu terminal:
    ```bash
    streamlit run app.py
    ```
2.  O dashboard será aberto automaticamente no seu navegador.

## 📄 Licença

Este projeto é distribuído sob os termos da licença especificada no arquivo `LICENSE`.
