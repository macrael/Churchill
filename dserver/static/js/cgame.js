var myPlayerID = -1;

Event.observe(window, 'load', function() {
    $('name').focus();
    $('joinbutton').observe('click',joinGame);
});

function joinGame(event){
    var player_name = $('name').getValue();
    console.log("Attempting to join as ",player_name);
    new Ajax.Request('/game/join',
      {
        method:'post',
        parameters: {"name": player_name},
        onSuccess: function(transport){
            joined(transport);
        },
        onFailure: function(transport){
            $("ajax_error").insert(transport.responseText)
        }
      });
}

function joined(transport){
    //save as a global variable your player id,you will need that later
    //start polling for the rest. (you will probably be polling when you say start game?)
    //setup the start game button and display all player's names. 
    var data = transport.responseText.evalJSON();
    myPlayerID = data["id"];
    
    new Ajax.Request('/game/joining',
      {
        method:'post',
        parameters: {"pid": myPlayerID},
        onSuccess: function(transport){
            joining(transport);
        },
        onFailure: function(transport){
            $("ajax_error").insert(transport.responseText)
        }
      });
    
    var start_link = new Element('a', { href: '/game/start' }).update("Start Game").observe('click',start_button_clicked);
    
    $("joining").update(start_link);
}

function start_button_clicked(e){
    alert("starting game!");
    e.stop();
}

function joining(transport){
    //if the game is starting, get that going
    //if the game is not starting, we just poll again? 
    //what would trigger a not starting. 
}
