game_start_time = 0;
good_wordlist = [];
found_words = [];
all_cubes = [
    ["A","F","I","R","S","Y"],
    ["A","D","E","N","N","N"],
    ["A","E","E","E","E","M"],
    ["A","A","A","F","R","S"],
    ["A","E","G","M","N","N"],
    ["A","A","E","E","E","E"],
    ["A","E","E","G","M","U"],
    ["A","A","F","I","R","S"],
    ["B","J","K","Qu","X","Z"],
    ["C","C","E","N","S","T"],
    ["C","E","I","L","P","T"],
    ["C","E","I","I","L","T"],
    ["C","E","I","P","S","T"],
    ["D","H","L","N","O","R"],
    ["D","H","L","N","O","R"],
    ["D","D","H","N","O","T"],
    ["D","H","H","L","O","R"],
    ["E","N","S","S","S","U"],
    ["E","M","O","T","T","T"],
    ["E","I","I","I","T","T"],
    ["F","I","P","R","S","Y"],
    ["G","O","R","R","V","W"],
    ["I","P","R","R","R","Y"],
    ["N","O","O","T","U","W"],
    ["O","O","O","T","T","U"]
];

board = [[],[],[],[],[]];

function setup_board(){
    cubes = all_cubes.slice(0);
    
    $("#board").empty();
    board_string = "<table>";
    for (i=0; i < 5; i ++){
        board_string += "<tr>";
        for (j=0; j < 5; j++){
            cube_index = Math.floor( Math.random() * cubes.length); 
            cube = cubes[cube_index];
            cubes.splice(cube_index,1);//for some reason slice turns the cube into a string.
            value = cube[Math.floor(Math.random() * cube.length)];
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
    game_time = 60 * 3 * 1000;
    remaining_seconds = Math.round((game_start_time.getTime() + game_time - nowTime.getTime()) / 1000);
    if (remaining_seconds > 0){
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
        } else if (remaining_seconds > 10){
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
    game_start_time = new Date();
    $("#input_field").attr("enabled","enabled");
    $("#input_field").focus();
    countdown();
}

function end_game(){
    $("#input_field").attr("disabled","disabled");
    $("#input_field").val("");
    $("#submitted").click();
    
    var score = 0;
    for (index in found_words){
        switch (found_words[index].length){
            case 1:
            case 2:
            case 3: console.log("What? short word!"); break;
            case 4: score += 1; break;
            case 5: score += 2; break;
            case 6: score += 3; break;
            case 7: score += 5; break;
            default: score += 11; 
        }
    }
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
    
    start_game();
    
});