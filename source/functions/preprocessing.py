import pandas as pd
import os
import json
from datetime import datetime as dt
import numpy as np
from itertools import chain
import re
import pickle


class Preprocessor:
    def __init__(self):
        self.training_data = None
        self.timestamp = None
        self.encode = None
        self.decode = None

    def execute_preprocessing(self):
        self.timestamp = self._get_timestamp()
        self._convert_to_parquet(self.timestamp)
        raw_data = self._load_data()
        processed_data = self._transform_data(raw_data)

        return processed_data

    def _load_data(self):
        data = pd.read_parquet(f'../data/scraped/{self.timestamp}'
                               '_scrape.parquet.gzip')

        return data

    @staticmethod
    def _convert_to_parquet(timestamp):
        files = os.listdir('../data/')
        files = filter(lambda x: '.json' in x, files)
        for entry in files:
            with open(f'../data/{entry}', 'r') as f:
                data = json.load(f)
            data = pd.DataFrame.from_dict(data)
            data.drop_duplicates(inplace=True)
            data.to_parquet(
                '../data/' + timestamp + '_haiku_info.parquet.gzip',
                engine='auto',
                compression='gzip'
            )
            os.system(f'rm ../data/{entry}')

    def _transform_data(self, raw_data):
        raw_text = raw_data.text.unique().tolist()

        text = [x.lower() for x in raw_text if isinstance(x, str)]
        text = [re.sub(r'[^a-z\s/]', '', x) for x in text]
        text = [re.sub(r'(?<=/)/', '', x) for x in text]

        haiku_text = ' || '.join(text)

        while '\n' in haiku_text:
            haiku_text = haiku_text.replace('\n', '')

        while '\r' in haiku_text:
            haiku_text = haiku_text.replace('\r', '')

        chars = list(chain.from_iterable(haiku_text))
        chars = list(set(chars))

        encode = {}
        for i, unique_char in enumerate(chars):
            encode[unique_char] = i

            decode = dict([(encode[key], key) for key in encode])

        maxlen = 15
        step = 3
        sentences = []
        next_chars = []
        for i in range(0, len(haiku_text) - maxlen, step):
            sentences.append(haiku_text[i: i + maxlen])
            next_chars.append(haiku_text[i + maxlen])
        print('nb sentences:', len(sentences))

        print('Vectorization...')
        X = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
        y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
        for i, sentence in enumerate(sentences):
            for t, char in enumerate(sentence):
                X[i, t, encode[char]] = 1
            y[i, encode[next_chars[i]]] = 1

        processed_data = X, y, encode, decode

        return processed_data

    @staticmethod
    def _get_timestamp():
        timestamp = str(dt.now())
        timestamp = timestamp.replace('-', '')[:6]

        return timestamp
