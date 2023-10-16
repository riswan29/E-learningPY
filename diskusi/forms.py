from django import forms
from .models import *

class DiscussionRoomForm(forms.ModelForm):
    class Meta:
        model = DiscussionRoom
        fields = ['name', 'cover', 'description']

class MessageForm(forms.ModelForm):
    file = forms.FileField(required=False)
    content = forms.CharField(widget=forms.Textarea(attrs={'class':'fn__chat_textarea', 'rows':'4' })) 
    class Meta:
        model = Message
        fields = ['content', 'file']
    