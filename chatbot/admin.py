from django.contrib import admin
from .models import *

class ConversationAdmin(admin.ModelAdmin):
    list_display = ['sesi', 'user', 'user_message', 'chatbot_response']
    search_fields = ['sesi__uuid', 'user__username', 'user_message', 'chatbot_response']
    list_filter = ['sesi', 'user']

class SesiChatAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'user']
    search_fields = ['uuid', 'user__username']
    list_filter = ['user']
admin.site.register(Conversation, ConversationAdmin)
admin.site.register(SesiChat, SesiChatAdmin)