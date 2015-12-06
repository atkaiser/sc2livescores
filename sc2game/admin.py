from django.contrib import admin

from sc2game.models import Stream, Game, Player, Bracket

admin.site.register(Stream)
admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Bracket)

# Register your models here.
