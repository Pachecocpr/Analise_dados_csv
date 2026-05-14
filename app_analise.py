import streamlit as st
import pandas as pd
import plotly.express as px
import os  # Necessário para verificar a extensão do arquivo

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="DataExtractor | Análise Multiformato",
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

# 3. BARRA LATERAL
with st.sidebar:
    st.title("🌐 DataSystem v1.1")
    st.markdown("---")
    menu = st.radio(
        "Navegação do Sistema:",
        ["🏠 Painel Inicial", "📁 Importar & Extrair", "📈 Gráficos Interativos"]
    )
    st.markdown("---")
    st.info("💡 **Dica:** Agora aceitamos ficheiros CSV, XLSX e XLS.")

# 4. FUNÇÃO DE APOIO: KPI
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
        st.metric("Colunas Numéricas", cols_num)

# 5. LÓGICA DAS PÁGINAS
if menu == "🏠 Painel Inicial":
    st.title("Bem-vindo ao DataExtractor Pro")
    st.markdown("""
    Esta aplicação foi desenhada para transformar ficheiros **CSV** e **Excel** em insights visuais imediatos.
    
    **Como utilizar:**
    1. Vá até a aba **Importar & Extrair**.
    2. Arraste o seu ficheiro (**CSV, XLSX ou XLS**).
    3. O sistema fará o tratamento automático de datas e tipos de dados.
    4. Explore os resultados na aba de **Gráficos**.
    """)

elif menu == "📁 Importar & Extrair":
    st.title("📁 Gestão de Ficheiros e Extração")
    
    # ATUALIZADO: Aceita múltiplos formatos
    arquivo_subido = st.file_uploader("Arraste o seu ficheiro aqui", type=["csv", "xlsx", "xls"])

    if arquivo_subido:
        try:
            # LÓGICA DE TRATAMENTO POR EXTENSÃO
            extensao = os.path.splitext(arquivo_subido.name)[1].lower()
            
            if extensao == '.csv':
                df = pd.read_csv(arquivo_subido, sep=',')
            else:
                # Carrega Excel (XLSX ou XLS)
                df = pd.read_excel(arquivo_subido)
            
            # --- TRATAMENTO AUTOMÁTICO DE DATAS ---
            for col in df.columns:
                if any(palavra in col.lower() for palavra in ['date', 'data', 'start', 'end']):
                    df[col] = pd.to_datetime(df[col], errors='coerce')

            st.session_state['meu_df'] = df
            st.success(f"✅ Ficheiro '{arquivo_subido.name}' processado com sucesso!")
            
            st.subheader("📊 Resumo da Extração")
            mostrar_kpis(df)
            
            st.subheader("📋 Visualização dos Dados")
            st.dataframe(df, use_container_width=True)
            
            with st.expander("🔍 Ver Análise Estatística Detalhada"):
                st.write(df.describe(include='all', datetime_is_numeric=True).fillna("-"))
        
        except Exception as e:
            st.error(f"Erro ao processar o ficheiro: {e}")

    else:
        st.warning("⚠️ Aguardando upload de ficheiro para iniciar a extração.")

elif menu == "📈 Gráficos Interativos":
    st.title("📈 Dashboard de Insights")
    
    if 'meu_df' in st.session_state:
        df = st.session_state['meu_df']
        
        c1, c2 = st.columns([1, 4])
        
        with c1:
            st.subheader("Configurações")
            eixo_x = st.selectbox("Eixo X", df.columns)
            modo_y = st.radio("Métrica:", ["Contagem (Linhas)", "Valor Numérico"])
            
            y_final = None
            if modo_y == "Valor Numérico":
                colunas_num = df.select_dtypes(include=['number']).columns
                if not colunas_num.empty:
                    y_final = st.selectbox("Selecione a Métrica", colunas_num)
                else:
                    st.error("Sem colunas numéricas.")
                    modo_y = "Contagem (Linhas)"

            tipo_grafico = st.selectbox("Estilo", ["Barras", "Linhas", "Área", "Dispersão"])
            cor_por = st.selectbox("Colorir por", [None] + list(df.columns))

        with c2:
            st.subheader("Visualização")
            try:
                if modo_y == "Contagem (Linhas)":
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
        st.error("❌ Por favor, carregue um ficheiro primeiro.")

# 6. RODAPÉ
st.markdown("---")
st.caption("DataExtractor Pro - Suporte para CSV e Excel.")
