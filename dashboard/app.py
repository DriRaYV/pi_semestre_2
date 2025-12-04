import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector
from dotenv import load_dotenv
import os
from pathlib import Path

plt.style.use("ggplot")

st.set_page_config(page_title="Dashboard Qualidade da Água", layout="wide")

st.markdown(
    """
<style>
.block-container { padding-top: 1rem; padding-bottom: 1rem; }
</style>
""",
    unsafe_allow_html=True,
)

st.title("Dashboard Qualidade da Água")

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = (BASE_DIR / ".." / ".env").resolve()
load_dotenv(ENV_PATH)


def format_label(text, max_chars=12):
    t = str(text)
    return t if len(t) <= max_chars else t[:max_chars] + "…"


@st.cache_data
def load_data():
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        port=os.getenv("MYSQL_PORT", 3306),
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
            qa.umidade
        FROM amostras a
        LEFT JOIN grupos g ON g.id = a.grupo_id
        LEFT JOIN localizacao l ON l.id = a.localizacao_id
        LEFT JOIN qualidade_agua qa ON qa.amostra_id = a.id
        ORDER BY a.id;
    """
    df = pd.read_sql_query(query, conn)
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
]

for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

with st.sidebar:
    st.markdown(
        """
<style>
.st-emotion-cache-1fwbbrh h2 { color: #ffff; }
.st-emotion-cache-1s2v671{ color: rgb(255 255 255); }

[data-testid=stSidebar] {
    background: linear-gradient(90deg, #32237E 11%, #0A0338 97%) !important;
    padding: 0 !important;
}

[data-testid="stSidebarHeader"] { display: none !important; }

[data-baseweb="select"] > div {
    background-color: transparent !important;
    border: 1px solid #ffff !important;
    color: #1f77b4 !important;
}

[data-baseweb="select"] input {
    background-color: transparent !important;
    color: #1f77b4 !important;
}

[data-baseweb="tag"] {
    background-color: #1f77b4 !important;
    color: white !important;
}

[data-baseweb="tag"] span { color: white !important; }
[data-baseweb="tag"] svg path { fill: white !important; }

.st-emotion-cache-dx6mrm.e10fdlpp4 { background: #ffffff !important; }

.st-emotion-cache-11xx4re {
    background: #ffffff !important;
    border: 2px solid #ffffff !important;
    box-shadow: none !important;
    outline: none !important;
    transition: none !important;
}

.st-emotion-cache-11xx4re:hover,
.st-emotion-cache-11xx4re:active {
    background: #ffffff !important;
    border: 2px solid #ffffff !important;
}

.st-emotion-cache-jigjfz {
    color: #ffffff !important;
    background: transparent !important;
}

.st-an.st-ap.st-aq.st-ao.st-dr.st-ds.st-am.st-dt.st-dp { background: #ffffff !important; }
.st-emotion-cache-111apq span { color: #ffffff !important; }

[data-baseweb="slider"] div:hover { background: none !important; }
[data-baseweb="slider"] *:focus { outline: none !important; box-shadow: none !important; }
</style>
""",
        unsafe_allow_html=True,
    )

    st.header("Qualidade da Água")
    st.header("Filtros")

    grupos = st.multiselect(
        "Grupo", df["grupo"].dropna().unique(), df["grupo"].dropna().unique()
    )

    if len(grupos) == 0:
        regioes = st.multiselect("Região", [], [], disabled=True)
    else:
        regioes_disp = df[df["grupo"].isin(grupos)]["regiao"].dropna().unique().tolist()
        regioes = st.multiselect("Região", regioes_disp, regioes_disp)

    top_n = st.slider("Quantidade de Tops", 3, 20, 10)

    filtros_numericos = {}
    for col in num_cols:
        min_val = float(df[col].min()) if not df[col].isna().all() else 0
        max_val = float(df[col].max()) if not df[col].isna().all() else 1
        filtros_numericos[col] = st.slider(
            col.replace("_", " ").title(), min_val, max_val, (min_val, max_val)
        )

df_filtered = df[
    (df["grupo"].isin(grupos))
    & (df["regiao"].isin(regioes) if len(regioes) > 0 else True)
]

for col, (min_val, max_val) in filtros_numericos.items():
    df_filtered = df_filtered[df_filtered[col].between(min_val, max_val)]

df_region = df_filtered.groupby("regiao")[num_cols].mean().reset_index()
df_region["regiao_label"] = df_region["regiao"].apply(lambda x: format_label(x, 12))

label_fontsize = max(7, 12 - int(top_n / 3))
label_color = "#555555"

blue = "#1f77b4"
light_blue = "#5dade2"
mid_blue = "#2471a3"

col1, col2, col3, col4 = st.columns(4)

media_ph = df_filtered["ph_arduino"].mean()
media_turb = df_filtered["turbidez"].mean()
media_temp = df_filtered["temperatura_coleta"].mean()

with col1:
    st.metric("Média de pH", f"{0 if pd.isna(media_ph) else media_ph:.2f}")
with col2:
    st.metric("Média de Turbidez", f"{0 if pd.isna(media_turb) else media_turb:.2f}")
with col3:
    st.metric("Temperatura Média", f"{0 if pd.isna(media_temp) else media_temp:.2f} °C")
with col4:
    st.metric("Qtd Amostras", len(df_filtered))

st.subheader("Gráficos Comparativos")

colA, colB = st.columns(2)

with colA:
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.set_title("Distribuição de pH", fontsize=12)
    ax.hist(df_filtered["ph_arduino"].dropna(), bins=8, color=blue, alpha=0.7)
    ax.set_xlabel("pH", fontsize=11)
    ax.set_ylabel("Frequência", fontsize=11)
    plt.xticks(fontsize=label_fontsize)
    plt.yticks(fontsize=label_fontsize)
    st.pyplot(fig)

with colB:
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.set_title("Relação entre Turbidez e pH", fontsize=12)
    ax.scatter(
        df_filtered["ph_arduino"],
        df_filtered["turbidez"],
        color=mid_blue,
        alpha=0.7,
        s=60,
    )
    ax.set_xlabel("pH", fontsize=11)
    ax.set_ylabel("Turbidez (NTU)", fontsize=11)
    plt.xticks(fontsize=label_fontsize)
    plt.yticks(fontsize=label_fontsize)
    st.pyplot(fig)

colC, colD = st.columns(2)

with colC:
    df_plot = df_region.sort_values("temperatura_coleta", ascending=False).head(top_n)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.set_title("Temperatura da Coleta", fontsize=12)
    ax.bar(df_plot["regiao_label"], df_plot["temperatura_coleta"], color=light_blue)
    ax.set_ylabel("Temperatura (°C)", fontsize=11)
    plt.xticks(rotation=45, ha="right", fontsize=label_fontsize)
    plt.yticks(fontsize=label_fontsize)
    st.pyplot(fig)

with colD:
    df_plot = df_region.sort_values("umidade", ascending=True).head(top_n)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.set_title("Umidade por Região", fontsize=12)
    ax.plot(df_plot["regiao_label"], df_plot["umidade"], color=blue, marker="D")
    ax.set_ylabel("Umidade (%)", fontsize=11)
    plt.xticks(rotation=45, ha="right", fontsize=label_fontsize)
    plt.yticks(fontsize=label_fontsize)
    st.pyplot(fig)


colX, colY = st.columns(2)

with colX:
    df_plot = df_region.sort_values("ph_arduino", ascending=False).head(top_n)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.set_title("Comparação pH Fita x Arduino", fontsize=12)
    x = range(len(df_plot))
    ax.bar(
        [p - 0.2 for p in x],
        df_plot["ph_fita"],
        width=0.4,
        label="pH Fita",
        color=light_blue,
    )
    ax.bar(
        [p + 0.2 for p in x],
        df_plot["ph_arduino"],
        width=0.4,
        label="pH Arduino",
        color=mid_blue,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(
        df_plot["regiao_label"], rotation=45, ha="right", fontsize=label_fontsize
    )
    ax.set_ylabel("pH", fontsize=11)
    ax.legend()
    st.pyplot(fig)

corr_cols = ["ph_arduino", "turbidez", "temperatura_coleta", "umidade"]
corr = df_filtered[corr_cols].corr()

st.subheader("Matriz de Correlação")
fig, ax = plt.subplots(figsize=(6, 4))
ax.set_title("Correlação entre Variáveis", fontsize=13)
cax = ax.matshow(corr, cmap="Blues")
fig.colorbar(cax)
ax.set_xticks(range(len(corr.columns)))
ax.set_yticks(range(len(corr.columns)))
ax.set_xticklabels(corr.columns, rotation=45, fontsize=10)
ax.set_yticklabels(corr.columns, fontsize=10)
plt.tight_layout()
st.pyplot(fig)

st.subheader("Dados filtrados")
st.dataframe(df_filtered)

csv = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button("Baixar CSV", csv, "dados_filtrados.csv", "text/csv")
