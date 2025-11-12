# Arquivo: src/paginas/historico.py (CORRIGIDO PARA SUPABASE)

import streamlit as st
import pandas as pd
from typing import Dict

def renderizar_historico(estoque_manager):
    """Renderiza a tab de Histórico de Movimentações."""
    st.subheader("📜 Histórico de Movimentações")
    
    # --- CORREÇÃO: Usar o método do SupabaseManager ---
    historico_data = estoque_manager.get_historico_data() 
    
    if not historico_data:
        st.info("Nenhuma movimentação registrada ainda.")
        return
        
    df_historico = pd.DataFrame(historico_data)
    
    # Reordenar colunas e formatar (os nomes das colunas são os mesmos do DB)
    df_historico = df_historico[['data', 'tipo', 'id', 'nome', 'quantidade', 'usuario', 'observacao']]
    
    # Renomear para exibição
    df_historico.columns = [
        "Data/Hora", 
        "Tipo de Mov.", 
        "Cód. Item", 
        "Produto", 
        "Qtd. Final", 
        "Usuário",
        "Observação" # Incluindo a observação
    ]
    
    # Formatação de data/hora (Opcional, se precisar de um formato mais amigável)
    try:
        df_historico['Data/Hora'] = pd.to_datetime(df_historico['Data/Hora']).dt.strftime('%d/%m/%Y %H:%M:%S')
    except Exception:
        # Se a data não estiver no formato correto, usa o original
        pass
    
    st.dataframe(df_historico, use_container_width=True, hide_index=True)