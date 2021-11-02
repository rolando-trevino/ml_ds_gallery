import pandas as pd
import numpy as np
import os
from io import BytesIO
from zipfile import ZipFile
import requests
import functools
import operator

if not os.path.exists("data/gallery/data_visualization/covid_19_mx"):
    os.makedirs("data/gallery/data_visualization/covid_19_mx")


def read_zip():
    #!/usr/bin/env python3

    url = "http://datosabiertos.salud.gob.mx/gobmx/salud/datos_abiertos/datos_abiertos_covid19.zip"
    r = requests.get(url)
    zip_ref = ZipFile(BytesIO(r.content))
    for name in zip_ref.namelist():
        print(name)
        with zip_ref.open(name) as file_contents:
            df = pd.read_csv(
                file_contents,
                encoding="utf8",
                usecols=lambda x: x.upper()
                in [
                    "FECHA_DEF",
                    "FECHA_ACTUALIZACION",
                    "FECHA_INGRESO",
                    "FECHA_SINTOMAS",
                    "CLASIFICACION_FINAL",
                    "ENTIDAD_RES",
                ],
            )
            return df


def process_df(df):
    # df[(df['CLASIFICACION_FINAL'] == 1) | (df['CLASIFICACION_FINAL'] == 2) | (df['CLASIFICACION_FINAL'] == 3) ].head()
    df["FECHA_DEF"] = [
        "2050-01-01" if x == "9999-99-99" else x for x in df["FECHA_DEF"]
    ]
    df["FECHA_ACTUALIZACION"] = pd.to_datetime(df["FECHA_ACTUALIZACION"])
    df["FECHA_INGRESO"] = pd.to_datetime(df["FECHA_INGRESO"])
    df["FECHA_SINTOMAS"] = pd.to_datetime(df["FECHA_SINTOMAS"])
    df["FECHA_SINTOMAS_MAS_CATORCE"] = pd.to_datetime(
        df["FECHA_SINTOMAS"]
    ) + pd.to_timedelta("14 days")
    fechaMuerte = pd.to_datetime("2050-01-01")
    df["FECHA_DEF"] = pd.to_datetime(df["FECHA_DEF"])
    df["IndicadorMuerte"] = [
        1 if rowFECHA_DEF != fechaMuerte else 0 for rowFECHA_DEF in df["FECHA_DEF"]
    ]
    df["IndicadorInfectado"] = [
        1 if x in [1, 2, 3] else 0 for x in df["CLASIFICACION_FINAL"]
    ]
    df["DiasSintomas"] = (
        pd.to_datetime(df["FECHA_ACTUALIZACION"]) - pd.to_datetime(df["FECHA_SINTOMAS"])
    ).dt.days
    df["IndicadorRecuperado"] = [
        1
        if (int(rowCLASIFICACION_FINAL) in [1, 2, 3])
        and (bool(rowIndicadorMuerte) == 0)
        and (int(rowDiasSintomas) >= 14)
        else 0
        for (rowCLASIFICACION_FINAL, rowIndicadorMuerte, rowDiasSintomas) in zip(
            df["CLASIFICACION_FINAL"], df["IndicadorMuerte"], df["DiasSintomas"]
        )
    ]
    df["Fecha_Muerte"] = [
        pd.to_datetime(rowFECHA_DEF)
        if (int(rowCLASIFICACION_FINAL) in [1, 2, 3])
        and (bool(rowIndicadorMuerte) == 1)
        else None
        for (rowFECHA_DEF, rowCLASIFICACION_FINAL, rowIndicadorMuerte) in zip(
            df["FECHA_DEF"], df["CLASIFICACION_FINAL"], df["IndicadorMuerte"]
        )
    ]
    df["Fecha_Recuperacion"] = [
        pd.to_datetime(rowFECHA_DEF)
        if (int(rowCLASIFICACION_FINAL) not in [1, 2, 3])
        and (bool(rowIndicadorMuerte) != 1)
        else None
        for (rowFECHA_DEF, rowCLASIFICACION_FINAL, rowIndicadorMuerte) in zip(
            df["FECHA_DEF"], df["CLASIFICACION_FINAL"], df["IndicadorMuerte"]
        )
    ]
    return df


def process_entidades(df):
    df_entidad = df[
        (df["CLASIFICACION_FINAL"] == 1)
        | (df["CLASIFICACION_FINAL"] == 2)
        | (df["CLASIFICACION_FINAL"] == 3)
    ].copy()
    df_entidad = df_entidad[["FECHA_SINTOMAS", "ENTIDAD_RES"]]
    temporal = df_entidad.groupby(["ENTIDAD_RES"])["FECHA_SINTOMAS"]
    df_entidad = df_entidad.assign(min=temporal.transform(min))
    df_entidad = df_entidad[["ENTIDAD_RES", "min"]]
    df_entidad = df_entidad.drop_duplicates()
    df_entidad = df_entidad.sort_values(by="ENTIDAD_RES", ascending=True)
    df_entidad = df_entidad.reset_index(drop=True)

    ListaFechas = []
    ListaFechasFixed = []
    ListaEntidades = []
    ListaEntidadesFixed = []
    Fecha_Maxima = df.loc[
        1,
    ]["FECHA_ACTUALIZACION"]

    for i in range(0, 32):
        ListaFechas = (
            pd.date_range(
                start=pd.to_datetime("1/1/2020"), end=pd.to_datetime(Fecha_Maxima)
            )
        ).date
        ListaEntidades = [i + 1] * len(ListaFechas)
        ListaFechasFixed.append(ListaFechas)
        ListaEntidadesFixed.append(ListaEntidades)

    ListaFechasFixed = functools.reduce(operator.iconcat, ListaFechasFixed, [])
    ListaEntidadesFixed = functools.reduce(operator.iconcat, ListaEntidadesFixed, [])
    df_entidad_fecha = pd.DataFrame()
    df_entidad_fecha["ENTIDAD_RES"] = ListaEntidadesFixed
    df_entidad_fecha["FECHA"] = ListaFechasFixed
    df_entidad_fecha["FECHA"] = pd.to_datetime(df_entidad_fecha["FECHA"])

    return df_entidad_fecha


def casos_diarios_estado(df, df_entidad_fecha):
    df_opt = df[
        [
            "CLASIFICACION_FINAL",
            "FECHA_INGRESO",
            "FECHA_SINTOMAS",
            "Fecha_Recuperacion",
            "Fecha_Muerte",
            "ENTIDAD_RES",
        ]
    ].copy()
    df_opt["nuevos_casos_sintomas"] = [0 for x in df_opt["CLASIFICACION_FINAL"]]
    df_opt["nuevos_casos_sintomas"] = [
        1
        if (
            (clasificacion in [1, 2, 3])
            & ((frecuperacion is not None) | (fmuerte is not None))
        )
        else 0
        for clasificacion, frecuperacion, fmuerte in zip(
            df_opt["CLASIFICACION_FINAL"],
            df_opt["Fecha_Recuperacion"],
            df_opt["Fecha_Muerte"],
        )
    ]
    df_opt["nuevos_casos_confirmados"] = [
        1
        if (
            (clasificacion in [1, 2, 3])
            & ((frecuperacion is not None) | (fmuerte is not None))
        )
        else 0
        for clasificacion, frecuperacion, fmuerte in zip(
            df_opt["CLASIFICACION_FINAL"],
            df_opt["Fecha_Recuperacion"],
            df_opt["Fecha_Muerte"],
        )
    ]

    df_casos_sintomas = df_opt[
        ["ENTIDAD_RES", "FECHA_SINTOMAS", "nuevos_casos_sintomas"]
    ].copy()
    df_casos_sintomas.set_index(["ENTIDAD_RES", "FECHA_SINTOMAS"], inplace=True)
    df_casos_sintomas.sort_index(inplace=True)
    df_casos_sintomas_resumidos = df_casos_sintomas.groupby(level=[0, 1]).sum().copy()
    df_casos_sintomas_resumidos = df_casos_sintomas_resumidos[
        df_casos_sintomas_resumidos["nuevos_casos_sintomas"] != 0
    ]
    temp = df_entidad_fecha.copy()
    temp["nuevos_casos_sintomas"] = [0 for x in df_entidad_fecha["ENTIDAD_RES"]]
    temp.columns = ["ENTIDAD_RES", "FECHA_SINTOMAS", "nuevos_casos_sintomas"]
    temp.set_index(["ENTIDAD_RES", "FECHA_SINTOMAS"], inplace=True)
    df_casos_sintomas_resumidos = df_casos_sintomas_resumidos.join(
        temp, how="outer", lsuffix="_orig", rsuffix="_calendario"
    )
    df_casos_sintomas_resumidos["nuevos_casos_sintomas"] = [
        orig if (~np.isnan(orig)) else calendario
        for orig, calendario in zip(
            df_casos_sintomas_resumidos["nuevos_casos_sintomas_orig"],
            df_casos_sintomas_resumidos["nuevos_casos_sintomas_calendario"],
        )
    ]
    del df_casos_sintomas_resumidos["nuevos_casos_sintomas_orig"]
    del df_casos_sintomas_resumidos["nuevos_casos_sintomas_calendario"]
    df_casos_sintomas_resumidos = df_casos_sintomas_resumidos.groupby(level=0)[
        "nuevos_casos_sintomas"
    ].cumsum()
    df_casos_sintomas_resumidos.columns = []
    df_casos_sintomas_resumidos = pd.DataFrame(df_casos_sintomas_resumidos)
    df_casos_sintomas_resumidos.reset_index(inplace=True)
    df_casos_sintomas_resumidos.columns = ["state", "date", "positive_symptoms"]

    df_casos_confirmados = df_opt[
        ["ENTIDAD_RES", "FECHA_INGRESO", "nuevos_casos_confirmados"]
    ].copy()
    df_casos_confirmados.set_index(["ENTIDAD_RES", "FECHA_INGRESO"], inplace=True)
    df_casos_confirmados.sort_index(inplace=True)
    df_casos_confirmados_resumidos = (
        df_casos_confirmados.groupby(level=[0, 1]).sum().copy()
    )
    df_casos_confirmados_resumidos = df_casos_confirmados_resumidos[
        df_casos_confirmados_resumidos["nuevos_casos_confirmados"] != 0
    ]
    temp = df_entidad_fecha.copy()
    temp["nuevos_casos_confirmados"] = [0 for x in df_entidad_fecha["ENTIDAD_RES"]]
    temp.columns = ["ENTIDAD_RES", "FECHA_INGRESO", "nuevos_casos_confirmados"]
    temp.set_index(["ENTIDAD_RES", "FECHA_INGRESO"], inplace=True)
    df_casos_confirmados_resumidos = df_casos_confirmados_resumidos.join(
        temp, how="outer", lsuffix="_orig", rsuffix="_calendario"
    )
    df_casos_confirmados_resumidos["nuevos_casos_confirmados"] = [
        orig if (~np.isnan(orig)) else calendario
        for orig, calendario in zip(
            df_casos_confirmados_resumidos["nuevos_casos_confirmados_orig"],
            df_casos_confirmados_resumidos["nuevos_casos_confirmados_calendario"],
        )
    ]
    del df_casos_confirmados_resumidos["nuevos_casos_confirmados_orig"]
    del df_casos_confirmados_resumidos["nuevos_casos_confirmados_calendario"]
    df_casos_confirmados_resumidos = df_casos_confirmados_resumidos.groupby(level=0)[
        "nuevos_casos_confirmados"
    ].cumsum()
    df_casos_confirmados_resumidos.columns = []
    df_casos_confirmados_resumidos = pd.DataFrame(df_casos_confirmados_resumidos)
    df_casos_confirmados_resumidos.reset_index(inplace=True)
    df_casos_confirmados_resumidos.columns = ["state", "date", "positive_confirmed"]

    df_casos_resumidos = pd.DataFrame()
    df_casos_resumidos["state"] = df_casos_confirmados_resumidos["state"]
    df_casos_resumidos["date"] = df_casos_confirmados_resumidos["date"]
    df_casos_resumidos["positive_symptoms"] = df_casos_sintomas_resumidos[
        "positive_symptoms"
    ]
    df_casos_resumidos["positive_confirmed"] = df_casos_confirmados_resumidos[
        "positive_confirmed"
    ]

    df_casos_resumidos.columns = [
        "state",
        "date",
        "positive_symptoms",
        "positive_confirmed",
    ]

    return df_casos_resumidos


# print("read_zip...")
df = read_zip()
# print("process_df...")
df = process_df(df)
# print("process_entidades...")
df_entidad_fecha = process_entidades(df)
# print("casos_diarios_estado...")
df_casos_diarios_resumidos = casos_diarios_estado(df, df_entidad_fecha)
# print(f"{len(df_casos_diarios_resumidos)=}")
# print("to_csv...")
df_casos_diarios_resumidos.to_csv(
    "data/gallery/data_visualization/covid_19_mx/per_state.csv", index=False
)
