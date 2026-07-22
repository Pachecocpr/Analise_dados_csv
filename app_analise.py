import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re
from google import genai

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="DataExtractor | Análise de Arquivos & IA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. ESTILO CSS
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

# --- INICIALIZAÇÃO SEGURA DA IA ---
api_key = st.secrets.get("GEMINI_API_KEY")
ai_disponivel = False

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        ai_disponivel = True
    except Exception as e:
        st.sidebar.error(f"Erro ao inicializar o Gemini: {e}")

# 3. BARRA LATERAL (Sem risco de NameError)
with st.sidebar:
    st.title("🖥️ Sistema de extração de Dados - v1.4")
    st.markdown("---")
    
    opcoes_menu = ["🏠 Painel Inicial", "📁 Importar & Extrair", "📈 Gráficos Interativos"]
    if ai_disponivel:
        opcoes_menu.append("🤖 Analista IA")
        
    menu = st.radio("Navegação do Sistema:", opcoes_menu, key="navegacao_principal")
    st.markdown("---")
    st.info("💡 **Dica:** Use a aba 'Importar' antes de gerar os gráficos.")

# 4. FUNÇÕES DE APOIO
def mostrar_kpis(df):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total de Linhas", df.shape[0])
    with c2:
        st.metric("Total de Colunas", df.shape[1])
    with c3:
        nulos = df.isnull().sum().sum()
        st.metric("Dados Ausentes", nulos, delta=f"{nulos} células", delta_color="inverse")
    with c4:
        cols_num = len(df.select_dtypes(include=['number']).columns)
        st.metric("Colunas Métricas", cols_num)

def limpar_codigo_texto(texto: str) -> str:
    """Remove blocos de código markdown caso a IA os inclua por engano."""
    texto_limpo = re.sub(r'```[\s\S]*?```', '', texto)
    return texto_limpo.strip()

# 5. LÓGICA DAS PÁGINAS
if menu == "🏠 Painel Inicial":
    st.title("Extrator De Dados-Pro")
    st.markdown("""
    Plataforma inteligente para conversão de dados brutos em insights e gráficos.
    
    **Formatos suportados:**
    * **CSV** (Separado por vírgulas)
    * **Excel** (.xlsx e .xls)
    """)
    # URL limpa para evitar MediaFileStorageError
    st.image("https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", width=200)

elif menu == "📁 Importar & Extrair":
    st.title("📁 Gestão de Ficheiros")
    
    arquivo_subido = st.file_uploader("Arraste o ficheiro aqui", type=["csv", "xlsx", "xls"])

    if arquivo_subido:
        try:
            extensao = os.path.splitext(arquivo_subido.name)[1].lower()

            if extensao == '.csv':
                df = pd.read_csv(arquivo_subido)
            else:
                df = pd.read_excel(arquivo_subido)
            
            # Força a conversão de colunas de tempo encontradas
            for col in df.columns:
                if any(p in col.lower() for p in ['date', 'data', 'start', 'end']):
                    df[col] = pd.to_datetime(df[col], errors='coerce')

            st.session_state['meu_df'] = df
            st.success(f"✅ Ficheiro '{arquivo_subido.name}' processado com sucesso!")
            
            st.subheader("📊 Resumo da Extração")
            mostrar_kpis(df)
            
            st.subheader("📋 Visualização dos Dados")
            st.dataframe(df.head(100), use_container_width=True)
            
            with st.expander("🔍 Ver Análise Estatística Detalhada"):
                st.write(df.describe(include='all').fillna("-"))
        
        except Exception as e:
            st.error(f"Erro ao processar o ficheiro: {e}")
    else:
        st.warning("⚠️ Aguardando upload de ficheiro.")

elif menu == "📈 Gráficos Interativos":
    st.title("📈 Dashboard de Insights")
    
    if 'meu_df' in st.session_state and st.session_state['meu_df'] is not None:
        df = st.session_state['meu_df']
        c1, c2 = st.columns([1, 4])
        
        with c1:
            st.subheader("Filtros")
            eixo_x = st.selectbox("Eixo X", df.columns)
            modo_y = st.radio("Métrica:", ["Contagem", "Valor Numérico"])
            
            y_final = None
            if modo_y == "Valor Numérico":
                colunas_num = df.select_dtypes(include=['number']).columns
                if not colunas_num.empty:
                    y_final = st.selectbox("Coluna para Métrica", colunas_num)
                else:
                    st.error("Sem colunas numéricas neste arquivo.")
                    modo_y = "Contagem"

            tipo_grafico = st.selectbox("Estilo", ["Barras", "Linhas", "Área", "Dispersão"])
            cor_por = st.selectbox("Colorir por", [None] + list(df.columns))

        with c2:
            st.subheader("Visualização")
            try:
                if modo_y == "Contagem":
                    if pd.api.types.is_datetime64_any_dtype(df[eixo_x]):
                        df_plot = df.groupby(df[eixo_x].dt.date).size().reset_index(name='Total')
                    else:
                        df_plot = df.groupby(eixo_x).size().reset_index(name='Total')
                    y_plot = 'Total'
                else:
                    df_plot = df
                    y_plot = y_final

                if tipo_grafico == "Barras":
                    fig = px.bar(df_plot, x=eixo_x, y=y_plot, color=cor_por, template="plotly_white")
                elif tipo_grafico == "Linhas":
                    fig = px.line(df_plot, x=eixo_x, y=y_plot, color=cor_por, markers=True)
                elif tipo_grafico == "Área":
                    fig = px.area(df_plot, x=eixo_x, y=y_plot, color=cor_por)
                else:
                    fig = px.scatter(df_plot, x=eixo_x, y=y_plot, color=cor_por)

                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao gerar gráfico: {e}")
    else:
        st.error("❌ Nenhum dado carregado. Vá à aba 'Importar & Extrair'.")

elif menu == "🤖 Analista IA":
    st.title("🤖 Consulta Interativa com Gemini")
    
    if 'meu_df' in st.session_state and st.session_state['meu_df'] is not None:
        df = st.session_state['meu_df']
        
        st.markdown("A IA analisará o **arquivo completo** para fornecer informações precisas.")
        
        # --- VARREDURA COMPLETA DO ARQUIVO ---
        total_linhas = len(df)
        total_colunas = len(df.columns)
        
        # Gera estatísticas descritivas cobrindo 100% dos dados
        resumo_estatistico = df.describe(include='all').fillna("-").to_string()
        
        # Mapeamento detalhado de cada coluna
        info_colunas = []
        for col in df.columns:
            nulos = df[col].isnull().sum()
            unicos = df[col].nunique()
            info_colunas.append(f"- Coluna '{col}': tipo={df[col].dtype}, valores_unicos={unicos}, nulos={nulos}/{total_linhas}")
        
        resumo_colunas_str = "\n".join(info_colunas)
        
        pergunta = st.text_area("O que você deseja saber sobre esses dados?")
        
        if st.button("Enviar Pergunta ao Gemini"):
            if pergunta:
                with st.spinner("Analisando o arquivo completo..."):
                    prompt_sistema = f"""
                    Você é um analista executivo de dados sênior. Você recebeu a varredura estatística completa de um arquivo com {total_linhas} linhas e {total_colunas} colunas.

                    VARREDURA TOTAL DOS DADOS:
                    Estatísticas descritivas cobrindo TODAS as {total_linhas} linhas do arquivo:
                    {resumo_estatistico}

                    Estrutura e integridade detalhada de todas as colunas:
                    {resumo_colunas_str}

                    REGRAS DE RESPOSTA OBRIGATÓRIAS:
                    1. Responda com base na totalidade do arquivo ({total_linhas} linhas).
                    2. Forneça APENAS respostas em texto claro, explicativo e em linguagem natural (português).
                    3. É ESTRITAMENTE PROIBIDO incluir qualquer código Python, SQL, scripts ou sintaxe de programação.
                    4. NÃO inclua blocos de código Markdown (como ```python ou ```).
                    5. Concentre-se diretamente nas conclusões, respostas numéricas exatas e insights de negócios.

                    Pergunta do usuário:
                    "{pergunta}"
                    """
                    try:
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt_sistema,
                        )
                        
                        # Garante a limpeza total de blocos técnicos acidentais
                        resposta_formatada = limpar_codigo_texto(response.text)
                        
                        st.markdown("### 📝 Resposta do Analista IA:")
                        st.write(resposta_formatada)
                    except Exception as e:
                        st.error(f"Falha ao se comunicar com a API do Gemini: {e}")
    else:
        st.error("❌ Nenhum dado carregado. Vá à aba 'Importar & Extrair'.")

# 6. RODAPÉ
st.markdown("---")
st.caption("DataExtractor Pro - Focado em Analytics Seguro e Inteligente.")
