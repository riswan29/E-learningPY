from django.contrib import admin
from .models import *

class TabelParisipan(admin.ModelAdmin):
    list_display = ['room', 'is_creator', 'user']
    list_filter = ['room', 'user']
    search_fields = ('user__username', 'user__email')
    list_per_page :15
    
class TabelMessage(admin.ModelAdmin):
    list_display = ['room', 'user']
    list_filter = ['room']
# Register your models here.
admin.site.register(DiscussionRoom)
admin.site.register(Participant, TabelParisipan)
admin.site.register(Message, TabelMessage)