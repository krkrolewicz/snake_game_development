import numpy as np
class Snake:

    def __init__(self, latitude, longitude):
        self.snake = np.ones(shape = (4,))
        self.snakehead = self.snake[0]
        self.states = {"U" : 0, "R": 1, "B": 2, "L": 3} 
        self.movements = {"L": np.array([[0, -1]]), "R": np.array([[0, 1]]), "U": np.array([[-1, 0]]), "B": np.array([[1, 0]])}
        #self.snakepart_location = np.zeros(shape = (4,2))
        self.right = None
        self.bottom = None
        self.state = None
        self.head_movement = np.random.choice(np.array(list(self.states.keys())))
        self.is_alive = True
        self.turning_points = {}
        self.generate_snake(latitude, longitude)

    def generate_snake(self, latitude, longitude):
        middle_latitude, middle_longitude = np.round(latitude/2), np.round(longitude/2)
        picked_latitude, picked_longitude = np.random.randint(middle_latitude - 4, middle_latitude + 4), np.random.randint(middle_longitude - 4, middle_longitude + 4)
        #self.snakepart_location[0] = [picked_latitude, picked_longitude]
        self.determine_direction()
        if self.right != False:
            self.snakepart_location = np.array([[picked_latitude, picked_longitude + (-1)*i*self.right] for i in range(4)])
        else:
            self.snakepart_location = np.array([[picked_latitude + i *(-1) * self.bottom, picked_longitude] for i in range(4)])


    def determine_direction(self):
        if self.states[self.head_movement]%2 != 0:
            self.bottom = False
            if self.head_movement == "R":
                self.right = 1 
            else:
                self.right = -1
        else:
            self.right = False
            if self.head_movement == "B":
                self.bottom = 1 
            else:
                self.bottom = -1

    def move(self, dir):
        self.head_movement = dir
        print(self.snakepart_location)
        new_head_pos = self.snakepart_location[0] + self.movements[dir]
        rest = self.snakepart_location[:-1]
        self.snakepart_location = np.concatenate([new_head_pos, rest], axis = 0)
        print(self.snakepart_location)
