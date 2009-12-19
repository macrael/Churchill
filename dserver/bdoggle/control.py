from bdoggle.models import Game
import datetime, random, threading

game_events = {}
game_word_lists = {}

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
    gameEvent = threading.Event()    
    game.save()
    game_id = game.pk
    game_events[game_id] = gameEvent
    
    return game
    
def end_game(game, words_found) :
    game.number_finished += 1 #This may need to be atomic!
    game.save()
    print "game",game.pk,"number finished", game.number_finished
    try :
        lists = game_word_lists[game.pk]
    except (KeyError):
        game_word_lists[game.pk] = []
        lists = game_word_lists[game.pk]
    
    lists.append(words_found)
    
    game.save() #might want this on the other side of the check? matters?
    if game.number_finished == game.number_of_players :
        game_events[game.pk].set()
    else:
        game_events[game.pk].wait()
    
    others_words = []
    exact_match = False
    for l in lists :
        if l == words_found :
            if exact_match :
                print "Woah! two players found the exact same words!"
                others_words.extend(l)
            exact_match = True
            continue
        others_words.extend(l)
    bad_words = []
    for word in words_found :
        if word in others_words :
            bad_words.append(word)
        else :
            score += 1 #obviously temporary score counting.
    
    return bad_words
