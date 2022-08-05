from time import sleep
import requests as rq
import pandas as pd
from datetime import datetime
import pytz
from flatten_json import flatten

index_col = ['stationid','compname','time']

def get_current_file_path() -> str:
    tz = pytz.timezone('Europe/Berlin')
    now = datetime.now(tz)
    year, week, weekday = now.isocalendar()
    return f'data/poll/data_{weekday}_{week}_{year}.csv'


def open_current_file() -> pd.DataFrame:
    try:
        return pd.read_csv(get_current_file_path(), index_col=index_col)
    except:
        return pd.DataFrame()

def persist_current_dataframe(df: pd.DataFrame) -> None:
        df.to_csv(get_current_file_path())

def extract_airpollution_data() -> pd.DataFrame:

    df = pd.DataFrame()

    for component in ['SO2','O3','NO2','NO','CO','PM10_K','PM2_5_K']:
        url = f'https://luft.umweltbundesamt.at/pub/map_chart/index.pl?runmode=values_json&MEANTYPE=HMW&COMPONENT={component}'

        res = rq.get(url)
        data = res.json()

        data = [flatten(record) for record in data['stations']]

        data = pd.DataFrame(data)
        
        df = pd.concat([df,data])

    # df = df.pivot_table(values='value', index=['stationid','time'], columns='compname', aggfunc='first')
    df = df.set_index(index_col)
    return df


while True:
    #read df
    df = open_current_file()
    
    new = extract_airpollution_data()
    new = new.loc[~new.index.isin(df.index)]
    df = pd.concat([df,new])

    persist_current_dataframe(df)
    sleep(300)

