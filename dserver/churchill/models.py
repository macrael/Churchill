from django.db import models

class Game(models.Model):
    start_time = models.DateTimeField('start time and date')
    number_finished = models.IntegerField(default=0)
    deck = models.CommaSeparatedIntegerField(max_length=200)
    started = models.BooleanField()
    round_mode = models.IntegerField(default=0) #0= game setup, 1 = choose character, 2 = turns, 3 = game over
    turn = models.IntegerField(default= -1) #character pk.
    king = models.IntegerField(default= -1) #character pk.
    characters = models.CommaSeparatedIntegerField(max_length=25,default="")
    remaining_characters = models.CommaSeparatedIntegerField(max_length=25,default="")
    visible_characters = models.CommaSeparatedIntegerField(max_length=10,default="")

class Player(models.Model):
    game = models.ForeignKey(Game)
    name = models.CharField(max_length=100)
    #username = modles.CharField(max_length=100)
    gold = models.IntegerField(default=0)
    character = models.IntegerField(default=-1) #characters are 0-7 thier order of play.
    hand = models.CommaSeparatedIntegerField(max_length=100,default="")
    played = models.CommaSeparatedIntegerField(max_length=100,default="")

