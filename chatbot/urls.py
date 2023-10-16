from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

# app_name = 'chat'
urlpatterns = [
    # path('chatbot/', views.chatbot_view, name='chatbot'),
    # path('chatbot/<uuid:conversation_id>/', views.chatbot_view, name='chatbot'),
    path('chat/new/', views.sesi, name='tabel'),
    # path('tabel/<uuid:uuid>/tambah/', views.chatbot_view, name='tambah_data_tabel'),
    path('chatbot/<uuid:uuid>/mhs/', views.chatbot_view_m, name='tambah_data_tabel'),
    path('chatbot/<uuid:uuid>/dsn/', views.chatbot_view_d, name='dsn_cb'),
    path('sesi/<uuid:uuid>/hapus/mhs', views.hapus_sesi, name='hapus_sesi'),
    path('sesi/<uuid:uuid>/hapus/dsn', views.hapus_sesi_d, name='hapus_sesi_d'),
]+ static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
