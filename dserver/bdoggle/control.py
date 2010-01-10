from bdoggle.models import Game
import datetime, random, threading

game_events = {}
game_locks = {}
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
    game.start_time = datetime.datetime.today() + datetime.timedelta(seconds=30)#(seconds=120)
    game.board = random_board()
<<<<<<< HEAD
    gameEvent = threading.Event()
=======
    gameEvent = threading.Event()    
>>>>>>> will/master
    game.save()
    game_id = game.pk
    game_events[game_id] = gameEvent
    gameLock = threading.RLock()
    game_locks[game_id] = gameLock
    print game_events
    
    return game
    
def end_game(game, words_found) :
    print "in the end game."
    game_locks[game.pk].acquire()
    game.number_finished += 1 #This may need to be atomic!
    game.save()
    try :
        lists = game_word_lists[game.pk]
    except (KeyError):
        game_word_lists[game.pk] = []
        lists = game_word_lists[game.pk]
    
    lists.append(words_found)
    print lists
    
    game.save() #might want this on the other side of the check? matters?

    print game.number_finished ,"finished", game.number_of_players, "total."
    if game.number_finished == game.number_of_players :
        game_events[game.pk].set()
    else:
        game_locks[game.pk].release()
        game_events[game.pk].wait()
        game_locks[game.pk].acquire()
        print "Released."
    
    others_words = []
    exact_match = False
    for l in lists :
        if l == words_found :
            if exact_match :
                others_words.extend(l)
            exact_match = True
            continue
        others_words.extend(l)
    bad_words = []
    score = 0
    for word in words_found :
        if word in others_words :
            bad_words.append(word)
        else :
            length = len(word)
            if length < 4 :
                print "WEIRD: word too short. Cheater."
            elif length == 4 :
                score += 1
            elif length == 5 :
                score += 2
            elif length == 6 :
                score += 3
            elif length == 7 :
                score += 5
            else :
                score += 11
    
    print "Done with the End Game. score: " + str(score)
    game_locks[game.pk].release()
    return bad_words, score
