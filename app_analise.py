import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="DataExtractor | Análise de Arquivos",
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
    st.title("🌐 DataSystem v1.0")
    st.markdown("---")
    menu = st.radio(
        "Navegação do Sistema:",
        ["🏠 Painel Inicial", "📁 Importar & Extrair", "📈 Gráficos Interativos"]
    )
    st.markdown("---")
    st.info("💡 **Dica:** Aceitamos CSV, XLSX e XLS.")

# 4. FUNÇÃO DE APOIO: KPIs
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

# 5. LÓGICA DAS PÁGINAS
if menu == "🏠 Painel Inicial":
    st.title("Bem-vindo ao DataExtractor Pro")
    st.markdown("""
    Plataforma para conversão de dados brutos em gráficos.
    
    **Formatos suportados:**
    * **CSV** (Separado por vírgulas)
    * **Excel** (.xlsx e .xls)
    """)
    st.image("https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", width=200)

elif menu == "📁 Importar & Extrair":
    st.title("📁 Gestão de Ficheiros")
    
    arquivo_subido = st.file_uploader("Arraste o ficheiro aqui", type=["csv", "xlsx", "xls"])

    if arquivo_subido:
        try:
            # Identifica a extensão para usar o motor correto
            extensao = os.path.splitext(arquivo_subido.name)[1].lower()

            if extensao == '.csv':
                df = pd.read_csv(arquivo_subido)
            else:
                df = pd.read_excel(arquivo_subido)
            
            # Tratamento de Datas
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
                st.write(df.describe(include='all', datetime_is_numeric=True).fillna("-"))
        
        except Exception as e:
            st.error(f"Erro ao processar o ficheiro: {e}")
    else:
        st.warning("⚠️ Aguardando upload de ficheiro.")

elif menu == "📈 Gráficos Interativos":
    st.title("📈 Dashboard de Insights")
    
    if 'meu_df' in st.session_state:
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
                    st.error("Sem colunas numéricas.")
                    modo_y = "Contagem"

            tipo_grafico = st.selectbox("Estilo", ["Barras", "Linhas", "Área", "Dispersão"])
            cor_por = st.selectbox("Colorir por", [None] + list(df.columns))

        with c2:
            st.subheader("Visualização")
            try:
                if modo_y == "Contagem":
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
        st.error("❌ Nenhum dado carregado. Vá à aba 'Importar'.")

# 6. RODAPÉ
st.markdown("---")
st.caption("DataExtractor Pro - Focado em CSV e Excel.")
