from src.game import  Game
import os
from tkinter import *

def train():
    game = Game(500, 1000, 6, 110, "2D Autopilot")

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'src/config/config-neat.txt')
    game.startNeat(config_path)

def runai():
    game = Game(500, 1000, 6, 110, "2D Autopilot")

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'src/config/config-neat.txt')
    game.run_with_ai(config_path)

def normalgame():
    game = Game(500, 1000, 6, 110, "2D Autopilot")

    game.run()

if __name__ == '__main__':
    window = Tk()

    window.title("2D Autonomno Vozilo Client")
    window.geometry('300x300')

    btn_train = Button(window, text="Pokreni Treniranje", command=train)
    btn_train.grid(column=1, row=0)

    btn_ai = Button(window, text="Pokreni AI",command=runai)
    btn_ai.grid(column=1, row=1)

    btn_ai = Button(window, text="Pokreni igricu", command=normalgame)
    btn_ai.grid(column=1, row=2)

    window.mainloop()



