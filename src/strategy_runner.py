from src.project_helper_functions.mt5_engine import mt5_connect_and_auth


class RunStrategy:

    def __init__(self, strategy_class):
        self.strategy = strategy_class

    def run(self):
        mt5_connect_and_auth(strategy=self.strategy.strategy_name)




if __name__ == '__main__':