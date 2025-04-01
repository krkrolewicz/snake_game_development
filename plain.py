import numpy as np

class Plain:

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.gameplain = np.zeros(shape = (self.latitude + 2, self.longitude + 2), dtype=np.int32)

    def obtain_pixels(self, objects):
        self.gameplain = np.zeros(shape = (self.latitude + 2, self.longitude + 2), dtype=np.int32)
        #print("printing object")
        #print(objects)
        for i, j in objects.items():
            #print(i)
            ind = 0
            for k in j:
                if ind == 0 and i == "snake":
                    self.gameplain[k[0], k[1]] = 2
                else:
                    self.gameplain[k[0], k[1]] = 1
                ind +=1
        #print(self.gameplain)
     