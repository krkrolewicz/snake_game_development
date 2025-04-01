import tkinter as tk

class CanvaRepresentation:

    possibilities_of_colors = {
        "black-white" : {1: "black", 0: "white", 2: "#701D84"},
        "white-black" : {1: "white", 0: "black"},
        "red-black" : {1: "red", 0: "black"},
        "green-red" : {1: "green", 0: "red"},
        "purple-yellow" : {1:"purple", 0:"yellow"}
    }


    def __init__(self, size_a, size_b, plain):
        self.plain_to_reflect = plain
        self.window = tk.Tk() #włąściwe okno
        self.window.title("Somsiedzka gra w węża")
        self.lifecolor = {0: "white", 1 : "black", 2: "purple"}
        self.window.geometry(f'{size_a}x{round(size_b)}') #definiuję rozmiar
        self.canva = tk.Canvas(self.window, width=size_a, height=round(size_b)*2.5/3, bg='white') #tworzę kanwę tak, aby na dole było jeszcze miejsce na wstawienie przycisków
        self.canva.pack()
        #self.update_all(plain)


    def set_color(self, a1, b1, color): #funkcja malująca odpowiednie komórki na właściwy jej kolor
        a1 = int(a1) #numer kolumny komórki do pomalowania
        b1 = int(b1) #numer rzędu komórki do pomalowania
        #color zaś to wcześniej zidentyfikowany kolor odpowiadający przerabianej komórce
        self.canva.create_rectangle(int(self.canva.cget('width')) / (self.plain_to_reflect.gameplain.shape[1] - 2) * a1,
                                    int(self.canva.cget('height')) / (self.plain_to_reflect.gameplain.shape[0] - 2) * b1,
                                    int(self.canva.cget('width')) / (self.plain_to_reflect.gameplain.shape[1] - 2) * (a1 + 1),
                                    int(self.canva.cget('height')) / (self.plain_to_reflect.gameplain.shape[0] - 2) * (b1 + 1),
                                    fill = color, outline = self.lifecolor[1]) #funkcja create_rectangle to funkcja rysująca prostokąt o zadeklarowanych współrzędnych i pomalowany w odpowiednim kolorze

    # def update_all(self, plain_to_reflect):
    #     self.plain_to_reflect = plain_to_reflect
    #     self.canva.delete("all")
    #     for i in range(1, self.plain_to_reflect.gameplain.shape[0]-1):#w tejże pętli ustalamy dla każdej komórki jej stan i rysujemy odpowiednim kolorem
    #         for j in range(1, self.plain_to_reflect.gameplain.shape[1]-1):
    #             self.set_color(j-1, i-1, self.lifecolor.get(self.gameplain.gameplain[i][j])) #rysujemy komórkę odpowiednim dla niej kolorem
