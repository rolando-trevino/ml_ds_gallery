"""Home page shown when the user enters the application"""
import streamlit as st
import pandas as pd
pd.options.plotting.backend = "plotly"

df = pd.DataFrame()

def write():
    import re

    global df

    col1, col2 = st.beta_columns(2)

    with col1:
        if st.button("Download info") and len(df) == 0:
            df = get_info()
            df.to_csv("data/gallery/data_visualization/covid_19_mx/per_state.csv", index=False)
            df['state'] = df['state'].astype(int)

    with col2:
        if st.button("Read last saved info") and len(df) == 0:
            df = pd.read_csv("data/gallery/data_visualization/covid_19_mx/per_state.csv")
            df['state'] = df['state'].astype(int)
            # st.write(df.head()

    state_list = [
        "(0): - NACIONAL -",
        "(1): AGUASCALIENTES",
        "(2): BAJA CALIFORNIA",
        "(3): BAJA CALIFORNIA SUR",
        "(4): CAMPECHE",
        "(5): COAHUILA",
        "(6): COLIMA",
        "(7): CHIAPAS",
        "(8): CHIHUAHUA",
        "(9): CIUDAD DE MEXICO",
        "(10): DURANGO",
        "(11): GUANAJUATO",
        "(12): GUERRERO",
        "(13): HIDALGO",
        "(14): JALISCO",
        "(15): MEXICO",
        "(16): MICHOACAN",
        "(17): MORELOS",
        "(18): NAYARIT",
        "(19): NUEVO LEON",
        "(20): OAXACA",
        "(21): PUEBLA",
        "(22): QUERETARO",
        "(23): QUINTANA ROO",
        "(24): SAN LUIS POTOSI",
        "(25): SINALOA",
        "(26): SONORA",
        "(27): TABASCO",
        "(28): TAMAULIPAS",
        "(29): TLAXCALA",
        "(30): VERACRUZ",
        "(31): YUCATAN",
    ]
    
    if len(df) > 0:
        selected_state = st.selectbox("Select state:", state_list, index=0)
        selected_state_int = int(re.findall(r"(\d)", selected_state)[0])
        if selected_state_int != 0:
            df_filtered = df[df['state'] == selected_state_int].copy()
        else:
            df_filtered = df.groupby("date").sum().reset_index()
        df_filtered.rename(columns={"date": "Date", "positive": "Positive Cases"}, inplace=True)
        st.write(df_filtered.plot(x='Date', y='Positive Cases'))
        df_filtered['New Cases'] = df_filtered['Positive Cases'].diff()
        st.write(df_filtered.plot(x='Date', y='New Cases'))
        df_filtered['Moving Average (7)'] = df_filtered['New Cases'].rolling(window=7).mean()
        st.write(df_filtered.plot(x='Date', y='Moving Average (7)'))


def get_info():
    from stqdm import stqdm
    import os

    if not os.path.exists('data'):
        os.makedirs('data')

    with stqdm(range(4), mininterval=1) as pbar:
        pbar.set_description_str("Trying to open data...")
        try:
            df = pd.read_csv("data/gallery/data_visualization/covid_19_mx/data.csv", encoding='utf8')
            pbar.update(1)
        except:
            pbar.set_description_str("Downloading data...")
            df = read_zip()
            df.to_csv("data/gallery/data_visualization/covid_19_mx/data.csv", index=False)
            pbar.update(1)

        pbar.set_description_str("Processing raw data...")
        df = process_df(df)
        pbar.update(1)

        pbar.set_description_str("Preparing data at state level...")
        df_entidad_fecha = process_entidades(df)
        pbar.update(1)

        pbar.set_description_str("Calculating new cases data at state level...")
        df_casos_diarios_resumidos = casos_diarios_estado(df, df_entidad_fecha)
        pbar.update(1)

        return df_casos_diarios_resumidos

    


def read_zip():
    #!/usr/bin/env python3

    from csv import DictReader
    from io import TextIOWrapper, BytesIO
    from zipfile import ZipFile

    import requests

    url = "http://datosabiertos.salud.gob.mx/gobmx/salud/datos_abiertos/datos_abiertos_covid19.zip"
    r = requests.get(url)
    zip_ref = ZipFile(BytesIO(r.content))
    for name in zip_ref.namelist():
        print(name)
        with zip_ref.open(name) as file_contents:
            df = pd.read_csv(file_contents, encoding="utf8")
            return df

def process_df(df):
    df[(df['CLASIFICACION_FINAL'] == 1) | (df['CLASIFICACION_FINAL'] == 2) | (df['CLASIFICACION_FINAL'] == 3) ].head()
    df['FECHA_DEF'] = [ '2050-01-01' if x == '9999-99-99' else x for x in df['FECHA_DEF'] ]
    df['FECHA_ACTUALIZACION'] = pd.to_datetime(df['FECHA_ACTUALIZACION'])
    df['FECHA_INGRESO'] = pd.to_datetime(df['FECHA_INGRESO'])
    df['FECHA_SINTOMAS'] = pd.to_datetime(df['FECHA_SINTOMAS'])
    df['FECHA_SINTOMAS_MAS_CATORCE'] = pd.to_datetime(df['FECHA_SINTOMAS']) + pd.to_timedelta('14 days')
    fechaMuerte = pd.to_datetime('2050-01-01')
    df['FECHA_DEF'] = pd.to_datetime(df['FECHA_DEF'])
    df['IndicadorMuerte'] = [1 if rowFECHA_DEF != fechaMuerte else 0 for rowFECHA_DEF in df['FECHA_DEF']]
    df['IndicadorInfectado'] = [ 1 if x in [1,2,3] else 0 for x in df['CLASIFICACION_FINAL'] ]
    df['DiasSintomas'] = (pd.to_datetime(df['FECHA_ACTUALIZACION']) - pd.to_datetime(df['FECHA_SINTOMAS'])).dt.days
    df['IndicadorRecuperado'] = [1 if (int(rowCLASIFICACION_FINAL) in [1,2,3]) and (bool(rowIndicadorMuerte) == 0) and (int(rowDiasSintomas) >= 14) else 0 for (rowCLASIFICACION_FINAL, rowIndicadorMuerte, rowDiasSintomas) in zip(df['CLASIFICACION_FINAL'], df['IndicadorMuerte'], df['DiasSintomas'])]
    df['Fecha_Muerte'] = [pd.to_datetime(rowFECHA_DEF) if (int(rowCLASIFICACION_FINAL) in [1,2,3]) and (bool(rowIndicadorMuerte) == 1) else None for (rowFECHA_DEF, rowCLASIFICACION_FINAL, rowIndicadorMuerte) in zip(df['FECHA_DEF'], df['CLASIFICACION_FINAL'], df['IndicadorMuerte'])]
    df['Fecha_Recuperacion'] = [pd.to_datetime(rowFECHA_DEF) if (int(rowCLASIFICACION_FINAL) not in [1,2,3]) and (bool(rowIndicadorMuerte) != 1) else None for (rowFECHA_DEF, rowCLASIFICACION_FINAL, rowIndicadorMuerte) in zip(df['FECHA_DEF'], df['CLASIFICACION_FINAL'], df['IndicadorMuerte'])]
    return df

def process_entidades(df):
    import functools
    import operator

    df_entidad = df[(df['CLASIFICACION_FINAL'] == 1) | (df['CLASIFICACION_FINAL'] == 2) | (df['CLASIFICACION_FINAL'] == 3) ]
    df_entidad = df_entidad[['FECHA_SINTOMAS', 'ENTIDAD_RES']]
    temporal = df_entidad.groupby(['ENTIDAD_RES'])['FECHA_SINTOMAS']
    df_entidad = df_entidad.assign(min = temporal.transform(min))
    df_entidad = df_entidad[['ENTIDAD_RES', 'min']]
    df_entidad = df_entidad.drop_duplicates()
    df_entidad = df_entidad.sort_values(by = 'ENTIDAD_RES', ascending = True)
    df_entidad = df_entidad.reset_index(drop =  True)
    
    ListaFechas = []
    ListaFechasFixed = []
    ListaEntidades = []
    ListaEntidadesFixed = []
    Fecha_Maxima = df.loc[1,]['FECHA_ACTUALIZACION']

    for i in range(0,32):
        ListaFechas = (pd.date_range(start=pd.to_datetime(df_entidad.loc[i,]['min']), end = pd.to_datetime(Fecha_Maxima))).date
        ListaEntidades = [i + 1] * len(ListaFechas)
        ListaFechasFixed.append(ListaFechas)
        ListaEntidadesFixed.append(ListaEntidades)
    
    ListaFechasFixed = functools.reduce(operator.iconcat, ListaFechasFixed, [])
    ListaEntidadesFixed = functools.reduce(operator.iconcat, ListaEntidadesFixed, [])
    df_entidad_fecha = pd.DataFrame()
    df_entidad_fecha['ENTIDAD_RES'] = ListaEntidadesFixed
    df_entidad_fecha['FECHA'] = ListaFechasFixed
    df_entidad_fecha['FECHA'] = pd.to_datetime(df_entidad_fecha['FECHA'])

    return df_entidad_fecha


def casos_diarios_estado(df, df_entidad_fecha):
    import numpy as np

    df_opt = df[['CLASIFICACION_FINAL', 'FECHA_SINTOMAS', 'Fecha_Recuperacion', 'Fecha_Muerte', 'ENTIDAD_RES']].copy()
    df_opt['nuevos_casos'] = [0 for x in df_opt['CLASIFICACION_FINAL']]
    df_opt['nuevos_casos'] = [ 1 if ((clasificacion in [1, 2, 3]) & ((frecuperacion is not None) | (fmuerte is not None))) else 0 for clasificacion, frecuperacion, fmuerte in zip(df_opt['CLASIFICACION_FINAL'], df_opt['Fecha_Recuperacion'], df_opt['Fecha_Muerte']) ]
    
    df_casos_diarios = df_opt[['ENTIDAD_RES', 'FECHA_SINTOMAS', 'nuevos_casos']].copy()
    df_casos_diarios.set_index(['ENTIDAD_RES', 'FECHA_SINTOMAS'], inplace=True)
    df_casos_diarios.sort_index(inplace=True)

    df_casos_diarios_resumidos = df_casos_diarios.groupby(level=[0,1]).sum().copy()
    df_casos_diarios_resumidos = df_casos_diarios_resumidos[df_casos_diarios_resumidos['nuevos_casos'] != 0]

    df_entidad_fecha['nuevos_casos'] = [0 for x in df_entidad_fecha['ENTIDAD_RES']]
    df_entidad_fecha.columns = ['ENTIDAD_RES', 'FECHA_SINTOMAS', 'nuevos_casos']
    df_entidad_fecha.set_index(['ENTIDAD_RES', 'FECHA_SINTOMAS'], inplace=True)

    df_casos_diarios_resumidos = df_casos_diarios_resumidos.join(df_entidad_fecha, how='outer', lsuffix='_orig', rsuffix='_calendario')
    df_casos_diarios_resumidos['nuevos_casos'] = [orig if (~np.isnan(orig)) else calendario for orig, calendario in zip(df_casos_diarios_resumidos['nuevos_casos_orig'], df_casos_diarios_resumidos['nuevos_casos_calendario'])]

    del df_casos_diarios_resumidos['nuevos_casos_orig']
    del df_casos_diarios_resumidos['nuevos_casos_calendario']

    df_casos_diarios_resumidos = df_casos_diarios_resumidos.groupby(level=0)['nuevos_casos'].cumsum()
    df_casos_diarios_resumidos.columns = []
    df_casos_diarios_resumidos = pd.DataFrame(df_casos_diarios_resumidos)

    df_casos_diarios_resumidos.reset_index(inplace=True)

    df_casos_diarios_resumidos.columns = ['state', 'date', 'positive']

    return df_casos_diarios_resumidos