"use strict";

var myPlayerID = -1;
var myName = "";
var myNumber = -1;
var myPlayers = [];
var currently_selected_character = null;

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
    $("players").insert(player_element);
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
    
    $("page_header").update("Citadels &#8212; Waiting for Game Start");
    
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
    console.log("Starting returned.");
    var data = transport.responseText.evalJSON();
    console.log(data);
}

function countdown(start_time,callback_fn){
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
        setTimeout(function(){countdown(start_time,callback_fn);},1000);
        return;
    }
    else {
        $("joining").update("So it begins.");
        callback_fn();
    }
}

function start_game(start_time){
    console.log("Starting at " + start_time);
    countdown(start_time, null); //full_monty);
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

function add_player_object(player){
    var p = new Element('li').writeAttribute("id","player_" + player["number"]).addClassName("player");
    var name = new Element('span').update(player["name"]).addClassName("name");
    if (player["number"] === myNumber){
        name.update("You");
    }
    p.insert(name);
    var gold = new Element('span').update(player["gold"]).addClassName("gold").addClassName("count");
    p.insert(gold);
    var hand_size = new Element('span').update(player["hand_size"]).addClassName("hand_size").addClassName("count");//needs to be sent
    p.insert(hand_size);
    var cards_played = new Element('span').update(player["played"].length).addClassName("cards_played").addClassName("count");
    p.insert(cards_played);
    var net_worth = new Element('span').update("-1").addClassName("net_worth").addClassName("count"); //needs to be calcualted
    p.insert(net_worth);
    $("players").insert(p);
}

function add_card_to_hand(card_index){
    //how to do this? we will have to translate.
}

function add_character(character_index){
    console.log("cindex: " + character_index);
    console.log(the_characters);
    var character = the_characters[character_index];
    console.log("adding character");
    console.log(character);
    char_img = get_character_image(character);
    char_element = new Element('div').writeAttribute("id","character_" +character_index ).addClassName("character");
    char_element.insert(char_img);
    char_element.insert("<br>");
    char_element.insert(character.name);
    char_container_element = new Element('li').addClassName("char_container");
    char_container_element.update(char_element);
    $("characters").insert(char_container_element);
    char_container_element.observe('click',select_character);
}

function select_character(event) {
    var new_select = event.target;
    if(!new_select.hasClassName('char_container')) {
        new_select = event.currentTarget;
    }
    if(currently_selected_character != null) {
        currently_selected_character.removeClassName("selected");
    }
    new_select.addClassName("selected");
    currently_selected_character = new_select;
}

function get_character_image(character){
    switch(character.name) {
        case "Assassin":
        case "Theif":
        case "Magician":
        case "King":
        case "Priest":
        case "Merchant":
        case "Architect":
         case "Warlord":
            return new Element('img').writeAttribute("src","/static/graphics/unchar.png");
            break;
    }
}

function mark_character_discarded(character_index){
    $("character_" + character_index).addClassName("discarded");
}

function full_monty_return(transport){
    console.log("full monty");
    console.log(transport);
    var data = transport.responseText.evalJSON();
    console.log(data);
    //players
    setup_deck();
    console.log(the_deck);
    setup_characters();
    console.log(the_characters);
    
    var you = data["you"];
    myNumber = you["number"];
    var hand = you["hand"];
    hand.each(add_card_to_hand);
    
    $("players").update("");//this won't be necessary in the future. 
    var players = $A(data["players"]);
    players.each(add_player_object);
    
    var game = data["game"];
    var king_num = game["king"];
    var turn_num = game["turn"];
    var characters = $A(game["characters"]);
    characters.each(add_character);
    var vis_chars = $A(game["visible_chars"]);
    vis_chars.each(mark_character_discarded)
    $("player_" + king_num).addClassName("king");
    $("player_" + turn_num).addClassName("turn");
    
    console.log("Done With The Monty.");
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
