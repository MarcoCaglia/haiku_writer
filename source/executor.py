from functions.preprocessing import Preprocessor
from functions.model_builder import ModelBuilder
import yaml


class Executor:
    def __init__(self):
        self.enable_proxy_pool = None
        self.optimize = None

        self._get_params()

    def _get_params(self):
        with open('../properties/config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        self.optimize = config['optimize']

    def execute_pipeline(self):
        preprocess = Preprocessor()
        processed_data = preprocess.execute_preprocessing()

        model_builder = ModelBuilder(processed_data, self.optimize)
        model_builder.build()


if __name__ == '__main__':
    executor = Executor()
    executor.execute_pipeline()
