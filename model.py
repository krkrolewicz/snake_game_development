import numpy as np
from sklearn.neural_network import MLPClassifier
import torch
import torch.nn as nn
import torch.nn.functional as F


class SnakeRoboticPlayer:

    def __init__(self, outputs, gridsize1, gridsize2):
        self.gridsize1 = gridsize1
        self.gridsize2 = gridsize2
        sqr4 = self.gridsize1 * self.gridsize2
        sqr = self.gridsize1 * self.gridsize2 * 4
        print(sqr)
        self.internal_visited_states = None
        #self.model = MLPClassifier(hidden_layer_sizes=[sqr] * 8, learning_rate_init=0.0001, max_iter = 400)

        self.model2 = nn.Sequential(
            nn.Linear(sqr4, sqr, device="cuda:0"),
            nn.ReLU(),
            nn.Linear(sqr, sqr, device="cuda:0"),
            nn.ReLU(),
            # nn.Linear(sqr, sqr, device="cuda:0"),
            # nn.ReLU(),
            # nn.Linear(sqr, sqr, device="cuda:0"),
            # nn.ReLU(),
            # nn.Linear(sqr, sqr, device="cuda:0"),
            # nn.ReLU(),
            # nn.Linear(sqr, sqr, device="cuda:0"),
            # nn.ReLU(),
            # nn.Linear(sqr, sqr, device="cuda:0"),
            # nn.ReLU(),
            nn.Linear(sqr, sqr, device="cuda:0"),
            nn.ReLU(),
            nn.Linear(sqr, sqr, device="cuda:0"),
            nn.ReLU(),
            nn.Linear(sqr, sqr, device="cuda:0"),
            nn.ReLU(),
            nn.Linear(sqr, sqr, device="cuda:0"),
            nn.ReLU(),
            nn.Linear(sqr, 4, device="cuda:0"),
            nn.Softmax(dim = 1)
        )

        self.loss_func = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(self.model2.parameters(), lr=0.00001)
        self.outputs = outputs
        self.num_epochs = 40

    def get_direction(self, input, first = False):
        input = input.flatten().reshape(1, -1)
        input = torch.from_numpy(input).to("cuda").to(torch.float32)
        if first:
            #print("failed")
            return np.random.choice(self.outputs)
        else:
            #res = self.model.predict(input)[0]
            res = self.model2(input)
            _, preds = torch.max(res, 1)
            #print(self.outputs[preds])
            #print(self.outputs[res] )
            #print("success")
            return self.outputs[preds] 

    def adjust(self, data_from_interactor, labels_from_interactor):
        Xt, y = data_from_interactor
        #y = y.reshape(-1,1)
        Xt = np.array([np.array(i) for i in Xt]) # X.reset_index()["index"].apply(lambda x: str(x)[1:-1]).str.split(",", expand=True).astype(int).values
        #print("adjusted")
        #print(X[0].shape)
        #self.model.fit(X, y)
        #print(X.shape)
        #print(y)
        Xt = torch.from_numpy(Xt).to("cuda").to(torch.float32)
        #print(Xt.shape)
        #print(Xt)
        y = torch.from_numpy(y)
        y = y.type(torch.LongTensor) 
        y = y.to("cuda")#.to(torch.float32)
        
        for n in range(self.num_epochs):
            y_pred = self.model2(Xt)
            #print(y_pred)
            loss = self.loss_func(y_pred, y)
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()


class Net(nn.Module):
    def __init__(self ):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels = 1, out_channels=10, kernel_size=2, stride=1, padding=0, device="cuda:0") #inputsize = 17 x 17, output = 16 x 16
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(10, 16, 5, 1, 0, device="cuda:0")
        self.fc1 = nn.Linear(16 * 3 * 3, 120, device="cuda:0")
        self.fc2 = nn.Linear(120, 84, device="cuda:0")
        self.fc3 = nn.Linear(84, 4, device="cuda:0")

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        #print(x.shape)
        x = self.pool(F.relu(self.conv2(x)))
        #print(x.shape)
        x = torch.flatten(x, 1) # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.softmax(self.fc3(x), dim = 1)
        return x


class SnakeRoboticPlayer2():

    def __init__(self, outputs_given, gridsize1, gridsize2):
        self.gridsize1 = gridsize1
        self.gridsize2 = gridsize2
        self.sqr4 = self.gridsize1 * self.gridsize2
        self.sqr = self.gridsize1 * self.gridsize2 * 4
        self.internal_visited_states = None
        self.model = Net()
        self.loss_func = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.00001)
        self.outputs = outputs_given
        self.num_epochs = 30

    def get_direction(self, input, first = False):
        #input = #input.flatten().reshape(1, -1)
        input = torch.from_numpy(input).to("cuda").to(torch.float32)
        input = torch.reshape(input, shape = (1,1, input.shape[0], input.shape[1])).to("cuda")
        if first:
            #print("failed")
            return np.random.choice(self.outputs)
        else:
            #res = self.model.predict(input)[0]
            res = self.model(input)
            _, preds = torch.max(res, 1)
            #print(self.outputs[preds])
            #print(self.outputs[res] )
            #print("success")
            return self.outputs[preds] 
    
    def adjust(self, data_from_interactor, labels_from_interactor):
        X, y = data_from_interactor
        #y = y.reshape(-1,1)
        X = np.array([np.array(i).reshape((self.gridsize1, self.gridsize2)) for i in X]) # X.reset_index()["index"].apply(lambda x: str(x)[1:-1]).str.split(",", expand=True).astype(int).values
        #print("adjusted")
        #print(X[0].shape)
        #self.model.fit(X, y)
        #print(X.shape)
        #print(y)
        X = torch.from_numpy(X).to("cuda").to(torch.float32)
        X = torch.reshape(X, shape = (X.shape[0], 1, X.shape[1], X.shape[2])).to("cuda")
        y = torch.from_numpy(y)
        y = y.type(torch.LongTensor) 
        y = y.to("cuda")#.to(torch.float32)
        
        for n in range(self.num_epochs):
            #for Xi, yj in zip(X, y):
                #y_pred = self.model2(X)
            y_pred = self.model(X)
            #print(y_pred)
            loss = self.loss_func(y_pred, y)
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()