# Arquivo: src/paginas/relatorios.py (CORRIGIDO PARA SUPABASE E CURVA ABC)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any

# --- Funções Auxiliares de Cálculo ---

def calcular_curva_abc(df_estoque: pd.DataFrame) -> pd.DataFrame:
    """Calcula a Curva ABC baseada no Valor Total de cada item."""
    
    # 1. Preparar o DataFrame para cálculo numérico
    # Gerar relatorio garante que df_estoque tenha todas as colunas necessárias e o 'Valor Total'
    df = df_estoque.copy()
    
    if df.empty:
        return pd.DataFrame()
        
    # Extrair e converter a coluna 'Valor Total' para float
    df['Valor_Numerico'] = (
        df['Valor Total']
        .astype(str)
        .str.replace('R$', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .str.strip()
        .astype(float)
    )

    # 2. Ordenar por Valor Total e calcular a participação
    df = df.sort_values(by='Valor_Numerico', ascending=False).reset_index(drop=True)
    df['Valor Acumulado'] = df['Valor_Numerico'].cumsum()
    
    valor_total_estoque = df['Valor_Numerico'].sum()
    
    df['% Valor Acumulado'] = (df['Valor Acumulado'] / valor_total_estoque) * 100
    df['% Item Acumulado'] = (df.index + 1) / len(df) * 100

    # 3. Classificação ABC
    def get_classe(percentual_valor):
        if percentual_valor <= 80:
            return 'A'
        elif percentual_valor <= 95:
            return 'B'
        else:
            return 'C'

    df['Classe ABC'] = df['% Valor Acumulado'].apply(get_classe)

    # 4. Formatação e seleção final
    df['Valor Total'] = df['Valor_Numerico'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df['% Valor Acumulado'] = df['% Valor Acumulado'].apply(lambda x: f"{x:,.2f}%".replace(",", "X").replace(".", ",").replace("X", "."))
    df['% Item Acumulado'] = df['% Item Acumulado'].apply(lambda x: f"{x:,.2f}%".replace(",", "X").replace(".", ",").replace("X", "."))
    
    return df[['Código', 'nome', 'Quantidade', 'Valor Total', 'Classe ABC', '% Valor Acumulado', '% Item Acumulado', 'Fornecedor', 'Localização']]


def calcular_consumo_medio(historico_data: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calcula o consumo diário médio de cada item com base no histórico de SAÍDAS."""
    
    if not historico_data:
        return {}
        
    df_hist = pd.DataFrame(historico_data)
    
    # Filtrar apenas saídas
    df_saidas = df_hist[df_hist['tipo'] == 'Saída'].copy()
    
    if df_saidas.empty:
        return {}
        
    # Converter 'data' para datetime
    df_saidas['data'] = pd.to_datetime(df_saidas['data'])

    
    return {} 

# --- Função Principal de Renderização ---

def renderizar_relatorios(estoque_manager):
    """Renderiza a tab de Relatórios e Análises (Análise de Dados)."""
    st.subheader("📊 Relatórios e Análises")
    
    # Gerar DataFrame e Estatísticas
    df_estoque = estoque_manager.gerar_relatorio()
    stats = estoque_manager.obter_estatisticas()
    
    if df_estoque.empty:
        st.info("Nenhum item cadastrado para gerar relatórios.")
        return

    # Seleção de relatório
    tipo_relatorio = st.selectbox(
        "Tipo de Relatório",
        ["Resumo Geral", "Análise por Fornecedor", "Análise por Localização", 
         "Itens Críticos", "Análise de Valor (Curva ABC)", "Previsão de Reposição"]
    )
    
    # -------------------------------------------------------------------------
    # 1. Resumo Geral
    # -------------------------------------------------------------------------
    if tipo_relatorio == "Resumo Geral":
        st.markdown("### 📋 Resumo Geral do Estoque")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Estatísticas Gerais**")
            st.write(f"- Total de SKUs: **{stats['total_itens']}**")
            st.write(f"- Quantidade total em estoque: **{stats['quantidade_total']:,.0f}**")
            st.write(f"- Valor Total de Estoque: **R$ {stats['valor_total']:,.2f}**")
            st.write(f"- Taxa de Ocupação (Em relação ao Máximo): **{stats['taxa_ocupacao']:,.2f}%**")
        
    # Gráfico 1: Distribuição por Status (Pizza - Bom para proporção)
        with col2: # Use a coluna correta (col_vis1 ou col2)
            st.markdown("#### 1. Distribuição por Status")
            status_counts = df_estoque['Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Quantidade']
            
            # --- NOVO MAPA DE CORES LÓGICO ---
            color_map = {
                '🟢 Normal': '#2ca02c',        # Verde
                '🟡 Abaixo do Mínimo': '#ff7f0e', # Laranja/Âmbar (Alerta)
                '🔴 Sem Estoque': '#d62728',     # Vermelho (Crítico)
                '🟠 Acima do Máximo': '#1f77b4'  # Azul (Atenção/Excesso)
            }
            
            fig_pie = px.pie(
                status_counts,
                values='Quantidade',
                names='Status',
                title='Proporção de SKUs por Status de Estoque',
                color='Status', # Define a coluna para mapeamento de cores
                color_discrete_map=color_map, # Aplica o mapa de cores
                height=380
            )
            # Melhoria na legenda e borda
            fig_pie.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
            st.plotly_chart(fig_pie, use_container_width=True)
            
    # -------------------------------------------------------------------------
    # 2. Análise por Fornecedor
    # -------------------------------------------------------------------------
    elif tipo_relatorio == "Análise por Fornecedor":
        st.markdown("### 🚚 Análise por Fornecedor")
        
        col1, col2 = st.columns(2)
        
        # Agrupamento por Fornecedor
        df_forn = df_estoque.copy()
        df_forn['Valor_Numerico'] = (
            df_forn['Valor Total']
            .astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False).str.strip().astype(float)
        )
        
        fornecedor_analise = df_forn.groupby('Fornecedor').agg(
            Total_SKUs=('Código', 'count'),
            Qtd_Total=('Quantidade', 'sum'),
            Valor_Total=('Valor_Numerico', 'sum')
        ).reset_index().sort_values('Valor_Total', ascending=False)
        
        fornecedor_analise['Valor Total'] = fornecedor_analise['Valor_Total'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        with col1:
            st.dataframe(fornecedor_analise[['Fornecedor', 'Total_SKUs', 'Qtd_Total', 'Valor Total']], use_container_width=True, hide_index=True)
            
        with col2:
            fig_bar = px.bar(
                fornecedor_analise,
                y='Fornecedor',
                x='Valor_Total',
                orientation='h',
                title='Valor Total de Estoque por Fornecedor',
                color='Valor_Total',
                color_continuous_scale=px.colors.sequential.Teal,
                height=450
            )
            fig_bar.update_layout(xaxis_title="Valor Total (R$)", yaxis_title="Fornecedor")
            st.plotly_chart(fig_bar, use_container_width=True)

    # -------------------------------------------------------------------------
    # 3. Análise por Localização
    # -------------------------------------------------------------------------
    elif tipo_relatorio == "Análise por Localização":
        st.markdown("### 📍 Análise por Localização")
        
        # Agrupamento por Localização
        localizacao_analise = df_estoque.groupby('Localização').agg(
            Total_SKUs=('Código', 'count'),
            Qtd_Total=('Quantidade', 'sum')
        ).reset_index().sort_values('Qtd_Total', ascending=False)
        
        st.dataframe(localizacao_analise, use_container_width=True, hide_index=True)
        
        fig_bar_loc = px.bar(
            localizacao_analise,
            x='Localização',
            y='Qtd_Total',
            title='Quantidade Total de Itens por Localização',
            color='Qtd_Total',
            color_continuous_scale=px.colors.sequential.Teal,
        )
        fig_bar_loc.update_layout(yaxis_title="Quantidade Total")
        st.plotly_chart(fig_bar_loc, use_container_width=True)

    # -------------------------------------------------------------------------
    # 4. Itens Críticos
    # -------------------------------------------------------------------------
    elif tipo_relatorio == "Itens Críticos":
        st.markdown("### 🚨 Itens Abaixo e Sem Estoque")
        
        df_criticos = df_estoque[
            (df_estoque['Status'] == '🔴 Sem Estoque') | 
            (df_estoque['Status'] == '🟡 Abaixo do Mínimo')
        ].sort_values('Quantidade', ascending=True)

        if df_criticos.empty:
            st.success("🎉 Nenhum item está em status crítico ou sem estoque. Ótimo trabalho!")
        else:
            st.info(f"Total de itens críticos/sem estoque: **{len(df_criticos)}**")
            st.dataframe(df_criticos[['Código', 'nome', 'Quantidade', 'Mínimo', 'Status', 'Fornecedor', 'Localização']], 
                         use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # 5. Análise de Valor (Curva ABC)
    # -------------------------------------------------------------------------
    elif tipo_relatorio == "Análise de Valor (Curva ABC)":
        st.markdown("### 💰 Análise de Valor e Curva ABC (80/15/5)")
        
        df_abc = calcular_curva_abc(df_estoque)
        
        if df_abc.empty:
            st.warning("Não foi possível calcular a Curva ABC.")
            return

        col_table, col_chart = st.columns([2, 3])
        
        with col_table:
            st.markdown("#### Tabela Curva ABC")
            df_grouped_abc = df_abc.groupby('Classe ABC').agg(
                Total_SKUs=('Código', 'count'),
                Porcentagem_Valor=('Valor Total', 'first') # Pega o valor acumulado do último item de cada classe
            ).reset_index()

            # Pega o último item (max) de cada classe para a % Valor Acumulado
            def get_max_percent(classe):
                last_index_of_class = df_abc[df_abc['Classe ABC'] == classe].index.max()
                if last_index_of_class is not None:
                    return df_abc.loc[last_index_of_class, '% Valor Acumulado']
                return "0.00%"
                
            df_grouped_abc['% Valor Total'] = df_grouped_abc['Classe ABC'].apply(get_max_percent)
            
            # Formata a tabela de resumo para exibição
            df_grouped_abc = df_grouped_abc.sort_values('Classe ABC')
            st.dataframe(df_grouped_abc[['Classe ABC', 'Total_SKUs', '% Valor Total']], hide_index=True)


        with col_chart:
            st.markdown("#### Distribuição da Curva ABC")
            fig_abc = px.bar(
                df_abc,
                x='% Item Acumulado',
                y='% Valor Acumulado',
                color='Classe ABC',
                title='Distribuição da Curva ABC (Itens x Valor)',
                color_discrete_map={'A': '#1f77b4', 'B': '#ff7f0e', 'C': '#2ca02c'}
            )
            fig_abc.add_trace(go.Scatter(
                x=df_abc['% Item Acumulado'].str.replace('%', '').str.replace(',', '.').astype(float),
                y=df_abc['% Valor Acumulado'].str.replace('%', '').str.replace(',', '.').astype(float),
                mode='lines',
                name='Curva Acumulada',
                line=dict(color='red', width=2)
            ))
            st.plotly_chart(fig_abc, use_container_width=True, height=450)
            
        st.markdown("---")
        st.markdown("#### Detalhes dos Itens (Ordenado por Valor)")
        st.dataframe(df_abc, use_container_width=True, hide_index=True)


    # -------------------------------------------------------------------------
    # 6. Previsão de Reposição (Modelo Simples de Demonstração)
    # -------------------------------------------------------------------------
    elif tipo_relatorio == "Previsão de Reposição":
        st.markdown("### ⏳ Previsão de Reposição (Modelo Simples)")
        
        st.info("""
        **Modelo de Reposição Simples (DEMO):** A previsão de consumo é baseada na diferença entre o Estoque Máximo e Mínimo, 
        simulando um ciclo de reposição de **30 dias**. 
        
        *Consumo Diário Médio (DEMO)* = (Qtd. Máxima - Qtd. Mínima) / 30 dias.
        """)
        
        df_reposicao = []
        
        # Filtra itens que estão abaixo do máximo e com alguma quantidade (para evitar divisão por zero)
        df_previsao = df_estoque[df_estoque['Quantidade'] > 0]
        
        for index, item in df_previsao.iterrows():
            # Consumo médio simulado para DEMO
            maximo = item['Máximo']
            minimo = item['Mínimo']
            quantidade_atual = item['Quantidade']
            
            # Simulação: a quantidade ideal para um ciclo de 30 dias é Max - Min.
            consumo_mensal_ideal = maximo - minimo
            
            if consumo_mensal_ideal <= 0: # Evita erro em caso de Max <= Min
                continue 
            
            consumo_diario = consumo_mensal_ideal / 30.0 # Dias do ciclo

            # Quantidade que falta para atingir o Mínimo
            qtd_ate_minimo = quantidade_atual - minimo
            
            # Dias até o Mínimo
            if consumo_diario > 0:
                dias_para_minimo = qtd_ate_minimo / consumo_diario
            else:
                dias_para_minimo = 999 # Se não há consumo, dias é alto

            # Só mostra itens que estão abaixo do estoque ideal (Máximo) e que vão atingir o mínimo em menos de 100 dias
            if quantidade_atual < maximo and dias_para_minimo < 100:
                df_reposicao.append({
                    "Código": item["Código"],
                    "nome": item["nome"],
                    "Qtd. Atual": item["Quantidade"],
                    "Mínimo": item["Mínimo"],
                    "Máximo": item["Máximo"],
                    "Consumo Diário Médio (DEMO)": round(consumo_diario, 2),
                    "Dias até Mínimo": round(dias_para_minimo, 1),
                    "Data Prevista (Mínimo)": (datetime.now() + timedelta(days=dias_para_minimo)).strftime("%d/%m/%Y"),
                    "Qtd. Sugerida para Compra": item["Máximo"] - item["Quantidade"]
                })
        
        if df_reposicao:
            df_reposicao = pd.DataFrame(df_reposicao)
            df_reposicao = df_reposicao.sort_values('Dias até Mínimo', ascending=True)
            
            st.dataframe(df_reposicao, use_container_width=True, hide_index=True)
            
            # Gráfico
            fig_reposicao_bar = px.bar(
                df_reposicao,
                y='nome',
                x='Dias até Mínimo',
                orientation='h',
                title='Itens com Maior Urgência de Reposição',
                color='Dias até Mínimo',
                color_continuous_scale=px.colors.sequential.Reds_r,
            )
            fig_reposicao_bar.update_layout(
                xaxis_title="Dias Estimados até Estoque Mínimo",
                yaxis_title="Produto",
                margin=dict(l=10, r=10, t=50, b=10)
            )
            st.plotly_chart(fig_reposicao_bar, use_container_width=True)
        else:
            st.info("Nenhum item com previsão de atingir o estoque mínimo em breve (ou todos estão em excesso).")