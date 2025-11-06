import pandas as pd
import plotly.express as px
from shiny import App, render, ui, reactive
from shinywidgets import output_widget, render_widget
import shinyswatch
import os

# --- Configuração do Layout (UI) ---
app_ui = ui.page_fluid(
    shinyswatch.theme.flatly(),
    ui.h1("Dashboard SIH - Análise de Internações na Bahia (Janeiro 2024)"),
    
    ui.layout_sidebar(
        ui.sidebar(
            ui.h4("Filtros"),
            ui.output_ui("filtros_municipio_ui"),
            title="Controles"
        ),
        ui.navset_card_tab(
            ui.nav_panel("Visão Geral", 
                ui.row(
                    ui.column(6, ui.card(output_widget("plot_dist_sexo"))),
                    ui.column(6, ui.card(output_widget("plot_dist_faixa_etaria")))
                ),
                ui.row(
                    ui.column(6, ui.card(output_widget("plot_dist_raca"))),
                    ui.column(6, ui.card(output_widget("plot_morte_raca")))
                )
            ),
            ui.nav_panel("Análise Geográfica", 
                ui.card(output_widget("plot_top10_municipios"))
            ),
            ui.nav_panel("Análise Hospitalar", 
                ui.row(
                    ui.column(6, ui.card(output_widget("plot_top10_hospitais_internacoes"))),
                    ui.column(6, ui.card(output_widget("plot_top10_hospitais_morte")))
                ),
                ui.row(
                    ui.column(6, ui.card(output_widget("plot_top10_hospitais_uti"))),
                    ui.column(6, ui.card(output_widget("plot_top10_hospitais_valor")))
                )
            ),
            ui.nav_panel("Análise de Custos e Tempo",
                ui.row(
                    ui.column(6, ui.card(output_widget("plot_tempo_faixa_etaria"))),
                    ui.column(6, ui.card(output_widget("plot_custo_obito")))
                ),
                 ui.row(
                    ui.column(6, ui.card(output_widget("plot_tempo_sexo"))),
                    ui.column(6, ui.card(output_widget("plot_idade_espec")))
                )
            ),
            ui.nav_panel("Análise Obstétrica",
                ui.card(output_widget("plot_risco_gestacional"))
            )
        )
    )
)

# --- Lógica do Servidor ---
def server(input, output, session):

    # --- 1. Carregamento e Processamento de Dados (Reativo) ---
    
    @reactive.calc
    def load_data():
        # Tentar carregar os dados
        try:
            # Caminhos dos datasets
            base_path = 'datasets'
            path_sih = os.path.join(base_path, 'RD202401.csv')
            path_cnes = os.path.join(base_path, 'cnes_estabelecimentos.csv')
            path_municipios = os.path.join(base_path, 'municipios.csv')
            path_cid = os.path.join(base_path, 'cid_capitulos.csv')

            df = pd.read_csv(path_sih, sep=';', low_memory=False)
            df_cnes = pd.read_csv(path_cnes, sep=';', encoding='latin1', low_memory=False)
            df_municipios = pd.read_csv(path_municipios)
            cid_capitulos = pd.read_csv(path_cid)
            
            return df, df_cnes, df_municipios, cid_capitulos

        except FileNotFoundError as e:
            ui.notification_show(f"Erro: Arquivo não encontrado. Verifique a pasta 'datasets'. Detalhe: {e}", duration=10, type="error")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        except Exception as e:
            ui.notification_show(f"Erro ao carregar dados: {e}", duration=10, type="error")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    @reactive.calc
    def processed_data():
        df, df_cnes, df_municipios, cid_capitulos = load_data()
        
        if df.empty or df_cnes.empty or df_municipios.empty or cid_capitulos.empty:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        # Célula 4: Seleção de colunas
        colunas_interesse = [
            'UF_ZI', 'ANO_CMPT', 'MES_CMPT', 'ESPEC', 'N_AIH', 'IDENT', 'CEP', 'MUNIC_RES', 'NASC', 'SEXO',
            'UTI_MES_TO', 'MARCA_UTI', 'UTI_INT_TO', 'DIAR_ACOM', 'QT_DIARIAS', 'PROC_SOLIC',
            'PROC_REA', 'VAL_SH', 'VAL_SP', 'VAL_TOT', 'VAL_UTI', 'US_TOT', 'DT_INTER', 'DT_SAIDA',
            'DIAG_PRINC', 'DIAG_SECUN', 'COBRANCA', 'NATUREZA', 'NAT_JUR', 'GESTAO',
            'IND_VDRL', 'MUNIC_MOV', 'COD_IDADE', 'IDADE', 'DIAS_PERM', 'MORTE', 'NACIONAL',
            'CAR_INT', 'HOMONIMO', 'NUM_FILHOS', 'INSTRU', 'CID_NOTIF', 'CONTRACEP1',
            'CONTRACEP2', 'GESTRISCO', 'INSC_PN', 'SEQ_AIH5', 'CBOR', 'CNAER',
            'VINCPREV', 'GESTOR_COD', 'GESTOR_TP', 'GESTOR_DT', 'CNES', 'INFEHOSP', 
            'CID_ASSO', 'CID_MORTE', 'COMPLEX', 'FINANC', 'FAEC_TP', 'REGCT', 'RACA_COR', 'ETNIA',
            'VAL_SH_FED', 'VAL_SP_FED', 'VAL_SH_GES', 'VAL_SP_GES', 'VAL_UCI', 'MARCA_UCI'
        ]
        df = df[colunas_interesse].copy()
        
        # Células 6, 7: Conversão de tipo
        df['DIAG_PRINC'] = df['DIAG_PRINC'].astype(str)
        df['CID_NOTIF'] = df['CID_NOTIF'].astype(str)
        df['UF_ZI'] = df['UF_ZI'].astype(str)

        # Célula 9: Filtrar Bahia
        df_bahia = df[df['UF_ZI'].str.startswith('29')].copy()
        
        # Célula 10: Converter datas
        df_bahia['DT_INTER'] = pd.to_datetime(df_bahia['DT_INTER'], format='%Y%m%d', errors='coerce')
        df_bahia['DT_SAIDA'] = pd.to_datetime(df_bahia['DT_SAIDA'], format='%Y%m%d', errors='coerce')
        df_bahia = df_bahia.dropna(subset=['DT_INTER', 'DT_SAIDA'])
        
        # Célula 12: Limpar municípios
        df_municipios['Codigo'] = df_municipios['Codigo'].astype(str).str[:6]
        df_municipios_bahia = df_municipios[df_municipios['Codigo'].str.startswith('29')].copy()

        # Célula 22: Mapeamento CID
        cid_capitulos['Capitulo'] = cid_capitulos['Capitulo'].astype(str).str.zfill(2)
        df_bahia['Capitulo_CID'] = df_bahia['DIAG_PRINC'].str[0:2]
        df_bahia = df_bahia.merge(
            cid_capitulos,
            left_on='Capitulo_CID',
            right_on='Capitulo',
            how='left'
        )
        df_bahia['Nome_Capitulo'] = df_bahia['Nome_Capitulo'].fillna('Não especificado')
        
        # Mapeamentos de Células 16, 17, 19, 21
        df_bahia['IDADE_INT'] = df_bahia['IDADE'].fillna(0).astype(int)
        
        map_sexo = {1: 'Masculino', 3: 'Feminino'}
        df_bahia['Sexo_Descricao'] = df_bahia['SEXO'].map(map_sexo).fillna('Ignorado')
        
        map_raca = {1: 'Indígena', 2: 'Branca', 3: 'Parda', 4: 'Preta', 5: 'Amarela', 99: 'Sem informação'}
        df_bahia['Raca_Cor_Descricao'] = df_bahia['RACA_COR'].map(map_raca).fillna('Sem informação')
        
        map_obito = {0: 'Sem Óbito', 1: 'Com Óbito'}
        df_bahia['Status_Obito'] = df_bahia['MORTE'].map(map_obito)
        
        map_espec = {
            1: 'Clínico', 2: 'Cirúrgico', 3: 'Obstétricos', 4: 'Pediátricos', 5: 'Psiquiatria',
            7: 'Crônicos', 8: 'Reabilitação', 9: 'Pneumologia Sanitária (Tisiologia)',
            51: 'Leito Dia / Cirúrgicos', 57: 'Leito Dia / Aids', 62: 'Leito Dia / Saúde Mental'
        }
        df_bahia['Especialidade_Descricao'] = df_bahia['ESPEC'].map(map_espec).fillna('Outros')

        return df_bahia, df_cnes, df_municipios_bahia, cid_capitulos

    # --- 2. Filtros UI ---
    @render.ui
    def filtros_municipio_ui():
        _, _, df_municipios_bahia, _ = processed_data()
        if df_municipios_bahia.empty:
            return ui.p("Carregando filtros...")
        
        # Prepara lista de municípios
        lista_municipios = df_municipios_bahia.sort_values("Nome")
        opcoes = {row["Codigo"]: row["Nome"] for index, row in lista_municipios.iterrows()}
        opcoes = {"todos": "Todos os Municípios" , **opcoes}

        return ui.input_select(
            "municipio_filtro", 
            "Filtrar por Município de Residência:",
            opcoes,
            selected="todos"
        )

    # --- 3. Dados Filtrados ---
    @reactive.calc
    def filtered_df_bahia():
        df_bahia, _, _, _ = processed_data()
        municipio_selecionado = input.municipio_filtro()
        
        if df_bahia.empty or not municipio_selecionado:
            return pd.DataFrame()

        if municipio_selecionado == "todos":
            return df_bahia
        
        return df_bahia[df_bahia['MUNIC_RES'].astype(str) == municipio_selecionado].copy()


    # --- 4. Render Functions for Plots ---
    
    @render_widget
    def plot_top10_municipios():
        df_bahia_filtrado = filtered_df_bahia()
        _, _, df_municipios_bahia, _ = processed_data()
        if df_bahia_filtrado.empty: return px.bar(title="Dados não disponíveis")
        
        # Célula 14
        internacoes_por_municipio = df_bahia_filtrado['MUNIC_RES'].value_counts().reset_index()
        internacoes_por_municipio.columns = ['MUNIC_RES', 'Total_Internacoes']
        internacoes_por_municipio['MUNIC_RES'] = internacoes_por_municipio['MUNIC_RES'].astype(str)
        
        top_10_municipios = internacoes_por_municipio.merge(
            df_municipios_bahia,
            left_on='MUNIC_RES',
            right_on='Codigo',
            how='left'
        ).nlargest(10, 'Total_Internacoes').sort_values('Total_Internacoes', ascending=True)
        
        top_10_municipios['Nome'] = top_10_municipios['Nome'].fillna('Desconhecido')
        top_10_municipios['Texto'] = top_10_municipios['Total_Internacoes'].astype(str)

        fig = px.bar(
            top_10_municipios,
            x='Total_Internacoes',
            y='Nome',
            orientation='h',
            title='Top 10 Municípios com maior número de internações',
            labels={'Nome': 'Município', 'Total_Internacoes': 'Total de Internações'},
            text='Texto',
            color='Total_Internacoes',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False, height=600, yaxis={'title': 'Município de Residência'})
        return fig

    @render_widget
    def plot_dist_sexo():
        df_bahia_filtrado = filtered_df_bahia()
        if df_bahia_filtrado.empty: return px.bar(title="Dados não disponíveis")

        # Célula 16
        sexo_counts = df_bahia_filtrado['Sexo_Descricao'].value_counts().reset_index()
        sexo_counts.columns = ['Sexo', 'Internações']
        sexo_counts = sexo_counts[sexo_counts['Sexo'] != 'Ignorado']
        
        if sexo_counts['Internações'].sum() == 0:
             return px.bar(title='Distribuição de internações por sexo - Bahia', labels={'Sexo': 'Sexo do paciente', 'Internações': 'Número de internações'}).update_layout(showlegend=False, height=400)
             
        sexo_counts['Percentual'] = (sexo_counts['Internações'] / sexo_counts['Internações'].sum())
        sexo_counts['Texto'] = sexo_counts['Percentual'].map(lambda x: f'{x:.1%}') + '<br>' + sexo_counts['Internações'].map(lambda x: f'{x:,.0f}')

        fig = px.bar(
            sexo_counts,
            x='Sexo',
            y='Internações',
            text='Texto',
            color='Sexo',
            color_discrete_map={'Masculino': '#1f77b4', 'Feminino': '#e377c2'},
            title='Distribuição de internações por sexo - Bahia',
            labels={'Sexo': 'Sexo do paciente', 'Internações': 'Número de internações'}
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(showlegend=False, height=400)
        return fig
        
    @render_widget
    def plot_dist_faixa_etaria():
        df_bahia_filtrado = filtered_df_bahia()
        if df_bahia_filtrado.empty: return px.bar(title="Dados não disponíveis")

        # Célula 18
        bins = [0, 9, 19, 29, 39, 49, 59, 69, 79, 89, 99, 120]
        labels = ['0–9', '10–19', '20–29', '30–39', '40–49', '50–59', '60–69', '70–79', '80–89', '90–99', '100+']
        df_bahia_filtrado['faixa_etaria'] = pd.cut(df_bahia_filtrado['IDADE_INT'], bins=bins, labels=labels, right=True)
        
        faixa_counts = df_bahia_filtrado['faixa_etaria'].value_counts().sort_index().reset_index()
        faixa_counts.columns = ['Faixa Etária', 'Internações']

        fig = px.bar(
            faixa_counts,
            x='Faixa Etária',
            y='Internações',
            text='Internações',
            color='Faixa Etária',
            color_discrete_sequence=px.colors.sequential.Tealgrn,
            title='Distribuição de internações por faixa etária - Bahia',
            labels={'Faixa Etária': 'Faixa Etária', 'Internações': 'Número de internações'}
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(showlegend=False, height=500, bargap=0.3)
        return fig

    @render_widget
    def plot_idade_espec():
        df_bahia_filtrado = filtered_df_bahia()
        if df_bahia_filtrado.empty: return px.bar(title="Dados não disponíveis")
        
        # Célula 16 (Pergunta 4)
        idade_media_espec = df_bahia_filtrado.groupby('Especialidade_Descricao')['IDADE'].mean().reset_index()
        idade_media_espec.columns = ['Especialidade do Leito', 'Idade Média (anos)']
        idade_media_espec = idade_media_espec.sort_values(by='Idade Média (anos)', ascending=True).head(15)

        fig = px.bar(
            idade_media_espec,
            x='Idade Média (anos)',
            y='Especialidade do Leito',
            orientation='h',
            title='Idade média dos pacientes por especialidade de leito (Top 15)',
            text=idade_media_espec['Idade Média (anos)'].map(lambda x: f'{x:.1f}'),
            color='Idade Média (anos)',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False, height=600, bargap=0.3, coloraxis_showscale=False)
        return fig

    @render_widget
    def plot_morte_raca():
        df_bahia_filtrado = filtered_df_bahia()
        if df_bahia_filtrado.empty: return px.bar(title="Dados não disponíveis")

        # Célula 17 (Pergunta 5)
        taxa_mortalidade_raca = df_bahia_filtrado.groupby('Raca_Cor_Descricao')['MORTE'].mean() * 100
        taxa_mortalidade_raca = taxa_mortalidade_raca.reset_index()
        taxa_mortalidade_raca.columns = ['Raça/Cor', 'Taxa de Mortalidade (%)']
        taxa_mortalidade_raca = taxa_mortalidade_raca.sort_values(by='Taxa de Mortalidade (%)', ascending=True)

        fig = px.bar(
            taxa_mortalidade_raca,
            x='Taxa de Mortalidade (%)',
            y='Raça/Cor',
            orientation='h',
            title='Taxa de Mortalidade por Raça/Cor - Bahia',
            text=taxa_mortalidade_raca['Taxa de Mortalidade (%)'].map(lambda x: f'{x:.2f}%'),
            color='Raça/Cor',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False, height=500, bargap=0.3)
        return fig

    @render_widget
    def plot_risco_gestacional():
        df_bahia_filtrado = filtered_df_bahia()
        if df_bahia_filtrado.empty: return px.pie(title="Dados não disponíveis")
        
        # Célula 18 (Pergunta 6)
        df_obstetricas_bahia = df_bahia_filtrado[df_bahia_filtrado['ESPEC'] == 3].copy()
        if df_obstetricas_bahia.empty:
            return px.pie(title='Proporção de Gestantes de Risco - Bahia (Sem dados obstétricos)')

        total_obstetricas = df_obstetricas_bahia.shape[0]
        total_gestrisco = df_obstetricas_bahia[df_obstetricas_bahia['GESTRISCO'] == 1].shape[0]
        total_sem_risco = total_obstetricas - total_gestrisco
        
        data = {
            'Categoria': ['Gestante de Risco (GESTRISCO=1)', 'Outras Internações Obstétricas'],
            'Total': [total_gestrisco, total_sem_risco],
        }
        df_risco = pd.DataFrame(data)

        fig = px.pie(
            df_risco,
            values='Total',
            names='Categoria',
            title='Proporção de Gestantes de Risco (GESTRISCO=1) entre Internações Obstétricas - Bahia',
            color_discrete_sequence=['#c44e52', '#4c72b0'],
            hole=0.4
        )
        fig.update_traces(
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Total: %{value:,.0f}<br>Percentual: %{percent:.1%}<extra></extra>'
        )
        return fig

    @render_widget
    def plot_dist_raca():
        df_bahia_filtrado = filtered_df_bahia()
        if df_bahia_filtrado.empty: return px.bar(title="Dados não disponíveis")
        
        # Célula 19
        raca_counts = df_bahia_filtrado['Raca_Cor_Descricao'].value_counts(normalize=True) * 100
        raca_counts = raca_counts.reset_index()
        raca_counts.columns = ['Raça/Cor', 'Percentual']

        fig = px.bar(
            raca_counts,
            x='Percentual',
            y='Raça/Cor',
            orientation='h',
            title='Distribuição de Internações por Raça/Cor - Bahia',
            text=raca_counts['Percentual'].map(lambda x: f'{x:.1f}%'),
            color='Raça/Cor',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_traces(
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>%{x:.2f}% das internações'
        )
        fig.update_layout(showlegend=False, height=500, bargap=0.3, xaxis_title='Percentual de Internações (%)', yaxis_title='Raça/Cor')
        return fig

    @render_widget
    def plot_tempo_faixa_etaria():
        df_bahia_filtrado = filtered_df_bahia()
        if df_bahia_filtrado.empty: return px.bar(title="Dados não disponíveis")
        
        # Célula 20
        bins = [0, 9, 19, 29, 39, 49, 59, 69, 79, 89, 99, 120]
        labels = ['0–9', '10–19', '20–29', '30–39', '40–49', '50–59', '60–69', '70–79', '80–89', '90–99', '100+']
        
        df_bahia_filtrado['faixa_etaria'] = pd.cut(df_bahia_filtrado['IDADE_INT'], bins=bins, labels=labels, right=True, ordered=False)
        df_bahia_filtrado_clean = df_bahia_filtrado.dropna(subset=['DIAS_PERM', 'faixa_etaria'])
        
        tempo_medio_permanencia = (
            df_bahia_filtrado_clean.groupby('faixa_etaria', observed=True)['DIAS_PERM']
            .mean()
            .reset_index()
            .sort_values(by='DIAS_PERM', ascending=False)
        )
        tempo_medio_permanencia.columns = ['Faixa_Etaria', 'Tempo_Medio_Permanencia_(dias)']

        fig = px.bar(
            tempo_medio_permanencia,
            x='Tempo_Medio_Permanencia_(dias)',
            y='Faixa_Etaria',
            orientation='h',
            text=tempo_medio_permanencia['Tempo_Medio_Permanencia_(dias)'].map(lambda x: f'{x:.1f}'),
            color='Tempo_Medio_Permanencia_(dias)',
            color_continuous_scale='Magma',
            title='Tempo médio de permanência por faixa etária - Bahia'
        )
        fig.update_traces(
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Tempo médio: %{x:.1f} dias'
        )
        fig.update_layout(coloraxis_showscale=False, showlegend=False, height=600, bargap=0.3)
        return fig

    @render_widget
    def plot_tempo_sexo():
        df_bahia_filtrado = filtered_df_bahia()
        if df_bahia_filtrado.empty: return px.bar(title="Dados não disponíveis")
        
        # Célula 21
        df_bahia_sexo_valido = df_bahia_filtrado.dropna(subset=['DIAS_PERM', 'Sexo_Descricao'])
        df_bahia_sexo_valido = df_bahia_sexo_valido[df_bahia_sexo_valido['Sexo_Descricao'] != 'Ignorado']
        
        tempo_medio_sexo = df_bahia_sexo_valido.groupby('Sexo_Descricao')['DIAS_PERM'].mean().reset_index()
        tempo_medio_sexo.columns = ['Sexo', 'Tempo_Medio_Dias']

        fig = px.bar(
            tempo_medio_sexo,
            x='Sexo',
            y='Tempo_Medio_Dias',
            title='Tempo médio de permanência por sexo - Bahia',
            text=tempo_medio_sexo['Tempo_Medio_Dias'].map(lambda x: f'{x:.2f}'),
            color='Sexo',
            color_discrete_map={'Masculino': 'rgb(228,26,28)', 'Feminino': 'rgb(55,126,184)'}
        )
        fig.update_traces(
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Tempo médio: %{y:.2f} dias'
        )
        fig.update_layout(showlegend=False, height=450, bargap=0.3)
        return fig

    @render_widget
    def plot_top10_hospitais_internacoes():
        df_bahia, df_cnes, _, _ = processed_data()
        if df_bahia.empty or df_cnes.empty: return px.bar(title="Dados não disponíveis")
        
        # Célula 23
        df_cnes_clean = df_cnes[['CO_CNES', 'NO_FANTASIA']].copy()
        df_cnes_clean['CO_CNES'] = df_cnes_clean['CO_CNES'].astype(str).str.strip()
        df_bahia_clean = df_bahia.dropna(subset=['CNES']).copy()
        df_bahia_clean['CNES'] = df_bahia_clean['CNES'].astype(str).str.strip()

        df_bahia_merged = df_bahia_clean.merge(
            df_cnes_clean,
            left_on='CNES',
            right_on='CO_CNES',
            how='left'
        )
        df_bahia_merged['NO_FANTASIA'] = df_bahia_merged['NO_FANTASIA'].fillna('NÃO IDENTIFICADO')
        
        internacoes_por_hospital = df_bahia_merged['NO_FANTASIA'].value_counts().reset_index()
        internacoes_por_hospital.columns = ['Hospital', 'Total_Internacoes']
        top_10_hospitais = internacoes_por_hospital.nlargest(10, 'Total_Internacoes').sort_values(by='Total_Internacoes', ascending=True)

        fig = px.bar(
            top_10_hospitais,
            x='Total_Internacoes',
            y='Hospital',
            orientation='h',
            title='Top 10 Hospitais por Número de Internações - Bahia',
            text='Total_Internacoes',
            color='Total_Internacoes',
            color_continuous_scale='Blues'
        )
        fig.update_traces(
            textposition='outside',
            hovertemplate='<b>Hospital:</b> %{y}<br><b>Internações:</b> %{x}<extra></extra>'
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False, height=600, margin=dict(l=150))
        return fig

    @render_widget
    def plot_top10_hospitais_uti():
        df_bahia, df_cnes, _, _ = processed_data()
        if df_bahia.empty or df_cnes.empty: return px.bar(title="Dados não disponíveis")

        # Célula 24
        df_cnes_clean = df_cnes[['CO_CNES', 'NO_FANTASIA']].copy()
        df_cnes_clean['CO_CNES'] = df_cnes_clean['CO_CNES'].astype(str).str.strip()
        df_cnes_clean['NO_FANTASIA'] = df_cnes_clean['NO_FANTASIA'].astype(str).str.strip()
        
        df_bahia_clean = df_bahia.dropna(subset=['CNES', 'MARCA_UTI']).copy()
        df_bahia_clean['CNES'] = df_bahia_clean['CNES'].astype(str).str.strip()

        df_bahia_merged = df_bahia_clean.merge(
            df_cnes_clean,
            left_on='CNES',
            right_on='CO_CNES',
            how='left'
        )
        df_bahia_merged['NO_FANTASIA'] = df_bahia_merged['NO_FANTASIA'].fillna('NÃO IDENTIFICADO')
        
        proporcao_uti_hosp = df_bahia_merged.groupby(['CNES', 'NO_FANTASIA']).agg(
            Total_Internacoes=('MARCA_UTI', 'size'),
            Total_UTI=('MARCA_UTI', lambda x: (x > 0).sum())
        ).reset_index()
        
        MIN_INTERNACOES = 50
        proporcao_uti_hosp = proporcao_uti_hosp[
            proporcao_uti_hosp['Total_Internacoes'] >= MIN_INTERNACOES
        ].copy()
        
        proporcao_uti_hosp['Proporcao_UTI_(%)'] = (
            proporcao_uti_hosp['Total_UTI'] / proporcao_uti_hosp['Total_Internacoes'] * 100
        )
        
        top_10_uti = proporcao_uti_hosp.sort_values(
            by='Proporcao_UTI_(%)', ascending=False
        ).head(10).sort_values(by='Proporcao_UTI_(%)', ascending=True)

        fig = px.bar(
            top_10_uti,
            x='Proporcao_UTI_(%)',
            y='NO_FANTASIA',
            orientation='h',
            color='Proporcao_UTI_(%)',
            color_continuous_scale='Purples',
            text=top_10_uti['Proporcao_UTI_(%)'].map(lambda x: f"{x:.1f}%"),
            title='Top 10 Hospitais por Proporção de Internações em UTI - Bahia'
        )
        fig.update_traces(
            textposition='outside',
            hovertemplate='<b>Hospital:</b> %{y}<br><b>Proporção em UTI:</b> %{x:.1f}%<extra></extra>'
        )
        fig.update_layout(coloraxis_showscale=False, showlegend=False, height=600, margin=dict(l=150))
        return fig

    @render_widget
    def plot_top10_hospitais_morte():
        df_bahia, df_cnes, _, _ = processed_data()
        if df_bahia.empty or df_cnes.empty: return px.bar(title="Dados não disponíveis")
        
        # Célula 25
        df_cnes_clean = df_cnes[['CO_CNES', 'NO_FANTASIA']].copy()
        df_cnes_clean['CO_CNES'] = df_cnes_clean['CO_CNES'].astype(str).str.strip()
        df_cnes_clean['NO_FANTASIA'] = df_cnes_clean['NO_FANTASIA'].astype(str).str.strip()

        df_bahia_clean = df_bahia.dropna(subset=['CNES', 'MORTE']).copy()
        df_bahia_clean['CNES'] = df_bahia_clean['CNES'].astype(str).str.strip()

        df_bahia_merged = df_bahia_clean.merge(
            df_cnes_clean, left_on='CNES', right_on='CO_CNES', how='left'
        )
        df_bahia_merged['NO_FANTASIA'] = df_bahia_merged['NO_FANTASIA'].fillna('NÃO IDENTIFICADO')
        
        mortalidade_hospital = df_bahia_merged.groupby(['CNES', 'NO_FANTASIA']).agg(
            Total_Internacoes=('MORTE', 'size'),
            Total_Obitos=('MORTE', 'sum')
        ).reset_index()
        
        MIN_INTERNACOES_MORTE = 50
        mortalidade_hospital = mortalidade_hospital[
            mortalidade_hospital['Total_Internacoes'] >= MIN_INTERNACOES_MORTE
        ].copy()
        
        mortalidade_hospital['Taxa_Mortalidade_(%)'] = (
            mortalidade_hospital['Total_Obitos'] / mortalidade_hospital['Total_Internacoes'] * 100
        )
        
        top_10_mortalidade = mortalidade_hospital.sort_values(
            by='Taxa_Mortalidade_(%)', ascending=False
        ).head(10).sort_values(by='Taxa_Mortalidade_(%)', ascending=True)

        fig = px.bar(
            top_10_mortalidade,
            x='Taxa_Mortalidade_(%)',
            y='NO_FANTASIA',
            orientation='h',
            color='Taxa_Mortalidade_(%)',
            color_continuous_scale='Inferno',
            text=top_10_mortalidade['Taxa_Mortalidade_(%)'].map(lambda x: f"{x:.1f}%"),
            title='Top 10 Hospitais por Taxa de Mortalidade Hospitalar - Bahia'
        )
        fig.update_traces(
            textposition='outside',
            hovertemplate='<b>Hospital:</b> %{y}<br><b>Taxa Mortalidade:</b> %{x:.2f}%<extra></extra>'
        )
        fig.update_layout(coloraxis_showscale=False, showlegend=False, height=600, margin=dict(l=150))
        return fig

    @render_widget
    def plot_top10_hospitais_valor():
        df_bahia, df_cnes, _, _ = processed_data()
        if df_bahia.empty or df_cnes.empty: return px.bar(title="Dados não disponíveis")
        
        # Célula 26
        df_cnes_clean = df_cnes[['CO_CNES', 'NO_FANTASIA']].copy()
        df_cnes_clean['CO_CNES'] = df_cnes_clean['CO_CNES'].astype(str).str.strip()
        df_cnes_clean['NO_FANTASIA'] = df_cnes_clean['NO_FANTASIA'].astype(str).str.strip()

        df_bahia_clean = df_bahia.dropna(subset=['CNES', 'VAL_TOT']).copy()
        df_bahia_clean['CNES'] = df_bahia_clean['CNES'].astype(str).str.strip()

        df_bahia_merged = df_bahia_clean.merge(
            df_cnes_clean, left_on='CNES', right_on='CO_CNES', how='left'
        )
        df_bahia_merged['NO_FANTASIA'] = df_bahia_merged['NO_FANTASIA'].fillna('NÃO IDENTIFICADO')
        
        valor_medio_hospital = (
            df_bahia_merged.groupby(['CNES', 'NO_FANTASIA'])['VAL_TOT']
            .mean()
            .reset_index()
            .sort_values(by='VAL_TOT', ascending=False)
        )
        top_10_valor_medio = valor_medio_hospital.head(10).sort_values(by='VAL_TOT', ascending=True)

        fig = px.bar(
            top_10_valor_medio,
            x='VAL_TOT',
            y='NO_FANTASIA',
            orientation='h',
            color='VAL_TOT',
            color_continuous_scale='Greens',
            text=top_10_valor_medio['VAL_TOT'].map(lambda x: f"R$ {x:,.0f}"),
            title='Top 10 Hospitais por Valor Médio Total da AIH - Bahia'
        )
        fig.update_traces(
            textposition='outside',
            hovertemplate='<b>Hospital:</b> %{y}<br><b>Valor Médio AIH:</b> R$ %{x:,.2f}<extra></extra>'
        )
        fig.update_layout(coloraxis_showscale=False, showlegend=False, height=600, margin=dict(l=150))
        return fig
    
    @render_widget
    def plot_custo_obito():
        df_bahia_filtrado = filtered_df_bahia()
        if df_bahia_filtrado.empty: return px.bar(title="Dados não disponíveis")
        
        # Célula 30
        valor_medio_obito = (
            df_bahia_filtrado.groupby('Status_Obito')['VAL_TOT']
            .mean()
            .reset_index()
            .sort_values(by='VAL_TOT', ascending=False)
        )
        valor_medio_obito.columns = ['Status', 'Valor_Medio_Internacao']

        fig = px.bar(
            valor_medio_obito,
            x='Status',
            y='Valor_Medio_Internacao',
            title='Valor Médio das Internações: Óbito vs. Não Óbito - Bahia',
            text=valor_medio_obito['Valor_Medio_Internacao'].map(lambda x: f"R$ {x:,.0f}"),
            color='Status',
            color_discrete_map={'Com Óbito': '#c44e52', 'Sem Óbito': '#4c72b0'}
        )
        fig.update_traces(
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Valor Médio: R$ %{y:,.2f}<extra></extra>'
        )
        fig.update_layout(showlegend=False, height=500, margin=dict(l=40, r=20, t=60, b=40))
        return fig

# --- Inicia a Aplicação ---
app = App(app_ui, server)