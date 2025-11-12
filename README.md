# 🛍️ Sistema de Gerenciamento de Produtos

<div align="center">


Sistema de Gestão de Estoque

</div>

---


##  Sobre o Projeto

O **Sistema de Gestão de Estoque** é uma aplicação web completa, desenvolvida para proporcionar controle total, análise visual e funcionalidade de relatórios preditivos para o inventário. O projeto se integra ao Supabase para garantir a persistência e segurança dos dados.



---

## 📋 Objetivos Principais

-   Fornecer um **Dashboard** intuitivo com métricas-chave em tempo real para monitoramento da saúde do estoque.
-   Garantir a rastreabilidade completa das mudanças de inventário através de um **Histórico de Movimentações**.
-   Oferecer ferramentas de análise avançada, como **Curva ABC** e **Previsão de Reposição**.
-   Garantir a segurança e integridade dos dados por meio de autenticação de usuários e integração eficiente com o **Supabase**.


---

## 🚀 Tecnologias Utilizadas

**Frontend/App** | Python (Streamlit) 
**Backend/DB** | Supabase (PostgreSQL) |
**Análise de Dados** | Pandas / Plotly | Manipulação de dados, geração de DataFrames e gráficos dinâmicos. |
**Segurança** | hashlib | Hashing das senhas de usuários. |

---

## ✨ Funcionalidades


1. Dashboard (📈 Dashboard)
Foco Analítico: Veja instantaneamente os KPIs e os gráficos Plotly de distribuição de estoque e ranking de valor.

2. Gerenciar Produtos (📦 Estoque)
Filtros Avançados: Utilize a barra lateral para aplicar filtros em tempo real por Busca de Nome/ID, Status do Estoque, Fornecedor ou Localização.

Download: O botão de Download CSV abaixo da tabela permite exportar os dados filtrados com um único clique.

3. Cadastro (➕ Cadastro)
Acesso Restrito: Apenas para Administradores.

Formulário com validação ativa para garantir a integridade dos dados (preço > 0, mínimo < máximo).

4. Histórico (📜 Histórico)
Rastreabilidade: Exibe a tabela completa de todas as Entradas e Saídas de estoque, com data, hora e usuário responsável.

📁 Estrutura do Projeto
desafio-crud/
├── .streamlit/
│   └── secrets.toml             # Credenciais do Supabase e usuário admin
├── src/
│   ├── paginas/
│   │   ├── cadastro.py          # Lógica de interface CREATE
│   │   ├── dashboard.py         # Lógica de visualização com Pandas e Plotly
│   │   ├── estoque.py           # Lógica de interface READ/UPDATE/DELETE e Filtros
│   │   ├── historico.py         # Visualização do log de movimentações
│   │   ├── movimentacoes.py     # Lógica de entrada/saída de estoque
│   │   └── configuracoes.py     # Página de status e admin (Acesso restrito)
│   ├── gestor_estoque.py        # Camada de Lógica de Negócio e Validação
│   └── supabase_manager.py      # Camada de Conexão e Queries (DB/Cache)
├── app.py                       # Ponto de Entrada / Router principal Streamlit
├── requirements.txt             # Dependências Python (streamlit, pandas, plotly, supabase)
└── README.md                    # Este arquivo

---



