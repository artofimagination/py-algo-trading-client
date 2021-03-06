from trade_platforms.platform_wrapper_base import Platforms
from trade_platforms.ftx_wrapper import FTX

from popup import show_error_box
from os.path import exists
from os import mkdir
import pandas as pd
from datetime import timedelta


## Returns the requested platform client.
def get_platform_client(platform):
    if platform['platform_type'] == Platforms.FTX:
        return FTX(
            base_currency=platform['base_currency'],
            quote_currency=platform['quote_currency'])


## Generates a dataset filename based on the platform,
#  start/end time and resolution.
def generate_dataset_filename(dataset, platform, start_time, end_time, resolution):
    start_string = start_time.strftime("%Y%m%d_T%H%M")
    end_string = end_time.strftime("%Y%m%d_T%H%M")
    filename = \
        f"{platform['platform_type'].value}_{platform['base_currency']}_\
{platform['quote_currency']}_{dataset}_{start_string}_{end_string}_{resolution}sec.h5"
    path = "src/bots/data/"
    return f"{path}{filename}"


## Generates candle data set from platform historical data.
#  Lowest resolution is 15 seconds
def generate_candle_historical_dataset(
        platform, start_time, end_time, resolution_sec: int):
    dataset_file = generate_dataset_filename(
        "candles", platform, start_time, end_time, resolution_sec)
    if exists(dataset_file):
        print("Dataset already created")
        return dataset_file

    if not exists('src/bots/data'):
        mkdir('src/bots/data')

    timestamp = start_time
    store = pd.HDFStore(dataset_file)
    try:
        while timestamp < end_time:
            start_date = timestamp
            # Data is always stored in 6 hourly chunks
            timestamp += timedelta(seconds=60 * 60 * 6 - 1)
            end_date = timestamp

            df = get_platform_client(platform).historical_data(
                start_time=start_date.timestamp(),
                end_time=end_date.timestamp(),
                resolution=resolution_sec)
            df['startTime'] = pd.to_datetime(
                df['startTime'],
                format="%Y-%m-%dT%H:%M:%S+00:00")
            print(f"Get data from {str(start_date)} to {str(end_date)} len {len(df)}")
            store.append("data", df)
            timestamp += timedelta(seconds=1)
        store.close()
    except Exception as e:
        show_error_box(e)
        return None
    return dataset_file
