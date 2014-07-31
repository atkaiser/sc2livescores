from django.db import models


class Stream(models.Model):
    name = models.CharField(max_length=100, default = "")
    url = models.CharField(max_length=100, default = "")
    up = models.BooleanField(default = False)


class Game(models.Model):
    game_on = models.BooleanField(default = False)
    on_map = models.CharField(max_length=100)
    current_time = models.CharField(max_length=10)
    current_round = models.CharField(max_length=100)
    stream = models.ForeignKey(Stream)


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


class Bracket(models.Model):
   url = models.CharField(max_length=100, default = "")
   stream = models.ForeignKey(Stream)
