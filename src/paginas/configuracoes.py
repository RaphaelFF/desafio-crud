import streamlit as st
import json
from datetime import datetime
import time

def renderizar_configuracoes(estoque_manager, tipo_usuario: str):
    """Renderiza a tab de Configurações (Status do Banco)."""
    st.subheader("⚙️ Configurações e Administração")
    
    if tipo_usuario != "Administrador":
        st.error("Acesso negado. Apenas Administradores podem acessar as configurações.")
        return
        
    st.markdown("### 💾 Status do Banco de Dados")
    
    # Obter dados para exibir contagem (usando os novos métodos)
    estoque_data = estoque_manager.get_estoque_data()
    historico_data = estoque_manager.get_historico_data()

    total_registros = len(estoque_data) if estoque_data else 0
    total_movimentacoes = len(historico_data) if historico_data else 0

    with st.container():
        st.info(f"""
        **Conexão:** ✅ Ativa (Supabase)
        **Tabela Produtos (Estoque):** **{total_registros}** registros
        **Tabela Histórico:** **{total_movimentacoes}** movimentações
        """)
        
        
    st.markdown("---")
    
    # Informações do sistema
    st.markdown("### ℹ️ Informações do Sistema")
    st.info(f"""
    **Versão da Aplicação:** 1.0.0  
    **Última Atualização do Módulo:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  
    **Gerenciador de Dados:** Supabase (PostgreSQL)  
    """)