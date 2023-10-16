from django.urls import path, include
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('create/',create_room, name='create_room'),
    path('dsn/create/',create_room_d, name='create_room_d'),
    path('room/<int:room_id>/',room_detail, name='room_detail'),
    path('dsn/room/<int:room_id>/',room_detail_d, name='room_detail_d'),
    path('dsn/room_list/', room_list_d, name='room_list_d'),
    path('mhs/room_list/', room_list, name='room_list'),
    path('dsn/join', dsn_rooms, name='dsn_join'),
    path('mhs/join', mhs_rooms, name='mhs_join'),
    
    path('join_room/<int:room_id>/', join_room, name='join_room'),
    path('leave_room/<int:room_id>/', leave_room, name='leave_room'),
    path('mhs/room_detail/<int:room_id>/',room_detail, name='room_detail'),
    path('dsn/room_detail/<int:room_id>/',room_detail_d, name='room_detail_d'),
    path('send_message/<int:room_id>/',send_message, name='send_message'),
    path('dsn/send_message/<int:room_id>/',send_message, name='send_message_d'),
    path('chat_room/<int:room_id>/',chat_room, name='chat_room'),
    path('dsn/chat_room/<int:room_id>/',chat_room_d, name='chat_room_d'),
    path('join_room/<int:room_id>/',join_room, name='join_room'),
    path('dsn/join_room/<int:room_id>/',join_room, name='join_room_d'),

]+ static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
