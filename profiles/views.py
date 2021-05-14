from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Profile, Relation
from .forms import ProfileForm


@login_required
def my_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    confirm = False

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            confirm = True

    context = {
        'profile': profile,
        'form': form,
        'confirm': confirm,
    }

    return render(request, 'profiles/my_profile.html', context)


@login_required
def invite_received_views(request):
    profile = Profile.objects.get(user=request.user)
    qs = Relation.objects.invitations_received(profile)
    result = list(map(lambda x: x.sender, qs))
    is_empty = False
    if len(result) == 0:
        is_empty = True

    context = {
        'invites': result,
        'is_empty': is_empty
    }

    return render(request, 'profiles/my_invites.html', context)


@login_required
def accept_invitation(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        user = request.user.pk
        s_profile = Profile.objects.get(id=pk)
        r_profile = Profile.objects.get(user_id=user)
        relation = get_object_or_404(Relation, sender=s_profile, receiver=r_profile)
        if relation.status == 'send':
            relation.status = 'accepted'
            relation.save()
    return redirect('profiles:invites')


@login_required
def reject_invitation(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        user = request.user.pk
        r_profile = Profile.objects.get(id=user)
        s_profile = Profile.objects.get(id=pk)
        relation = get_object_or_404(Relation, sender=s_profile, receiver=r_profile)
        relation.delete()
    return redirect('profiles:invites')


@login_required
def profile_list_view(request):
    user = request.user
    qs = Profile.objects.get_all_profiles(user)

    context = {
        'profiles': qs
    }

    return render(request, 'profiles/profiles_list.html', context)


@login_required
def invite_profile_list_view(request):
    user = request.user
    qs = Profile.objects.get_all_profiles_to_invite(user)

    context = {
        'profiles': qs
    }

    return render(request, 'profiles/profiles_list.html', context)


class ProfileListView(LoginRequiredMixin, ListView):
    template_name = 'profiles/profiles_list.html'

    def get_queryset(self):
        return Profile.objects.get_all_profiles(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user=self.request.user)
        rel_r = Relation.objects.filter(sender=profile)
        rel_s = Relation.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []
        for item in rel_r:
            rel_receiver.append(item.receiver.user)
        for item in rel_s:
            rel_sender.append(item.sender.user)

        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context['is_empty'] = False
        if len(self.get_queryset()) == 0:
            context['is_empty'] = True

        return context


class ProfileDetail(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'profiles/detail.html'

    # def get_object(self, **kwargs):
    #     pk = self.kwargs.get('pk')
    #     profile = Profile.objects.get(id=pk)
    #     return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user=self.request.user)
        rel_r = Relation.objects.filter(sender=profile)
        rel_s = Relation.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []
        for item in rel_r:
            rel_receiver.append(item.receiver.user)
        for item in rel_s:
            rel_sender.append(item.sender.user)

        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context['posts'] = self.get_object().get_all_author_post()
        context['len_post'] = True if len(self.get_object().get_all_author_post()) > 0 else False

        return context


@login_required
def send_invitation(request):
    if request.method == 'POST':
        user = request.user
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(user_id=pk)
        Relation.objects.create(sender=sender, receiver=receiver, status='send')
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('profiles:invites')


@login_required
def delete_from_friend(request):
    if request.method == 'POST':
        user = request.user
        profile_id = request.POST.get('profile_id')
        me = Profile.objects.get(user=user)
        profile = Profile.objects.get(id=profile_id)
        Relation.objects.get(
            Q(sender=me, receiver=profile, status='accepted') | Q(sender=profile, receiver=me,
                                                                  status='accepted')).delete()
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('profiles:invites')
