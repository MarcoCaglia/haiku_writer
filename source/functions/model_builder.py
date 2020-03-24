from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import RMSprop, Adam, Adadelta
from sklearn.utils import shuffle
from functions.haiku_writer import HaikuWriter
import numpy as np
from IPython import display
from hyperopt import hp, tpe, fmin
import pickle
import datetime as dt


class NotImplementedError(Exception):
    pass


class InconsistentLengthError(Exception):
    pass


class ModelBuilder:
    def __init__(self, processed_data, optimize):
        self.X, self.y, self.encoding, self.decoding = processed_data
        self.optimize = optimize

    def build(self):
        model = self._build_model()
        self._save_model(model)

    def _build_model(self):
        if not self.optimize:
            construction_dict = {
                            'lstm_layers': 2,
                            'dense_layers': 0,
                            'base_neurons': 64,
                            'optimizer': RMSprop(lr=0.01),
                            'activation': 'relu',
                            'learning_rate': 0.01
                            }
        else:
            construction_dict = self._optimization()

        model = self._compile_and_fit(construction_dict, opt_step=False)

        return model

    def _compile_and_fit(self,
                         construction_dict=None,
                         opt_step=True,
                         **kwargs
                         ):

        if not isinstance(construction_dict, dict):
            construction_dict = self._compile_construction_dict(**kwargs)
        total_layers = construction_dict['lstm_layers'] + \
            construction_dict['dense_layers']
        units = (construction_dict['base_neurons'] * x for x in
                 list(range(1, total_layers+1))[::-1])

        model = Sequential()

        for i, _ in enumerate(range(construction_dict['lstm_layers'])):
            model.add(
                LSTM(next(units),
                     return_sequences=not bool(
                         i == (construction_dict['lstm_layers']-1)
                         ),
                     input_shape=(self._get_maxlen(), len(self.encoding))
                     )
                )

        for i, _ in enumerate(range(construction_dict['dense_layers'])):
            model.add(
                Dense(
                    next(units),
                    activation=construction_dict['activation']
                    )
                    )

        model.add(Dense(len(self.encoding), activation='softmax'))

        optimizer = construction_dict['optimizer']
        optimizer.lr = construction_dict['learning_rate']

        model.compile(loss='categorical_crossentropy', optimizer=optimizer)

        print(model.summary())

        history = model.fit(
            self.X,
            self.y,
            batch_size=128,
            epochs=10 + (opt_step) * 0,
            validation_split=0.15,
            shuffle=True
            )

        if opt_step:
            return history.history['val_loss'][-1]
        else:
            return model

    @staticmethod
    def _save_model(model):
        timestamp = str(dt.datetime.now())
        timestamp = timestamp.replace('-', '')[:6]
        model.save(f'../data/models/{timestamp}_haiku_writer')

    def _get_maxlen(self):
        all_len = np.array([len(i) for i in self.X])

        if len(np.unique(all_len)) != 1:
            raise InconsistentLengthError('Incosistent length in'
                                          'training data.')

        return np.unique(all_len)[0]

    def _optimization(self):
        space = {
            'lstm_layers': hp.choice('lstm_layers', (1, 5)),
            'dense_layers': hp.choice('dense_layers', (1, 5)),
            'base_neurons': hp.choice('base_neurons', (64, 128, 256)),
            'optimizer': hp.choice(
                'optimizer', (RMSprop(), Adam(), Adadelta())
                ),
            'activation': hp.choice('activation', ('relu', 'tanh')),
            'learning_rate': hp.uniform('learning_rate', 0.01, 0.5)
            }

        construction_dict = fmin(
            fn=self._compile_and_fit,
            space=space,
            algo=tpe.suggest,
            max_evals=50
        )

        return construction_dict

    @staticmethod
    def _compile_construction_dict(**kwrags):
        construction_dict = {
            'lstm_layers': lstm_layers,
            'dense_layers': dense_layers,
            'base_neurons': base_neurons,
            'optimizer': optimizer,
            'activation': activation,
            'learning_rate': learning_rate
        }

        return construction_dict
