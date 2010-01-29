"use strict";

var myPlayerID = -1;
var myName = "";
var myNumber = -1;
var myPlayers = [];
var current_turn  = -1;
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
    $("players_section").show();
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
        //calling the null callback is giving us an error. I think we will do something different for the actual start of the game anyway.
        //callback_fn();
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
    console.log("Adding card " + card_index + " to hand.");
    var card_element = card_for_index(card_index);
    $("hand").insert(card_element);
}

function card_for_index(card_index){
    var card = the_deck[card_index];
    var card_element = new Element('div').addClassName("district"); //should we give every card its own ID?
    card_element.insert(new Element('div').addClassName("cost").update(card.cost));
    card_element.insert(new Element('div').addClassName("name").update(card.name));
    //description may not be for every one. 
//    card_element.insert(new Element('div').addClassName("description").update(card.cost));
    return card_element;
}

function add_character(character_index){
    console.log("cindex: " + character_index);
    chelement = character_element(character_index);
    chelement.writeAttribute("id","character_" +character_index );
    $("all_characters").insert(chelement);
}

function character_element(character_index){
    var character = the_characters[character_index];
    console.log(character);
    char_img = get_character_image(character);
    char_element = new Element('li').addClassName("character");
    char_element.insert(char_img);
    char_element.insert(character.name);
    
    return char_element;
}

function select_character(event) {
    var new_select = event.target;
    if(!new_select.hasClassName('character')) {
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
            return new Element('div').addClassName("char_image").addClassName("unchar");
            break;
    }
}

function mark_character_discarded(character_index){
    $("character_" + character_index).addClassName("discarded");
}

//The fully monty should only have to happen once per load of the game. Right?
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
    $("hand").show();
    
    $("players").update("");//this won't be necessary in the future. 
    var players = $A(data["players"]);
    players.each(add_player_object);
    
    $("action_body").update(players[0].name + " is choosing a character.").addClassName('text_body');;
    $("action_section").show();
    
    var game = data["game"];
    var king_num = game["king"];
    var turn_num = game["turn"];
    current_turn = game["turn"];
    var characters = $A(game["characters"]);
    $('characters_section').show();
    characters.each(add_character);
    var vis_chars = $A(game["visible_chars"]);
    vis_chars.each(mark_character_discarded)
    set_unique_player_class("king", king_num);
    set_unique_player_class("turn", turn_num);
    
    console.log("Done With The Monty.");
    
    seek_status();
}

function set_unique_player_class(classname, player_num){
    var players = $("players").childElements();
    console.log(players);
    for (var i = 0; i < players.length; i++){
        if (players[i].hasClassName(classname)){
            players[i].removeClassName(classname);
        }
    }
    $("player_" + player_num ).addClassName(classname);
    console.log("Finished adding " + classname);
}

function seek_status(){
    var data = JSON.stringify({"pid": myPlayerID, "turn":current_turn});
    new Ajax.Request('/game/status',
      {
        method:'post',
        parameters: {"data": data},
        onSuccess: function(transport){
            status(transport);
        },
        onFailure: function(transport){
            $("ajax_error").update(transport.responseText);
        }
      });
}

//this is the return from the status of the game. could be your turn, another turn could have ended.
function status(transport){
    console.log("status returns.");
    console.log(transport.responseText.evalJSON());
    
    var data = transport.responseText.evalJSON();
    var game = data["game"];
    var myturn = data["myturn"];
    set_unique_player_class("turn", game["turn"]);
    current_turn = game["turn"];
    if (myturn) {
        if (game.mode == 1){
            choose_character(game["remaining_characters"]);
        }else if (game.mode==2) {
            take_turn();
        }else {
            console.log("Not ready for this mode.");
        }
    }else{
        seek_status();
    }
}

function take_turn() {
    var chooser = new Element('div').writeAttribute("id", "chooser");
    var choices = new Element("div").addClassName("choices");
    var drawButton = new Element('button').update("Draw Cards");
    drawButton.observe('click',action_draw);
    var goldButton = new Element('button').update("Take 2 Gold");
    goldButton.observe('click',action_gold);
    var instructions = new Element('div').addClassName("instructions").update("What action will you take?");
    chooser.insert(instructions);
    choices.insert(drawButton);
    choices.insert(goldButton);
    chooser.insert(choices);
    $("main").insert({top: chooser});
}

function action_draw() {
    var data = JSON.stringify({"pid": myPlayerID, "action":"draw_cards"});
    new Ajax.Request('/game/action',
    {
        method:'post',
        parameters: {"data": data},
        onSuccess: function(transport){
            action_draw_return(transport);
        },
        onFailure: function(transport){
        $("ajax_error").update(transport.responseText);
        }
    });
}

function action_draw_return(transport){
    var data = transport.responseText.evalJSON();
    console.log(data);
    var drawn = data["drawn_cards"];
    var chooser = $("chooser");
    var choices = new Element("div").addClassName("choices");
    console.log(drawn);
    for (var i = 0; i < drawn.length ; i++){
        var card = card_for_index(drawn[i]);
        console.log(card);
        choices.insert(card);
    }
    chooser.update(choices);

}

function action_gold() {
    
    take_action();
}

function take_action() {
    $("chooser").remove();
    //do swiches for different "on action" characters.
}

function choose_character(character_list){
    var chooser = new Element('div').writeAttribute("id", "chooser");
    var instructions = new Element('div').addClassName("instructions").update("Choose a Character?");
    chooser.insert(instructions);
    var characters = new Element('ol').addClassName("characters");
    var cids = $A(character_list);
    for (var i=0; i < cids.length; i ++){
        var char_element = character_element(cids[i]);
        char_element.writeAttribute("id","choose_character_" + cids[i]);
        characters.insert(char_element);
        char_element.observe('click',select_character);
        char_element.id_num = cids[i];
        char_element.addClassName("button");
    }
    chooser.insert(characters);
    var choose_button = new Element('button').update('Choose Character');
    choose_button.observe('click',choose_selected_character);
    chooser.insert(choose_button);
    $("action_header").update("Please choose a character");
    $("main").insert({top: chooser});
}

function choose_selected_character(event){
    if (currently_selected_character == null){
        return;
    }
    
    var cid = currently_selected_character.id_num;
    console.log("Choosing character id: " + cid);
    
    $("chooser").remove();
    $("character_" + cid).addClassName("your_character");
    
    $("log").insert("<p>You have chosen character #" + cid + "</p>");
    $("action_header").update("Currently...");
    
    var data = JSON.stringify({"pid": myPlayerID, "action":"choose_character", "character": cid});
    new Ajax.Request('/game/action',
      {
        method:'post',
        parameters: {"data": data},
        onSuccess: function(transport){
            action_return(transport);
        },
        onFailure: function(transport){
            $("ajax_error").update(transport.responseText);
        }
      });
}

function action_return(transport){
    console.log("action returned.");
    var data = transport.responseText.evalJSON();
    console.log(data);
    
    if (data["success"]){
        console.log("Success!");
        //current_turn = data["turn"];
        //set_unique_player_class("turn", current_turn);
        //I think that this should be in the status seeking, actually.
        //the action doesn't need to ruturn anything. 
    }else {
        console.log("FAIL!");
    }
    
    seek_status();
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
