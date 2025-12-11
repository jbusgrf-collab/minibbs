from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
  author = models.ForeignKey(User, on_delete=models.CASCADE)
  content = models.TextField()
  image = models.ImageField(upload_to='post_images/', blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

  def __str__(self):
    return self.content[:20]  # 管理画面等で最初の20文字が表示される


class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  icon = models.ImageField(upload_to='profile_icons/', blank=True, null=True)
  bio = models.TextField(blank=True, null=True)

  def __str__(self):
    return self.user.username


class Comment(models.Model):
  post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
  author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
  content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
      return f'Comment by {self.author} on {self.post}'