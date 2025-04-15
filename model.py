import numpy as np
from sklearn.neural_network import MLPClassifier
import pandas as pd


class SnakeRoboticPlayer:

    def __init__(self):
        self.internal_visited_states = None
        self.model = None

    def get_direction(self):
        pass

    def adjust(self):
        pass