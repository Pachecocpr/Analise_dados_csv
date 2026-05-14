import streamlit as st
import pandas as pd
import plotly.express as px
from duckduckgo_search import DDGS # IA Gratuita sem Key

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="DataExtractor Pro IA", layout="wide")

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- MENU LATERAL ---
with st.sidebar:
    st.title("🌐 DataSystem IA")
    st.markdown("---")
    menu = st.radio("Navegação:", ["🏠 Home", "📁 Importar Dados", "📈 Gráficos", "🤖 Analista IA (Grátis)"])
    st.markdown("---")
    st.success("IA Ativa: Llama 3 (Free Mode)")

# --- LÓGICA DE IMPORTAÇÃO ---
if menu == "🏠 Home":
    st.title("Bem-vindo ao DataExtractor Inteligente")
    st.write("Analise ficheiros CSV/Excel e use IA para tirar conclusões sem precisar de chaves de API.")

elif menu == "📁 Importar Dados":
    st.title("📁 Importação e Verificação")
    arquivo = st.file_uploader("Suba seu ficheiro", type=["csv", "xlsx"])
    
    if arquivo:
        if arquivo.name.endswith('.csv'):
            df = pd.read_csv(arquivo)
        else:
            df = pd.read_excel(arquivo)
        
        # Converter datas automaticamente
        for col in df.columns:
            if any(p in col.lower() for p in ['date', 'data']):
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        st.session_state['meu_df'] = df
        st.success("✅ Ficheiro carregado com sucesso!")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Linhas", df.shape[0])
        c2.metric("Total de Colunas", df.shape[1])
        c3.metric("Campos Vazios", df.isnull().sum().sum())
        st.dataframe(df, use_container_width=True)

elif menu == "📈 Gráficos":
    st.title("📈 Análise Visual")
    if 'meu_df' in st.session_state:
        df = st.session_state['meu_df']
        col_x = st.selectbox("Selecione o Eixo X", df.columns)
        
        modo = st.radio("Tipo de análise:", ["Contagem de Eventos", "Soma de Valores"])
        
        if modo == "Contagem de Eventos":
            df_plot = df.groupby(col_x).size().reset_index(name='Total')
            fig = px.bar(df_plot, x=col_x, y='Total', color=col_x, title=f"Eventos por {col_x}")
        else:
            col_num = df.select_dtypes(include='number').columns
            eixo_y = st.selectbox("Selecione coluna para somar", col_num)
            fig = px.histogram(df, x=col_x, y=eixo_y, histfunc='sum', title=f"Soma de {eixo_y} por {col_x}")
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Importe um ficheiro primeiro.")

# --- ABA DE IA GRATUITA (SEM API KEY) ---
elif menu == "🤖 Analista IA (Grátis)":
    st.title("🤖 Analista de Dados Virtual")
    
    if 'meu_df' in st.session_state:
        df = st.session_state['meu_df']
        
        # Criar o resumo para a IA
        colunas = list(df.columns)
        amostra = df.head(5).to_string()
        total_linhas = len(df)
        
        st.info("A IA está pronta para analisar a estrutura dos seus dados.")
        pergunta = st.text_input("Ex: Qual o resumo desses dados? Quais tendências você vê?")

        if st.button("Perguntar à IA"):
            if pergunta:
                with st.spinner("A IA está a analisar..."):
                    try:
                        # Montamos o contexto para a IA
                        prompt = f"""
                        Você é um analista de dados especialista.
                        Dados do Ficheiro:
                        - Colunas: {colunas}
                        - Total de Linhas: {total_linhas}
                        - Amostra dos dados:
                        {amostra}

                        Pergunta do usuário: {pergunta}
                        Responda em Português de forma clara e profissional.
                        """
                        
                        # Chamada gratuita via DuckDuckGo AI (Usa Llama 3)
                        with DDGS() as ddgs:
                            respostas = ddgs.chat(prompt, model='llama-3-70b')
                            st.markdown("### 📝 Conclusão da IA:")
                            st.write(respostas)
                            
                    except Exception as e:
                        st.error("Houve um pequeno erro na conexão gratuita. Tente novamente.")
            else:
                st.warning("Escreva uma pergunta primeiro.")
    else:
        st.error("Suba um ficheiro primeiro para a IA poder ler.")
