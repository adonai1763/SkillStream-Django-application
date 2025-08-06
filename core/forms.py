from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomerUser, Video, Comment


class CustomerCreationForm(UserCreationForm):
    class Meta:
        model = CustomerUser
        fields = ('username', 'email')

class VideouploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('title', 'video_file', 'description')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your comment here...'})
        }
        