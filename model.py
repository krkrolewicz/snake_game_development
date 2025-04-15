import numpy as np
from sklearn.neural_network import MLPClassifier
import pandas as pd


class SnakeRoboticPlayer:

    def __init__(self, outputs):
        self.internal_visited_states = None
        self.model = None
        self.outputs = outputs

    def get_direction(self):
        return np.random.choice(self.outputs)
        pass

    def adjust(self):
        pass