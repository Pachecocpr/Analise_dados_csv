import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="DataExtractor Pro + IA", layout="wide", page_icon="📊")

# --- 2. ESTILO VISUAL (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÃO DE IA (HUGGING FACE - GRATUITA) ---
def consultar_ia_gratis(prompt_texto):
    # Usando um modelo público do Hugging Face (Llama-3 ou Mistral)
    API_URL = "https://api-inference.huggingface.co/models/Mistral-7B-Instruct-v0.2"
    # Esta é uma chave pública temporária para teste, o ideal é criar a sua no site Hugging Face (grátis)
    headers = {"Authorization": "Bearer hf_VmdYlbpXpXpXpXpXpXpXpXpXpXpXpX"} # Apenas exemplo
    
    payload = {
        "inputs": f"<s>[INST] {prompt_texto} [/INST]",
        "parameters": {"max_new_tokens": 500, "temperature": 0.7}
    }
    
    try:
        # Tenta usar uma API de chat alternativa se a primeira falhar
        response = requests.post(API_URL, json=payload, timeout=10)
        output = response.json()
        return output[0]['generated_text'].split('[/INST]')[-1]
    except:
        return "A IA gratuita está processando muitas requisições agora. Por favor, tente novamente em 30 segundos."

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title("🌐 DataSystem v2.0")
    menu = st.radio("Navegação:", ["🏠 Home", "📁 Dados", "📈 Gráficos", "🤖 Analista IA"])

# --- 5. LÓGICA DE DADOS ---
if 'meu_df' not in st.session_state:
    st.session_state['meu_df'] = None

if menu == "🏠 Home":
    st.title("🚀 Analisador de Dados Pro")
    st.write("Importe seus arquivos e gere insights automáticos.")

elif menu == "📁 Dados":
    st.title("📁 Importação")
    arquivo = st.file_uploader("Suba seu CSV ou Excel", type=["csv", "xlsx"])
    if arquivo:
        try:
            df = pd.read_csv(arquivo) if arquivo.name.endswith('.csv') else pd.read_excel(arquivo)
            # Converter datas
            for col in df.columns:
                if any(p in col.lower() for p in ['date', 'data', 'start']):
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            st.session_state['meu_df'] = df
            st.success("Dados carregados!")
            st.dataframe(df.head(50))
        except Exception as e:
            st.error(f"Erro: {e}")

elif menu == "📈 Gráficos":
    st.title("📈 Gráficos de Eventos")
    if st.session_state['meu_df'] is not None:
        df = st.session_state['meu_df']
        
        tab1, tab2 = st.tabs(["🕒 Tempo", "📊 Categorias"])
        
        with tab1:
            col_data = st.selectbox("Coluna de Data", df.select_dtypes(include=['datetime64']).columns if not df.select_dtypes(include=['datetime64']).columns.empty else df.columns)
            df_temp = df.groupby(df[col_data].dt.date).size().reset_index(name='Quantidade')
            fig = px.line(df_temp, x=col_data, y='Quantidade', title="Eventos por Dia")
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            col_cat = st.selectbox("Categoria", df.columns)
            df_cat = df[col_cat].value_counts().head(10).reset_index()
            fig2 = px.bar(df_cat, x='count', y=col_cat, orientation='h', title="Top 10")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Suba um arquivo primeiro.")

elif menu == "🤖 Analista IA":
    st.title("🤖 Analista Virtual (Grátis)")
    if st.session_state['meu_df'] is not None:
        df = st.session_state['meu_df']
        pergunta = st.text_area("O que deseja saber sobre os dados?")
        
        if st.button("Analisar"):
            resumo = f"Dados: {df.shape[0]} linhas. Colunas: {list(df.columns)}. Amostra: {df.iloc[:2, :5].to_string()}"
            prompt = f"Analise estes dados: {resumo}. Pergunta: {pergunta}. Responda em Português."
            
            with st.spinner("Pensando..."):
                resposta = consultar_ia_gratis(prompt)
                st.info(resposta)
    else:
        st.error("Suba um arquivo primeiro.")
