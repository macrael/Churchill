import json
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
    jsond = control.join_game(pname)
    print "returning string",jsond
    return HttpResponse(jsond)
    
def joining(request) :
    # This is the polling function for joinging the game. 
    # get new player names and tell that the game has started.
    data = json.loads(request.POST["data"])
    
    pid = data["pid"]
    player_count = data["player_count"]
    print pid, "is joining..."
    jsond = control.joining_poll(pid,player_count)
    return HttpResponse(jsond)
    
def start_game(request) :
    pid = request.POST["pid"]
    jsond = control.start_game(pid)
    return HttpResponse(jsond)
    
def full_monty(request):
    data = json.loads(request.POST["data"])
    
    pid = data["pid"]
    jsond = control.full_monty(pid)
    return HttpResponse(jsond)
