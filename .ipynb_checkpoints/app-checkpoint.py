import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configuração da página e tema
st.set_page_config(
    page_title="Dashboard SIH/SUS - Bahia",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. Funções de Carregamento e Pré-processamento (Otimizadas com Cache) ---

# Usar o cache do Streamlit para evitar reprocessar dados a cada interação
@st.cache_data
def carregar_dados():
    """Carrega e pré-processa todos os dados do notebook."""
    try:
        # Carrega a base de dados principal (AJUSTE O CAMINHO SE NECESSÁRIO)
        df = pd.read_parquet('datasets/RD202401.parquet')
        
        # Recorte de colunas de interesse
        colunas_interesse = [
            'UF_ZI', 'ESPEC', 'MUNIC_RES', 'SEXO', 'DIAR_ACOM', 'QT_DIARIAS', 
            'VAL_TOT', 'DT_INTER', 'DT_SAIDA', 'DIAG_PRINC', 'GESTRISCO',
            'COD_IDADE', 'IDADE', 'DIAS_PERM', 'MORTE', 'RACA_COR', 'CNES',
            'COMPLEX', 'MARCA_UTI', 'MUNIC_MOV', 'VAL_UTI' # Adicionei VAL_UTI
        ]
        df = df[colunas_interesse].copy()

        # Filtrar para a Bahia (código 29)
        df['UF_ZI'] = df['UF_ZI'].astype(str)
        df_bahia = df[df['UF_ZI'].str.startswith('29')].copy()

        # Conversões de Tipo
        df_bahia['DIAG_PRINC'] = df_bahia['DIAG_PRINC'].astype(str)
        df_bahia['CNES'] = df_bahia['CNES'].astype(str).str.strip()
        df_bahia['MORTE'] = pd.to_numeric(df_bahia['MORTE'], errors='coerce')
        df_bahia['IDADE'] = pd.to_numeric(df_bahia['IDADE'], errors='coerce')
        df_bahia['DIAS_PERM'] = pd.to_numeric(df_bahia['DIAS_PERM'], errors='coerce')
        df_bahia['VAL_TOT'] = pd.to_numeric(df_bahia['VAL_TOT'], errors='coerce')
        df_bahia['ESPEC'] = pd.to_numeric(df_bahia['ESPEC'], errors='coerce')
        df_bahia['COMPLEX'] = pd.to_numeric(df_bahia['COMPLEX'], errors='coerce')
        df_bahia['MARCA_UTI'] = pd.to_numeric(df_bahia['MARCA_UTI'], errors='coerce')
        df_bahia['GESTRISCO'] = pd.to_numeric(df_bahia['GESTRISCO'], errors='coerce')
        
        df_bahia['MUNIC_MOV'] = df_bahia['MUNIC_MOV'].astype(str).str.strip()

        # Limpeza e Mapeamento
        # Mapeamento Sexo: 1=Masc, 2=Fem (o código 3 do seu notebook é limpo para 2)
        df_bahia.loc[df_bahia['SEXO'] == 3, 'SEXO'] = 2
        
        # Criação de Faixa Etária
        bins = [0, 9, 19, 29, 39, 49, 59, 69, 79, 89, 99, 120]
        labels = ['0–9', '10–19', '20–29', '30–39', '40–49', '50–59', '60–69', '70–79', '80–89', '90–99', '100+']
        df_bahia['faixa_etaria'] = pd.cut(df_bahia['IDADE'].fillna(-1).astype(int), bins=bins, labels=labels, right=True, ordered=False)
        
        # Mapeamento do Status de Óbito
        map_obito = {0: 'Sem Óbito', 1: 'Com Óbito'}
        df_bahia['Status_Obito'] = df_bahia['MORTE'].map(map_obito)

        # Mapeamento de Raça/Cor
        map_raca_cor = {
            1: 'Branca', 2: 'Preta', 3: 'Parda', 4: 'Amarela', 5: 'Indígena', 99: 'Sem informação'
        }
        df_bahia['Raça/Cor'] = df_bahia['RACA_COR'].map(map_raca_cor).fillna('Não Informado')

        # Carrega dados de municípios (AJUSTE O CAMINHO SE NECESSÁRIO)
        df_municipios = pd.read_csv('datasets/municipios.csv')
        df_municipios['Codigo'] = df_municipios['Codigo'].astype(str).str[:6]
        df_municipios = df_municipios[df_municipios['Codigo'].str.startswith('29')]
        
        # Tratamento de datas (Necessário para filtros, embora não usado nos gráficos atuais)
        df_bahia['DT_INTER'] = pd.to_datetime(df_bahia['DT_INTER'], format='%Y%m%d', errors='coerce')
        df_bahia['DT_SAIDA'] = pd.to_datetime(df_bahia['DT_SAIDA'], format='%Y%m%d', errors='coerce')
        df_bahia.dropna(subset=['DT_INTER', 'DT_SAIDA'], inplace=True)
        
        return df_bahia, df_municipios

    except FileNotFoundError as e:
        st.error(f"Erro ao carregar o arquivo: {e}. Verifique se os arquivos de dados estão no diretório correto.")
        return pd.DataFrame(), pd.DataFrame()

df_bahia, df_municipios = carregar_dados()

if df_bahia.empty:
    st.stop()

# --- 2. Funções de Geração de Gráficos e Resultados (Adaptadas do notebook) ---

# Requisito 1: Quais cidades tem o maior numero de internações?
# Função plot_top_municipios (aproximadamente linha 94)
# Requisito 1: Quais cidades tem o maior numero de internações?
def plot_top_municipios(df_bahia, df_municipios):
    # Cria uma cópia temporária e remove NaNs para o cálculo
    df_temp = df_bahia.dropna(subset=['MUNIC_MOV']).copy()
    
    # Contagem das 10 cidades com mais internações (MUNIC_MOV já é string)
    contagem_internacoes = df_temp['MUNIC_MOV'].value_counts().nlargest(10).reset_index()
    contagem_internacoes.columns = ['MUNIC_MOV', 'INTER']
    
    # Merge com o dataframe de municípios (MUNIC_MOV e Codigo são strings)
    top_municipios = pd.merge(contagem_internacoes, df_municipios, left_on='MUNIC_MOV', right_on='Codigo', how='left')

    # Criando coluna com nome formatado
    top_municipios['Municipios'] = top_municipios['Nome'].fillna('CNES Inválido') + ' - BA'
    
    # Gráfico (agora fig será definida)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=top_municipios, x='INTER', y='Municipios', palette='viridis', ax=ax)
    ax.set_title('Top 10 Municípios com Maior Nº de Internações (Local)', fontsize=14)
    ax.set_xlabel('Total de Internações', fontsize=12)
    ax.set_ylabel('Município de Estabelecimento', fontsize=12)
    plt.tight_layout()
    return fig

# Requisito 2: Distribuição de internações por sexo
def plot_distribuicao_sexo(df_bahia):
    map_sexo = {1: 'Masculino', 2: 'Feminino'}
    sexo_counts = df_bahia['SEXO'].map(map_sexo).value_counts().reset_index()
    sexo_counts.columns = ['Sexo', 'QTD_INTERNAÇÕES']
    
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(data=sexo_counts, x='Sexo', y='QTD_INTERNAÇÕES', palette='pastel', ax=ax)
    ax.set_title('Distribuição de Internações por Sexo', fontsize=14)
    ax.set_xlabel('Sexo do paciente', fontsize=12)
    ax.set_ylabel('Número de Internações', fontsize=12)
    for container in ax.containers:
        ax.bar_label(container, fmt='%d', fontsize=10)
    plt.tight_layout()
    return fig

# Requisito 3: Faixa etária mais frequente
def plot_distribuicao_idade(df_bahia):
    faixa_counts = df_bahia['faixa_etaria'].value_counts().sort_index().reset_index()
    faixa_counts.columns = ['Faixa Etária', 'Internações']
    
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=faixa_counts, x='Faixa Etária', y='Internações', palette='crest', ax=ax)
    ax.set_title('Distribuição de Internações por Faixa Etária', fontsize=14)
    ax.set_xlabel('Faixa Etária', fontsize=12)
    ax.set_ylabel('Número de Internações', fontsize=12)
    plt.xticks(rotation=45)
    for container in ax.containers:
        ax.bar_label(container, fmt='%d', fontsize=10)
    plt.tight_layout()
    return fig

# Requisito 5: Percentual de óbitos
def calcular_percentual_obitos(df_bahia):
    total_internacoes = len(df_bahia)
    total_obitos = df_bahia[df_bahia['MORTE'] == 1].shape[0]
    percentual_obitos = (total_obitos / total_internacoes) * 100 if total_internacoes > 0 else 0
    return total_internacoes, total_obitos, percentual_obitos

# Requisito 7: Distribuição de pacientes por raça/cor
def plot_distribuicao_raca(df_bahia):
    raca_counts = df_bahia['Raça/Cor'].value_counts().reset_index()
    raca_counts.columns = ['Raça/Cor', 'Total_Internacoes']
    total_internacoes_bahia = raca_counts['Total_Internacoes'].sum()
    raca_counts['Percentual'] = (raca_counts['Total_Internacoes'] / total_internacoes_bahia) * 100
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=raca_counts,
        x='Percentual',
        y='Raça/Cor',
        palette='Set2',
        order=raca_counts.sort_values('Total_Internacoes', ascending=False)['Raça/Cor'],
        ax=ax
    )
    ax.set_title('Distribuição de Internações por Raça/Cor', fontsize=14)
    ax.set_xlabel('Percentual de Internações (%)', fontsize=12)
    ax.set_ylabel('Raça/Cor', fontsize=12)
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f%%', fontsize=10, padding=5)
    plt.tight_layout()
    return fig

# Requisito 8: Tempo médio de permanência por faixa etária
def plot_tempo_medio_idade(df_bahia):
    df_temp = df_bahia.dropna(subset=['DIAS_PERM', 'faixa_etaria']).copy()
    tempo_medio_permanencia = (
        df_temp.groupby('faixa_etaria', observed=True)['DIAS_PERM']
        .mean()
        .reset_index()
    )
    tempo_medio_permanencia.columns = ['Faixa_Etaria', 'Tempo_Medio_Permanencia_(dias)']
    
    # Ordem das faixas
    labels = ['0–9', '10–19', '20–29', '30–39', '40–49', '50–59', '60–69', '70–79', '80–89', '90–99', '100+']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=tempo_medio_permanencia,
        x='Tempo_Medio_Permanencia_(dias)',
        y='Faixa_Etaria',
        palette='magma',
        order=labels,
        ax=ax
    )
    ax.set_title('Tempo Médio de Permanência por Faixa Etária', fontsize=14)
    ax.set_xlabel('Tempo médio de permanência (dias)', fontsize=12)
    ax.set_ylabel('Faixa Etária', fontsize=12)
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f', fontsize=10, padding=5)
    plt.tight_layout()
    return fig

# Requisito 10: Distribuição por Capítulo Principal da CID-10
def plot_distribuicao_cid10(df_bahia):
    map_cid_capitulo = {
        'A': 'I. Doenças infecciosas', 'B': 'I. Doenças infecciosas',
        'C': 'II. Neoplasias (tumores)', 'D': 'III. Doenças sangue',
        'E': 'IV. Doenças endócrinas', 'F': 'V. Transtornos mentais',
        'G': 'VI. Doenças do sistema nervoso',
        'H': 'VII/VIII. Doenças do olho/ouvido',
        'I': 'IX. Doenças do aparelho circulatório',
        'J': 'X. Doenças do aparelho respiratório',
        'K': 'XI. Doenças do aparelho digestivo',
        'L': 'XII. Doenças da pele', 'M': 'XIII. Doenças osteomusculares',
        'N': 'XIV. Doenças do aparelho geniturinário', 'O': 'XV. Gravidez parto e puerpério',
        'P': 'XVI. Afecções perinatais', 'Q': 'XVII. Malformações congênitas',
        'R': 'XVIII. Sintomas sinais anormais',
        'S': 'XIX. Lesões envenenamentos', 'T': 'XIX. Lesões envenenamentos',
        'V': 'XX. Causas externas', 'W': 'XX. Causas externas',
        'X': 'XX. Causas externas', 'Y': 'XX. Causas externas',
        'Z': 'XXI. Contatos com serviços de saúde', 'U': 'XXII. Códigos especiais'
    }

    df_temp = df_bahia.dropna(subset=['DIAG_PRINC']).copy()
    df_temp = df_temp[df_temp['DIAG_PRINC'].str.len() >= 1].copy()
    df_temp['CAPITULO_CID'] = df_temp['DIAG_PRINC'].str[0].str.upper()
    df_temp['DESCRICAO_CAPITULO'] = df_temp['CAPITULO_CID'].map(map_cid_capitulo).fillna('Não Mapeado')

    frequencia_capitulos = df_temp['DESCRICAO_CAPITULO'].value_counts().reset_index()
    frequencia_capitulos.columns = ['Capitulo_CID', 'Frequencia']
    total_internacoes = frequencia_capitulos['Frequencia'].sum()
    frequencia_capitulos['Percentual'] = (frequencia_capitulos['Frequencia'] / total_internacoes) * 100

    ordem = frequencia_capitulos.sort_values(by='Frequencia', ascending=False)['Capitulo_CID']
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(
        data=frequencia_capitulos,
        x='Percentual',
        y='Capitulo_CID',
        palette='Spectral',
        order=ordem,
        ax=ax
    )
    ax.set_title('Internações por Capítulo Principal da CID-10', fontsize=14)
    ax.set_xlabel('Percentual (%)', fontsize=12)
    ax.set_ylabel('Capítulo CID-10', fontsize=12)
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f%%', fontsize=10, padding=5)
    plt.tight_layout()
    return fig

# --- 3. Estrutura do Dashboard no Streamlit ---

st.title("🏥 Dashboard de Internações Hospitalares (SIH/SUS) - Bahia")
st.markdown("Análise de dados de Autorizações de Internação Hospitalar (AIH) do SUS no estado da Bahia, baseada no arquivo `RD202401.csv`.")
st.markdown("---")


# --- METRICS (Requisitos 5, 16, 17) ---
st.header("🎯 Principais Métricas")

total_internacoes, total_obitos, percentual_obitos = calcular_percentual_obitos(df_bahia)
valor_total_gasto = df_bahia['VAL_TOT'].sum()
custo_medio_internacao = df_bahia['VAL_TOT'].mean()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total de Internações",
        value=f"{total_internacoes:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    )
with col2:
    st.metric(
        label="Percentual de Óbitos",
        value=f"{percentual_obitos:.2f}%",
        delta=f"{total_obitos:,.0f} Óbitos".replace(',', 'X').replace('.', ',').replace('X', '.')
    )
with col3:
    st.metric(
        label="Custo Total (VAL_TOT)",
        value=f"R$ {valor_total_gasto:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    )
with col4:
    st.metric(
        label="Custo Médio por Internação",
        value=f"R$ {custo_medio_internacao:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    )

st.markdown("---")

# --- GRÁFICOS E TABELAS (Análise Demográfica) ---

st.header("👥 Análise Demográfica dos Pacientes")

col_demografia1, col_demografia2 = st.columns(2)

with col_demografia1:
    st.subheader("Distribuição por Sexo")
    fig_sexo = plot_distribuicao_sexo(df_bahia)
    st.pyplot(fig_sexo)

with col_demografia2:
    st.subheader("Distribuição por Faixa Etária")
    fig_idade = plot_distribuicao_idade(df_bahia)
    st.pyplot(fig_idade)

st.markdown("---") # Opcional: separador visual

col_raca_tempo1, col_raca_tempo2 = st.columns(2)

with col_raca_tempo1:
    st.subheader("Distribuição por Raça/Cor")
    fig_raca = plot_distribuicao_raca(df_bahia)
    st.pyplot(fig_raca)

with col_raca_tempo2:
    st.subheader("Tempo Médio de Permanência por Faixa Etária")
    fig_tempo_idade = plot_tempo_medio_idade(df_bahia)
    st.pyplot(fig_tempo_idade)

# --- GRÁFICOS E TABELAS (Análise de Condições e Localização) ---

st.header("📍 Condições de Saúde e Localização")

col_local1, col_local2 = st.columns(2)

with col_local1:
    st.subheader("Top 10 Cidades de Estabelecimento")
    fig_municipios = plot_top_municipios(df_bahia, df_municipios)
    st.pyplot(fig_municipios)

with col_local2:
    st.subheader("Internações por Capítulo da CID-10 (Principal)")
    fig_cid = plot_distribuicao_cid10(df_bahia)
    st.pyplot(fig_cid)

st.markdown("---")

# --- ANÁLISE DETALHADA POR HOSPITAL (Requisitos 11, 12, 13, 15) ---
st.header("🏥 Análise por Hospital (CNES)")

# Função de formatação de valores R$ para as tabelas
def formatar_reais(valor):
    if pd.isna(valor):
        return "-"
    return f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

# 11: Top 10 Hospitais por Número de Internações
def get_top_hospitais_internacoes(df_bahia):
    df_temp = df_bahia.dropna(subset=['CNES']).copy()
    df_temp = df_temp[df_temp['CNES'].str.len() > 0].copy()
    frequencia_hospitais = df_temp['CNES'].value_counts().reset_index()
    frequencia_hospitais.columns = ['CNES', 'Total_Internacoes']
    return frequencia_hospitais.head(10)

# 12: Top 10 Hospitais por Tempo Médio de Permanência
def get_top_hospitais_tempo_medio(df_bahia):
    df_temp = df_bahia.dropna(subset=['CNES', 'DIAS_PERM']).copy()
    df_temp = df_temp[df_temp['CNES'].str.len() > 0].copy()
    tempo_medio_hospitais = (
        df_temp.groupby('CNES')['DIAS_PERM']
        .mean()
        .reset_index()
        .sort_values(by='DIAS_PERM', ascending=False)
    )
    tempo_medio_hospitais.columns = ['CNES', 'Tempo_Medio_Permanencia_(dias)']
    return tempo_medio_hospitais.head(10)

# 13: Top 10 Hospitais por Taxa de Mortalidade
def get_top_hospitais_mortalidade(df_bahia):
    df_temp = df_bahia.dropna(subset=['CNES', 'MORTE']).copy()
    df_temp['CNES'] = df_temp['CNES'].astype(str).str.strip()
    df_temp = df_temp[df_temp['CNES'].str.len() > 0].copy()
    
    mortalidade_hosp = df_temp.groupby('CNES').agg(
        Total_Internacoes=('MORTE', 'size'),
        Total_Obitos=('MORTE', lambda x: (x == 1).sum())
    ).reset_index()
    
    MIN_INTERNACOES = 50 
    mortalidade_hosp = mortalidade_hosp[mortalidade_hosp['Total_Internacoes'] >= MIN_INTERNACOES].copy()
    mortalidade_hosp['Taxa_Mortalidade_(%)'] = (mortalidade_hosp['Total_Obitos'] / mortalidade_hosp['Total_Internacoes']) * 100
    
    return mortalidade_hosp.sort_values(by='Taxa_Mortalidade_(%)', ascending=False).head(10)

# 15: Top 10 Hospitais por Proporção de Internações em UTI
def get_top_hospitais_uti(df_bahia):
    df_temp = df_bahia.dropna(subset=['CNES', 'MARCA_UTI']).copy()
    df_temp['CNES'] = df_temp['CNES'].astype(str).str.strip()
    df_temp = df_temp[df_temp['CNES'].str.len() > 0].copy()
    
    proporcao_uti_hosp = df_temp.groupby('CNES').agg(
        Total_Internacoes=('MARCA_UTI', 'size'),
        Total_UTI=('MARCA_UTI', lambda x: (x > 0).sum())
    ).reset_index()
    
    MIN_INTERNACOES = 50
    proporcao_uti_hosp = proporcao_uti_hosp[proporcao_uti_hosp['Total_Internacoes'] >= MIN_INTERNACOES].copy()
    proporcao_uti_hosp['Proporcao_UTI_(%)'] = (proporcao_uti_hosp['Total_UTI'] / proporcao_uti_hosp['Total_Internacoes']) * 100
    
    return proporcao_uti_hosp.sort_values(by='Proporcao_UTI_(%)', ascending=False).head(10)

# 18: Valor Médio das Internações: Óbito vs. Não Óbito
def get_valor_medio_obito(df_bahia):
    valor_medio_obito = (
        df_bahia.groupby('Status_Obito')['VAL_TOT']
        .mean()
        .reset_index()
        .sort_values(by='VAL_TOT', ascending=False)
    )
    valor_medio_obito.columns = ['Status', 'Valor_Medio_Internacao']
    valor_medio_obito['Valor_Medio_R$'] = valor_medio_obito['Valor_Medio_Internacao'].apply(formatar_reais)
    return valor_medio_obito[['Status', 'Valor_Medio_R$']]

# Exibir os resultados em colunas
col_hosp1, col_hosp2 = st.columns(2)

with col_hosp1:
    st.subheader("📈 Top 10 Hospitais por Internações")
    df_hosp_internacoes = get_top_hospitais_internacoes(df_bahia)
    st.dataframe(df_hosp_internacoes, hide_index=True)
    
    st.subheader("💀 Top 10 Hospitais por Taxa de Mortalidade (Min. 50 Internações)")
    df_hosp_mortalidade = get_top_hospitais_mortalidade(df_bahia)
    df_hosp_mortalidade['Taxa_Mortalidade_(%)'] = df_hosp_mortalidade['Taxa_Mortalidade_(%)'].map('{:.2f}%'.format)
    st.dataframe(df_hosp_mortalidade[['CNES', 'Total_Internacoes', 'Taxa_Mortalidade_(%)']], hide_index=True)


with col_hosp2:
    st.subheader("⏱️ Top 10 Hospitais por Tempo Médio de Permanência (dias)")
    df_hosp_tempo = get_top_hospitais_tempo_medio(df_bahia)
    df_hosp_tempo['Tempo_Medio_Permanencia_(dias)'] = df_hosp_tempo['Tempo_Medio_Permanencia_(dias)'].map('{:.2f}'.format)
    st.dataframe(df_hosp_tempo, hide_index=True)

    st.subheader(" intensive_care_unit: Top 10 Hospitais por Proporção de UTI (Min. 50 Internações)")
    df_hosp_uti = get_top_hospitais_uti(df_bahia)
    df_hosp_uti['Proporcao_UTI_(%)'] = df_hosp_uti['Proporcao_UTI_(%)'].map('{:.2f}%'.format)
    st.dataframe(df_hosp_uti[['CNES', 'Total_Internacoes', 'Proporcao_UTI_(%)']], hide_index=True)

st.markdown("---")

# --- ANÁLISE FINANCEIRA DE ÓBITOS E GESTRISCO (Requisitos 6, 18) ---
st.header("💲 Análise Financeira e Obstétrica")

col_fin1, col_fin2 = st.columns(2)

# Requisito 6: Proporção de gestantes de risco
def calcular_proporcao_gestrisco(df_bahia):
    df_obstetricas_bahia = df_bahia[df_bahia['ESPEC'] == 2].copy()
    total_obstetricas = len(df_obstetricas_bahia)
    total_gestrisco = df_obstetricas_bahia[df_obstetricas_bahia['GESTRISCO'] == 1].shape[0]
    proporcao_gestrisco = (total_gestrisco / total_obstetricas) * 100 if total_obstetricas > 0 else 0
    return total_obstetricas, total_gestrisco, proporcao_gestrisco

with col_fin1:
    st.subheader("Valor Médio de Internação: Óbito vs. Não Óbito")
    df_valor_obito = get_valor_medio_obito(df_bahia)
    st.dataframe(df_valor_obito, hide_index=True)

with col_fin2:
    total_obstetricas, total_gestrisco, proporcao_gestrisco = calcular_proporcao_gestrisco(df_bahia)
    st.subheader("Proporção de Gestantes de Risco (Internações Obstétricas)")
    st.metric(
        label="Total de Internações Obstétricas (ESPEC=2)",
        value=f"{total_obstetricas:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    )
    st.metric(
        label="Gestantes de Risco (GESTRISCO=1)",
        value=f"{total_gestrisco:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    )
    st.metric(
        label="Proporção de Risco",
        value=f"{proporcao_gestrisco:.2f}%"
    )

st.markdown("---")
st.caption("Dados de referência: SIH/SUS - Bahia (RD202401).")
