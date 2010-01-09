game_start_time = 0;
good_wordlist = [];
found_words = [];

board_rep = "";
game_number = -1;
board = [[],[],[],[],[]];
game_started = false;

function join_game(data){
    console.log(data)
    board_rep = data["board"];
    game_number = data["number"];
    game_start_time = new Date(data["start_time"]* 1000);
    console.log("start: " + game_start_time);
    
    countdown()
}

function setup_board(){
    $("#board").empty();
    board_string = "<table>";
    for (i=0; i < 5; i ++){
        board_string += "<tr>";
        for (j=0; j < 5; j++){
            value = board_rep[5*i + j];
            if (value == 'Q'){
                value = "Qu";
            }
            board[i][j] = value;
            board_string += "<td>"+ value + "</td>";
        }
        board_string += "</tr>";
    }
    board_string += "</table>";
    $("#board").append(board_string);
}

function load_words(text){
    words = text.split("\n");
    for (index in words){
        if (words[index].length > 3){
            good_wordlist.push(words[index]);
        }
    }
}

function highlight_text(x, y, word){
    if (0 > x || x > 4 || 0 > y || y > 4){
        //out of bounds
        return 0;
    }
    if ((board[x][y].length > 1 && board[x][y] != "Qu") || board[x][y] === "Quv"){
        //this piece has been visited before.
        return 0;
    }
    bChar = board[x][y];
    wChar = word.charAt(0);
    if (bChar == "Qu"){
        wChar = word.substring(0,2);
    }
    if (bChar == wChar.toUpperCase() || wChar.toUpperCase() == "QU"){
        if (word == wChar){
            $("#board tr:nth-child("+ (x + 1) +") td:nth-child("+ (y + 1) +")").addClass("highlight");
            return 1;
        }
        var subword = word.substring(1);
        if (wChar.toUpperCase() == "QU"){
            subword = word.substring(2);
        }
        board[x][y] += "v";
        var allClear = 0;
        allClear += highlight_text(x-1, y-1, subword);
        allClear += highlight_text(x, y-1, subword);
        allClear += highlight_text(x+1, y-1, subword);
        allClear += highlight_text(x-1, y, subword);
        allClear += highlight_text(x+1, y, subword);
        allClear += highlight_text(x-1, y+1, subword);
        allClear += highlight_text(x, y+1, subword);
        allClear += highlight_text(x+1, y+1, subword);
        if (board[x][y] == "Quv"){
            board[x][y] = "Qu";
        }else {
            board[x][y] = board[x][y].charAt(0);   
        }
        if (allClear){
            $("#board tr:nth-child("+ (x + 1) +") td:nth-child("+ (y + 1) +")").addClass("highlight");
        }
        return allClear;
    }
    return 0;
}

function check_for_word(){
    var word = $("#input_field").val();
    $("#board td").removeClass("highlight");
    var valid = 0;
    for (i=0; i < 5; i ++){
        for (j=0; j < 5; j++){
            valid += highlight_text(i,j,word);
        }
    }
    return valid;
}

function submit_word(){
    word = $("#input_field").val();
    if (check_for_word() === 0){
        $("#input_field").val("");
        return;
    }
    $("#input_field").val("");
    if ($.inArray(word.toLowerCase(),good_wordlist) != -1){
        if ($.inArray(word.toLowerCase(), found_words) == -1){
            found_words.push(word.toLowerCase());
            $("#submitted").append("<li>" + word + "</li>");   
        }
    }
}

function countdown(){
    nowTime = new Date();
    game_time = 60 * 3 * 1000; //should be 60 * 3 * 10000
    remaining_seconds = Math.round((game_start_time.getTime() + game_time - nowTime.getTime()) / 1000);
    if (remaining_seconds > game_time/1000){
        seconds_to_game = remaining_seconds - game_time/1000;
        text = "game starts in " + seconds_to_game + "seconds";
        $("#timer").text(text);
        setTimeout(function(){countdown();},1000);
        return;
    }
    if (remaining_seconds > 0){
        if (!game_started){
            start_game()
        }
        text = "";
         if (remaining_seconds > 60){
             minutes = Math.round(remaining_seconds / 60);
             text += minutes;
             text += " Minute";
             if (minutes > 1){
                 text += "s";
             }
             text += " Remain";
             if (minutes == 1){
                 text += "s";
             }
        } else if (remaining_seconds > 20){
            seconds = Math.round(remaining_seconds / 10) * 10;
            text = seconds + " Seconds Remain"
        } else {
            text = remaining_seconds + " Second";
            if (remaining_seconds != 1){
                text += "s";
            }
            text += " Remain";
            if (remaining_seconds == 1){
                 text += "s";
            }
        }
        $("#timer").text(text);
        setTimeout(function(){countdown();},1000);
        return;
    }
    end_game();

}

function start_game(){
    setup_board();
    game_started = true;
    $("#input_field").attr("enabled","enabled");
    $("#input_field").focus();
}

function end_game(){
    $("#input_field").attr("disabled","disabled");
    $("#input_field").val("");
    $("#submitted").click();
    
    var send_data = { "gnumber" : game_number, "word_list" : found_words };
    console.log(send_data);
    console.log(JSON.stringify(send_data));
    var data = JSON.stringify(send_data);
    //format up the variables, send ajax request
    console.log(data);
    
    //return;
    
    $.ajax({
        contentType:"application/json",
        data:{"data":data},
        type:"GET",
        dataType: "json",
        cache: false,
        url: "end",
        error: function(request, textStatus, errorThrown){
            $("#ajax_error").text("Error." + request + " st: " + textStatus + " er: " + errorThrown);
        },
        success: function(msg, textStatus){
            console.log("message Recieved. executing. " + textStatus);
            handle_results(msg);
        }
    });
}

function handle_results(data){
    console.log("recieved data");
    console.log(data);
    
    var bad_words = data["bad_words"];
    
    for ( var i =0; i < bad_words.length; i ++){
        found_words = found_words.splice($.inArray(bad_words[i],found_words));
        $("#submitted li:contains("+ bad_words[i] +")").addClass("bad");
    }
    console.log(found_words);
    
    var score = data["score"];
    $("#timer").text("Game Over. Your Score: " + score);
}

$(document).ready(function(){    
    $.ajax({
      dataType: "text",
      cache: true,
      url: "/static/words.txt",
      success: function(msg){
        load_words(msg);
      }
    });
    
    $("#input_field").keyup(function (){
        if (event.keyCode == 13){//Return Key Pressed
            submit_word();
            return;
        }
        check_for_word();
    });
    
    
    $("a[href=join]").click(function (){
        event.preventDefault();
        $("a[href=join]").remove();
        $.ajax({
          dataType: "json",
          cache: false,
          url: "join",
          success: function(msg){
            join_game(msg);
          }
        });
    });
    
    //start_game();
    
});