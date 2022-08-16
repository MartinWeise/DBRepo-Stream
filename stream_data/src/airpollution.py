from queue import Empty
from time import sleep
import requests as rq
import pandas as pd
from datetime import datetime
import pytz
from flatten_json import flatten
import pika
import json
import numpy as np
import dbrepo as dbr


client = dbr.Client(username='jtaha',password='pw',url='http://s125.dl.hpc.tuwien.ac.at')


index_col = ['stationid','component','time']

def get_current_file_path() -> str:
    tz = pytz.timezone('Europe/Berlin')
    now = datetime.now(tz)
    year, week, weekday = now.isocalendar()
    return f'data/poll/data_{year}_{week}_{weekday}.csv'


def open_current_file() -> pd.DataFrame:
    try:
        return pd.read_csv(get_current_file_path())
    except:
        return pd.DataFrame()

def persist_current_dataframe(df: pd.DataFrame) -> None:
        df.to_csv(get_current_file_path())

def extract_airpollution_data() -> pd.DataFrame:

    df = pd.DataFrame()

    for component in ['SO2','O3','NO2','NO','CO','PM10_K','PM2_5_K']:
        url = f'https://luft.umweltbundesamt.at/pub/map_chart/index.pl?runmode=values_json&MEANTYPE=HMW&COMPONENT={component}'

        res = rq.get(url)
        data = res.json()['stations']
        for station in data:
            if 'Fotos' in station:
                del station['Fotos']    
            if 'FotoAnzahl' in station:
                del station['FotoAnzahl']    

        data = [flatten(record) for record in data]

        data = pd.DataFrame(data)
        df = pd.concat([df,data])

    # df = df.pivot_table(values='value', index=['stationid','time'], columns='compname', aggfunc='first')
    # df = df.set_index(index_col)
    df = df.rename(columns={
    'compname':'component',
    'gml$Point_gml$coord_X':'x_coord',
    'gml$Point_gml$coord_Y':'y_coord',
    'gml$Point_gml$coord_Z':'z_coord',
    'MetaInfo_Name': 'meta_name',
    'MetaInfo_Owner': 'meta_owner',
    'MetaInfo_Location': 'meta_location',
    })

    col = ['component','stationid','unit','meantype','value','meta_name','meta_owner',
            'meta_location','x_coord','y_coord','z_coord','time']
    df = df[col]

    df['time'] = pd.to_datetime(df['time']).values.astype(int) / 10**9
    df['time'] = df['time'].astype(int)
    df['value'] = df['value'].fillna(0).astype(float)
    
    return df

def send(df : pd.DataFrame):
    client.add_data_table(1,1,1,df)

    # credentials = pika.PlainCredentials('jtaha', 'pw')
    # parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials)
    # connection = pika.BlockingConnection(parameters=parameters)
    # channel = connection.channel()

    # for index, row in df.iterrows():
    #     # message = {
    #     #     'meantype': row['meantype'],
    #     #     'x_coord': row['gml$Point_gml$coord_X'],
    #     #     'y_coord': row['gml$Point_gml$coord_Y'],
    #     #     'z_coord': row['gml$Point_gml$coord_Z'],
    #     #     'component': row['compname'],
    #     #     'stationid': row['stationid'],
    #     #     'unit': row['unit'],
    #     #     'value': row['value'],
    #     #     'meta_name': row['MetaInfo_Name'],
    #     #     'meta_owner': row['MetaInfo_Owner'],
    #     #     'meta_location': row['MetaInfo_Location'],
    #     #     'time': row['time'],
    #     # }
    #     payload = json.dumps(row.to_dict()).encode('utf8')
    #     channel.basic_publish(exchange='airdata', routing_key='austria', body=payload)
    
        

while True:
    df = open_current_file()
    df = df if df.empty else df.set_index(index_col)
    new = extract_airpollution_data()
    new = new.set_index(index_col) 

    new = new.loc[~new.index.isin(df.index)]
    df = pd.concat([df,new])
    persist_current_dataframe(df)

    new.reset_index(inplace=True)
    send(new)

    sleep(600)


