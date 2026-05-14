import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="DataExtractor Pro + IA", layout="wide", page_icon="📊")

# --- 2. CONFIGURAÇÃO DA IA (GEMINI) ---
# Tenta pegar a chave dos segredos do Streamlit ou de um campo de texto
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    with st.sidebar:
        st.warning("⚠️ API Key não encontrada nos Secrets.")
        api_key = st.text_input("Insira sua Gemini API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)

# --- 3. ESTILO VISUAL ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title("🌐 DataSystem Pro")
    menu = st.radio("Navegação:", ["🏠 Home", "📁 Dados", "📈 Gráficos", "🤖 Analista IA"])

# --- 5. LÓGICA DE DADOS ---
if menu == "🏠 Home":
    st.title("🚀 Analisador de Dados Inteligente")
    st.write("Importe arquivos CSV ou Excel e use o poder do Gemini para analisar seus dados.")

elif menu == "📁 Dados":
    st.title("📁 Importação de Arquivos")
    arquivo = st.file_uploader("Suba seu arquivo", type=["csv", "xlsx"])
    if arquivo:
        df = pd.read_csv(arquivo) if arquivo.name.endswith('.csv') else pd.read_excel(arquivo)
        for col in df.columns:
            if any(p in col.lower() for p in ['date', 'data', 'start']):
                df[col] = pd.to_datetime(df[col], errors='coerce')
        st.session_state['meu_df'] = df
        st.success("Dados carregados com sucesso!")
        st.dataframe(df.head(50))

elif menu == "📈 Gráficos":
    st.title("📈 Visualizações Estatísticas")
    if 'meu_df' in st.session_state:
        df = st.session_state['meu_df']
        t1, t2, t3 = st.tabs(["🕒 Linha do Tempo", "📊 Top Marcas", "⚙️ Customizado"])
        
        with t1:
            col_data = st.selectbox("Coluna de Data", df.select_dtypes(include=['datetime64']).columns)
            df_temp = df.groupby(df[col_data].dt.date).size().reset_index(name='Quantidade')
            st.plotly_chart(px.line(df_temp, x=col_data, y='Quantidade', title="Registros por Dia"), use_container_width=True)
            
        with t2:
            # Focado no seu arquivo: Vehicle Make
            col_cat = st.selectbox("Escolha a Categoria", df.columns, index=min(10, len(df.columns)-1))
            df_cat = df[col_cat].value_counts().head(15).reset_index()
            st.plotly_chart(px.bar(df_cat, x='count', y=col_cat, orientation='h', title="Top 15"), use_container_width=True)

        with t3:
            c1, c2 = st.columns(2)
            x = c1.selectbox("Eixo X", df.columns)
            y = c2.selectbox("Eixo Y", df.select_dtypes(include='number').columns)
            st.plotly_chart(px.scatter(df, x=x, y=y, color=x), use_container_width=True)
    else:
        st.warning("Por favor, suba um arquivo primeiro.")

elif menu == "🤖 Analista IA":
    st.title("🤖 Analista Virtual (Gemini)")
    if 'meu_df' in st.session_state:
        if not api_key:
            st.error("Insira a API Key na barra lateral para usar a IA.")
        else:
            df = st.session_state['meu_df']
            pergunta = st.text_input("O que você deseja saber sobre esses dados?")
            if st.button("Analisar"):
                model = genai.GenerativeModel('gemini-1.5-flash')
                contexto = f"Dataset com {len(df)} linhas. Colunas: {list(df.columns)}. Amostra: {df.head(3).to_string()}"
                with st.spinner("IA processando..."):
                    response = model.generate_content(f"{contexto}\n\nPergunta: {pergunta}")
                    st.info(response.text)
    else:
        st.error("Sem dados para analisar.")
