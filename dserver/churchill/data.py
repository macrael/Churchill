cards = []
fresh_deck = []
characters = []

GREEN = "green"
BLUE = "blue"
RED = "red"
PURPLE = "purple"
YELLOW = "yellow"

class District(object) :
    name = "NONAME"
    cost = -1
    color = "NOCOLOR"
    
class Character(object) :
    name = "NONAME"
    
def setup_deck() :
    market = District()
    market.name = "Market"
    market.cost = 2
    market.color = GREEN
    cards.append(market)
    index = cards.index(market)
    fresh_deck.append(index)
    fresh_deck.append(index)
    fresh_deck.append(index)
    fresh_deck.append(index)
    
    castle = District()
    castle.name = "Castle"
    castle.cost = 4
    castle.color = YELLOW
    cards.append(castle)
    index = cards.index(castle)
    fresh_deck.append(index)
    fresh_deck.append(index)
    fresh_deck.append(index)
    fresh_deck.append(index)
    fresh_deck.append(index)
    
    
    church = District()
    church.name = "Church"
    church.cost = 3
    church.color = PURPLE
    cards.append(church)
    index = cards.index(church)
    fresh_deck.append(index)
    fresh_deck.append(index)
    fresh_deck.append(index)
    fresh_deck.append(index)
    fresh_deck.append(index)


def setup_characters() :
    assassin = Character()
    assassin.name = "Assassin"
    assassin.description = "The Assassin can kill one character."
    characters.append(assassin)
    
    thief = Character()
    thief.name = "Thief"
    thief.description = "The Theif can steal from one character."
    characters.append(thief)
    
    magician = Character()
    magician.name = "Magician"
    magician.description = "The Magician can switch out cards."
    characters.append(magician)
    
    king = Character()
    king.name = "King"
    king.description = "The King gets a bonus gold from yellow districts."
    characters.append(king)
    
    priest = Character()
    priest.name = "Priest"
    priest.description = "The Priest can't have his districts destroied. He gets a bonus gold for each blue district."
    characters.append(priest)
    
    merchant = Character()
    merchant.name = "Merchant"
    merchant.description = "The Merchant gets an exra gold when he takes an action. The Merchant gets an extra gold for every green district."
    characters.append(merchant)
    
    architect = Character()
    architect.name = "Architect"
    architect.description = "The Architect can draw two extra cards and can build three districts."
    characters.append(architect)
    
    warlord = Character()
    warlord.name = "Warlord"
    warlord.description = "The Warlord can destroy a district by paying one less than the cost. He gets an extra gold for every red district."
    characters.append(warlord)
