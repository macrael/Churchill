cards = []
fresh_deck = []
characters = []

GREEN = "green"
BLUE = "blue"
RED = "red"
ORANGE = "orange"
PURPLE = "purple"
GOLD = "gold"

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
    castle.color = GOLD
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
    characters.append(assassin)
    
    thief = Character()
    thief.name = "Thief"
    characters.append(thief)
    
    magician = Character()
    magician.name = "Magician"
    characters.append(magician)
    
    king = Character()
    king.name = "King"
    characters.append(king)