var the_deck = [];
var the_characters = [];

var GREEN = "green";
var BLUE = "blue";
var RED = "red";
var PURPLE = "purple";
var YELLOW = "yellow";

function setup_deck() {
    console.log("Setting Up Deck");
    var market = {};
    market["name"] = "Market";
    market["cost"] = 2;
    market["color"] = "green";
    the_deck.push(market);

    var castle = {};
    castle["name"] = "Castle";
    castle["cost"] = 4;
    castle["color"] = "yellow";
    the_deck.push(castle);

    var church = {};
    church.name = "Church";
    church.cost = 3;
    church.color = "purple";
    the_deck.push(church);
}

function setup_characters(){
    console.log("Setting Up Characters");
    var assassin = {};
    assassin.name="Assassin";
    assassin.description="The Assassin can kill one character.";
    the_characters.push(assassin);
    
    var theif = {};
    theif.name="Theif";
    theif.description = "The Theif can steal from one character";
    the_characters.push(theif);
    
    var magician = {};
    magician.name = "Magician";
    magician.description = "The Magician can switch out cards.";
    the_characters.push(magician);
    
    var king = {};
    king.name = "King";
    king.description = "The King gets a bonus gold from yellow districts.";
    the_characters.push(king);
    
    var priest = {};
    priest.name = "Priest";
    priest.description = "The Priest can't have his districts destroied. He gets a bonus gold for each blue district.";
    the_characters.push(priest);
    
    var merchant = {};
    merchant.name = "Merchant";
    merchant.description = "The Merchant gets an exra gold when he takes an action. The Merchant gets an extra gold for every green district.";
    the_characters.push(merchant);
    
    var architect = {};
    architect.name = "Architect";
    architect.description = "The Architect can draw two extra cards and can build three districts.";
    the_characters.push(architect);
    
    var warlord = {};
    warlord.name = "Warlord";
    warlord.description = "The Warlord can destroy a district by paying one less than the cost. He gets an extra gold for every red district.";
    the_characters.push(warlord);
}