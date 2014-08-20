from django.core.management.base import BaseCommand
from sc2game.models import Stream, Game, Player

class Command(BaseCommand):

    def handle(self, *args, **options):
        s = Stream()
        s.name = 'test'
        s.url = 'test'
        s.up = True
        s.save()
        
        g = Game(stream=s)
        g.save()
        
        p1 = Player(stream=s)
        p1.name = "p1"
        p1.save()
        
        p2 = Player(stream=s)
        p2.name = "p2"
        p2.save()