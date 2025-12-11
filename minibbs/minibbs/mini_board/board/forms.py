from django import forms
from .models import Post, Profile, Comment

class PostForm(forms.ModelForm):
  class Meta:
    model = Post
    fields = ['content', 'image']

class ProfileForm(forms.ModelForm):
  class Meta:
      model = Profile
      fields = ['icon', 'bio']

class CommentForm(forms.ModelForm):
  class Meta:
      model = Comment
      fields = ['content']