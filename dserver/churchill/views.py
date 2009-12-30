from django.http import HttpResponse
from django.shortcuts import render_to_response
import control

initalized = False

def index(request) :
    global initalized
    s = ""
    if not initalized :
        control.initialize()
        initalized = True
        s = "Initalized."
    else :
        s = "Already Done."
    print s
    
    return render_to_response('churchill/join.html', {'game_count': "Zero"})

def init(request) :
    global initalized
    s = ""
    if not initalized :
        control.initialize()
        initalized = True
        s = "Initalized."
    else :
        s = "Already Done."
    
    return HttpResponse(s)

def join(request) :
    #send them back their player id, names of other players. 
    #they will then poll to find out about new players, or the start of the game. 
    pname = request.POST["name"]
    print pname, "has joined the game."
    json = control.join_game(pname)
    print "returning string",json
    return HttpResponse(json)
    
def joining(request) :
    print "joining.."
    # This is the polling function for joinging the game. 
    # get new player names and tell that the game has started.
    return HttpResponse("HEYO!")
    
def start_game(request) :
    print "yes"
    # This is the start game command, tell all other players to start in 5 seconds.