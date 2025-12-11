from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.utils.timezone import localtime
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.template.loader import render_to_string
from django.http import JsonResponse
from .models import Post, Profile, Comment
from .forms import PostForm, ProfileForm, CommentForm


# 投稿一覧
class PostListView(ListView):
    model = Post
    template_name = 'board/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    paginate_by = 16 # 1ページに表示する投稿数

    def get_queryset(self):
        queryset = super().get_queryset()
        for post in queryset:
            created = localtime(post.created_at).strftime("%Y%m%d%H%M")
            updated = localtime(post.updated_at).strftime("%Y%m%d%H%M")
            post.is_updated = (created != updated)

            # いいね判定（匿名ユーザーはFalse）
            user = self.request.user
            if user.is_authenticated:
                post.is_liked = post.likes.filter(pk=user.pk).exists()
            else:
                post.is_liked = False

        return queryset


# 投稿作成
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'board/post_form.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):    # 投稿ユーザーをリクエストユーザーと紐付ける
        form.instance.author = self.request.user
        return super().form_valid(form)

# 投稿編集
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'board/post_form.html'
    success_url = reverse_lazy('post_list')

    def test_func(self):    # 更新ユーザーと投稿ユーザーが一致するか判定
        post = self.get_object()
        return self.request.user == post.author

# 投稿削除
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'board/post_confirm_delete.html'
    success_url = reverse_lazy('post_list')

    def test_func(self):    # 削除ユーザーと投稿ユーザーが一致するか判定
        post = self.get_object()
        return self.request.user == post.author

 # いいね機能（Ajax）
class PostLikeAjaxView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        liked = False
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
            liked = True
        return JsonResponse({
            'liked': liked,
            'like_count': post.likes.count(),
        })

# ユーザー登録
class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = 'board/signup.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)    # 自動ログイン
        print(f"ログイン直後 user.is_authenticated = {self.request.user.is_authenticated}")
        print(f"session key = {self.request.session.session_key}")
        return super().form_valid(form)

# ユーザー投稿一覧
class UserPostListView(ListView):
    model = Post
    template_name = 'board/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs['username'])
        context['profile'] = Profile.objects.filter(user=user).first()
        if context['profile'] is None:
            # 例えば匿名Profileを渡すか、空のProfileを作るなど。あるいはテンプレートでNoneチェックする。
            pass
        return context

# プロフィール編集
class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'board/profile_update.html'
    #success_url = reverse_lazy('post_list')

    def get_object(self, queryset=None):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def get_success_url(self):
        # ログインユーザーのusernameを取得してリダイレクト先URLを生成
        return reverse('user_posts', kwargs={'username': self.request.user.username})

    def test_func(self):
        # アクセス制限: ログインユーザーのみ
        return self.request.user.is_authenticated

# 投稿詳細（Ajax）
class PostDetailAjaxView(View):
    def get(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)

        # いいねアイコンを一覧画面と詳細画面で同期
        if request.user.is_authenticated:
            post.is_liked = post.likes.filter(pk=request.user.pk).exists()
        else:
            post.is_liked = False
        
        context = {
            'post': post,
        }
        html = render_to_string('board/post_detail_partial.html', context, request=request)
        return JsonResponse({'html': html})

# コメント作成
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'board/comment_form.html'

    def form_valid(self, form):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, id=post_id)
        form.instance.post = post
        form.instance.author = self.request.user
        form.save()
        # 完了ページにpost渡して表示
        return render(self.request, 'board/comment_done.html', {'post': post})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_id = self.kwargs['post_id']
        context['post'] = get_object_or_404(Post, id=post_id)
        return context

# コメント投稿後の詳細画面
class PostDetailView(DetailView):
    model = Post
    template_name = 'board/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        # いいね状態を渡す（ログイン済みなら判定）
        user = self.request.user
        if user.is_authenticated:
            post.is_liked = post.likes.filter(pk=user.pk).exists()
        else:
            post.is_liked = False

        context['post'] = post
        return context

# コメント編集
class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'board/comment_form.html'

    def get_success_url(self):
        # 編集完了後は投稿詳細へ戻る
        return reverse_lazy('post_detail', kwargs={'pk': self.object.post.pk})

    def test_func(self):
        # 編集権限チェック（コメントの投稿者のみ）
        comment = self.get_object()
        return self.request.user == comment.author

# コメント削除
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'board/comment_confirm_delete.html'

    def get_success_url(self):
        # 削除完了後は投稿詳細へ戻る
        return reverse_lazy('post_detail', kwargs={'pk': self.object.post.pk})

    def test_func(self):
        # 削除権限チェック（コメントの投稿者のみ）
        comment = self.get_object()
        return self.request.user == comment.author