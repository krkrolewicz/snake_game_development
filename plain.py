import numpy as np

class Plain:

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.gameplain = np.zeros(shape = (self.latitude + 2, self.longitude + 2), dtype=np.int32)

    def obtain_pixels(self, object):
        self.gameplain = np.zeros(shape = (self.latitude + 2, self.longitude + 2), dtype=np.int32)
        for i in object:
            self.gameplain[i[0] + 1, i[1] + 1] = 1
     