import data, json, datetime, threading, time, random
from models import Game, Player

game_events = {}
game_locks = {}

#----Helper methods to convet to and from comma separated integer strings. 
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

#------End helper methods. 

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
    
    condLock = game_locks[game.pk];
    condLock.acquire()
    
    try :
        player = Player.objects.get(name=name)
    except Player.DoesNotExist :
        player = new_player(name)
        
    player_count = game.player_set.count()
    player.number = player_count
    player.game = game
    player.save()
    
    players_data = []
    for p in game.player_set.all() :
        player_data = {"name" : p.name, "number" : p.number}
        players_data.append(player_data)
    
    #should anything be done in this lock?
    condLock.notifyAll()
    condLock.release()
    
    info = {"id" : player.pk , "players" : players_data, "number" : player_count}
    return json.dumps(info)


def joining_poll(player_id,player_count):
    #This is a polling request on joining, waiting for players to join and waiting for the game to start.    
    game = Player.objects.get(pk=player_id).game
    
    condLock = game_locks[game.pk];
    condLock.acquire()
    game_player_count = game.player_set.count()
    while game_player_count == player_count :
        game = Player.objects.get(pk=player_id).game
        if game.started :
            break
        print player_id, "just went to sleep"
        condLock.wait()
        print player_id, "just woke up"
        game_player_count = game.player_set.count()
    
    print "done with loop."
    game_player_count = game.player_set.count()
    players_data = []
    if game_player_count != player_count:
        new_players = game.player_set.all()[player_count :]
        for p in new_players :
            player_data = {"name" : p.name, "number" : p.number}
            players_data.append(player_data)
    
    info = {"new_players" : players_data, "started": game.started, "start_time" : time.mktime(game.start_time.utctimetuple())}
    condLock.release()
    json_string = json.dumps(info)
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
    new_deck = data.fresh_deck[:]
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
            game.king = player.number
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
    info = {"start_time" : time.mktime(game.start_time.utctimetuple())}
    return json.dumps(info)

def full_monty(player_id) :
    #This function should return all the state neccecary for a client to display the game. 
    print "hello fully monty.",player_id
    you = {}
    gameD = {}
    others = []
    you_player = Player.objects.get(pk=player_id)
    game = you_player.game
    gameD["mode"] = game.round_mode
    gameD["king"] = game.king
    gameD["turn"] = game.turn
    gameD["visible_chars"] = csstr_to_list(game.visible_characters)
    if game.turn == player_id :
        gameD["remaining_chars"] = csstr_to_list(game.remaining_characters)
    else :
        gameD["remaining_chars"] = -1
    
    you["gold"] = you_player.gold
    you["hand"] = csstr_to_list(you_player.hand)
    you["played"] = csstr_to_list(you_player.played)
    you["char"] = you_player.character
    
    for p in game.player_set.all() :
        if p.pk == player_id :
            continue
        player = {}
        player["gold"] = p.gold
        player["played"] = csstr_to_list(p.played)
        player["char"] = p.character
        player["number"] = p.number 
        others.append(player)
    info = { "you" : you, "game" : gameD, "others": others}
    return json.dumps(info)