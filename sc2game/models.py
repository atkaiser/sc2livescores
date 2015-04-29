from django.db import models
from django.utils import timezone


class Stream(models.Model):
    name = models.CharField(max_length=100, default = "")
    url = models.CharField(max_length=100, default = "")
    up = models.BooleanField(default = False)
    
    def __str__(self):
        return self.name

class Game(models.Model):
    game_on = models.BooleanField(default = False)
    game_off_time = models.DateTimeField(default = timezone.now)
    on_map = models.CharField(max_length=100)
    current_time = models.CharField(max_length=10)
    current_round = models.CharField(max_length=100)
    stream = models.ForeignKey(Stream)

    def __str__(self):
        return "Game for stream: " + self.stream.name

class Player(models.Model):
    name = models.CharField(max_length=100, default = "")
    race = models.CharField(max_length=15, default = "")
    score = models.IntegerField(default=-1)
    supply = models.CharField(max_length=10, default = "")
    minerals = models.IntegerField(default=0)
    gas = models.IntegerField(default=0)
    workers = models.IntegerField(default=0)
    army = models.IntegerField(default=0)
    stream = models.ForeignKey(Stream)

    def __str__(self):
        return "Player for stream: " + self.stream.name

class Bracket(models.Model):
    url = models.CharField(max_length=100, default = "")
    stream = models.ForeignKey(Stream)
    
    def __str__(self):
        return "Bracket for stream: " + self.stream.name
