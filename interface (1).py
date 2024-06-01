#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import re
import google.generativeai as genai

# Configuração da página
st.set_page_config(page_title="News Summarizer", page_icon=":newspaper:")
st.title("📰 News Summarizer")

# Carregar modelo de linguagem (Gemini Pro)
genai.configure(api_key="AIzaSyCtj2xGASpn_FrNYW9D-Nbt_F8-CXpFypQ")  # Substitua pela sua chave de API do Gemini Pro
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# Carregar DataFrame com as notícias
@st.cache_data  # Carrega os dados apenas uma vez
def carregar_dados():
    df = pd.read_excel("google_alerts.xlsx")
    return df

df = carregar_dados()

# Função para gerar o resumo
def gerar_resumo(texto, instrucao):
    """Gera um resumo personalizado usando o modelo Gemini Pro."""
    prompt = f"Por favor, forneça um resumo conciso do seguinte texto, com foco em: {instrucao}\n\n{texto}"
    response = model.generate_content(prompt)
    return response.text

# Interface do usuário
st.sidebar.header("Opções de Resumo")
opcao_resumo = st.sidebar.radio(
    "Escolha uma opção:",
    ("Resumir notícia específica", "Resumir grupo de notícias")
)

if opcao_resumo == "Resumir notícia específica":
    # Selecionar notícia por índice
    indice_noticia = st.number_input(
        "Digite o índice da notícia (de 1 a {}):".format(len(df)),
        min_value=1,
        max_value=len(df),
        step=1,
    )
    indice_noticia -= 1  # Ajusta o índice para o DataFrame (começa em 0)

    if indice_noticia >= 0:
        noticia = df.iloc[indice_noticia]
        st.header(f"Notícia {indice_noticia + 1}: {noticia['Título']}")
        st.write(noticia['Conteúdo'])

        # Instrução para o resumo
        instrucao_resumo = st.text_input("Instrução para o resumo:")

        # Botão para gerar o resumo
        if st.button("Gerar Resumo"):
            with st.spinner("Gerando resumo..."):
                resumo = gerar_resumo(noticia['Conteúdo'], instrucao_resumo)
                st.success("**Resumo:**")
                st.write(resumo)

elif opcao_resumo == "Resumir grupo de notícias":
    # Agrupar notícias em clusters
    n_clusters = st.sidebar.slider(
        "Número de clusters:", min_value=2, max_value=10, value=3
    )
    df_com_clusters = agrupar_noticias(df.copy(), n_clusters=n_clusters)

    # Exibir clusters e permitir seleção
    st.header("Selecione um cluster:")
    for i in range(n_clusters):
        st.subheader(f"Cluster {i+1}")
        noticias_cluster = df_com_clusters[df_com_clusters["Cluster"] == i]
        for j, noticia in noticias_cluster.iterrows():
            st.write(f"- {noticia['Título']}")

    cluster_selecionado = st.number_input(
        "Digite o número do cluster que deseja resumir:",
        min_value=1,
        max_value=n_clusters,
        step=1,
    )

    # Instrução para o resumo
    instrucao_resumo = st.text_input("Instrução para o resumo:")

    # Botão para gerar o resumo
    if st.button("Gerar Resumo"):
        with st.spinner("Gerando resumo..."):
            textos_cluster = df_com_clusters[df_com_clusters["Cluster"] == cluster_selecionado - 1]['Conteúdo'].tolist()
            texto_resumo = " ".join(textos_cluster)
            resumo = gerar_resumo(texto_resumo, instrucao_resumo)
            st.success("**Resumo:**")
            st.write(resumo)


# In[ ]:




