from django.db import models
from app.models import CustomUser 
from django.contrib.auth import get_user_model
import uuid

class SesiChat(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return f"Tabel {self.uuid} - Sesi: {self.user.username}"

class Conversation(models.Model):
    sesi = models.ForeignKey(SesiChat, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    user_message = models.TextField()
    chatbot_response = models.TextField()
    title = models.CharField(max_length=100)  # Tambahkan kolom title

    def save(self, *args, **kwargs):
        # Ambil 4 kata pertama dari user_message dan atur sebagai title
        self.title = ' '.join(self.user_message.split()[:4])
        
        # Cek apakah ada sesi sebelumnya dengan sesi yang sama
        previous_conversation = Conversation.objects.filter(sesi=self.sesi, user=self.user).order_by('-id').first()
        if previous_conversation:
            self.title = previous_conversation.title
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pengguna: {self.user.username}, User: {self.user_message}, Chatbot: {self.chatbot_response}"
