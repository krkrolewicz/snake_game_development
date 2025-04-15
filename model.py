import numpy as np
from sklearn.neural_network import MLPClassifier
import pandas as pd


class SnakeRoboticPlayer:

    def __init__(self, outputs, gridsize1, gridsize2):
        self.gridsize1 = gridsize1 + 2
        self.gridsize2 = gridsize2 + 2
        sqr = self.gridsize1 * self.gridsize2
        self.internal_visited_states = None
        self.model = MLPClassifier(hidden_layer_sizes=(sqr, sqr*2, sqr))
        self.outputs = outputs

    def get_direction(self, input, first = False):
        input = input.flatten().reshape(1, -1)
        #print("jag ar har")
        #print(input)
        if first:
            #print("failed")
            return np.random.choice(self.outputs)
        else:
            res = self.model.predict(input)[0]
            #print(res)
            #print("success")
            return self.outputs[res] 

    def adjust(self, data_from_interactor, labels_from_interactor):
        X, y = data_from_interactor
        #y = y.reshape(-1,1)
        X = np.array([np.array(i) for i in X]) # X.reset_index()["index"].apply(lambda x: str(x)[1:-1]).str.split(",", expand=True).astype(int).values
        #print("adjusted")
        #print(X[0].shape)
        self.model.fit(X, y)