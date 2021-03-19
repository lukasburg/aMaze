from django.contrib import admin

from play_together import models


# Register your models here.
class GameAdmin(admin.ModelAdmin):
    model = models.Game
    fieldsets = [
        ('General', {'fields': ('name', 'price')}),
        ('Multiplayer', {'fields': (
            'available_on', 'multiplayer_count', 'crossplay_support', 'comment'
        )})
    ]


class OwnedGames(admin.TabularInline):
    extra = 3
    model = models.OwnedGames
    fields = ('console', 'game')


class PlayerAdmin(admin.ModelAdmin):
    exclude = ['user']
    inlines = (OwnedGames, )

    def has_view_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user == obj.user

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user == obj.user


admin.site.register(models.Game, GameAdmin)
admin.site.register(models.Console)
admin.site.register(models.Player, PlayerAdmin)
admin.site.register(models.PlayerGroup)
