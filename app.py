import streamlit as st
import pandas as pd
import time
import json
from src.supabase_manager import SupabaseManager 
from src.paginas.dashboard import renderizar_dashboard
from src.paginas.estoque import renderizar_estoque
from src.paginas.cadastro import renderizar_cadastro
from src.paginas.movimentacoes import renderizar_movimentacoes
from src.paginas.relatorios import renderizar_relatorios
from src.paginas.historico import renderizar_historico
from src.paginas.configuracoes import renderizar_configuracoes

# Configuração da página e Estilos CSS
st.set_page_config(
    page_title="Sistema de Gestão de Estoque",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    /* Tema principal
    .stApp {
        background-color: #f5f5f5;
    }

   Cards de métricas */
    [data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
   
    
    /* Tabelas */
    .dataframe {
        font-size: 14px;
    }
    
    /* Botões personalizados */
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #0c4c78;
    }
    /* Centralizar o botão de login */
    .stButton {
        text-align: center;
    }
    
    /* Cor para alertas de status */
    .stAlert {
        border-radius: 10px;
    }

    /* Ocultar botão 'menu' do streamlit (hamburguer menu) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def main():
    
    # INICIALIZAÇÃO E CONEXÃO COM SUPABASE

    
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "usuario_atual" not in st.session_state:
        st.session_state.usuario_atual = "Recrutador (Demo)" 
    if "tipo_usuario" not in st.session_state:
        st.session_state.tipo_usuario = "Administrador" 
        
    if "db_conectado" not in st.session_state:
        st.session_state.db_conectado = False
        
    # Inicialização do SupabaseManager e conexão
    if "estoque_manager" not in st.session_state or not st.session_state.db_conectado:
        try:
            # Tenta obter as credenciais do secrets.toml (ou Streamlit Cloud Secrets)
            SUPABASE_URL = st.secrets["supabase"]["url"]
            SUPABASE_KEY = st.secrets["supabase"]["key"]
            
            # Inicializa o SupabaseManager
            st.session_state.estoque_manager = SupabaseManager(SUPABASE_URL, SUPABASE_KEY)
            
        except KeyError:
            st.error("❌ Erro de Conexão: As credenciais do Supabase não foram encontradas. Crie o arquivo `.streamlit/secrets.toml`.")
            st.session_state.db_conectado = False
            return 
        except Exception as e:
            st.error(f"❌ Erro ao inicializar o banco de dados: {e}")
            st.session_state.db_conectado = False
            return 

    # Alias para o gerenciador
    estoque_manager = st.session_state.estoque_manager 
    
 
    # TELA DE INTRODUÇÃO (DEMONSTRAÇÃO)
  
    if not st.session_state.autenticado:
        st.markdown("<h1 style='text-align: center; color: #1f77b4;'>📦 Sistema de Gestão de Estoque</h1>", unsafe_allow_html=True)
       
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<h2 style='text-align: center; color: #333;'>👋 Bem-vindo(a)!</h2>", unsafe_allow_html=True)
            st.markdown("---")
            st.info("""
            ### 🎯 Mensagem para o Recrutador(a)
            
            Este projeto é uma demonstração prática das minhas habilidades em **Engenharia de Dados** e **Desenvolvimento de Aplicações de Dados** com Python, Pandas e Streamlit.
            
            **Destaques para avaliação:**
            * **Arquitetura Modular (src/):** Código limpo e de fácil manutenção, separando a lógica de negócios da interface de usuário.
            * **Persistência de Dados:** Migração para o **Supabase (PostgreSQL)** com uso de cache (`@st.cache_data`) para otimização de consultas.
            * **Análise de Dados:** Uso robusto de Pandas para relatórios (`groupby`, Curva ABC) e Plotly para visualizações dinâmicas (Dashboard).
            
            Seu acesso de demonstração é como **Administrador**, permitindo total interação com as funções de Cadastro, Edição e Exclusão.
            """)
            st.markdown("---")
            
            if st.button("🚀 Iniciar Demonstração", use_container_width=True):
                st.session_state.autenticado = True
                st.rerun()

        return
    
 
    # INTERFACE PRINCIPAL
    
    # Sidebar e Filtros
    with st.sidebar:
        st.title("📦 Gestão de Estoque")
        st.markdown(f"**Usuário:** {st.session_state.usuario_atual}")
        st.markdown(f"**Tipo:** {st.session_state.tipo_usuario}")
        
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()
        
        st.markdown("---")
        
        st.subheader("🔍 Filtros")
        
        # Obtém todos os dados para extrair fornecedores/localizações (Dados do Supabase)
        df_completo = estoque_manager.gerar_relatorio() 
        
        # Lógica de Filtros
        busca = st.text_input("Buscar (código ou nome)")
        
        # Filtros baseados nos dados atuais do Supabase
        if not df_completo.empty:
            fornecedores = ["Todos"] + list(df_completo["Fornecedor"].unique())
            localizacoes = ["Todas"] + list(df_completo["Localização"].unique())
        else:
            fornecedores = ["Todos"]
            localizacoes = ["Todas"]


        fornecedor_filtro = st.selectbox("Fornecedor", fornecedores)
        
        status_filtro = st.selectbox("Status", 
                                    ["Todos", "Normal", "Abaixo do Mínimo", 
                                     "Sem Estoque", "Acima do Máximo"])
        
        localizacao_filtro = st.selectbox("Localização", localizacoes)
        
        # Dicionário de filtros para passar para as páginas
        filtros = {
            "busca": busca,
            "fornecedor": fornecedor_filtro,
            "status": status_filtro,
            "localizacao": localizacao_filtro
        }
    
    st.title("📊 Sistema de Gestão de Estoque")
    
    # Tabs principais
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📈 Dashboard", "📦 Estoque", "➕ Cadastro", 
        "🔄 Movimentações", "📊 Relatórios", "📜 Histórico", "⚙️ Configurações"
    ])
    
    # Roteamento 
    
    with tab1:
        renderizar_dashboard(estoque_manager)
    
    with tab2:
        renderizar_estoque(estoque_manager, filtros)
    
    with tab3:
        renderizar_cadastro(estoque_manager, st.session_state.tipo_usuario)
        
    with tab4:
        renderizar_movimentacoes(estoque_manager, st.session_state.tipo_usuario)
        
    with tab5:
        renderizar_relatorios(estoque_manager)
        
    with tab6:
        renderizar_historico(estoque_manager)
        
    with tab7:
        renderizar_configuracoes(estoque_manager, st.session_state.tipo_usuario)


if __name__ == "__main__":
    main()