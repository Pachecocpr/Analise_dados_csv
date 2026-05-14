import streamlit as st
import pandas as pd
import plotly.express as px
from duckduckgo_search import DDGS
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="DataExtractor Pro + IA", layout="wide", page_icon="📊")

# --- 2. ESTILO VISUAL (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #eee; }
    .sidebar .sidebar-content { background-image: linear-gradient(#2e7bcf, #052b5e); color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.title("🌐 DataSystem IA")
    st.markdown("---")
    menu = st.radio("Navegação:", ["🏠 Home", "📁 Dados & Verificação", "📈 Gráficos Completos", "🤖 Analista IA (Grátis)"])
    st.markdown("---")
    st.info("Suporte: CSV e Excel (XLSX)")

# --- 4. FUNÇÃO DE CARREGAMENTO E VALIDAÇÃO ---
def load_data(file):
    try:
        ext = os.path.splitext(file.name)[1].lower()
        if ext == '.csv':
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # Limpeza e Conversão de Datas Automática
        for col in df.columns:
            if any(p in col.lower() for p in ['date', 'data', 'start']):
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df, None
    except Exception as e:
        return None, str(e)

# --- 5. LÓGICA DAS PÁGINAS ---

if menu == "🏠 Home":
    st.title("🚀 Bem-vindo ao DataExtractor Pro")
    st.markdown("""
    Esta plataforma integra **Tratamento de Dados**, **Visualização Estatística** e **IA Generativa** em um só lugar.
    
    1. **Importe** seu arquivo CSV ou Excel.
    2. **Visualize** gráficos de tendência e volumetria.
    3. **Pergunte** para a IA tirar conclusões automáticas sem precisar de códigos.
    """)

elif menu == "📁 Dados & Verificação":
    st.title("📁 Importação e Integridade")
    arquivo = st.file_uploader("Arraste seu ficheiro aqui", type=["csv", "xlsx"])
    
    if arquivo:
        df, erro = load_data(arquivo)
        if erro:
            st.error(f"Erro no arquivo: {erro}")
        else:
            st.session_state['meu_df'] = df
            st.success(f"Arquivo '{arquivo.name}' carregado com sucesso!")
            
            # KPIs de Verificação
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total de Registros", df.shape[0])
            c2.metric("Total de Colunas", df.shape[1])
            c3.metric("Campos Vazios", df.isnull().sum().sum())
            c4.metric("Duplicados", df.duplicated().sum())
            
            st.subheader("📋 Visualização dos Dados")
            st.dataframe(df.head(100), use_container_width=True)

elif menu == "📈 Gráficos Completos":
    st.title("📈 Painel de Visualizações Avançadas")
    
    if 'meu_df' in st.session_state:
        df = st.session_state['meu_df']
        
        tab1, tab2, tab3 = st.tabs(["🕒 Evolução Temporal", "🏢 Marcas & Categorias", "📊 Customizado"])
        
        with tab1:
            st.subheader("Análise de Eventos por Data")
            col_data = st.selectbox("Selecione a coluna de Data:", df.select_dtypes(include=['datetime64']).columns if not df.select_dtypes(include=['datetime64']).columns.empty else df.columns)
            
            periodo = st.selectbox("Agrupar por:", ["Dia", "Mês", "Ano"])
            if periodo == "Dia":
                df_temp = df.groupby(df[col_data].dt.date).size().reset_index(name='Registros')
            elif periodo == "Mês":
                df_temp = df.groupby(df[col_data].dt.to_period('M').astype(str)).size().reset_index(name='Registros')
            else:
                df_temp = df.groupby(df[col_data].dt.year).size().reset_index(name='Registros')
            
            fig1 = px.line(df_temp, x=col_data, y='Registros', title="Fluxo de Registros no Tempo", markers=True)
            st.plotly_chart(fig1, use_container_width=True)

        with tab2:
            st.subheader("Distribuição por Marcas e Tipos")
            col_cat = st.selectbox("Selecione a Categoria (ex: Vehicle Make):", df.columns, index=min(10, len(df.columns)-1))
            
            df_cat = df[col_cat].value_counts().head(15).reset_index()
            df_cat.columns = [col_cat, 'Quantidade']
            
            fig2 = px.bar(df_cat, x='Quantidade', y=col_cat, orientation='h', color='Quantidade', title=f"Top 15 - {col_cat}")
            st.plotly_chart(fig2, use_container_width=True)

        with tab3:
            st.subheader("Explorador Livre")
            c1, c2, c3 = st.columns(3)
            x_free = c1.selectbox("Eixo X", df.columns)
            y_free = c2.selectbox("Eixo Y (Métrica)", df.select_dtypes(include='number').columns)
            tipo_free = c3.selectbox("Tipo de Gráfico", ["Dispersão", "Barras", "Área", "Histograma"])
            
            if tipo_free == "Dispersão":
                fig3 = px.scatter(df, x=x_free, y=y_free, color=x_free)
            elif tipo_free == "Barras":
                fig3 = px.bar(df, x=x_free, y=y_free)
            elif tipo_free == "Área":
                fig3 = px.area(df, x=x_free, y=y_free)
            else:
                fig3 = px.histogram(df, x=x_free)
            
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("⚠️ Carregue um arquivo na aba 'Dados' primeiro.")

elif menu == "🤖 Analista IA (Grátis)":
    st.title("🤖 Analista IA (Llama-3 Free)")
    
    if 'meu_df' in st.session_state:
        df = st.session_state['meu_df']
        
        pergunta = st.text_input("O que você deseja saber sobre esses dados?")
        
        if st.button("Analisar com IA"):
            if pergunta:
                with st.spinner("Analisando..."):
                    contexto = f"""
                    Dataset: {len(df)} linhas e colunas {list(df.columns)}.
                    Estatísticas: {df.describe().to_string()}
                    Amostra: {df.head(3).to_string()}
                    Pergunta: {pergunta}
                    """
                    try:
                        with DDGS() as ddgs:
                            res = ddgs.chat(contexto, model='llama-3-70b')
                            st.markdown("### 📝 Resposta da IA")
                            st.info(res)
                    except:
                        st.error("Servidor de IA ocupado. Tente novamente em instantes.")
    else:
        st.error("Suba um arquivo primeiro.")
