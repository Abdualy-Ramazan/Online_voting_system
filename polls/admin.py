from django.contrib import admin
from .models import Poll, Vote, Rating, Announcement, Choice

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'pub_date', 'end_date', 'is_active')
    inlines = [ChoiceInline]

admin.site.register(Poll, PollAdmin)
admin.site.register(Vote)
admin.site.register(Rating)
admin.site.register(Announcement)
