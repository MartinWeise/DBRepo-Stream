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


col = ['stationid','component','time','unit','meantype','value','meta_name','meta_owner',
            'meta_location','x_coord','y_coord','z_coord']

col_type = ['string','string','number','string','string','decimal','string','string','string','decimal','decimal','decimal']



index_col = ['stationid','component','time']

def get_current_file_path() -> str:
    tz = pytz.timezone('Europe/Berlin')
    now = datetime.now(tz)
    year, week, weekday = now.isocalendar()
    return f'data/poll/data_{year}_{week}_{weekday}.csv'

def get_current_dbrepo_table_name() -> str:
    tz = pytz.timezone('Europe/Berlin')
    now = datetime.now(tz)
    year, week, weekday = now.isocalendar()
    table_name = f'data_{year}_{week}'
    table_desc = f'This table provides real-time air-data from around 170 air measuring stations in Austria from week {week} of year {year}.'
    return table_name, table_desc

def generate_dbrepo_table(name, desc):
    columns = [{
            "name": x,
            "type": y,
            "null_allowed": True,
            "primary_key": False,
            "check_expression": None,
            "foreign_key": None,
            "references": None,
            "unique": False
        } for x,y in zip(col,col_type)]
    client.generate_table_in_database(cid,dbid,name,desc,columns)

def get_current_tables_in_database(cid, dbid) -> list:
    data = client.fetch_database_info(cid, dbid)
    return data['name']

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

    df = df[col]

    df['time'] = pd.to_datetime(df['time']).values.astype(int) / 10**9
    df['time'] = df['time'].astype(int)
    df = df.astype({"x_coord": float, "y_coord": float, "z_coord": float, "value": float}, errors='ignore')

    return df

def send(df : pd.DataFrame):

    table_name, desc = get_current_dbrepo_table_name()
    db_info = client.fetch_table_info(cid,dbid)
    db_contains_table = not db_info.empty and db_info['name'].str.contains(table_name).any()

    if not db_contains_table:
        generate_dbrepo_table(table_name, desc)

    credentials = pika.PlainCredentials(user, passw)
    parameters = pika.ConnectionParameters(broker_url, 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()

    for _, row in df.iterrows():
        payload = row.to_json()
        channel.basic_publish(exchange=db_name.lower(), routing_key=table_name, body=payload)

    channel.close()






url = 'https://dbrepo.ossdip.at'
broker_url = '128.130.202.19'

user = 'jtaha'
passw = 'pw'

db_name = 'AirQuality'
db_desc = 'This database contains real-time airquality data from 170 stations in Austria || Data-Source: luft.umweltbundesamt.at'
dbid = cid = None

client = dbr.Client(username=user,password=passw,url=url, verifyTLS=False)



def main():

    global dbid, cid, db_name

    data = client.fetch_database_info()

    if not data.empty:
        data = data.loc[data['name'].str.contains(db_name, na=False, case=False)]

    if data.empty:
        dbid = cid = client.generate_database(db_name, db_desc)
    else:
        data = data[['id','name']].values[0]
        dbid = cid = data[0] 
        db_name = data[1] 
        

    while True:

        df = open_current_file()
        df = df if df.empty else df.set_index(index_col)
        new = extract_airpollution_data()
        new = new.set_index(index_col) 

        new = new.loc[~new.index.isin(df.index)]
        df = pd.concat([df,new])
        persist_current_dataframe(df)

        new.reset_index(inplace=True)

        if not new.empty:
            send(new)

        sleep(600)

main()