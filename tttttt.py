import numpy as np
import tkinter as tk
import random



class Cells:

    def __init__(self, a, b, canva):
        self.canva = canva
        x = np.zeros((a, b), dtype=int)
        lifecolor = {1: "black", 0: "white"}

        # tworzymy wartosci poczatkowe
        for i in range(1, a - 1):
            for j in range(1, b - 1):
                x[i][j] = random.randint(0, 1)
        self.zycie = x
        print(self.zycie)

        for i in range(1, self.zycie.shape[0]-1):
            for j in range(1, self.zycie.shape[1]-1):
                self.canva.create_rectangle(700/(self.zycie.shape[1]-2) * (j - 1),
                                            700/(self.zycie.shape[0]-2) * (i - 1), 700/(self.zycie.shape[1]-2) * j,
                                            700/(self.zycie.shape[0]-2) * i, fill=lifecolor.get(self.zycie[i][j]))
        self.change()

    def __str__(self):
        return str(self.zycie)

    def neighbours(self):
        neighbours = np.zeros(self.zycie.shape[:], dtype=int)
        for i in range(1, self.zycie.shape[0] - 1):
            for j in range(1, self.zycie.shape[1] - 1):
                neighbours[i][j] = sum(self.zycie[i - 1][j - 1:j + 2]) + self.zycie[i][j - 1] + self.zycie[i][j + 1] + \
                                   sum(self.zycie[i + 1][j - 1:j + 2])
        return neighbours

    def change(self):
        neigh = self.neighbours()
        self.canva.delete("all")
        lifecolor = {1: "black", 0: "white"}
        lifedict2 = {0: {0: 0, 1: 0, 2: 0, 3: 1, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}, 1: {0: 0, 1: 0, 2: 1, 3: 1, 4: 0, 5: 0,
                                                                                    6: 0, 7: 0, 8: 0}}
        for i in range(1, self.zycie.shape[0] - 1):
            for j in range(1, self.zycie.shape[1] - 1):
                self.zycie[i][j] = lifedict2[self.zycie[i][j]].get(neigh[i][j])
        for i in range(1, self.zycie.shape[0] - 1):
            for j in range(1, self.zycie.shape[1] - 1):
                self.canva.create_rectangle(700/(self.zycie.shape[1]-2) * (j - 1),
                                            700/(self.zycie.shape[0]-2) * (i - 1), 700/(self.zycie.shape[1]-2) * j,
                                            700/(self.zycie.shape[0]-2) * i, fill=lifecolor.get(self.zycie[i][j]))
        self.canva.after(1000, self.change)


# class Okno:
#     def __init__(self, sizea, sizeb):
#         self.okno = tk.Tk()
#         self.okno.geometry(f'{sizea}x{sizeb}')
#         self.can = tk.Canvas(self.okno, width=sizea, height=sizeb, bg='white')
#         self.can.pack()


okno = tk.Tk()
okno.geometry('700x700')
can = tk.Canvas(okno, width=700, height=700, bg="white")
can.pack()

komorki = Cells(25, 25, can)

okno.mainloop()
