import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict

def renderizar_dashboard(estoque_manager):
    """Renderiza a tab Dashboard com métricas e gráficos."""
    st.subheader("📈 Análise Visual e Métricas Chave")
    
    # Gerar dados
    df_estoque = estoque_manager.gerar_relatorio()
    stats = estoque_manager.obter_estatisticas()
    
    # Indicadores Chave
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("SKUs Totais", stats['total_itens'])
    col2.metric("Valor Total do Estoque", f"R$ {stats['valor_total']:,.2f}")
    col3.metric("Itens Críticos (Qtd < Mín.)", stats['itens_criticos'], delta_color="inverse")
    col4.metric("Itens em Excesso (Qtd > Máx.)", stats['itens_excesso'], delta_color="off")

    st.markdown("---")
    
    if df_estoque.empty:
        st.info("Nenhum item cadastrado no estoque para exibir no Dashboard.")
        return

    # Preparação para gráficos numéricos
    df_num = df_estoque.copy()
    df_num['Valor_Numerico'] = (
        df_num['Valor Total']
        .astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False).str.strip().astype(float)
    )

    # Análise de Estoque e Valor
    col_vis1, col_vis2 = st.columns(2)

    # Gráfico 1: Distribuição por Status (Pizza)
    with col_vis1:
        st.markdown("#### 1. Distribuição por Status")
        status_counts = df_estoque['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Quantidade']
        
        # Mapeamento de cores para status
        color_map = {
            ' Normal': '#2ca02c', 
            ' Abaixo do Mínimo': '#ff7f0e', 
            ' Sem Estoque': '#d62728',  
            ' Acima do Máximo': '#1f77b4'
        }
        
        fig_pie = px.pie(
            status_counts,
            values='Quantidade',
            names='Status',
            title='Proporção de SKUs por Status de Estoque',
            color='Status',
            color_discrete_map=color_map,
            height=380
        )
        fig_pie.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Gráfico 2: Top 10 Itens por Valor Total (Barras Horizontais)
    with col_vis2:
        st.markdown("#### 2. Top 10 Itens por Valor Total")
        df_top = df_num.nlargest(10, 'Valor_Numerico')

        fig_bar = px.bar(
            df_top,
            y='nome', 
            x='Valor_Numerico',
            orientation='h',
            title="Itens que mais representam valor no estoque (R$)",
            color='Valor_Numerico',
            color_continuous_scale=px.colors.sequential.Teal,
            height=380
        )
        fig_bar.update_layout(
            xaxis_title="Valor Total (R$)",
            yaxis_title="Produto"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

