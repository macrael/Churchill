import data, json, datetime

from models import Game,Player

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
    print "creating a new game."
    return game

def new_player(name):
    player = Player()
    player.name = name
    return player

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
    names = []
    for p in players :
        if p.name != name :
            names.append(p.name)
        else :
            print "You already joined this game, OK."
    
    try :
        player = Player.objects.get(name=name)
    except Player.DoesNotExist :
        player = new_player(name)
        
    #this needs to be cleaner, people can use the same name?
    player.game = game
    player.save()
    
    info = {"id" : player.pk , "players" : names}
    return json.dumps(info)
