import pandas as pd
import pymysql
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
    encoding="latin1",
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
