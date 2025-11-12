import streamlit as st
from typing import Dict

def renderizar_cadastro(estoque_manager, tipo_usuario: str):
    """Renderiza a tab de Cadastro de Itens (CRUD - Create)."""
    st.subheader("➕ Cadastro de Novo Item")
    
    if tipo_usuario != "Administrador":
        st.error("Acesso negado. Apenas Administradores podem cadastrar novos itens.")
        return

    with st.form("cadastro_form"):
        st.markdown("### Dados do Produto")
        
        col_id, col_nome = st.columns(2)
        item_id = col_id.text_input("Código do Item (ID)", max_chars=10).upper()
        nome = col_nome.text_input("Nome do Item", max_chars=100)
        
        unidade = st.selectbox("Unidade de Medida", 
                               ["PÇ", "M", "KG", "UN", "CX"], index=0)
        
        col_qtd, col_min, col_max = st.columns(3)
        quantidade = col_qtd.number_input("Quantidade Inicial", min_value=0, step=1)
        minimo = col_min.number_input("Estoque Mínimo", min_value=0, step=1)
        maximo = col_max.number_input("Estoque Máximo", min_value=1, step=1, value=100)
        
        col_loc, col_forn, col_preco = st.columns(3)
        localizacao = col_loc.text_input("Localização (Ex: A-01)", max_chars=20)
        fornecedor = col_forn.text_input("Fornecedor Principal", max_chars=50)
        preco = col_preco.number_input("Preço Unitário (R$)", min_value=0.01, step=0.01)
        
        st.markdown("---")
        
        submitted = st.form_submit_button("✅ Cadastrar Item", use_container_width=True)
        
        if submitted:
            # 1. Validação de campos
            if not item_id or not nome:
                st.error("O Código do Item e o Nome são obrigatórios.")
                return
                
            if estoque_manager.get_item_by_id(item_id) is not None:
                st.error(f"O Código '{item_id}' já existe no estoque.")
                return

            # 3. Validação de limites
            if minimo >= maximo:
                st.error("Estoque Mínimo deve ser menor que o Estoque Máximo.")
                return
            
            # 4. Tentativa de Cadastro
            if estoque_manager.adicionar_item(item_id, nome, unidade, quantidade, 
                                            minimo, maximo, localizacao, 
                                            fornecedor, preco):
                st.success(f"Item '{nome}' cadastrado com sucesso!")
                st.balloons()
                
   