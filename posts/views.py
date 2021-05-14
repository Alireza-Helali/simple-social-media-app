from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, UpdateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Post, Profile, Like
from .forms import PostModelForm, CommentModelForm


@login_required
def comment_and_post_create_list_view(request):
    qs = Post.objects.all()
    profile = Profile.objects.get(user=request.user)

    p_form = PostModelForm()
    c_form = CommentModelForm()
    post_added = False

    if 'submit_p_form' in request.POST:
        p_form = PostModelForm(request.POST, request.FILES)
        if p_form.is_valid():
            instance = p_form.save(commit=False)
            instance.author = profile
            instance.save()
            p_form = PostModelForm()
            post_added = True

    if 'submit_c_form' in request.POST:
        c_form = CommentModelForm(request.POST)
        if c_form.is_valid():
            instance = c_form.save(commit=False)
            instance.user = profile
            instance.Post = Post.objects.get(id=request.POST.get('post_id'))
            instance.save()
            c_form = CommentModelForm()

    context = {
        'qs': qs,
        'profile': profile,
        'form': p_form,
        'c_form': c_form,
        'post_added': post_added
    }

    return render(request, 'posts/main2.html', context)


@login_required
def like_unlike(request):
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        profile = Profile.objects.get(user=user)
        post = Post.objects.get(id=post_id)
        post_like = post.liked.all()
        if profile not in post_like:
            post.liked.add(profile)
        else:
            post.liked.remove(profile)

        like, created = Like.objects.get_or_create(user_id=profile.id, post_id=post_id)

        if not created:
            if like.value == 'like':
                like.value = 'unlike'
            else:
                like.value = 'like'
        else:
            like.value = 'like'

        like.save()
        post.save()
    return redirect('posts:comment')


class PostDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'posts/confirm_del.html'
    model = Post
    success_url = reverse_lazy('posts:comment')

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        obj = Post.objects.get(id=pk)
        if obj.author.user != self.request.user:
            messages.warning(self.request, 'you have to be the author to delete this post')
        return obj


class PostUpdateView(LoginRequiredMixin, UpdateView):
    form_class = PostModelForm
    model = Post
    template_name = 'posts/confirm_up.html'
    success_url = reverse_lazy('posts:comment')

    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        if form.instance.author == profile:
            return super().form_valid(form)
        else:
            form.add_error(None, 'you have to be the author to update this post')
            return super().form_valid(form)
