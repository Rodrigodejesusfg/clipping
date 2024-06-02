#!/usr/bin/env python
# coding: utf-8

# In[1]:

import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime
import plotly.express as px

genai.configure(api_key="GOOGLE_API_KEY")

# Encontrar um modelo compatível 
MODELO_NOME = "gemini-pro"  

model = genai.GenerativeModel(MODELO_NOME)

# Configuração da página
st.set_page_config(page_title="Barbosa.Ai", page_icon=":newspaper:")
st.title("📰 Clip.Ai")

# Cor personalizada
COR_PERSONALIZADA = "#518CB7"

# Carregar DataFrame com as notícias
@st.cache_data
def carregar_dados():
    df = pd.read_excel(r"C:\Users\070283\OneDrive - Construtora Barbosa Mello SA\python\projeto clipping\google_alerts2.xlsx")
    df['Data'] = pd.to_datetime(df['Data']).dt.strftime('%Y-%m-%d') # Formatando data durante o carregamento
    return df

df = carregar_dados()

# Função para gerar o comentário
def gerar_comentário(texto, instrucao):
    """Gera um comentário personalizado usando o modelo Gemini Pro."""
    prompt = (
        f"Por favor, comece se apresentando com o nome: o Barbosa, "
        f"forneça um comentário sobre o seguinte texto de uma empresa de engenharia pesada, "
        f"com foco em: {instrucao}\n\n"
        f"Texto:\n{texto}\n\n"
        f"Comentário:"
    )
    response = model.generate_content(prompt)
    return response.text  

# Paleta de cores
COR_FUNDO = "#FFFFFF"  # Branco
COR_PRIMARIA = "#2C5794"
COR_SECUNDARIA = "#518CB7"
COR_TEXTO = "#3F3F3F"
COR_ACENTO = "#D1D1D1"

# Configurar cores do tema do Streamlit
st.markdown(f"""
<style>
    body {{
        background-color: {COR_FUNDO};
        color: {COR_TEXTO};
    }}
    .stApp {{
        background-color: {COR_FUNDO};
    }}
    .stTextInput > div > div > input {{
        background-color: {COR_ACENTO};
        color: {COR_TEXTO};
    }}
    /* ... outros estilos ... */
</style>
""", unsafe_allow_html=True)



# Interface do usuário
opcao_resumo = st.sidebar.radio(
    "Escolha uma opção:",
    ("Comentar Notícias", "Resumir por Tema e Data")
)

# Número de notícias por página
noticias_por_pagina = 8
# Criar a aba
aba_noticias, aba_estatisticas = st.tabs(["Notícias", "📊 Estatísticas"])

# Filtro de busca
filtro_busca = st.text_input("Pesquisar notícias (por palavras-chave):")

if opcao_resumo == "Comentar Notícias":
    # Filtrar notícias com base na busca
    if filtro_busca:
        df_filtrado = df[df['Título'].str.contains(filtro_busca, case=False) | 
                         df['Conteúdo'].str.contains(filtro_busca, case=False)]
    else:
        df_filtrado = df

    # Paginação
    pagina = st.number_input("Página:", min_value=1, max_value=(len(df_filtrado) // noticias_por_pagina) + 1)
    inicio = (pagina - 1) * noticias_por_pagina
    fim = inicio + noticias_por_pagina

    # Exibir notícias da página atual
    for i in range(inicio, fim):
        if i < len(df_filtrado):
            noticia = df_filtrado.iloc[i]

            # Formatando data (já formatada durante o carregamento)
            data_noticia = noticia['Data']

            # Definindo a cor do sentimento
            cor_sentimento = {
                'Neutro': 'yellow',
                'Positivo': 'green',
                'Negativo': 'red'
            }.get(noticia['Sentimento'], 'gray') # 'gray' para casos não encontrados

            # Exibindo a notícia
            st.markdown(
                f"""
                <div style='background-color: {COR_PERSONALIZADA}; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                    <div style='display: flex; align-items: center;'>
                        <p style='color: white; margin-right: 10px;'>{data_noticia}</p>
                        <p style='color: white; margin-right: 10px;'>Relevância: {noticia['Relevância']}</p>
                        <div style='background-color: {cor_sentimento}; width: 15px; height: 15px; border-radius: 50%; margin-right: 10px;'></div>
                    </div>
                    <div style='background-color: white; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                        <h3 style='color: black;'>{i+1}. {noticia['Título']}</h3>
                        <p style='color: black;'>{noticia['Conteúdo']}</p>
                        <p style='color: black;'><strong>Palavras-chave:</strong> {noticia['Palavras-chave']}</p>
                        <a href="{noticia['Link']}" target="_blank" style="color: black;">Abrir link da notícia</a>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Instrução para o resumo
            instrucao_resumo = st.text_input(f"Instrução para o comentário da notícia {i+1}:")

            if st.button(f"Gerar comentário da Notícia {i+1}"):
                with st.spinner("Ok, estou lendo! Um segundo..."):
                    comentario = gerar_comentário(noticia['Conteúdo'], instrucao_resumo)
                    st.success("**Comentário:**")
                    st.write(comentario)

elif opcao_resumo == "Resumir por Tema e Data":
    # Obter lista de clusters únicos
    clusters_unicos = df['cluster'].unique()

    # Selecionar cluster
    cluster_selecionado = st.selectbox("Selecione um Tema e Data para resumir:", clusters_unicos)

    # Filtrar notícias do cluster selecionado
    noticias_cluster = df[df["cluster"] == cluster_selecionado] 

    # Paginação
    pagina = st.number_input("Página:", min_value=1, max_value=(len(noticias_cluster) // noticias_por_pagina) + 1)
    inicio = (pagina - 1) * noticias_por_pagina
    fim = inicio + noticias_por_pagina

    # Exibir notícias da página atual
    for i in range(inicio, fim):
        if i < len(noticias_cluster):
            noticia = noticias_cluster.iloc[i]

            # Formatando data (já formatada durante o carregamento)
            data_noticia = noticia['Data']

            # Definindo a cor do sentimento
            cor_sentimento = {
                'Neutro': 'yellow',
                'Positivo': 'green',
                'Negativo': 'red'
            }.get(noticia['Sentimento'], 'gray') # 'gray' para casos não encontrados

            # Exibindo a notícia
            st.markdown(
                f"""
                <div style='background-color: {COR_PERSONALIZADA}; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                    <div style='display: flex; align-items: center;'>
                        <p style='color: white; margin-right: 10px;'>{data_noticia}</p>
                        <p style='color: white; margin-right: 10px;'>Relevância: {noticia['Relevância']}</p>
                        <div style='background-color: {cor_sentimento}; width: 15px; height: 15px; border-radius: 50%; margin-right: 10px;'></div>
                    </div>
                    <div style='background-color: white; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                        <h3 style='color: black;'>{i+1}. {noticia['Título']}</h3>
                        <p style='color: black;'>{noticia['Conteúdo']}</p>
                        <p style='color: black;'><strong>Palavras-chave:</strong> {noticia['Palavras-chave']}</p>
                        <a href="{noticia['Link']}" target="_blank" style="color: black;">Abrir link da notícia</a>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Instrução para o resumo do cluster
    instrucao_resumo = st.text_input("Instrução para o resumo do cluster:")

    if st.button("Gerar Resumo do Cluster"):
        with st.spinner("Gerando resumo..."):
            textos_cluster = noticias_cluster['Conteúdo'].tolist()
            texto_resumo = " ".join(textos_cluster)
            resumo = gerar_comentário(texto_resumo, instrucao_resumo)
            st.success("**Resumo:**")
            st.write(resumo)


# --- Aba de Estatísticas ---
st.sidebar.markdown("---")
st.sidebar.header("Filtrar datas")



with st.sidebar:
    # Filtro deslizante de data
    data_inicio, data_fim = st.slider(
        "Selecione o intervalo de datas:",
        min_value=datetime.strptime(df['Data'].min(), '%Y-%m-%d').date(),
        max_value=datetime.strptime(df['Data'].max(), '%Y-%m-%d').date(),
        value=(
            datetime.strptime(df['Data'].min(), '%Y-%m-%d').date(), 
            datetime.strptime(df['Data'].max(), '%Y-%m-%d').date()
        ),
        format="DD/MM/YYYY"
    )

# Aplicar filtro ao DataFrame
df_filtrado = df[(df['Data'] >= data_inicio.strftime('%Y-%m-%d')) & 
                 (df['Data'] <= data_fim.strftime('%Y-%m-%d'))]

# --- Conteúdo da Aba de Estatísticas ---
with aba_estatisticas:
    st.subheader("Quantidade de notícias por dia")
    noticias_por_dia = df_filtrado.groupby('Data').size().reset_index(name='Quantidade')
    fig_noticias_dia = px.bar(
        noticias_por_dia, 
        x='Data', 
        y='Quantidade', 
        color_discrete_sequence=[COR_PRIMARIA]
    )
    fig_noticias_dia.update_layout(
        xaxis_title="Data",
        yaxis_title="Quantidade de Notícias",
        plot_bgcolor=COR_FUNDO,  # Cor de fundo branca
        paper_bgcolor=COR_FUNDO   # Cor de fundo branca
    )
    st.plotly_chart(fig_noticias_dia)

    # Gráfico 2: Contagem de Fontes
    st.subheader("Contagem de Fontes")
    contagem_fontes = df_filtrado['Fonte'].value_counts().reset_index()
    contagem_fontes.columns = ['Fonte', 'Quantidade']
    fig_fontes = px.bar(
        contagem_fontes, 
        x='Fonte', 
        y='Quantidade', 
        color_discrete_sequence=[COR_SECUNDARIA]
    )
    fig_fontes.update_layout(
        xaxis_title="Fonte",
        yaxis_title="Quantidade",
        plot_bgcolor=COR_FUNDO,  # Cor de fundo branca
        paper_bgcolor=COR_FUNDO   # Cor de fundo branca
    )
    st.plotly_chart(fig_fontes)

    # Gráfico 3: Gráfico de Pizza para Temas
    st.subheader("Distribuição de Temas")
    contagem_temas = df_filtrado['Tema'].value_counts()
    fig_pizza_temas = px.pie(
        contagem_temas, 
        values=contagem_temas.values, 
        names=contagem_temas.index,
        color_discrete_sequence=[COR_PRIMARIA, COR_SECUNDARIA, COR_ACENTO, COR_TEXTO]
    )
    fig_pizza_temas.update_layout(
        plot_bgcolor=COR_FUNDO,  # Cor de fundo branca
        paper_bgcolor=COR_FUNDO   # Cor de fundo branca
    )
    st.plotly_chart(fig_pizza_temas)


            
# In[ ]:





