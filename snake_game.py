import numpy as np
import tkinter as tk
from functools import partial
from snake import Snake
from plain import Plain
from food import Food
from canvarepresentation import CanvaRepresentation
import time
from model_game_interaction import model_game_interact

class Game:

    def __init__(self, latitude, longitude, window_size1, window_size2):

        #self.movements = {"L": [1, -1], "R": [1,1], "U": [0, -1], "B": [0, 1]}
        self.gameplain = Plain(latitude, longitude)
        self.gamesnake = Snake(latitude, longitude)

        self.mi = model_game_interact(self.gameplain, self.gamesnake)

        self.CR = CanvaRepresentation(window_size1, window_size2, self.gameplain)
        #self.gameplain.obtain_pixels(self.gamesnake.snakepart_location)
        self.CR.window.bind('<Left>', func=partial(self.determine_movement, "L"))
        self.CR.window.bind('<Right>', func=partial(self.determine_movement, "R"))
        self.CR.window.bind('<Up>', func=partial(self.determine_movement, "U"))
        self.CR.window.bind('<Down>', func = partial(self.determine_movement, "D"))

        real_player_button = tk.Button(self.CR.window, text = "Play yourself", command = None)
        robotic_player_button = tk.Button(self.CR.window, text="Create machine", command=None)
        real_player_button.place(x = window_size1 * 1/7, y = window_size2* 2.5/2.8)
        robotic_player_button.place(x = window_size1 * 3/7, y = window_size2* 2.5/2.8)

        self.speed = 100
        self.food = None
        self.score = 0
        self.score_print = tk.StringVar()
        self.score_print.set(f"Score: {self.score}")
        score_lab = tk.Label(self.CR.window,
                            bg = "black",
                            fg = "purple",
                            textvariable = self.score_print,
                            font="Helvetica 16 bold italic", justify=tk.LEFT)
        self.score = 0
        score_lab.pack(side="left")
        self.generate_food()
        self.gameplain.obtain_pixels({"snake": self.gamesnake.snakepart_location, "food": self.food.coords})
        self.robotic_movements = True
        self.update_all()

    def update_all(self):
        self.CR.canva.delete("all")
        self.determine_movement(self.gamesnake.head_movement)
        self.mi.insert_to_episode(self.gamesnake, self.gameplain, self.food)
        self.gamesnake.move()
        self.mi.evaluate_actions(self.gamesnake, self.food, self.gameplain.latitude, self.gameplain.longitude)
        self.gameplain.obtain_pixels({"snake": self.gamesnake.snakepart_location, "food": self.food.coords})
        self.food_check()
        for i in range(1, self.gameplain.gameplain.shape[0]-1):#w tejże pętli ustalamy dla każdej komórki jej stan i rysujemy odpowiednim kolorem
            for j in range(1, self.gameplain.gameplain.shape[1]-1):
                self.CR.set_color(j-1, i-1, self.CR.lifecolor.get(self.gameplain.gameplain[i][j])) #rysujemy komórkę odpowiednim dla niej kolorem
                
        check_living = self.gamesnake.is_alive
        if check_living == False:
            self.CR.canva.delete("all")
            self.CR.canva.after(self.speed, self.end)
        else:
            self.CR.canva.after(self.speed, self.update_all)

    def generate_food(self):
        self.food = Food(self.gameplain, self.gamesnake.snakepart_location)

    def food_check(self):
        snakehead = self.gamesnake.snakepart_location[0]
        if np.all(snakehead == self.food.coords[0]):
            self.score += 1
            self.score_print.set(f"Score: {self.score}")
            self.gamesnake.expand()
            self.food = Food(self.gameplain, self.gamesnake.snakepart_location)
            self.gameplain.obtain_pixels({"snake": self.gamesnake.snakepart_location, "food": self.food.coords})

    def end(self):
        print("loss")
        self.CR.canva.configure(background="black")
        self.CR.canva.create_text(400, 350, text  = "You lost", fill = "#701D84", font = ("Arial", 80))
        self.CR.canva.update()
        self.mi.divide_and_discount()
        time.sleep(3)
        self.CR.window.destroy()

    def determine_movement(self, *args):
        movement = args[0]
        self.gamesnake.determine_direction(movement)

    def order_move(self):
        self.gamesnake.move()

    ##### robotic moves ######################




game = Game(25, 25, 800, 800)
game.CR.window.mainloop()
