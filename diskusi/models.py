from django.db import models
from django.contrib.auth.models import User
from app.models import CustomUser
from django.utils.crypto import get_random_string


class DiscussionRoom(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=7, unique=True, blank=True)
    cover = models.ImageField(upload_to='coverGroup')

    def save(self, *args, **kwargs):
        # Generate a random 7-digit code if it doesn't exist
        if not self.code:
            self.code = get_random_string(length=7, allowed_chars='0123456789')
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"room : {self.name} - code : {self.code}"

class Participant(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    room = models.ForeignKey(DiscussionRoom, on_delete=models.CASCADE)
    is_creator = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'room')

    def __str__(self):
        return f"user : {self.user} - room : {self.room}"

class Message(models.Model):
    room = models.ForeignKey('DiscussionRoom', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='message_files/', null=True, blank=True)

    def __str__(self):
        return f'Message by {self.user.username} in {self.room.name}' 