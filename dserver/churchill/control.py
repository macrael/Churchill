import data, json, datetime, threading, time

from models import Game,Player

game_events = {}
game_locks = {}

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

def start_game(player_id):
    game = Player.objects.get(pk=player_id).game
    condLock = game_locks[game.pk];
    condLock.acquire()
    
    game.started = True
    game.start_time = datetime.datetime.today() + datetime.timedelta(seconds=10)
    game.save()
    
    condLock.notifyAll()
    condLock.release()
    
    #return the game start time. 
    data = {"start_time" : time.mktime(game.start_time.utctimetuple())}
    return json.dumps(data)
