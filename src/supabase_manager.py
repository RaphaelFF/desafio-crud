import streamlit as st
import pandas as pd
from supabase import create_client, Client
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import time
import hashlib

# Hash de Senha (Função auxiliar)
def hash_senha(senha: str) -> str:
    """Hash de senha para segurança"""
    return hashlib.sha256(senha.encode()).hexdigest()

class SupabaseManager:
    """Gerencia a conexão e todas as operações CRUD com o Supabase."""
    
    def __init__(self, url: str, key: str):
   
        try:
            self.supabase: Client = create_client(url, key)
            st.cache_data.clear() 
            st.session_state.db_conectado = True
        except Exception as e:
            st.error(f"Erro ao conectar ao Supabase: {e}")
            st.session_state.db_conectado = False
            return
        
        self.TABELA_PRODUTOS = "produtos" 
        self.TABELA_HISTORICO = "historico"
        self.TABELA_USUARIOS = "usuarios" 
        pass 


    @st.cache_data(ttl=60)
    def get_estoque_data(_self) -> List[Dict[str, Any]]:
        """Busca todos os itens da tabela 'produtos' no Supabase."""
        try:
            response = _self.supabase.table(_self.TABELA_PRODUTOS).select("*").order("id").execute()
            return response.data
        except Exception as e:
            st.error(f"Erro ao buscar estoque: {e}")
            return []

    @st.cache_data(ttl=5)
    def get_historico_data(_self) -> List[Dict[str, Any]]:
        """Busca todas as movimentações da tabela 'historico'."""
        try:
            response = _self.supabase.table(_self.TABELA_HISTORICO).select("*").order("data", desc=True).execute()
            return response.data
        except Exception as e:
            st.error(f"Erro ao buscar histórico: {e}")
            return []

    def get_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Busca um item específico pelo ID (Não cacheado, usado para checagens em tempo real)."""
        try:
            response = self.supabase.table(self.TABELA_PRODUTOS).select("*").eq("id", item_id).limit(1).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception:
            return None

    @st.cache_data(ttl=60)
    def gerar_relatorio(_self) -> pd.DataFrame:
        """Busca dados brutos, calcula o status e o valor total, e retorna um DataFrame formatado."""
        data = _self.get_estoque_data() 
        
        if not data:
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        
        # Limpeza de dados 
        df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce', downcast='integer')
        df['minimo'] = pd.to_numeric(df['minimo'], errors='coerce', downcast='integer')
        df['maximo'] = pd.to_numeric(df['maximo'], errors='coerce', downcast='integer')
        df['preco'] = pd.to_numeric(df['preco'], errors='coerce')
        
        # Cálculo de Status
        def calcular_status(row):
            if row['quantidade'] == 0:
                return ' Sem Estoque'
            if row['quantidade'] < row['minimo']:
                return ' Abaixo do Mínimo'
            if row['quantidade'] > row['maximo']:
                return ' Acima do Máximo'
            return ' Normal'

        df['Status'] = df.apply(calcular_status, axis=1)

        # Cálculo do Valor Total
        df['Valor Total'] = df['quantidade'] * df['preco']
        
        # Formatação
        df['Preço'] = df['preco'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        df['Valor Total'] = df['Valor Total'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        # Seleção e Renomeação de Colunas
        df = df[['id', 'nome', 'unidade', 'quantidade', 'minimo', 'maximo', 'localizacao', 'fornecedor', 'preco', 'Status', 'Preço', 'Valor Total']].rename(columns={
            'id': 'Código',
            'nome': 'nome',
            'unidade': 'Unidade',
            'quantidade': 'Quantidade',
            'minimo': 'Mínimo',
            'maximo': 'Máximo',
            'localizacao': 'Localização',
            'fornecedor': 'Fornecedor',
            'preco': 'Preço Bruto' 
        })
        
        return df


    @st.cache_data(ttl=60)
    def obter_estatisticas(_self) -> Dict:
        """Retorna estatísticas do estoque baseado no relatório."""
        df = _self.gerar_relatorio() # Chama o método cacheado
        
        if df.empty:
            return {
                "total_itens": 0, "quantidade_total": 0, "valor_total": 0.0,
                "itens_criticos": 0, "itens_excesso": 0, "taxa_ocupacao": 0.0
            }
            
        df_num = df.copy()
        df_num['Quantidade'] = pd.to_numeric(df_num['Quantidade'], errors='coerce')
        df_num['Mínimo'] = pd.to_numeric(df_num['Mínimo'], errors='coerce')
        df_num['Máximo'] = pd.to_numeric(df_num['Máximo'], errors='coerce')
        df_num['Valor_Numerico'] = (
            df_num['Valor Total']
            .astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False).str.strip().astype(float)
        )
        
        qtd_total = df_num['Quantidade'].sum()
        valor_total = df_num['Valor_Numerico'].sum()
        
        itens_criticos = len(df_num[df_num['Quantidade'] < df_num['Mínimo']])
        itens_excesso = len(df_num[df_num['Quantidade'] > df_num['Máximo']])
        
        maximo_total = df_num['Máximo'].sum()
        taxa_ocupacao = (qtd_total / maximo_total) * 100 if maximo_total > 0 else 0
        
        return {
            "total_itens": len(df),
            "quantidade_total": qtd_total,
            "valor_total": valor_total,
            "itens_criticos": itens_criticos,
            "itens_excesso": itens_excesso,
            "taxa_ocupacao": taxa_ocupacao
        }

    # MÉTODOS CRUD (CREATE, UPDATE, DELETE) 

    def adicionar_item(self, item_id, nome, unidade, quantidade, minimo, maximo, localizacao, fornecedor, preco) -> bool:
        """Adiciona um novo item ao Supabase."""
        try:
            novo_item = {
                "id": item_id, 
                "nome": nome, 
                "unidade": unidade, 
                "quantidade": int(quantidade), 
                "minimo": int(minimo), 
                "maximo": int(maximo), 
                "localizacao": localizacao, 
                "fornecedor": fornecedor, 
                "preco": float(preco)
            }
            self.supabase.table(self.TABELA_PRODUTOS).insert(novo_item).execute()
            st.cache_data.clear() 
            return True
        except Exception as e:
            st.error(f"Erro ao adicionar item: {e}")
            return False

    def atualizar_item(self, item_id: str, campo: str, novo_valor: Any) -> bool:
        """Atualiza um único campo de um item no Supabase."""
        try:
            if campo in ['quantidade', 'minimo', 'maximo']:
                novo_valor = int(novo_valor)
            elif campo in ['preco']:
                novo_valor = float(novo_valor)
            
            self.supabase.table(self.TABELA_PRODUTOS).update({campo: novo_valor}).eq("id", item_id).execute()
            st.cache_data.clear()
            return True
        except Exception as e:
            st.error(f"Erro ao atualizar item: {e}")
            return False

    def excluir_item(self, item_id: str) -> bool:
        """Exclui um item do Supabase e seu histórico de movimentações."""
        try:
            self.supabase.table(self.TABELA_PRODUTOS).delete().eq("id", item_id).execute()
            self.supabase.table(self.TABELA_HISTORICO).delete().eq("id", item_id).execute()
            
            st.cache_data.clear()
            return True
        except Exception as e:
            st.error(f"Erro ao excluir item: {e}")
            return False

    # MÉTODOS DE MOVIMENTAÇÃO (UPDATE ESPECIALIZADO)

    def _registrar_historico(self, item_id: str, nome: str, tipo: str, quantidade_final: int, observacao: str) -> bool:
        """Registra a movimentação na tabela de histórico (Não cacheado)."""
        try:
            mov = {
                "id": item_id, 
                "nome": nome, 
                "tipo": tipo, 
                "quantidade": quantidade_final, 
                "data": datetime.now().isoformat(),
                "usuario": st.session_state.username if 'username' in st.session_state else 'Sistema',
                "observacao": observacao
            }
            self.supabase.table(self.TABELA_HISTORICO).insert(mov).execute()
            st.cache_data.clear()
            return True
        except Exception as e:
            st.error(f"Erro ao registrar histórico: {e}")
            return False
            
    def entrada_estoque(self, item_id: str, quantidade: int, observacao: str) -> bool:
        """Incrementa a quantidade do item e registra no histórico."""
        item_atual = self.get_item_by_id(item_id)
        if item_atual:
            nova_quantidade = item_atual['quantidade'] + quantidade
            if self.atualizar_item(item_id, 'quantidade', nova_quantidade):
                return self._registrar_historico(item_id, item_atual['nome'], "Entrada", nova_quantidade, observacao)
        return False
        
    def saida_estoque(self, item_id: str, quantidade: int, observacao: str) -> bool:
        """Decrementa a quantidade do item e registra no histórico."""
        item_atual = self.get_item_by_id(item_id)
        if item_atual and item_atual['quantidade'] >= quantidade:
            nova_quantidade = item_atual['quantidade'] - quantidade
            if self.atualizar_item(item_id, 'quantidade', nova_quantidade):
                return self._registrar_historico(item_id, item_atual['nome'], "Saída", nova_quantidade, observacao)
        return False

    # MÉTODOS DE AUTENTICAÇÃO

    @st.cache_data(ttl=3600)
    def buscar_usuario(_self, username: str) -> Optional[Dict[str, Any]]:
        """Busca o usuário pelo nome de usuário no Supabase."""
        try:
            response = _self.supabase.table(_self.TABELA_USUARIOS).select("*").eq("username", username).limit(1).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception:
            return None

    def autenticar_usuario(self, username: str, senha: str) -> Optional[str]:
        """Autentica o usuário e retorna o tipo de usuário se for bem-sucedido."""
        usuario_db = self.buscar_usuario(username)
        if usuario_db and usuario_db.get('senha_hash') == hash_senha(senha): 
            return usuario_db.get('tipo', 'Operador') 
        return None