import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai  # Importando o Gemini

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="DataExtractor Pro + AI", layout="wide")

# Configurar a Chave da API (O ideal é usar st.secrets para produção)
# Aqui, o usuário poderá inserir a própria chave na barra lateral para teste
with st.sidebar:
    st.title("⚙️ Configurações de IA")
    api_key = st.text_input("Insira sua Gemini API Key:", type="password")
    if api_key:
        genai.configure(api_key=api_key)

# 2. MENU LATERAL
with st.sidebar:
    st.title("🌐 DataSystem v1.0")
    menu = st.radio("Navegação:", ["🏠 Home", "📁 Importar", "📈 Gráficos", "🤖 Chat IA (Gemini)"])

# --- LÓGICA DE CARREGAMENTO (Simplificada para o exemplo) ---
if menu == "🏠 Home":
    st.title("Bem-vindo ao DataExtractor IA")
    st.write("Suba um arquivo e converse com seus dados usando Inteligência Artificial.")

elif menu == "📁 Importar":
    st.title("📁 Importação de Dados")
    arquivo = st.file_uploader("Suba seu CSV ou Excel", type=["csv", "xlsx"])
    if arquivo:
        if arquivo.name.endswith('.csv'):
            df = pd.read_csv(arquivo)
        else:
            df = pd.read_excel(arquivo)
        st.session_state['meu_df'] = df
        st.success("Dados carregados!")
        st.dataframe(df.head())

elif menu == "📈 Gráficos":
    st.title("📈 Análise Visual")
    if 'meu_df' in st.session_state:
        df = st.session_state['meu_df']
        col_x = st.selectbox("Eixo X", df.columns)
        fig = px.histogram(df, x=col_x, title=f"Distribuição de {col_x}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Carregue dados primeiro.")

# --- NOVA ABA: CHAT IA (GEMINI) ---
elif menu == "🤖 Chat IA (Gemini)":
    st.title("🤖 Pergunte aos seus Dados")
    
    if not api_key:
        st.error("Por favor, insira sua API Key do Gemini na barra lateral.")
    elif 'meu_df' not in st.session_state:
        st.error("Carregue um arquivo na aba 'Importar' primeiro.")
    else:
        df = st.session_state['meu_df']
        
        # Criar um resumo dos dados para dar contexto à IA
        resumo_dados = f"""
        Você é um analista de dados. Aqui está um resumo do dataset atual:
        - Colunas: {list(df.columns)}
        - Total de linhas: {len(df)}
        - Estatísticas principais:
        {df.describe().to_string()}
        
        Amostra dos dados (primeiras 3 linhas):
        {df.head(3).to_string()}
        """

        st.info("A IA analisará o resumo das colunas e estatísticas para responder.")
        
        pergunta = st.text_input("O que você deseja saber sobre esses dados?")
        
        if st.button("Analisar com Gemini"):
            if pergunta:
                with st.spinner("O Gemini está pensando..."):
                    try:
                        model = genai.GenerativeModel('gemini-pro')
                        # Enviamos o resumo + a pergunta do usuário
                        prompt = f"{resumo_dados}\n\nPergunta do usuário: {pergunta}"
                        response = model.generate_content(prompt)
                        
                        st.markdown("### 📝 Resposta da IA:")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Erro ao consultar a IA: {e}")
            else:
                st.warning("Digite uma pergunta.")
