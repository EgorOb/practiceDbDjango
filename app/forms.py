from django import forms
from .models import Comment, Entry
from django.contrib.auth.models import User
from django.contrib.auth.forms import UsernameField
from django.forms import EmailField
from django.contrib.auth.forms import UserCreationForm


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'parent']


class CustomUserCreationForm(UserCreationForm):
    email = EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        # field_classes = {"username": UsernameField}


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['blog', 'headline', 'slug_headline', 'summary',
                  'body_text', 'pub_date', 'authors', 'image', 'tags']
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}),
            'body_text': forms.Textarea(attrs={'id': 'id_content'}),
            # Другие настройки виджетов по необходимости
        }
