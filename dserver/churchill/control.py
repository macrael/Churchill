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

def status_poll(pid, turn): #may need to send mode? or just need a good distributed message system.
    game = Player.objects.get(pk=pid).game
    condLock = game_locks[game.pk];
    condLock.acquire()
    game_turn = game.turn
    debug_loop = 0
    while game_turn == turn :
        debug_loop += 1
        if debug_loop > 1 :
            print "INTERESTING: the poll has looped. Might not need to loop for broadcasting"
        player = Player.objects.get(pk=pid)
        game = player.game
        if game.turn == player.number :
            break
        print pid, "just went to sleep."
        condLock.wait()
        print pid, "just woke up."
        player = Player.objects.get(pk=pid)
        game = player.game
        game_turn = game.turn
    
    #either, it is your turn, or the turn has changed.(or both)
    #if the turn has changed, the mode could have changed. mostly doesn't matter. 
    #if it is your turn, we can mostly assume you haven't done anything...
        #at some point we will have to worry if they started their turn, then reloaded? 
        #actually, probably not, they can just redo, so long as they don't get to make a choice twice. 
    info = {}
    gameD = {}
    player = Player.objects.get(pk=pid)
    info["myturn"] = game.turn == player.number
    if info["myturn"] :
        mode = game.round_mode
        gameD["mode"] = game.round_mode
        if mode == 1 :
            gameD["remaining_characters"] = csstr_to_list(game.remaining_characters)
        elif mode == 2 :
            #not sure there is anything for us to do here.
            print "mode 2"
        else :
            print "HMM.. Not ready for this mode."
    
    gameD["turn"] = game.turn
    
    info["game"] = gameD
    
    condLock.release()
    
    return json.dumps(info)

def take_action(pid, actionD):
    player = Player.objects.get(pk=pid)
    game = player.game
    lock = game_locks[game.pk]
    lock.acquire()
    action = actionD["action"]
    info = {}
    info["success"] = True
    if action == "choose_character" :
        if game.round_mode != 1 :
            print "ERROR: shouldn't be choosing characters at a time like this."
            info["success"] = False
        choice = actionD["character"]
        remaining = csstr_to_list(game.remaining_characters)
        if choice not in remaining :
            print "ERROR: character is not a valid choice."
            info["success"] = False
        remaining.remove(choice)
        player.character = choice
        player.save()
        game.remaining_characters = list_to_csstr(remaining)
        game.save()
        #these next two things are done at the end of every turn.
        next_turn(game)
        lock.notifyAll()
        
    if action == "draw_cards" :
        if "draw_count" in actionD :
            draw_count = actionD["draw_count"]
        else :
            draw_count = 2
        drawn_cards = []
        for i in range(draw_count) :
            drawn_cards.append(draw_card(game))
        info["drawn_cards"] = drawn_cards
        
    if action == "discard_cards" :
        if "chosen_card" in actionD :
            hand = csstr_to_list(player.hand)
            hand.append(actionD["chosen_card"])
            player.hand = list_to_csstr(hand)
            player.save()
        discards = actionD["discards"]
        #for now, do nothing. One day may have to keep track of these things and reshuffle if the whole deck is used.
    if action == "take_gold" :
        player.gold += 2
        player.save()
    
    
    #action == "play_card"
    #action == "invoke_ability"
    #action == "end_turn"
    
    lock.release()
    
    return json.dumps(info)


def next_turn(game):
    if game.round_mode == 1 :
        turn = game.turn
        turn += 1
        turn = turn % game.player_set.count()
        game.turn = turn
        if turn == game.king :
            #mode is over.
            game.round_mode = 2
            game.turn = -1
    if game.round_mode == 2 :
        players = game.player_set.all()
        turn_order = game.turn
        if turn_order != -1 :
            curr_player = players[game.turn]
            #assert curr_player has a character.
            turn_order = curr_player.character % 9
        player = None
        while player == None and turn_order < 9 :
            turn_order += 1
            player = player_with_character(players, turn_order)
        if player == None :
            game.round_mode = 1
            game.turn = game.king
        else :
            game.turn = player.number
        
    print "Game Turn is now:", game.turn, "mode:",game.round_mode
    game.save()

def player_with_character(players, char_turn):
    for player in players :
        if player.character % 9 == char_turn  :
            return player
    return None

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
    game.characters = "0,1,2,3,4,5,6,7"
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
    game.visible_discards = discard
    game.remaining_characters = list_to_csstr(remaining)
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
    players = []
    you_player = Player.objects.get(pk=player_id)
    game = you_player.game
    gameD["mode"] = game.round_mode
    gameD["king"] = game.king
    gameD["turn"] = game.turn
    gameD["characters"] = csstr_to_list(game.characters)
    gameD["visible_chars"] = csstr_to_list(game.visible_discards)
    
    you["number"] = you_player.number
    you["hand"] = csstr_to_list(you_player.hand)
        
    for p in game.player_set.all() :
        player = {}
        player["gold"] = p.gold
        player["played"] = csstr_to_list(p.played)
        player["char"] = p.character
        player["number"] = p.number 
        player["name"] = p.name
        player["hand_size"] = len(csstr_to_list(you_player.hand))
        players.append(player)
    info = { "you" : you, "game" : gameD, "players": players}
    return json.dumps(info)
