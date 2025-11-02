# Projeto de Análise de Dados do DataSUS (SIA e SINAN)

Este projeto para a análise exploratória de dados dos sistemas de saúde pública do Brasil (DataSUS), com foco no **Sistema de Informações Ambulatoriais (SIA)** e no **Sistema de Informação de Agravos de Notificação (SINAN)**, especificamente para casos de Dengue.

---

## 📝 Índice

* [Sobre o Projeto](#-sobre-o-projeto)
* [Estrutura dos Arquivos](#-estrutura-dos-arquivos)
* [Tecnologias Utilizadas](#-tecnologias-utilizadas)
* [Como Começar](#-como-começar)
    * [Pré-requisitos](#pré-requisitos)
    * [Instalação](#instalação)
* [Como Usar](#-como-usar)

---

## 📖 Sobre o Projeto

O objetivo deste repositório é processar, analisar e extrair insights de grandes volumes de dados do DataSUS. A análise principal está contida no notebook `sia.ipynb`, que provavelmente lida com os dados de produção ambulatorial (SIA).

O projeto também inclui datasets de amostra, como dados de notificação de Dengue do SINAN para 2024 e um arquivo de municípios, permitindo a análise e o cruzamento de informações.

## 🗂️ Estrutura dos Arquivos

* **`sia.ipynb`**: Notebook Jupyter principal contendo o código para análise dos dados do Sistema de Informações Ambulatoriais (SIA).
* **`datasets/`**: Diretório contendo os dados utilizados nas análises.
    * **`RD202401.parquet`**: Provavelmente um arquivo de "Produção Ambulatorial Reduzida" (SIA) referente a Janeiro de 2024, em formato Parquet.
    * **`sinan_dengue_sample_2024.parquet`**: Um arquivo de amostra com dados de notificações de Dengue do SINAN para o ano de 2024.
    * **`municipios.csv`**: Arquivo CSV contendo uma lista de municípios brasileiros, provavelmente com códigos IBGE, nomes e UFs.

## 🛠️ Tecnologias Utilizadas

* **Python 3.x**
* **Jupyter Notebook / Jupyter Lab**
* **Pandas** (ou Polars/DuckDB, para manipulação dos arquivos `.parquet`)
* **PyArrow** (para leitura de arquivos Parquet)

## 🏁 Como Começar

Siga estas instruções para configurar e rodar o projeto localmente.

### Pré-requisitos

Você precisará ter o Python 3 e um gerenciador de pacotes (como `pip`) instalados em sua máquina.

### Instalação

1.  Clone o repositório:
    ```bash
    git clone [https://github.com/seu-usuario/data-sus-project.git](https://github.com/seu-usuario/data-sus-project.git)
    ```
2.  Acesse o diretório do projeto:
    ```bash
    cd data-sus-project
    ```
3.  Instale as bibliotecas necessárias. (É recomendado criar um ambiente virtual).
    ```bash
    # Crie um ambiente virtual (opcional, mas recomendado)
    python -m venv venv
    source venv/bin/activate  # No Windows: .\venv\Scripts\activate
    
    # Instale as bibliotecas
    pip install jupyterlab pandas pyarrow
    ```

## 🏃 Como Usar

1.  Inicie o Jupyter Lab (ou Notebook) a partir do seu terminal:
    ```bash
    jupyter lab
    ```
2.  No seu navegador, abra o arquivo `sia.ipynb`.
3.  Execute as células do notebook para ver a análise de dados.

---
