from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    PostListView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    SignupView,
    PostLikeAjaxView,
    UserPostListView,
    ProfileUpdateView,
    PostDetailView,
    PostDetailAjaxView,
    CommentCreateView,
    CommentUpdateView,
    CommentDeleteView
)

urlpatterns = [
  path('', PostListView.as_view(), name='post_list'),
  path('create/', PostCreateView.as_view(), name='post_create'),
  path('update/<int:pk>/', PostUpdateView.as_view(), name='post_update'),
  path('delete/<int:pk>/', PostDeleteView.as_view(), name='post_delete'),

  path('posts/<int:pk>/like/ajax/', PostLikeAjaxView.as_view(), name='post_like_ajax'), 
  path('posts/<int:pk>/detail/ajax/', PostDetailAjaxView.as_view(), name='post_detail_ajax'),
  path('user/<str:username>/', UserPostListView.as_view(), name='user_posts'),
  path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    
  path('signup/', SignupView.as_view(), name='signup'),
  path('login/', auth_views.LoginView.as_view(template_name='board/login.html'), name='login'),
  path('logout/', auth_views.LogoutView.as_view(next_page='post_list'), name='logout'),

  path('post/<int:post_id>/comment/', CommentCreateView.as_view(), name='comment_create'),
  path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
  path('comment/<int:pk>/edit/', CommentUpdateView.as_view(), name='comment_edit'),
  path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
]