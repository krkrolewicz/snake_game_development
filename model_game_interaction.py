import numpy as np
#import cupy as cp
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

        self.twohundred_last_episodes_data = []

        self.ready_for_pass_data = None
        self.ep_no = 1
        self.investigate = False

        self.reward = 5000
        self.fatal = -1000000
        self.neutrum = -1

    def empty_arrays(self):
        self.episodes_states = np.array([])
        self.episodes_actions = np.array([])
        self.episodes_values = np.array([])      

    def insert_to_episode(self, snake, plain, food):
        action = snake.head_movement
        value_s = np.array([self.evaluate_action(snake, food, plain.latitude, plain.longitude)])
        mapped_plain = self.objects_to_plain_translate(snake.snakepart_location, plain, food.coords)
        #print(self.episodes_values)
        #print(value_s)
        if value_s > 0:
            self.investigate = tuple(mapped_plain.flatten())
            #print(self.investigate)
        self.episodes_states = concatenator(self.episodes_states, mapped_plain)
        self.episodes_values = concatenator(self.episodes_values, value_s)
        self.episodes_actions = concatenator(self.episodes_actions, action)

    def divide_and_discount(self, beta = 0.85):
        limits = np.where(self.episodes_values == self.reward)[0] + 1
        self.episodes_actions[-1] = self.fatal
        subepisodes = np.split(self.episodes_values, limits)
        for index in range(0, len(subepisodes)):
            subep = subepisodes[index]
            subep = np.flip(subep.flatten())
            for i in range(1, len(subep)):
                subep[i] = subep[i] + beta*subep[i-1] - ((i+1)/2)**3
            subep = np.flip(subep)
            subepisodes[index] = subep
        
        self.episodes_values = np.concatenate(subepisodes)
        self.pass_to_visited_states()

    def pass_to_visited_states(self):
        some = pd.DataFrame({"State": list(self.episodes_states), 
                             "Action": self.episodes_actions, 
                             "Q(s, a)": self.episodes_values})
        
        some["State"] = some["State"].apply(lambda x: tuple(x.flatten()))
        # if self.first:
        #     self.visited_states = some
        #     self.first = False
        # else:
        #     self.visited_states = pd.concat([self.visited_states, some])

        #self.visited_states = some

        if len(self.twohundred_last_episodes_data) <= 200:
            self.twohundred_last_episodes_data.append(some)
        else:
            self.twohundred_last_episodes_data = self.twohundred_last_episodes_data[1:]
            self.twohundred_last_episodes_data.append(some)

        self.visited_states = pd.concat(self.twohundred_last_episodes_data)
        self.pass_to_model(epsilon=0.0)


    def pass_to_model(self, epsilon = 0.1):

        refactored = self.visited_states.groupby(["State", "Action"]).agg({"Q(s, a)": [("Q(s, a)", "mean"), ("N(s, a)", "count")]})
        refactored = refactored.droplevel(0, axis =1)
        refactored = refactored["Q(s, a)"]
        refactored = refactored.unstack("Action")
        existing_cols = set(refactored.columns.to_list())
        non_existing = set(self.available_actions).difference(existing_cols)
        if len(non_existing) != 0:
            refactored[list(non_existing)] = 0

        refactored = refactored.fillna(0)
        refactored = refactored[self.available_actions]
        states = refactored.index
        #print(self.investigate in states)
        # if self.investigate:
        #     print(self.investigate in states)
            #print(refactored.loc[(self.investigate), :])
        #print(refactored)
        #print(states)
        refactored = refactored.values
        teststat = refactored > 0
        stat2 = np.sum(teststat)
        #print(stat2)
        maxes = np.max(refactored, axis = 1)
        maxes = np.reshape(maxes, newshape=(maxes.size ,1))
        refactored = (refactored == maxes).astype(int) #refactored.iloc[:, :-1].apply(lambda x: np.where(x == refactored["maxes"], 1, 0))
        m2s = refactored.sum(axis = 1)
        m2s = np.reshape(m2s, newshape=(m2s.size, 1))
        m = len(self.available_actions)
        refactored = epsilon/m + refactored* (1-epsilon)/m2s #refactored.iloc[:, :-1].apply(lambda x: np.where(x == 1, epsilon/m + (1 - epsilon)/refactored["m2s"], epsilon/m ))
        # wybór akcji do modelu - jako wektor
        #print(self.available_actions)
        #print(refactored)
        os = refactored.shape
        refactored = np.array([np.random.choice(np.arange(4), p = i) for i in refactored])
        nr = np.zeros(shape = os)
        nr[np.arange(os[0]), np.array(refactored)] = 1
        #print(refactored)
        #print(nr)

        self.ready_for_pass_data = (states, refactored)
        print(f"Episode {self.ep_no} processed")
        self.ep_no += 1

    def get_alternatives(self, snake):
        
        snakes, keys = snake.alternative_moves()
        snakes_upd = dict(zip(keys.values(), snakes.values()))
        return snakes_upd

    def objects_to_plain_translate(self, snake, plain, food):

        mapped_plain = np.zeros(shape = (plain.latitude + 2, plain.longitude + 2), dtype=np.int32)
        objects = {"snake": snake, "food" : food}
        for i, j in objects.items():
            ind = 0
            for k in j:
                if ind == 0 and i == "snake":
                    mapped_plain[k[0], k[1]] = 1
                elif i == "food":
                    mapped_plain[k[0], k[1]] = 10
                else:
                    mapped_plain[k[0], k[1]] = -10
                ind +=1
        mapped_plain[:, 0] = -10
        mapped_plain[0, :] = -10
        mapped_plain[:, mapped_plain.shape[1]-1] = -10
        mapped_plain[mapped_plain.shape[0]-1, :] = -10
        return mapped_plain


    def evaluate_actions(self, snake, food, latitude, longitude):

        snakes = self.get_alternatives(snake)
        actions_values = {action: self.fatal for action in snake.states.keys()}
        for i, j in snakes.items():
            head = j[0]
            rest = j[1:]
            #food_check
            if np.all(head == food.coords[0]):
                actions_values[i] = self.reward
            else:
                head = head.tolist()
                rest = rest.tolist()
                if (head in rest) or (len(set(head).intersection({0, latitude + 1, longitude + 1})) > 0):
                    actions_values[i] = self.fatal
                else:
                    actions_values[i] = self.neutrum
        #print(actions_values)

    def evaluate_action(self, snake, food, latitude, longitude):
        evaluated_snake_loc = snake.move(evaluate = True)
        head = evaluated_snake_loc[0]
        rest = evaluated_snake_loc[1:]
        if np.all(head == food.coords[0]):
                return self.reward
        else:
                head = head.tolist()
                rest = rest.tolist()
                if (head in rest) or (len(set(head).intersection({0, latitude + 1, longitude + 1})) > 0):
                    return self.fatal
                else:
                    return self.neutrum



def concatenator(first, second):

    #try:
    if len(first) == 0:
        first = np.array([second])
    else:
        first = np.concatenate([first, np.array([second])])
    return first
    # except:
    #     pass