import streamlit as st
import pandas as pd
from typing import Dict
from datetime import datetime

def renderizar_estoque(estoque_manager, filtros: Dict):
    """Renderiza a tab de Visualização do Estoque (Apenas Leitura)."""
    st.subheader("📦 Visualização do Estoque")
    
    df_estoque = estoque_manager.gerar_relatorio()
    
    if df_estoque.empty:
        st.info("Nenhum item cadastrado no estoque.")
        return

    # Aplicação de Filtros 
    df_filtrado = df_estoque.copy()
    
    # Filtro de Busca (código ou nome)
    if filtros["busca"]:
        termo = filtros["busca"].lower()
        df_filtrado = df_filtrado[
            df_filtrado["Código"].str.lower().str.contains(termo) |
            df_filtrado["nome"].str.lower().str.contains(termo)
        ]

    # Filtro de Fornecedor
    if filtros["fornecedor"] != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Fornecedor"] == filtros["fornecedor"]]

    # Filtro de Localização
    if filtros["localizacao"] != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Localização"] == filtros["localizacao"]]

    # Filtro de Status
    if filtros["status"] != "Todos":
        status_map = {
            "Normal": " Normal",
            "Abaixo do Mínimo": " Abaixo do Mínimo",
            "Sem Estoque": " Sem Estoque",
            "Acima do Máximo": " Acima do Máximo"
        }
        status_filtrar = status_map.get(filtros["status"])
        if status_filtrar:
             df_filtrado = df_filtrado[df_filtrado["Status"] == status_filtrar]

    st.markdown(f"### Itens Encontrados: {len(df_filtrado)}")
    
    # Exibir tabela 
    st.dataframe(
        df_filtrado, 
        use_container_width=True,
        hide_index=True
    )
    
    csv_str = df_filtrado.to_csv(index=False, sep=';')
    csv_bytes = csv_str.encode('utf-8-sig')

    st.download_button(
        label="⬇️ Exportar Tabela (.csv)",
        data=csv_bytes,
        file_name=f'estoque_filtrado_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
        mime='text/csv',
        use_container_width=True
    )
    
    st.info("Para realizar **Movimentações (Entrada/Saída)**, **Editar Dados** ou **Excluir Itens**, utilize a aba **🔄 Movimentações**.")