import data, json, datetime, threading, time, random
from models import Game, Player

game_events = {}
game_locks = {}

def csstr_to_list(csstr):
    cslist = []
    if csstr == "" :
        return cslist
    for s in csstr.split(",") :
        try :
            cslist.append(int(s))
        except ValueError :
            print "error in ctl:",csstr
    return cslist

def list_to_csstr(cslist):
    csstr = ""
    for i in cslist :
        csstr += str(i)
        csstr += ","
    csstr = csstr[0:-1]
    return csstr

#initialze everything.
def initialize() :
    data.setup_deck()
    data.setup_characters()
    print "INITIALIZING"

def new_game():
    game = Game()
    game.deck = ""
    game.started = False
    game.start_time = datetime.datetime.today() + datetime.timedelta(hours=1)#a timeout at some point?
    game.save()
    game_id = game.pk
    #This actually belongs somewhere else, needs to be recreated with every server reboot.
    gameEvent = threading.Event()
    game_events[game_id] = gameEvent
    gameLock = threading.Condition()
    game_locks[game_id] = gameLock
    print "creating a new game.", game.pk
    return game

def new_player(name):
    player = Player()
    player.name = name
    return player

def player_names(game):
    players = game.player_set.all()
    names = []
    for p in players :
        names.append(p.name)
    return names

def join_game(name):
    games = Game.objects.all()
    game = 0;
    if not games :
        print "no games!"
        game = new_game()
    else :
        game = games[len(games) -1]
    if game.started :
        game = new_game()
        
    if game == 0 :
        print "ERROR"
        return HttpResponse("ERROR -- No Game For You.")
    
    players = game.player_set.all()
    names = player_names(game)
    
    if name in names :
        names.remove(name)
        print "You already joined this game, OK."
    
    condLock = game_locks[game.pk];
    condLock.acquire()
    
    try :
        player = Player.objects.get(name=name)
    except Player.DoesNotExist :
        player = new_player(name)
        
    #this needs to be cleaner, people can use the same name?
    player.game = game
    player.save()
        
    #should anything be done in this lock?
    condLock.notifyAll()
    condLock.release()
    
    info = {"id" : player.pk , "players" : names}
    return json.dumps(info)

def same_arrays(aone, atwo):
    for item in aone :
        if item not in atwo :
            print item, "not in", atwo
            return False
    return True


def joining_poll(current_players, player_id):
    #This is a polling request on joining, waiting for players to join and waiting for the game to start.    
    game = Player.objects.get(pk=player_id).game
    the_players = player_names(game)
    
    condLock = game_locks[game.pk];
    condLock.acquire()
    while same_arrays(the_players,current_players) :
        game = Player.objects.get(pk=player_id).game
        if game.started :
            break
        print player_id, "just went to sleep"
        condLock.wait()
        print player_id, "just woke up"
        the_players = player_names(game)
    condLock.release()
    print "done with loop."
    
    def notin(x) : return x not in current_players
    new_players = filter(notin, the_players)
    
    data = {"new_players" : new_players, "started": game.started, "start_time" : time.mktime(game.start_time.utctimetuple())}
    
    json_string = json.dumps(data)
    print "returning string: " + json_string
    return json_string

def draw_card(game):
    #This removes the first card from the deck and returns that number. 
    #Should already have the lock here.
    #obviously very slow. maybe faster to reverse search
    deck = game.deck
    if len(deck) == 0 :
        print "ERROR: The deck is dry."
        return -1
    decknums = csstr_to_list(deck)
    draw = decknums[0]
    deck = list_to_csstr(decknums[1:])
    game.deck = deck
    game.save()
    return draw

def game_start_init(game):
    #We already have the lock here. 
    #This is the function to deal the initial hand etc. 
    players = game.player_set.all()
    #give the game a deck?
    new_deck = []
    for i in range(len(data.deck)) :
        new_deck.append(i)
    random.shuffle(new_deck)
    deck_string = list_to_csstr(new_deck)
    print "Saving the deck:",deck_string
    game.deck = deck_string
    game.characters = "0,1,2,3"
    #for each player, give them a hand, give them gold
    #give one player the crown
    noking = True
    for player in players :
        if noking :
            game.king = player.pk
            noking = False
        hand = []
        for i in range(2) : #TODO: SHOULD BE 4 !!
            hand.append(draw_card(game))
        player.hand = list_to_csstr(hand)
        player.gold = 2
        player.save()
    
    game.save()
    start_round(game)

def start_round(game):
    characters = csstr_to_list(game.characters)
    discard = random.choice(characters)
    remaining = characters[:]
    remaining.remove(discard)
    game.remaining_characters = list_to_csstr(remaining)
    game.visible_characters = str(discard)
    game.turn = game.king
    game.round_mode = 1
    game.save()

def start_game(player_id):
    game = Player.objects.get(pk=player_id).game
    condLock = game_locks[game.pk];
    condLock.acquire()
    if not game.started :
        game.started = True
        game.start_time = datetime.datetime.today() + datetime.timedelta(seconds=10)
        game.save()
        game_start_init(game)
        condLock.notifyAll()
    condLock.release()
    #return the game start time. 
    data = {"start_time" : time.mktime(game.start_time.utctimetuple())}
    return json.dumps(data)

def full_monty(player_id) :
    #This function should return all the state neccecary for a client to display the game. 
    print "hello fully monty.",player_id
    you = {}
    gameD = {}
    others = {}
    you_player = Player.objects.get(pk=player_id)
    game = you_player.game
    gameD["mode"] = game.round_mode
    gameD["king"] = game.king
    gameD["turn"] = game.turn
    gameD["v_chars"] = csstr_to_list(game.visible_characters)
    if game.turn == player_id :
        gameD["r_chars"] = csstr_to_list(game.remaining_characters)
    else :
        gameD["r_chars"] = -1
    
    you["gold"] = you_player.gold
    you["hand"] = csstr_to_list(you_player.hand)
    you["played"] = csstr_to_list(you_player.played)
    you["char"] = you_player.character
    
    for p in game.player_set.all() :
        if p.pk == player_id :
            continue
        player = {}
        player["gold"] = you_player.gold
        player["played"] = csstr_to_list(you_player.played)
        player["char"] = you_player.character
        others[p.pk] = player
    data = { "you" : you, "game" : gameD, "others": others}
    return json.dumps(data)
    
