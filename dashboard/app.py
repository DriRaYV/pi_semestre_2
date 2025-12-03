import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import psycopg2
from dotenv import load_dotenv
import os
from pathlib import Path

plt.style.use("ggplot")

st.set_page_config(page_title="Dashboard Qualidade da Água", layout="wide")
st.title("Dashboard de Qualidade da Água")

BASE_DIR = Path(__file__).resolve().parent

ENV_PATH = BASE_DIR / ".." / ".env"

ENV_PATH = ENV_PATH.resolve()

load_dotenv(ENV_PATH)


@st.cache_data
def load_data():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )
    query = """
        SELECT 
            a.id AS amostra_id,
            g.nome AS grupo,
            l.nome AS local,
            l.nome AS regiao,
            l.latitude, l.longitude,
            qa.temperatura_coleta,
            qa.temperatura_analise,
            qa.turbidez,
            qa.ph_fita,
            qa.ph_arduino,
            qa.umidade,
            c.condutividade
        FROM amostras a
        LEFT JOIN grupos g ON g.id = a.grupo_id
        LEFT JOIN localizacao l ON l.id = a.localizacao_id
        LEFT JOIN qualidade_agua qa ON qa.amostra_id = a.id
        LEFT JOIN condutividade c ON c.amostra_id = a.id
        ORDER BY a.id;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


df = load_data()

num_cols = [
    "temperatura_coleta",
    "temperatura_analise",
    "turbidez",
    "ph_fita",
    "ph_arduino",
    "umidade",
    "condutividade",
]

for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

with st.sidebar:
    st.markdown(
        """
        <style>
        .stMultiSelect > div > div {
            background-color: #e8f3fc !important;
            border: 1px solid #1f77b4 !important;
            color: #1f77b4 !important;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    st.header("Filtros")

    grupos = st.multiselect(
        "Grupo", df["grupo"].dropna().unique(), df["grupo"].dropna().unique()
    )

    if len(grupos) == 0:
        regioes = st.multiselect("Região", [], [], disabled=True)
    else:
        regioes_disp = df[df["grupo"].isin(grupos)]["regiao"].dropna().unique().tolist()
        regioes = st.multiselect("Região", regioes_disp, regioes_disp)

df_filtered = df[
    (df["grupo"].isin(grupos))
    & (df["regiao"].isin(regioes) if len(regioes) > 0 else True)
]

df_region = df_filtered.groupby("regiao")[num_cols].mean().reset_index()

df_region_top10 = df_region.sort_values("ph_arduino", ascending=False).head(10)

blue = "#1f77b4"
light_blue = "#5dade2"
mid_blue = "#2471a3"

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Média de pH", f"{df_filtered['ph_arduino'].mean():.2f}")
with col2:
    st.metric("Média de Turbidez", f"{df_filtered['turbidez'].mean():.2f}")
with col3:
    st.metric("Média de Condutividade", f"{df_filtered['condutividade'].mean():.2f}")
with col4:
    st.metric("Temperatura Média", f"{df_filtered['temperatura_coleta'].mean():.2f} °C")

st.subheader("Comparação do pH das Regiões em relação ao pH neutro (7)")

df_comp = df_region.sort_values("ph_arduino", ascending=False).head(10)
fig, ax = plt.subplots(figsize=(8, 5))
colors = ["#0a4f8f" if v < 7 else "#4ea3ff" for v in df_comp["ph_arduino"]]
ax.barh(df_comp["regiao"], df_comp["ph_arduino"], color=colors)
ax.axvline(7, color="red", linestyle="--", linewidth=2)
ax.set_xlabel("pH")
ax.set_ylabel("Região")
st.pyplot(fig)

st.subheader("Top 10 - pH médio por região")
df_plot = df_region.sort_values("ph_arduino", ascending=False).head(10)
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(df_plot["regiao"], df_plot["ph_arduino"], color=blue)
plt.xticks(rotation=45)
st.pyplot(fig)

st.subheader("Top 10 - Turbidez média por região")
df_plot = df_region.sort_values("turbidez", ascending=False).head(10)
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(df_plot["regiao"], df_plot["turbidez"], color=light_blue)
plt.xticks(rotation=45)
st.pyplot(fig)

st.subheader("Top 10 - Temperatura (coleta) por região")
df_plot = df_region.sort_values("temperatura_coleta", ascending=False).head(10)
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(df_plot["regiao"], df_plot["temperatura_coleta"], color=mid_blue)
plt.xticks(rotation=45)
st.pyplot(fig)

st.subheader("Top 10 - Umidade por região")
df_plot = df_region.sort_values("umidade", ascending=False).head(10)
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(df_plot["regiao"], df_plot["umidade"], color=blue)
plt.xticks(rotation=45)
st.pyplot(fig)

st.subheader("Top 10 - Condutividade por região")
df_plot = df_region.sort_values("condutividade", ascending=False).head(10)
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(df_plot["regiao"], df_plot["condutividade"], color=mid_blue)
plt.xticks(rotation=45)
st.pyplot(fig)

corr_cols = ["condutividade", "ph_arduino", "turbidez", "temperatura_coleta", "umidade"]
corr = df_filtered[corr_cols].corr()

st.subheader("Matriz de Correlação")
fig, ax = plt.subplots(figsize=(6, 5))
cax = ax.matshow(corr, cmap="Blues")
fig.colorbar(cax)
ax.set_xticks(range(len(corr.columns)))
ax.set_yticks(range(len(corr.columns)))
ax.set_xticklabels(corr.columns, rotation=45)
ax.set_yticklabels(corr.columns)
st.pyplot(fig)

st.subheader("Dados filtrados")
st.dataframe(df_filtered)

csv = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button("Baixar CSV", csv, "dados_filtrados.csv", "text/csv")
