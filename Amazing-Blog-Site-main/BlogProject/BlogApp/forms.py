from .models import Comment
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CommentForm(forms.ModelForm):
  class Meta:
    model = Comment
    fields = ['content']

  content = forms.CharField(
    widget=forms.Textarea(attrs={
      'class': 'form-control',
      'id': 'comment',
      'rows': '4',
      'placeholder': 'Enter your comment'
    })
  )


class ContactForm(forms.Form):
  name = forms.CharField(
      max_length=100,
      widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'})
  )
  email = forms.EmailField(
      widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
  )
  message = forms.CharField(
      widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter your message'})
  )

class LoginForm(AuthenticationForm):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['username'].widget.attrs.update({'class': 'form-control'})
    self.fields['password'].widget.attrs.update({'class': 'form-control'})


class SignupForm(UserCreationForm):
  username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}))
  email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
  password1 = forms.CharField(
    label="Password",
    strip=False,
    widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}),
  )
  password2 = forms.CharField(
    label="Confirm Password",
    widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'}),
    strip=False,
  )

  class Meta:
    model = User
    fields = ('username', 'email', 'password1', 'password2')

class UserProfileForm(forms.ModelForm):
  username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}))
  email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
  first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}))
  last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}))
  bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your bio', 'rows': 3}))
  profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control-file'}))
  social_media_links = forms.URLField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Facebook, Instagram, Twitter links'}))

  class Meta:
    model = User
    fields = ['username', 'email', 'first_name', 'last_name', 'bio', 'profile_picture','social_media_links']
