import numpy as np
import cupy as cp
import pandas as pd

class model_game_interact:

    def __init__(self, plain, snake):
        self.value_translator = {-1: -1000000,
                                0: -1,
                                1: 50
                                }
        self.shape_of_states = (plain.latitude + 2, plain.longitude + 2)
        self.visited_states = pd.DataFrame(columns = ["N(s, a)", "Q(s, a)"], index = pd.MultiIndex(levels = [[], []], codes = [[], []], names = ["State", "Action"])) # array size visited states in episode x 3 (each row contains state, action, q(s, a) amd N(s, a))
        #self.visited_states = pd.DataFrame(columns = ["S", "a", "N(s, a)","Q(s, a)"]) # array size visited states in episode x 3 (each row contains state, action, q(s, a) amd N(s, a))
        self.sign_translator = None
        self.available_actions = list(snake.states.keys()) 
        self.plain_mapper = {
            "food": 2,
            "head_snake": 1,
            "rest_snake_and_limit": -1, 
            "other": 0
        }
        self.first = True
        self.episodes_states = np.array([])

        self.episodes_actions = np.array([])

        self.episodes_values = np.array([])

    def insert_to_episode(self, snake, plain, food):
        action = snake.head_movement
        value_s = np.array([self.evaluate_action(snake, food, plain.latitude, plain.longitude)])
        mapped_plain = self.objects_to_plain_translate(snake.snakepart_location, plain, food.coords)

        self.episodes_states = concatenator(self.episodes_states, mapped_plain)
        self.episodes_values = concatenator(self.episodes_values, value_s)
        self.episodes_actions = concatenator(self.episodes_actions, action)

    def divide_and_discount(self, beta = 0.95):
        limits = np.where(self.episodes_values == 50)[0] + 1
        subepisodes = np.split(self.episodes_values, limits)
        for index in range(0, len(subepisodes)):
            subep = subepisodes[index]
            subep = np.flip(subep.flatten())
            for i in range(1, len(subep)):
                subep[i] = subep[i] + beta*subep[i-1]
            subep = np.flip(subep)
            subepisodes[index] = subep
        
        self.episodes_values = np.concatenate(subepisodes)
        #print(self.episodes_values)
        print("first_done")
        self.pass_to_visited_states()

    def pass_to_visited_states(self):

        some = pd.DataFrame({"State": list(self.episodes_states), 
                             "Action": self.episodes_actions, 
                             "Q(s, a)": self.episodes_values})
        
        some["State"] = some["State"].apply(lambda x: tuple(x.flatten()))
        #print(some)
        some = some.groupby(["State", "Action"]).agg({"Q(s, a)": [("Q(s, a)", "mean"), ("N(s, a)", "count")]})
        some = some.droplevel(0, axis =1)
        #print(some)
        #print(some.columns)
        if self.first:
            self.visited_states = some
            self.first = False
        else:
            pass
        # for index in range(0, len(self.episodes_values)):
        #     taken_state = tuple(self.episodes_states[index])
        #     taken_action = self.episodes_actions[index]
        #     taken_value = self.episodes_values[index]
        #     if taken_state not in self.visited_states.index.get_level_values("State"):
        #         partial_df = pd.DataFrame(columns = ["N(s, a)", "Q(s, a)"], index = pd.MultiIndex.from_product([[taken_state], self.available_actions], names=["State", "Action"]))
        #         partial_df.loc[:, "N(s, a)"] = 0
        #         partial_df.loc[:, "Q(s, a)"] = 0
        #         self.visited_states = pd.concat([self.visited_states, partial_df])
                
        #     vs = self.visited_states.loc[(taken_state, taken_action), "Q(s, a)"].to_numpy()
        #     n1 = self.visited_states.loc[(taken_state, taken_action), "N(s, a)"].to_numpy()
        #     n1 += 1
        #     self.visited_states.loc[(taken_state, taken_action), "N(s, a)"] = n1
        #     ns = self.visited_states.loc[(taken_state, taken_action), "N(s, a)"].to_numpy()
        #     self.visited_states.loc[(taken_state, taken_action), "Q(s, a)"] = vs + 1/(ns)*(taken_value - vs)
        print("dome")
        self.pass_to_model()
    def pass_to_model(self, epsilon = 0.1):

        # iterowanie po indeksie stanu (inaczej się nie uda) - zrobione w poprzedniej funkcji
        # weryfikacja czy wszystkie akcje są uwzględnione - uzwględnione
        # sprawdzenie która akcja jest najlepsza

        refactored = self.visited_states["Q(s, a)"]
        refactored = refactored.unstack("Action")
        existing_cols = set(refactored.columns.to_list())
        non_existing = set(self.available_actions).difference(existing_cols)
        if len(non_existing) != 0:
            refactored[list(non_existing)] = 0

        refactored = refactored.fillna(0)
        refactored = refactored[self.available_actions]
        #print(refactored)
        refactored = refactored.values
        maxes = np.max(refactored, axis = 1)
        maxes = np.reshape(maxes, newshape=(maxes.size ,1))
        refactored = (refactored == maxes).astype(int) #refactored.iloc[:, :-1].apply(lambda x: np.where(x == refactored["maxes"], 1, 0))
        m2s = refactored.sum(axis = 1)
        m2s = np.reshape(m2s, newshape=(m2s.size, 1))
        m = len(self.available_actions)
        refactored = epsilon/m + refactored* (1-epsilon)/m2s #refactored.iloc[:, :-1].apply(lambda x: np.where(x == 1, epsilon/m + (1 - epsilon)/refactored["m2s"], epsilon/m ))
        #print(maxes)
        # wybór akcji do modelu - jako wektor
        #print(refactored)


    def get_alternatives(self, snake):
        
        snakes, keys = snake.alternative_moves()
        snakes_upd = dict(zip(keys.values(), snakes.values()))
        return snakes_upd

    def objects_to_plain_translate(self, snake, plain, food):

        mapped_plain = np.zeros(shape = (plain.latitude + 2, plain.longitude + 2), dtype=np.int32)
        #print("printing object")
        #print(objects)
        objects = {"snake": snake, "food" : food}
        for i, j in objects.items():
            #print(i)
            ind = 0
            for k in j:
                if ind == 0 and i == "snake":
                    mapped_plain[k[0], k[1]] = 1
                elif i == "food":
                    mapped_plain[k[0], k[1]] = 2
                else:
                    mapped_plain[k[0], k[1]] = -1
                ind +=1
        #print(mapped_plain)
        return mapped_plain


    def evaluate_actions(self, snake, food, latitude, longitude):

        snakes = self.get_alternatives(snake)
        actions_values = {action: -1000000 for action in snake.states.keys()}
        for i, j in snakes.items():
            head = j[0]
            rest = j[1:]
            #food_check
            if np.all(head == food.coords[0]):
                actions_values[i] = 50

            else:
                head = head.tolist()
                rest = rest.tolist()
                if (head in rest) or (len(set(head).intersection({0, latitude + 1, longitude + 1})) > 0):
                    actions_values[i] = -1000000

                else:
                    actions_values[i] = -1
        
        #print(actions_values)

    def evaluate_action(self, snake, food, latitude, longitude):
        evaluated_snake_loc = snake.move(evaluate = True)
        #print(evaluated_snake_loc)
        head = evaluated_snake_loc[0]
        rest = evaluated_snake_loc[1:]
        if np.all(head == food.coords[0]):
                return 50.0

        else:
                head = head.tolist()
                rest = rest.tolist()
                if (head in rest) or (len(set(head).intersection({0, latitude + 1, longitude + 1})) > 0):
                    return -1000000.0

                else:
                    return -1.0



def concatenator(first, second):

    if len(first) == 0:
        first = np.array([second])
    else:
        first = np.concatenate([first, np.array([second])])
    return first