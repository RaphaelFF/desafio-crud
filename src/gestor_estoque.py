# Arquivo: src/gestor_estoque.py

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import hashlib
import time
from typing import Dict, List, Tuple, Optional
import random

class EstoqueManager:
    """Gerencia toda a lógica de estoque, incluindo dados, autenticação e histórico."""
    
    def __init__(self):
        self.estoque = {}
        self.historico = []
        self.usuarios = {
            "admin": {"senha": self.hash_senha("admin123"), "tipo": "Administrador"},
            "user": {"senha": self.hash_senha("user123"), "tipo": "Operador"}
        }
        self.inicializar_estoque()
    
    def hash_senha(self, senha: str) -> str:
        """Hash de senha para segurança"""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def inicializar_estoque(self):
        """Inicializa estoque com dados de exemplo baseados na planilha"""
        dados_exemplo = [
            {"id": "001", "nome": "ABRAÇADEIRA TIPO D 1/2", "descricao": "Abraçadeira de metal para fixação de tubos de 1/2 polegada.","unidade": "PÇ", 
             "quantidade": 50, "minimo": 10, "maximo": 100, "localizacao": "A-01", 
             "fornecedor": "Fornecedor A", "preco": 2.50},
            
            {"id": "002", "nome": "ABRAÇADEIRA TIPO D 3/4", "descricao": "Abraçadeira de metal para fixação de tubos de 1/2 polegada.","unidade": "PÇ", 
             "quantidade": 30, "minimo": 15, "maximo": 80, "localizacao": "A-02", 
             "fornecedor": "Fornecedor A", "preco": 3.00},
            
            {"id": "003", "nome": "ABRAÇADEIRA TIPO D 1", "descricao": "Abraçadeira de metal para fixação de tubos de 1/2 polegada.","unidade": "PÇ", 
             "quantidade": 5, "minimo": 20, "maximo": 60, "localizacao": "A-03", 
             "fornecedor": "Fornecedor A", "preco": 3.50},
            
            {"id": "004", "nome": "ABRAÇADEIRA TIPO D 2", "descricao": "Abraçadeira de metal para fixação de tubos de 1/2 polegada.","unidade": "PÇ", 
             "quantidade": 25, "minimo": 10, "maximo": 50, "localizacao": "A-04", 
             "fornecedor": "Fornecedor B", "preco": 4.50},
            
            {"id": "005", "nome": "ABRAÇADEIRA TIPO U 1/2", "descricao": "Abraçadeira de metal para fixação de tubos de 1/2 polegada.","unidade": "PÇ", 
             "quantidade": 100, "minimo": 30, "maximo": 200, "localizacao": "B-01", 
             "fornecedor": "Fornecedor B", "preco": 1.80},
            
            {"id": "006", "nome": "ABRAÇADEIRA TIPO U 3/4", "descricao": "Abraçadeira de metal para fixação de tubos de 1/2 polegada.","unidade": "PÇ", 
             "quantidade": 75, "minimo": 25, "maximo": 150, "localizacao": "B-02", 
             "fornecedor": "Fornecedor C", "preco": 2.20},
            
            {"id": "007", "nome": "PARAFUSO SEXTAVADO 1/2 x 2", "descricao": "Abraçadeira de metal para fixação de tubos de 1/2 polegada.","unidade": "PÇ", 
             "quantidade": 200, "minimo": 50, "maximo": 300, "localizacao": "C-01", 
             "fornecedor": "Fornecedor C", "preco": 0.50},
            
            {"id": "008", "nome": "PORCA SEXTAVADA 1/2", "descricao": "Abraçadeira de metal para fixação de tubos de 1/2 polegada.","unidade": "PÇ", 
             "quantidade": 150, "minimo": 50, "maximo": 250, "localizacao": "C-02", 
             "fornecedor": "Fornecedor D", "preco": 0.30},
            
            {"id": "009", "nome": "ARRUELA LISA 1/2", "descricao": "Abraçadeira de metal para fixação de tubos de 1/2 polegada.","unidade": "PÇ", 
             "quantidade": 180, "minimo": 100, "maximo": 300, "localizacao": "C-03", 
             "fornecedor": "Fornecedor D", "preco": 0.15},
            
            {"id": "010", "nome": "BUCHA DE REDUÇÃO 1 x 3/4", "descricao": "Abraçadeira de metal para fixação de tubos de 1/2 polegada.","unidade": "PÇ", 
             "quantidade": 8, "minimo": 20, "maximo": 60, "localizacao": "D-01", 
             "fornecedor": "Fornecedor E", "preco": 5.00}
        ]
        self.estoque = {}
        for item in dados_exemplo:
            item_id = item.pop("id")
            self.estoque[item_id] = {
                "nome": item["nome"], 
                "descricao": item["descricao"], 
                "unidade": item["unidade"],
                "quantidade": item["quantidade"],
                "minimo": item["minimo"],
                "maximo": item["maximo"],
                "localizacao": item["localizacao"],
                "fornecedor": item["fornecedor"],
                "preco": item["preco"], 
                "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def autenticar_usuario(self, usuario: str, senha: str) -> bool:
        """Autentica usuário"""
        if usuario in self.usuarios:
            return self.usuarios[usuario]["senha"] == self.hash_senha(senha)
        return False
    
    def adicionar_item(self, id: str, nome: str, unidade: str, 
                      quantidade: int, minimo: int, maximo: int, 
                      localizacao: str, fornecedor: str, preco: float) -> bool:
        """Adiciona novo item ao estoque"""
        if id in self.estoque:
            return False
        
        self.estoque[id] = {
            "nome": nome,
            "unidade": unidade,
            "quantidade": quantidade,
            "minimo": minimo,
            "maximo": maximo,
            "localizacao": localizacao,
            "fornecedor": fornecedor,
            "preco": preco,
            "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.registrar_historico("CADASTRO", id, nome, quantidade, 
                               st.session_state.usuario_atual)
        return True
    
    def excluir_item(self, item_id: str) -> bool:
        """Exclui um item do estoque baseado no ID"""
        if item_id in self.estoque:
            descricao = self.estoque[item_id]["nome"]
            del self.estoque[item_id]
            self.registrar_historico("EXCLUSÃO", item_id, descricao, 0, 
                                   st.session_state.usuario_atual)
            return True
        return False
    
    def atualizar_item(self, id: str, campo: str, valor) -> bool:
        """Atualiza campo específico de um item"""
        if id not in self.estoque:
            return False
        
        valor_anterior = self.estoque[id].get(campo)
        self.estoque[id][campo] = valor
        self.estoque[id]["ultima_atualizacao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.registrar_historico("ATUALIZAÇÃO", id, 
                               f"{campo}: {valor_anterior} → {valor}", 
                               self.estoque[id]["quantidade"], 
                               st.session_state.usuario_atual)
        return True
    
    def entrada_estoque(self, id: str, quantidade: int, observacao: str = "") -> bool:
        """Registra entrada no estoque"""
        if id not in self.estoque or quantidade <= 0:
            return False
        
        qtd_anterior = self.estoque[id]["quantidade"]
        self.estoque[id]["quantidade"] += quantidade
        self.estoque[id]["ultima_atualizacao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.registrar_historico("ENTRADA", id, 
                               f"Qtd: +{quantidade}. {observacao}", 
                               self.estoque[id]["quantidade"], 
                               st.session_state.usuario_atual)
        return True
    
    def saida_estoque(self, id: str, quantidade: int, observacao: str = "") -> bool:
        """Registra saída do estoque"""
        if id not in self.estoque or quantidade <= 0:
            return False
        
        if self.estoque[id]["quantidade"] < quantidade:
            return False
        
        self.estoque[id]["quantidade"] -= quantidade
        self.estoque[id]["ultima_atualizacao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.registrar_historico("SAÍDA", id, 
                               f"Qtd: -{quantidade}. {observacao}", 
                               self.estoque[id]["quantidade"], 
                               st.session_state.usuario_atual)
        return True
    
    def registrar_historico(self, tipo: str, id: str, nome: str, 
                          quantidade: int, usuario: str):
        """Registra operação no histórico"""
        registro = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": tipo,
            "id": id,
            "nome": nome,
            "quantidade": quantidade,
            "usuario": usuario
        }
        self.historico.append(registro)
    
    def obter_alertas(self) -> Dict[str, List]:
        """Retorna alertas de estoque"""
        alertas = {
            "critico": [],
            "baixo": [],
            "reposicao": [],
            "excesso": []
        }
        
        for id, item in self.estoque.items():
            qtd = item["quantidade"]
            minimo = item["minimo"]
            maximo = item["maximo"]
            
            if qtd == 0:
                alertas["critico"].append({
                    "id": id,
                    "nome": item["nome"],
                    "quantidade": qtd,
                    "minimo": minimo
                })
            elif qtd < minimo:
                alertas["baixo"].append({
                    "id": id,
                    "nome": item["nome"],
                    "quantidade": qtd,
                    "minimo": minimo
                })
            elif qtd < minimo * 1.2:
                alertas["reposicao"].append({
                    "id": id,
                    "nome": item["nome"],
                    "quantidade": qtd,
                    "minimo": minimo
                })
            elif qtd > maximo:
                alertas["excesso"].append({
                    "id": id,
                    "nome": item["nome"],
                    "quantidade": qtd,
                    "maximo": maximo
                })
        
        return alertas
    
    def gerar_relatorio(self) -> pd.DataFrame:
        """Gera relatório completo do estoque"""
        dados = []
        for id, item in self.estoque.items():
            dados.append({
                "Código": id,
                "nome": item["nome"],
                "Unidade": item["unidade"],
                "Quantidade": item["quantidade"],
                "Mínimo": item["minimo"],
                "Máximo": item["maximo"],
                "Localização": item["localizacao"],
                "Fornecedor": item["fornecedor"],
                "Valor Unit.": f"R$ {item['preco']:.2f}",
                "Valor Total": f"R$ {item['quantidade'] * item['preco']:.2f}",
                "Status": self.get_status(item["quantidade"], item["minimo"], item["maximo"]),
                "Última Atualização": item["ultima_atualizacao"]
            })
        
        return pd.DataFrame(dados)
    
    def get_status(self, qtd: int, minimo: int, maximo: int) -> str:
        """Retorna status do item baseado na quantidade"""
        if qtd == 0:
            return "🔴 Sem Estoque"
        elif qtd < minimo:
            return "🟡 Abaixo do Mínimo"
        elif qtd > maximo:
            return "🟠 Acima do Máximo"
        else:
            return "🟢 Normal"
    
    def buscar_item(self, termo: str) -> Dict:
        """Busca item por código ou nome"""
        resultados = {}
        termo_lower = termo.lower()
        
        for id, item in self.estoque.items():
            if (termo_lower in id.lower() or 
                termo_lower in item["nome"].lower()):
                resultados[id] = item
        
        return resultados
    
    def calcular_valor_total(self) -> float:
        """Calcula valor total do estoque"""
        total = 0
        for item in self.estoque.values():
            total += item["quantidade"] * item["preco"]
        return total
    
    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas do estoque"""
        qtd_total = sum(item["quantidade"] for item in self.estoque.values())
        itens_criticos = len([1 for item in self.estoque.values() 
                            if item["quantidade"] < item["minimo"]])
        itens_excesso = len([1 for item in self.estoque.values() 
                           if item["quantidade"] > item["maximo"]])
        
        # Prevenção de divisão por zero
        maximo_total = sum(item["maximo"] for item in self.estoque.values())
        taxa_ocupacao = (qtd_total / maximo_total) * 100 if maximo_total > 0 else 0
        
        return {
            "total_itens": len(self.estoque),
            "quantidade_total": qtd_total,
            "valor_total": self.calcular_valor_total(),
            "itens_criticos": itens_criticos,
            "itens_excesso": itens_excesso,
            "taxa_ocupacao": taxa_ocupacao
        }