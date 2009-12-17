from bdoggle.models import Game
import datetime, random

all_cubes = [
    ["A","F","I","R","S","Y"],
    ["A","D","E","N","N","N"],
    ["A","E","E","E","E","M"],
    ["A","A","A","F","R","S"],
    ["A","E","G","M","N","N"],
    ["A","A","E","E","E","E"],
    ["A","E","E","G","M","U"],
    ["A","A","F","I","R","S"],
    ["B","J","K","Q","X","Z"],
    ["C","C","E","N","S","T"],
    ["C","E","I","L","P","T"],
    ["C","E","I","I","L","T"],
    ["C","E","I","P","S","T"],
    ["D","H","L","N","O","R"],
    ["D","H","L","N","O","R"],
    ["D","D","H","N","O","T"],
    ["D","H","H","L","O","R"],
    ["E","N","S","S","S","U"],
    ["E","M","O","T","T","T"],
    ["E","I","I","I","T","T"],
    ["F","I","P","R","S","Y"],
    ["G","O","R","R","V","W"],
    ["I","P","R","R","R","Y"],
    ["N","O","O","T","U","W"],
    ["O","O","O","T","T","U"]
];

def random_board():
    cubes = all_cubes[:]
    board = ""
    for i in range(25) :
        cube = random.choice(cubes)
        cubes.remove(cube)
        side = random.choice(cube)
        board += side
    return board

def new_game() :
    game = Game()
    game.start_time = datetime.datetime.today() + datetime.timedelta(seconds=120)
    game.board = random_board()
    game.save()
    return game