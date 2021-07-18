"""Home page shown when the user enters the application"""
import streamlit as st
import pandas as pd
pd.options.plotting.backend = "plotly"
import plotly.express as px

df = pd.DataFrame()

def write():
    import re
    from datetime import datetime, date
    import json
    from urllib.request import urlopen

    global df

    st.write(f"Today is: {datetime.date(datetime.now())}")

    check_download = st.checkbox("Download updated info")

    if st.button("Run process"):
        df_full = pd.DataFrame()
        if check_download:
            df = get_info()
            df.to_csv("data/gallery/data_visualization/covid_19_mx/per_state.csv", index=False)
            df['state'] = df['state'].astype(int)
            df['date'] = pd.to_datetime(df['date'])
            df.sort_values(by=['state', 'date'], inplace=True)
            st.success("Data is now up to date")
        else:
            df = pd.read_csv("data/gallery/data_visualization/covid_19_mx/per_state.csv")
            df['state'] = df['state'].astype(int)
            df['date'] = pd.to_datetime(df['date'])
            df.sort_values(by=['state', 'date'], inplace=True)

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
        date_now = datetime.strftime(pd.to_datetime(df['date'].values[-1]), "%Y-%m-%d")
        st.write(f"Data Date: {date_now}")

        # Overall map
        with urlopen('https://covid19.sinave.gob.mx/coronavirus/Mexico_estados.json') as response:
            Mexico = json.load(response) # Javascrip object notation 

        state_id_map = {}
        for feature in Mexico['features']:
            id_ = feature['id']
            estado_ = feature['properties']['ESTADO']
            state_id_map[id_] = estado_

        df_to_map = df.copy()
        df_to_map.set_index(['state', 'date'])
        df_to_map['new cases'] = df_to_map['positive'].diff(1)
        df_to_map['new cases'] = [x if x >= 0 else 0 for x in df_to_map['new cases']]
        df_to_map = df_to_map.reset_index().groupby(['state', pd.Grouper(key='date', freq='M')]).sum().reset_index()
        df_to_map['state_fill'] = [(str(x).zfill(2)) for x in df_to_map['state']]
        df_to_map['state_name'] = [state_id_map[x] for x in df_to_map['state_fill']]
        df_to_map['date'] = pd.to_datetime(df_to_map['date'])
        df_to_map['day'] = df_to_map['date'].dt.day
        df_to_map['month'] = df_to_map['date'].dt.month
        df_to_map['year'] = df_to_map['date'].dt.year
        df_to_map['date'] = [datetime.strftime(date(y, m, d), "%Y-%m-%d") for (y, m, d) in zip(df_to_map['year'], df_to_map['month'], df_to_map['day'])]

        fig = px.choropleth(
            df_to_map, # database
            locations = 'state_fill', #define the limits on the map/geography
            geojson = Mexico, #shape information
            color = "new cases", #defining the color of the scale through the database
            hover_name = 'state_name', #the information in the box
            title = 'COVID-19 Monthly New Cases in Mexico', #title of the map
            animation_frame  = 'date',
            width = 1024,
            height = 768
        )
        fig.update_geos(fitbounds = "locations", visible = False)
        st.plotly_chart(fig, use_container_width=True)
        
        selected_state = st.selectbox("Select state:", state_list, index=0)
        selected_state_int = int(re.findall(r"(\d+)", selected_state)[0])

        if selected_state_int != 0:
            df_filtered = df[df['state'] == selected_state_int].copy()
        else:
            df_filtered = df.groupby('date').sum().reset_index()

        df_filtered.rename(columns={"date": "Date", "positive": "Positive Cases"}, inplace=True)

        # Cases over time
        fig = px.line(df_filtered, x="Date", y="Positive Cases", title="Cumulative Positive Cases")
        st.plotly_chart(fig, use_container_width=True)

        # New cases
        df_filtered['New Cases'] = df_filtered['Positive Cases'].diff(1)
        fig = px.line(df_filtered, x="Date", y="New Cases", title="Daily New Cases")
        st.plotly_chart(fig, use_container_width=True)

        # New cases moving average of 7 days
        df_filtered['Moving Average (7)'] = df_filtered['New Cases'].rolling(window=7).mean()
        fig = px.line(df_filtered, x="Date", y="Moving Average (7)", title="New Cases Moving Average (7 days)")
        st.plotly_chart(fig, use_container_width=True)


def get_info():
    from stqdm import stqdm
    import os

    if not os.path.exists('data'):
        os.makedirs('data')

    with stqdm(range(4), mininterval=1) as pbar:
        pbar.set_description_str("Downloading data...")
        df = read_zip()
        # df.to_csv("data/gallery/data_visualization/covid_19_mx/data.csv", index=False)
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
    # df[(df['CLASIFICACION_FINAL'] == 1) | (df['CLASIFICACION_FINAL'] == 2) | (df['CLASIFICACION_FINAL'] == 3) ].head()
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

    df_entidad = df[(df['CLASIFICACION_FINAL'] == 1) | (df['CLASIFICACION_FINAL'] == 2) | (df['CLASIFICACION_FINAL'] == 3) ].copy()
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
        ListaFechas = (pd.date_range(start=pd.to_datetime("1/1/2020"), end = pd.to_datetime(Fecha_Maxima))).date
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