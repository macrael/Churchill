"use strict";

var myPlayerID = -1;
var myName = "";
var myNumber = -1;
var myPlayers = [];

Event.observe(window, 'load', function() {
    $('name').focus();
    $('joinbutton').observe('click',joinGame);
});

function joinGame(event){
    var player_name = $('name').getValue();
    myName = player_name;
    console.log("Attempting to join as ",player_name);
    new Ajax.Request('/game/join',
      {
        method:'post',
        parameters: {"name": player_name},
        onSuccess: function(transport){
            joined(transport);
        },
        onFailure: function(transport){
            $("ajax_error").update(transport.responseText);
        }
      });
}

function join_add_player(player_name, player_number){
    var player_element = new Element('li').update(player_name).writeAttribute("id","player_" + player_number).addClassName("player");
    $("player_list").insert(player_element);
    myPlayers.push(player_name);
    console.log(myPlayers);
    //Do something here so that the new player blinks into existance. 
    //player_element.addClassName("hilight");
}

function joined(transport){
    //save as a global variable your player id,you will need that later
    //start polling for the rest. (you will probably be polling when you say start game?)
    //setup the start game button and display all player's names. 
    var data = transport.responseText.evalJSON();
    myPlayerID = data["id"];
    myNumber = data["number"]
    var other_players = data["players"];
    for (var i = 0; i < other_players.length; i++ ){
        console.log(other_players[i]["name"] + " is playing.");
        join_add_player(other_players[i]["name"], other_players[i]["number"]);
    }
    console.log("We Are Requesting Joining.");
    console.log(myPlayers);
    var data = JSON.stringify({"pid": myPlayerID, "player_count": myPlayers.length});
    new Ajax.Request('/game/joining',
      {
        method:'post',
        parameters: {"data" : data},
        onSuccess: function(transport){
            joining(transport);
        },
        onFailure: function(transport){
            $("ajax_error").update(transport.responseText);
        }
      });
    
    var start_link = new Element('a', { href: '/game/start' }).update("Start Game").observe('click',start_button_clicked);
    
    $("joining").update(start_link);
}

function start_button_clicked(e){
    console.log("attempting to start game at server.");
    
    new Ajax.Request('/game/start',
      {
        method:'post',
        parameters: {"pid": myPlayerID},
        onSuccess: function(transport){
            start_game_returned(transport);
        },
        onFailure: function(transport){
            $("ajax_error").update(transport.responseText);
        }
      });
          
    e.stop();
}

function start_game_returned(transport){
    //This may be a pretty useless function, the joining poll is still going to return, probably. 
    //Really don't need to do anything. could not exist. 
    console.log("Starting retunred.");
    var data = transport.responseText.evalJSON();
    console.log(data);
}

function countdown(start_time){
    game_start_time = new Date(start_time * 1000);
    nowTime = new Date();
    remaining_seconds = Math.round((game_start_time.getTime() - nowTime.getTime()) / 1000);
    if (remaining_seconds > 0){
        text = "Game Starts in ";
        text += remaining_seconds + " Second";
        if (remaining_seconds != 1){
            text += "s";
        }
        
        $("joining").update(text);
        setTimeout(function(){countdown(start_time);},1000);
        return;
    }
    $("joining").update("So it begins.");
}

function start_game(start_time){
    console.log("Starting at " + start_time);
    countdown(start_time);
    full_monty();
    //need to get the html for the game (could this be prefetched?)
        //most of the frames should be there already. 
    //should know at this point who is king
    //should know your starting hand and gold and such. 
    //should start the infinite poll that keeps track of game state.
}

function full_monty(){
    //request the full update, then start the poll.
    var data = JSON.stringify({"pid": myPlayerID});
    new Ajax.Request('/game/full',
      {
        method:'post',
        parameters: {"data": data},
        onSuccess: function(transport){
            full_monty_return(transport);
        },
        onFailure: function(transport){
            $("ajax_error").update(transport.responseText);
        }
      });
}

function full_monty_return(transport){
    console.log("full monty");
    console.log(transport);
    var data = transport.responseText.evalJSON();
    
    console.log(data);
    game = data["game"]
    king_num = game["king"];
    turn_num = game["turn"];
    $("player_" + king_num).addClassName("king");
    $("player_" + turn_num).addClassName("turn");
}

function joining(transport){
    console.log("joining...");
    console.log(transport);
    var data = transport.responseText.evalJSON();
    var new_players = data["new_players"];
    var started = data["started"];
    
    for (i=0; i < new_players.length; i++){
        join_add_player(new_players[i]["name"], new_players[i]["number"]);
    }
    //if the game is starting, get that going
    if (started){
        start_game(data["start_time"]);
        return;
    }else {
        var data = JSON.stringify({"pid": myPlayerID, "player_count": myPlayers.length});
        new Ajax.Request('/game/joining',
          {
            method:'post',
            parameters: {"data": data},
            onSuccess: function(transport){
                joining(transport);
            },
            onFailure: function(transport){
                $("ajax_error").update(transport.responseText);
            }
          });
    }
}
