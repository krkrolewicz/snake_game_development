import numpy as np

class Food:
    
    def __init__(self, plain, snake_location):
        
        possibilities = np.reshape(np.stack(np.meshgrid(np.arange(1, plain.latitude + 1), np.arange(1,plain.latitude + 1)), axis = 2), newshape=(plain.latitude * plain.longitude, 2))
        possibilities_exclusion = np.array([i for i in possibilities if i.tolist() not in snake_location.tolist()])
        coords_ind = np.random.choice(np.shape(possibilities_exclusion)[0])
        self.coords = np.array([possibilities_exclusion[coords_ind]])
        self.latitude, self.longitude = possibilities_exclusion[coords_ind]
        #print(self.coords)
