import pandas as pd
import json
import os


def json_to_parquet():
    files = os.listdir('../data/')
    for entry in files:
        with open(f'../data/{entry}', 'r') as f:
            data = json.load(f)
        data = pd.DataFrame.from_dict(data)
        data.drop_duplicates(inplace=True)
        data.to_parquet(
            '../data/' + entry.split('.')[0] + '.parquet.gzip',
            engine='auto',
            compression='gzip'
            )
        os.system(f'rm ../data/{entry}')


json_to_parquet()