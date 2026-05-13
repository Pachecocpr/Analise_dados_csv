import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="DataExtractor Pro", layout="wide")

# --- ESTILO CSS PARA PARECER SISTEMA ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (NAVEGAÇÃO) ---
with st.sidebar:
    st.title("🌐 DataSystem")
    menu = st.radio("Navegação", ["Início", "Explorador de Dados", "Gráficos Avançados"])
    st.info("Dica: Arraste o ficheiro na aba 'Explorador'")

# --- LÓGICA DE EXTRAÇÃO DE DADOS ---
def extrair_maximo_info(df):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Linhas", df.shape[0])
    col2.metric("Total de Colunas", df.shape[1])
    col3.metric("Dados em Falta (Nulos)", df.isnull().sum().sum())
    col4.metric("Colunas Numéricas", len(df.select_dtypes(include=['number']).columns))

# --- PÁGINAS ---
if menu == "Início":
    st.title("Bem-vindo ao Extração Inteligente")
    st.write("Selecione 'Explorador de Dados' para subir o seu ficheiro CSV e iniciar o tratamento automático.")

elif menu == "Explorador de Dados":
    st.title("📁 Importação e Tratamento")
    arquivo = st.file_uploader("Arraste o seu CSV aqui", type="csv")

    if arquivo:
        # Lendo o arquivo (Tratando separador por vírgula)
        df = pd.read_csv(arquivo, sep=',')
        
        # Tentativa automática de converter datas
        for col in df.columns:
            if 'Date' in col or 'date' in col:
                df[col] = pd.to_datetime(df[col], errors='ignore')

        st.session_state['meu_df'] = df # Salva na memória do sistema
        
        st.subheader("📊 Resumo Automático")
        extrair_maximo_info(df)
        
        st.subheader("📋 Tabela de Dados")
        st.dataframe(df, use_container_width=True)
        
        st.subheader("🔍 Análise por Coluna")
        st.write(df.describe(include='all').fillna('-'))

elif menu == "Gráficos Avançados":
    st.title("📈 Visualização de Insights")
    if 'meu_df' in st.session_state:
        df = st.session_state['meu_df']
        
        c1, c2 = st.columns([1, 3])
        with c1:
            col_x = st.selectbox("Eixo X (Categorias)", df.columns)
            col_y = st.selectbox("Eixo Y (Contagem ou Valor)", df.select_dtypes(include=['number']).columns)
            tipo_grafico = st.selectbox("Tipo", ["Barras", "Linhas", "Dispersão"])

        with c2:
            if tipo_grafico == "Barras":
                fig = px.bar(df, x=col_x, y=col_y, color=col_x, title=f"{col_y} por {col_x}")
            elif tipo_grafico == "Linhas":
                fig = px.line(df, x=col_x, y=col_y, title="Tendência Temporal")
            else:
                fig = px.scatter(df, x=col_x, y=col_y, color=col_x)
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Por favor, carregue um ficheiro na aba 'Explorador de Dados' primeiro.")
