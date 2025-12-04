import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector
from dotenv import load_dotenv
import os
from pathlib import Path
import streamlit.components.v1 as components

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

[data-testid=stSidebar] p{ 
color: white !important;
}

[data-baseweb="radio"] label {
    color: white !important;
}

[data-baseweb="radio"] svg {
    fill: white !important;
}

[data-baseweb="radio"] svg circle {
    stroke: white !important;
}

[data-baseweb="radio"] svg path {
    fill: white !important;
}

[data-baseweb="radio"] label:hover {
    color: white !important;
    opacity: 0.8;
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

.st-au.st-av.st-aw.st-ax.st-ay.st-az.st-b0.st-ae.st-b1.st-b2.st-b3.st-b4.st-b5.st-b6.st-b7.st-b8.st-b9.st-ba.st-bb.st-bc {
    background-color: #1f77b4 !important;
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
    st.header("Navegação")

    pages = {
        "Dashboard": "dashboard",
        "VitaHidric": "hf_space",
        "Sobre": "about",
        "Banco de Dados": "database",
    }
    page = st.radio("Ir para:", list(pages.keys()), index=0)


if pages[page] == "hf_space":
    st.write(
        "O modelo de visão computacional revoluciona nosso modo de classificação da turbidez da água, visando ser uma solução acessível e eficiente no tratamento hídrico."
    )

    hf_space_url = "https://drirayv-pi-2-semestre.hf.space"

    components.iframe(hf_space_url, height=800, scrolling=True)

elif pages[page] == "about":
    st.subheader("Sobre este app")
    st.markdown(
        """
# Sobre o Projeto – Vitta Hídic

O **Vitta Hídic** é uma solução inteligente desenvolvida para avaliar a qualidade da água de forma rápida, visual e acessível. O sistema combina análise de dados e inteligência artificial para oferecer um diagnóstico claro e confiável sobre diferentes parâmetros da água.

## Análise e Tratamento de Dados
- Utiliza informações fornecidas por diferentes consumidores finais, incluindo pH, temperatura, turbidez e condutividade.
- O código em Python realiza limpeza, padronização e modelagem dos dados para gerar indicadores precisos.

## Inteligência Artificial
- Emprega um modelo de visão computacional via Hugging Face para estimar a turbidez da água por meio de imagens.
- Complementa as medições com uma análise visual automatizada, ampliando a precisão do diagnóstico.

## Dashboard e Visualização
- Os resultados são apresentados em um dashboard desenvolvido no Power BI.
- Exibe valores ideais, parâmetros medidos e comparações entre o estado ideal e o estado real da água.

## Compromisso Ambiental
- O projeto se alinha à Meta 6.3 dos ODS, contribuindo para o monitoramento e melhoria contínua da qualidade da água.
"""
    )
elif pages[page] == "database":
    st.subheader("Nossa base de dados")
    st.image(image="https://i.ibb.co/6KhxNk1/Diagrama-sem-nome-drawio.png")
    st.write("Criação das tabelas")
    st.code(
        """
CREATE TABLE grupos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL
);

CREATE TABLE localizacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),
    latitude DECIMAL(12,6),
    longitude DECIMAL(12,6),
    descricao TEXT
);

CREATE TABLE amostras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_inclusao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    grupo_id INT NOT NULL,
    localizacao_id INT NOT NULL,
    FOREIGN KEY (grupo_id) REFERENCES grupos(id),
    FOREIGN KEY (localizacao_id) REFERENCES localizacao(id)
);

CREATE TABLE qualidade_agua (
    id INT AUTO_INCREMENT PRIMARY KEY,
    amostra_id INT NOT NULL UNIQUE,
    temperatura_coleta DECIMAL(5,2),
    temperatura_analise DECIMAL(5,2),
    turbidez DECIMAL(10,2),
    ph_fita DECIMAL(4,2),
    ph_arduino DECIMAL(4,2),
    umidade DECIMAL(5,2),
    FOREIGN KEY (amostra_id) REFERENCES amostras(id)
);

CREATE TABLE condutividade (
    id INT AUTO_INCREMENT PRIMARY KEY,
    amostra_id INT NOT NULL UNIQUE,
    condutividade DECIMAL(10,2),
    FOREIGN KEY (amostra_id) REFERENCES amostras(id)
);

""",
        language="sql",
    )

    st.write("Tratamento dos dados")
    st.code(
        language="python",
        body="""import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = (BASE_DIR / ".." / ".." / ".." / ".env").resolve()
load_dotenv(ENV_PATH)

engine = create_engine(
    f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"
)

df_coleta = pd.read_csv(
    "../planilhas/BcTec 2025_Coleta_Agua - Página1.csv",
    encoding="utf-8",
    sep=None,
    engine="python",
)

df_coleta["Ph(Arduino)"] = (
    df_coleta["Ph(Arduino)"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.strip()
    .astype(float)
)
df_coleta["Ph(Fita)"] = (
    df_coleta["Ph(Fita)"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.strip()
    .astype(float)
)

df_coleta["Umidade(%)"] = (
    df_coleta["Umidade(%)"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.strip()
    .astype(float)
)
df_coleta["Turbidez(NTU)"] = (
    df_coleta["Turbidez(NTU)"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.strip()
    .astype(float)
)

cols_temp = ["Temperatura_Coleta", "Temperatura_Analise"]
for col in cols_temp:
    df_coleta[col] = (
        df_coleta[col]
        .astype(str)
        .str.replace("Â", "", regex=False)
        .str.replace("º", "", regex=False)
        .str.replace("°", "", regex=False)
        .str.replace("C", "", regex=False)
        .str.replace("c", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

df_coleta["Grupo"] = (
    df_coleta["Grupo"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace(" ", "", regex=False)
    .str.replace('"', "", regex=False)
    .str.replace("'", "", regex=False)
    .str.strip()
    .astype(int)
)

df_coleta["Latitude"] = df_coleta["Latitude"].astype(str)
df_coleta["Longitude"] = df_coleta["Longitude"].astype(str)

df_coleta["Latitude"] = (
    df_coleta["Latitude"]
    .str.replace("Â", "", regex=False)
    .str.replace("º", "", regex=False)
    .str.replace("°", "", regex=False)
    .str.replace("'", "", regex=False)
    .str.replace(",", ".", regex=False)
)

df_coleta["Longitude"] = (
    df_coleta["Longitude"]
    .str.replace("Â", "", regex=False)
    .str.replace("º", "", regex=False)
    .str.replace("°", "", regex=False)
    .str.replace("'", "", regex=False)
    .str.replace(",", ".", regex=False)
)

df_coleta.loc[df_coleta["Longitude"].str.match(r"^-?\d{7,9}$"), "Longitude"] = (
    df_coleta["Longitude"].str.replace(r"(-?\d{2})(\d+)", r"\1.\2", regex=True)
)

df_coleta.loc[df_coleta["Latitude"].str.match(r"^-?\d{7,9}$"), "Latitude"] = df_coleta[
    "Latitude"
].str.replace(r"(-?\d{2})(\d+)", r"\1.\2", regex=True)

df_coleta["Latitude"] = df_coleta["Latitude"].str.replace("..", ".", regex=False)
df_coleta["Longitude"] = df_coleta["Longitude"].str.replace("..", ".", regex=False)

df_coleta["Latitude"] = df_coleta["Latitude"].str.replace(r"\.(?=.*\.)", "", regex=True)
df_coleta["Longitude"] = df_coleta["Longitude"].str.replace(
    r"\.(?=.*\.)", "", regex=True
)

df_coleta["Latitude"] = df_coleta["Latitude"].astype(float)
df_coleta["Longitude"] = df_coleta["Longitude"].astype(float)

df_local = df_coleta.rename(
    columns={
        "Local": "nome",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Descricao_Local": "descricao",
    }
)[["nome", "latitude", "longitude", "descricao"]]

df_local.to_sql("localizacao", engine, if_exists="append", index=False)

localizacoes = (
    pd.read_sql("SELECT * FROM localizacao", engine)
    .sort_values("id")
    .reset_index(drop=True)
)

df_coleta = df_coleta.reset_index(drop=True)
df_coleta["localizacao_id"] = localizacoes["id"]

df_grupos = df_coleta[["Grupo"]].drop_duplicates().rename(columns={"Grupo": "id"})
df_grupos["nome"] = "Grupo " + df_grupos["id"].astype(str)
df_grupos.to_sql("grupos", engine, if_exists="append", index=False)

df_amostras = pd.DataFrame(
    {"grupo_id": df_coleta["Grupo"], "localizacao_id": df_coleta["localizacao_id"]}
)

df_amostras.to_sql("amostras", engine, if_exists="append", index=False)

amostras = pd.read_sql("SELECT * FROM amostras", engine)

df_q = pd.DataFrame(
    {
        "amostra_id": amostras["id"],
        "temperatura_coleta": df_coleta["Temperatura_Coleta"],
        "temperatura_analise": df_coleta["Temperatura_Analise"],
        "turbidez": df_coleta["Turbidez(NTU)"],
        "ph_fita": df_coleta["Ph(Fita)"],
        "ph_arduino": df_coleta["Ph(Arduino)"],
        "umidade": df_coleta["Umidade(%)"],
    }
)

df_q.to_sql("qualidade_agua", engine, if_exists="append", index=False)

grupo4_amostras = amostras[amostras["grupo_id"] == 4]

df_cond = pd.DataFrame(
    {
        "amostra_id": grupo4_amostras["id"],
        "condutividade": [17.4, 79.5, -157, -141, 126, 89, 194],
    }
)

df_cond.to_sql("condutividade", engine, if_exists="append", index=False)
""",
    )

else:
    with st.sidebar:
        st.header("Filtros")

        grupos = st.multiselect(
            "Grupo", df["grupo"].dropna().unique(), df["grupo"].dropna().unique()
        )

        if len(grupos) == 0:
            regioes = st.multiselect("Região", [], [], disabled=True)
        else:
            regioes_disp = (
                df[df["grupo"].isin(grupos)]["regiao"].dropna().unique().tolist()
            )
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
        st.metric(
            "Média de Turbidez", f"{0 if pd.isna(media_turb) else media_turb:.2f}"
        )
    with col3:
        st.metric(
            "Temperatura Média", f"{0 if pd.isna(media_temp) else media_temp:.2f} °C"
        )
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
        df_plot = df_region.sort_values("temperatura_coleta", ascending=False).head(
            top_n
        )
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
