import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA (ESTILO DASHBOARD PROFISSIONAL)
st.set_page_config(
    page_title="DataExtractor | Análise de Eventos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. ESTILO CSS PARA CUSTOMIZAÇÃO VISUAL
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        border: 1px solid #ececf1;
    }
    div.stButton > button:first-child {
        background-color: #007bff;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. BARRA LATERAL - NAVEGAÇÃO DO SISTEMA
with st.sidebar:
    st.title("🌐 DataSystem v1.0")
    st.markdown("---")
    menu = st.radio(
        "Navegação do Sistema:",
        ["🏠 Painel Inicial", "📁 Importar & Extrair", "📈 Gráficos Interativos"]
    )
    st.markdown("---")
    st.info("💡 **Dica:** Carregue o CSV na aba 'Importar' para libertar as análises.")

# 4. FUNÇÃO DE APOIO: EXTRAÇÃO DE METADADOS
def mostrar_kpis(df):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total de Linhas (Eventos)", df.shape[0])
    with c2:
        st.metric("Total de Colunas", df.shape[1])
    with c3:
        nulos = df.isnull().sum().sum()
        st.metric("Dados Ausentes", nulos, delta=f"{nulos} células", delta_color="inverse")
    with c4:
        cols_num = len(df.select_dtypes(include=['number']).columns)
        st.metric("Colunas Métricas", cols_num)

# 5. LÓGICA DAS PÁGINAS
if menu == "🏠 Painel Inicial":
    st.title("Bem-vindo ao DataExtractor Pro")
    st.markdown("""
    Esta aplicação foi desenhada para transformar ficheiros CSV brutos em insights visuais imediatos.
    
    **Como utilizar:**
    1. Vá até a aba **Importar & Extrair** no menu lateral.
    2. Arraste o seu ficheiro CSV (separado por vírgulas).
    3. O sistema fará o tratamento automático de datas e tipos de dados.
    4. Explore os resultados na aba de **Gráficos**.
    """)
    st.image("https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", width=200)

elif menu == "📁 Importar & Extrair":
    st.title("📁 Gestão de Ficheiros e Extração")
    
    arquivo_subido = st.file_uploader("Arraste o seu CSV aqui", type="csv")

    if arquivo_subido:
        # Carregar dados
        df = pd.read_csv(arquivo_subido, sep=',')
        
        # --- TRATAMENTO AUTOMÁTICO DE DATAS ---
        # Tenta identificar colunas que contenham "Date" ou "Data" no nome
        for col in df.columns:
            if any(palavra in col.lower() for palavra in ['date', 'data', 'start', 'end']):
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Guardar no estado da sessão para outras abas
        st.session_state['meu_df'] = df
        
        st.success("✅ Ficheiro processado com sucesso!")
        
        # Mostrar Indicadores
        st.subheader("📊 Resumo da Extração")
        mostrar_kpis(df)
        
        # Mostrar Tabela
        st.subheader("📋 Visualização dos Dados Brutos")
        st.dataframe(df, use_container_width=True)
        
        # Análise Estatística
        with st.expander("🔍 Ver Análise Estatística Detalhada"):
            st.write(df.describe(include='all', datetime_is_numeric=True).fillna("-"))

    else:
        st.warning("⚠️ Aguardando upload de ficheiro para iniciar a extração.")

elif menu == "📈 Gráficos Interativos":
    st.title("📈 Dashboard de Insights")
    
    if 'meu_df' in st.session_state:
        df = st.session_state['meu_df']
        
        # Filtros de Gráfico
        c1, c2 = st.columns([1, 4])
        
        with c1:
            st.subheader("Configurações")
            eixo_x = st.selectbox("Eixo X (Categorias/Datas)", df.columns)
            
            modo_y = st.radio("Métrica do Eixo Y:", ["Contagem de Eventos (Linhas)", "Valor de Coluna Numérica"])
            
            if modo_y == "Valor de Coluna Numérica":
                colunas_num = df.select_dtypes(include=['number']).columns
                if len(colunas_num) > 0:
                    eixo_y = st.selectbox("Selecione a Métrica", colunas_num)
                else:
                    st.error("Nenhuma coluna numérica encontrada.")
                    modo_y = "Contagem de Eventos (Linhas)"
            
            tipo_grafico = st.selectbox("Estilo do Gráfico", ["Barras", "Linhas", "Área", "Dispersão"])
            cor_por = st.selectbox("Colorir por (Legenda)", [None] + list(df.columns))

        with c2:
            st.subheader("Visualização")
            
            # Lógica de Construção do Gráfico com Plotly
            try:
                if modo_y == "Contagem de Eventos (Linhas)":
                    # Agrupa e conta linhas
                    df_plot = df.groupby(eixo_x).size().reset_index(name='Total de Eventos')
                    y_final = 'Total de Eventos'
                else:
                    df_plot = df
                    y_final = eixo_y

                if tipo_grafico == "Barras":
                    fig = px.bar(df_plot, x=eixo_x, y=y_final, color=cor_por, barmode='group', template="plotly_white")
                elif tipo_grafico == "Linhas":
                    fig = px.line(df_plot, x=eixo_x, y=y_final, color=cor_por, markers=True)
                elif tipo_grafico == "Área":
                    fig = px.area(df_plot, x=eixo_x, y=y_final, color=cor_por)
                else:
                    fig = px.scatter(df_plot, x=eixo_x, y=y_final, color=cor_por)

                fig.update_layout(hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Erro ao gerar gráfico: {e}")
    else:
        st.error("❌ Erro: Nenhum dado carregado. Vá à aba 'Importar & Extrair' primeiro.")

# 6. RODAPÉ
st.markdown("---")
st.caption("DataExtractor Pro - Desenvolvido para análise rápida de CSV em Python.")
