import streamlit as st
import pandas as pd
import time
from typing import Dict

def renderizar_movimentacoes(estoque_manager, tipo_usuario: str):
    """Renderiza a tab de Movimentações (Entrada/Saída), Edição e Exclusão."""
    st.subheader("🔄 Movimentações, Edição e Exclusão de Estoque")
    
    if tipo_usuario not in ["Administrador", "Operador"]:
        st.error("Acesso negado. Apenas usuários autenticados podem realizar movimentações e edições.")
        return

    # Obter dados e montar opções de seleção (usando gerar_relatorio)
    itens = estoque_manager.gerar_relatorio()
    
    # Criar um dicionário de opções para o Selectbox
    opcoes_estoque = {row["Código"]: f"{row['Código']} - {row['nome']} (Qtd: {row['Quantidade']})" 
                      for index, row in itens.iterrows()}

    opcoes_lista = [None] + list(opcoes_estoque.keys()) 
    
    
    # Tabs para organizar as diferentes funcionalidades
    tab_movimentacao, tab_edicao, tab_exclusao = st.tabs([
        "➕➖ Entrada/Saída", 
        "📝 Edição Detalhada", 
        "🗑️ Exclusão (Admin)"
    ])

    
    # Tab Movimentação (Entrada/Saída)
    with tab_movimentacao:
        st.markdown("### Registrar Entrada ou Saída")
        
        col_sel, col_qtd, col_tipo = st.columns([2, 1, 1])
        
        codigo_selecionado_mov = col_sel.selectbox(
            "Selecione o Item",
            options=opcoes_lista,
            format_func=lambda x: opcoes_estoque.get(x, "Selecione um Item..."),
            key="sel_mov"
        )
        
        quantidade_mov = col_qtd.number_input("Quantidade", min_value=1, step=1, value=1)
        tipo_movimentacao = col_tipo.radio("Tipo", ["Entrada", "Saída"], horizontal=True)
        observacao_mov = st.text_input("Observação (Motivo, NF, etc.)")
        
        submitted_mov = st.button("✅ Registrar Movimentação", use_container_width=True, 
                                  disabled=codigo_selecionado_mov is None)
        
        if submitted_mov:
            item_atual = estoque_manager.get_item_by_id(codigo_selecionado_mov)
            
            if item_atual is None:
                st.error("Item não encontrado no estoque.")
                
            elif tipo_movimentacao == "Entrada":
                if estoque_manager.entrada_estoque(codigo_selecionado_mov, quantidade_mov, observacao_mov):
                    st.success(f"Entrada de {quantidade_mov} unidades de **{item_atual['nome']}** registrada com sucesso.")
                    st.rerun()

            elif tipo_movimentacao == "Saída":
                if item_atual['quantidade'] < quantidade_mov:
                    st.error(f"Quantidade insuficiente no estoque. Disponível: {item_atual['quantidade']}")
                elif estoque_manager.saida_estoque(codigo_selecionado_mov, quantidade_mov, observacao_mov):
                    st.success(f"Saída de {quantidade_mov} unidades de **{item_atual['nome']}** registrada com sucesso.")
                    st.rerun()
                
    
    # Tab Edição Detalhada
    with tab_edicao:
        st.markdown("### 📝 Edição Detalhada")
        
        col_sel_edit, _ = st.columns([1, 2])
        with col_sel_edit:
            codigo_selecionado_edit = st.selectbox(
                "Selecione o Item para Edição",
                options=opcoes_lista,
                format_func=lambda x: opcoes_estoque.get(x, "Selecione um Item..."),
                key="sel_edit"
            )

        item_edit = None
        if codigo_selecionado_edit:
            item_edit = estoque_manager.get_item_by_id(codigo_selecionado_edit)

        if item_edit:
            st.info(f"Editando item: **{item_edit['nome']}**")
            
            # Mapeamento de campos.
            campos_para_edicao = {
                "Nome": {"campo_db": "nome", "tipo": "text", "valor_atual": item_edit.get("nome", "")},
                "Unidade": {"campo_db": "unidade", "tipo": "select", "opcoes": ["PÇ", "M", "KG", "UN", "CX"], "valor_atual": item_edit.get("unidade", "PÇ")},
                "Mínimo": {"campo_db": "minimo", "tipo": "number", "min_value": 0, "valor_atual": item_edit.get("minimo", 0)},
                "Máximo": {"campo_db": "maximo", "tipo": "number", "min_value": 1, "valor_atual": item_edit.get("maximo", 1)},
                "Localização": {"campo_db": "localizacao", "tipo": "text", "valor_atual": item_edit.get("localizacao", "")},
                "Fornecedor": {"campo_db": "fornecedor", "tipo": "text", "valor_atual": item_edit.get("fornecedor", "")},
                "Preço Unitário": {"campo_db": "preco", "tipo": "number", "min_value": 0.01, "valor_atual": item_edit.get("preco", 0.01)},
            }

            col_edit1, col_edit2 = st.columns(2)
            
            novos_valores = {}
            for i, (label, meta) in enumerate(campos_para_edicao.items()):
                col = col_edit1 if i % 2 == 0 else col_edit2
                
                with col:
                    if meta['tipo'] == 'text':
                        novos_valores[label] = st.text_input(label, value=meta['valor_atual'], key=f"edit_{meta['campo_db']}")
                        
                    elif meta['tipo'] == 'number':
                        is_price_field = meta['campo_db'] == 'preco'
                        
                        if is_price_field:
                            input_step = 0.01
                            input_type_func = float
                        else: 
                            input_step = 1
                            input_type_func = int

                        novos_valores[label] = st.number_input(
                            label, 
                            value=input_type_func(meta['valor_atual']), 
                            min_value=input_type_func(meta.get('min_value')), 
                            step=input_step, 
                            key=f"edit_{meta['campo_db']}"
                        )
                        
                    elif meta['tipo'] == 'select':
                        novos_valores[label] = st.selectbox(label, options=meta['opcoes'], index=meta['opcoes'].index(meta['valor_atual']), key=f"edit_{meta['campo_db']}")
            
            if st.button("✅ Salvar Edições", use_container_width=True):
                houve_mudanca = False
                for label, meta in campos_para_edicao.items():
                    campo_db = meta['campo_db']
                    novo_valor = novos_valores[label]
                    valor_atual = meta['valor_atual']

                    if novo_valor != valor_atual:
                        if estoque_manager.atualizar_item(codigo_selecionado_edit, campo_db, novo_valor):
                            houve_mudanca = True
                
                if houve_mudanca:
                    st.success("Item atualizado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Nenhuma alteração detectada para salvar.")


    # Tab Exclusão
    with tab_exclusao:
        st.markdown("### 🗑️ Exclusão Permanente de Item")
        
        if tipo_usuario != "Administrador":
            st.error("A exclusão de itens é uma operação crítica e é **restrita a Administradores**.")
            return

        col_sel_del, _ = st.columns([1, 2])
        with col_sel_del:
            codigo_selecionado_del = st.selectbox(
                "Selecione o Item para Exclusão",
                options=opcoes_lista,
                format_func=lambda x: opcoes_estoque.get(x, "Selecione um Item..."),
                key="sel_del"
            )

        item_del = None
        if codigo_selecionado_del:
            item_del = estoque_manager.get_item_by_id(codigo_selecionado_del)

        if item_del:
            st.warning(f"Confirme a exclusão permanente do item: **{item_del['nome']}** ({codigo_selecionado_del}). Esta ação não pode ser desfeita.")
            
            confirm_delete = st.checkbox(f"Eu confirmo que desejo **EXCLUIR** o item {codigo_selecionado_del}.", key="confirm_del")
            
            if st.button("🔴 EXCLUIR PRODUTO DEFINITIVAMENTE", use_container_width=True, disabled=not confirm_delete):
                if estoque_manager.excluir_item(codigo_selecionado_del):
                    st.success(f"Item {codigo_selecionado_del} excluído com sucesso!")
                    time.sleep(1)
                    st.rerun()