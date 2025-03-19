import numpy as np
import tkinter as tk
from functools import partial
from snake import Snake
from plain import Plain
from food import Food
from canvarepresentation import CanvaRepresentation

possibilities_of_colors = {
    "black-white" : {1: "black", 0: "white"},
    "white-black" : {1: "white", 0: "black"},
    "red-black" : {1: "red", 0: "black"},
    "green-red" : {1: "green", 0: "red"},
    "purple-yellow" : {1:"purple", 0:"yellow"}
}

class Game:

    def __init__(self, latitude, longitude,window_size_a, window_size_b):
        self.movements = {"L": [1, -1], "R": [1,1], "U": [0, -1], "B": [0, 1]}
        self.gameplain = Plain(latitude, longitude)
        self.gamesnake = Snake(latitude, longitude)
        
        self.CR = CanvaRepresentation(window_size_a, window_size_b, self.gameplain)
        self.gameplain.obtain_pixels(self.gamesnake.snakepart_location)
        self.CR.window.bind('<Left>', func=partial(self.determine_movement, "L"))
        self.CR.window.bind('<Right>', func=partial(self.determine_movement, "R"))
        self.CR.window.bind('<Up>', func=partial(self.determine_movement, "U"))
        self.CR.window.bind('<Down>', func = partial(self.determine_movement, "B"))
        
        self.speed = 500

    def update_all(self):
        self.CR.canva.delete("all")
        for i in range(1, self.gameplain.gameplain.shape[0]-1):#w tejże pętli ustalamy dla każdej komórki jej stan i rysujemy odpowiednim kolorem
            for j in range(1, self.gameplain.gameplain.shape[1]-1):
                self.CR.set_color(j-1, i-1, self.CR.lifecolor.get(self.gameplain.gameplain[i][j])) #rysujemy komórkę odpowiednim dla niej kolorem
        #self.CR.canva.after(self.speed, self.gamesnake.move(self.gamesnake.head_movement))

    def determine_movement(self, *args):
        movement = args[0]
        self.gamesnake.move(movement)
        self.gameplain.obtain_pixels(self.gamesnake.snakepart_location)
        self.CR.canva.after(self.speed, self.update_all())


game = Game(15, 15, 800, 800)
game.update_all()
game.CR.window.mainloop()


#######################################################################################






class Cells: #klasa, w której tworzymy przestrzeń życiową komórek

    lifecolor = possibilities_of_colors["black-white"]#słownik życia - jeśli element macierzy (która niedługo powstanie)
    # ma wartość 1, komórka jej odpowiadająca na płótnie (kanwie) okna jest żywa i przyjmuje kolor czarny. W przeciwnym
    #wypadku przyjmuje kolor biały i jest martwa
    lifedict2 = {0: {0: 0, 1: 0, 2: 0, 3: 1, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0},
                 1: {0: 0, 1: 0, 2: 1, 3: 1, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}}

    def __init__(self, a, b, size_a, size_b): #konstruktor klasy, za argumenty przyjmuje liczbę komórek na płótnie poziomo odjąć dwa,
        #liczbę komórek na płotnie pionowo odjąć dwa (razem komórek: (a-2) * (b-2)) oraz kanwę, na której rysujemy komórki
        #Powód dla któego liczba komórek jest właśnie taka podam w poniższych linijkach - znacznie to ułatwia obliczenia, gdyż zera stanowiace zewnętrzną barierę macierzy posłużą jako "granica z niczym"
        self.a = a
        self.b = b
        self.window = tk.Tk() #włąściwe okno
        self.window.title("Somsiedzka gra w życie Conwaya")
        self.window.geometry(f'{size_a}x{round(size_b)}') #definiuję rozmiar
        self.canva = tk.Canvas(self.window, width=size_a, height=round(size_b)*2.5/3, bg='white') #tworzę kanwę tak, aby na dole było jeszcze miejsce na wstawienie przycisków
        self.canva.pack()

        self.scaler = None

        self.random_fraction = 0.25

        menu = tk.Menu(self.window)
        self.window.config(menu = menu)
        colormenu = tk.Menu(menu)

        for i in possibilities_of_colors.keys():
            act = partial(self.set_lifecolor_dict, i)
            colormenu.add_command(label=i, command=act)
        menu.add_cascade(label="Cell colors", menu=colormenu)

        x = np.zeros((self.a, self.b), dtype=int) #tu tworzymy macierz komórek
        self.zycie = x #macierz przypisujemy jako argument instancji
        self.update_all()
        self.state = False #bardzo specyficzny atrybut. Kontroluje on przebieg symulacji gry. Jeśli jego wartość wynosi FALSE, obliczenia nie są dokonywane i symulacja nie zachodzi

    def set_lifecolor_dict(self, colors):
        self.lifecolor = possibilities_of_colors[colors]
        self.canva.delete("all")
        self.update_all()

    def set_new_random_fraction(self, argument):
        self.random_fraction = float(argument)

    def update_all(self, advanced = False):
        self.canva.delete("all")
        if advanced == True:
            neigh = self.neighbours()
        for i in range(1, self.zycie.shape[0]-1):#w tejże pętli ustalamy dla każdej komórki jej stan i rysujemy odpowiednim kolorem
            for j in range(1, self.zycie.shape[1]-1):
                if advanced == True:
                    self.zycie[i][j] = self.lifedict2[self.zycie[i][j]].get(neigh[i][j])
                self.set_color(j-1, i-1, self.lifecolor.get(self.zycie[i][j])) #rysujemy komórkę odpowiednim dla niej kolorem


    def set_color(self, a1, b1, color): #funkcja malująca odpowiednie komórki na właściwy jej kolor
        a1 = int(a1) #numer kolumny komórki do pomalowania
        b1 = int(b1) #numer rzędu komórki do pomalowania
        #color zaś to wcześniej zidentyfikowany kolor odpowiadający przerabianej komórce
        self.canva.create_rectangle(int(self.canva.cget('width')) / (self.zycie.shape[1] - 2) * a1,
                                    int(self.canva.cget('height')) / (self.zycie.shape[0] - 2) * b1,
                                    int(self.canva.cget('width')) / (self.zycie.shape[1] - 2) * (a1 + 1),
                                    int(self.canva.cget('height')) / (self.zycie.shape[0] - 2) * (b1 + 1),
                                    fill = color, outline = self.lifecolor[1]) #funkcja create_rectangle to funkcja rysująca prostokąt o zadeklarowanych współrzędnych i pomalowany w odpowiednim kolorze

    def start_choice_phase(self):
        #funkcja aktualizująca stan symulacji z jakiegokolwiek stanu do stanu uśpienia symulacji i prowadząca do funkcji umożliwiającej wybór komórek początkowych symulacji
        self.state = False
        self.choice()

    def set_random_config(self):
        x = np.random.choice([1,0], size = (self.a-2, self.b-2), p=[self.random_fraction, 1 - self.random_fraction]) #tu tworzymy macierz komórek
        self.zycie[1:self.zycie.shape[0] - 1, 1:self.zycie.shape[1] - 1] = x #macierz przypisujemy jako argument instancji
        self.update_all()

    def set_cell(self, event):
        #jest to najtrudniejsza funkcja w objaśnieniu, głównie ze względu na charakter obliczeń. W pierwszej kolejności
        #funkcja zmienia stan komórki w zależności od tego, czy użytkownik kliknął w nią.
        #Zmienna event to właśnie kliknięcie w pewien punkt kanwy, dlatego też event.x odnosi się do współrzędnej width, zaś .y height

        #obliczenie stanu klikniętej komórki wymaga określenia, która komórka została w zasadzie kliknięta. Na początku
        #oblicza się wymiary poszczególnych prostokątów, dzieląc odpowiedni wymiar kanwy przez odpowiadający mu wymiar
        #macierzy pomniejszony o 2. Następnie to, co obliczyliśmy, staje się mianownikiem przy dzieleniu bez reszty (floor division) odpowiedniego wymiaru
        #pochodzącego ze zmiennej event, po czym dodajemy do finalnego wyniku jeden, gdyż trzeba pamiętać, że indeksujemy elementy nieskrajne (granice, tzn elementy skrajne, pomijamy).

        #Przy każdym kliknięciu wartość macierzy komórek zwiększa się o jeden i jest dzielona przez 2 modulo, zapewniając możliwość zmianę w obie strony

        self.zycie[int(event.y // (int(self.canva.cget('height')) / (self.zycie.shape[0] - 2)) + 1)][int(event.x // (int(self.canva.cget('width')) / (self.zycie.shape[1] - 2)) + 1)] \
            = (self.zycie
               [int(event.y // (int(self.canva.cget('height')) / (self.zycie.shape[0] - 2)) + 1)]
               [int(event.x // (int(self.canva.cget('width')) / (self.zycie.shape[1] - 2)) + 1)]
               + 1) % 2

        #następnie funkcja maluje komórkę w odpowiedni kolor

        self.set_color((event.x // (int(self.canva.cget('width')) / (self.zycie.shape[1] - 2))),
                       (event.y // (int(self.canva.cget('height')) / (self.zycie.shape[0] - 2))),
                       self.lifecolor.get(
                           self.zycie
                           [int(event.y // (int(self.canva.cget('height')) / (self.zycie.shape[0] - 2)) + 1)]
                           [int(event.x // (int(self.canva.cget('width')) / (self.zycie.shape[1] - 2)) + 1)]))

    def choice(self):
        #funkcja ta przypisuje klawisz myszki lewy do funkcji set_cell, wykonującą się gdy kliknięty zostanie element kanwy
        self.canva.bind("<Button-1>", self.set_cell)

    def neighbours(self):
        #najważniejsza funkcja, dzięki której możemy aktualizować stan komórek
        neighbours = np.zeros(self.zycie.shape[:], dtype=int)#najpierw tworzymy macierz o tych samych wymiarach co macierz komórek, w przyszłości stanie się ona macierzą liczby sąsiadów
        for i in range(1, self.zycie.shape[0] - 1): #iteracja ponownie następuje po elementach nieskrajnych
            for j in range(1, self.zycie.shape[1] - 1):
                neighbours[i][j] = sum(self.zycie[i - 1][j - 1:j + 2]) + self.zycie[i][j - 1] + self.zycie[i][j + 1] + \
                                   sum(self.zycie[i + 1][j - 1:j + 2]) #sumujemy wartości komórek otaczających komórkę, dla której wykonujemy obliczenia, uzyskaną wartość wstawiamy do odpowiadającego jej
                                                                       #elementu macierzy liczby sąsiadów. Tu okazuje się, czemu elementy skrajne (nie widać ich na kanwie) zawsze są zerami - jeśli
                                                                       #komórka jest komórką graniczną na kanwie, to z co najmniej jednej strony nie graniczy z niczym, czyli tak jakby nie miała tam sąsiadów
        return neighbours

    def start(self):
        #funkcja zmieniająca stan symulacji na True i kierująca do funkcji kalkulującej kolejne stany przestrzeni życiowej
        self.state = True
        self.change()

    def stop(self):
        #funkcja zatrzymująca symulację - tzn zmieniająca stan symulacji na False
        self.state = False

    def change(self):
        #funkcja zmieniajaca stan przestrzeni życiowej - tzn aktualizująca stan komórek w zależności od liczby sąsiadów
        if self.state is True: #funkcja zajdzie tylko, gdy stan symulacji jest ustawiony na True
            self.canva.bind("<Button-1>", '') #przypisujemy lewy przycisk myszy do zdarzenia pustego - gdy klikniemy na kanwę, nic się nie stanie
            #neigh = self.neighbours() #tworzymy macierz liczby sąsiadów danej komórki za pomocą wcześniej zdefiniowanej metody

            #klucze słownika głównego odnoszą się do obecnego stanu komórki, zaś klucze zagnieżdżonych słowników to liczby sąsiadów, a wartości im przypisane to stan komórki w kolejnej iteracji
            self.update_all(advanced=True)
            # for i in range(1, self.zycie.shape[0] - 1):#w tejże pętli ustalamy dla każdej komórki jej stan i rysujemy odpowiednim kolorem
            #     for j in range(1, self.zycie.shape[1] - 1):
            #         self.zycie[i][j] = self.lifedict2[self.zycie[i][j]].get(neigh[i][j]) #pobieramy wartość stanu komórki w przyszłej iteracji za pomocą podwójnego pobierania
            #         #wartości ze słownika - najpierw pobieramy słownik odpowiadający stanowi obecnemu komórki, a nastepnie z pomocą macierzy liczby sasiadow wybieramy stan odpowiadajacy liczbe sasiadow danej komorki
            #         self.set_color( j - 1, i - 1, self.lifecolor.get(self.zycie[i][j])) #rysujemy komórkę odpowiednim dla niej kolorem

            self.canva.after(1000, self.change) #po chwili przerwy przechodzimy ponownie do tej samej funkcji

# class Window: #tu tworzę klasę okno
#     def __init__(self, size_a, size_b): #konstruktor pobiera informacje o szerokości i wysokości okna
#         self.window = tk.Tk() #włąściwe okno
#         self.window.geometry(f'{size_a}x{round(size_b)}') #definiuję rozmiar
#         self.canvas = tk.Canvas(self.window, width=size_a, height=round(size_b)*2.5/3, bg='white') #tworzę kanwę tak, aby na dole było jeszcze miejsce na wstawienie przycisków
#         self.canvas.pack() #umieszczam kanwę w oknie
#         # menu = tk.Menu(self.window)
#         # self.window.config(menu = menu)
#         # colormenu = tk.Menu(menu)

# cells = Cells(cells_number + 2, cells_number + 2, width, height*3/2.5)#tworzymy przestrzeń życiową komórek
# startsim = tk.Button(cells.window, text = 'Zacznij symulację', command=cells.start)#przycisk, który rozpocyzna symulację
# startsim.place(x = width*0.5/7, y = height*3/2.8)#ustalenie pozycji przycisku
# choosestet = tk.Button(cells.window, text = 'Wybierz komórki startowe', command=cells.start_choice_phase)#przycisk wyboru komórek startowych
# choosestet.place(x = width*1.6/7, y = height*3/2.8)#ustalenie pozycji przycisku
# stopsim = tk.Button(cells.window, text = 'Zakończ symulacje', command=cells.stop)#przycisk kończenia symulacji
# stopsim.place(x = width*3/7, y = height*3/2.8)#ustalenie pozycji przycisku
# random_sel = tk.Button(cells.window, text = "Losowe ustawienie", command = cells.set_random_config)
# random_sel.place(x = width*4.2/7, y = height*3/2.8)
# cells.scaler = tk.Scale(cells.window, from_= 0, to=1, resolution=0.01, orient="horizontal", command=cells.set_new_random_fraction)
# cells.scaler.set(0.25)
# cells.scaler.place(x = width*5.5/7, y = height*2.95/2.8)
# label = tk.Label(cells.window, text="Ułamek żywych komórek\n w losowym ustawieniu:")
# label.place(x = width*5.35/7, y = height*2.85/2.8)


# cells.window.mainloop()#rozpoczęcie działania okna
