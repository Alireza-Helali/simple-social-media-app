from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse


class ProfileManager(models.Manager):
    def get_all_profiles(self, me):
        qs = Profile.objects.all().exclude(user=me)
        return qs

    def get_all_profiles_to_invite(self, sender):
        profiles = Profile.objects.all().exclude(user=sender)
        profile = Profile.objects.get(user=sender)
        relation = Relation.objects.filter(Q(sender=profile) | Q(receiver=profile))
        accepted = set([])
        for rel in relation:
            if rel.status == 'accepted':
                accepted.add(rel.sender)
                accepted.add(rel.receiver)

        future_friends = [person for person in profiles if person not in accepted]
        return future_friends


class Profile(models.Model):
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default='no bio ...', max_length=300)
    avatar = models.ImageField(upload_to='avatars/', default='avatar.png')
    email = models.EmailField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    friends = models.ManyToManyField(User, blank=True, related_name='friends')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = ProfileManager()

    def get_friends(self):
        return self.friends.prefetch_related('friends__user').all()

    def get_friends_no(self):
        return self.friends.prefetch_related('friends__user').count()

    def get_post_no(self):
        return self.post.all().count()

    def get_all_author_post(self):
        return self.post.all()

    def get_num_of_like_given(self):
        likes = self.like_set.all()
        total_num = 0
        for like in likes:
            if like.value == 'like':
                total_num += 1
        return total_num

    def get_num_of_like_received(self):
        posts = self.post.all()
        total_like = 0
        for post in posts:
            total_like += post.liked.count()
        return total_like

    def __str__(self):
        return f'{self.user.username}'

    def get_absolute_url(self):
        return reverse("profiles:detail", kwargs={"pk": self.pk, 'name': self.user.username})


STATUS_CHOICE = [
    ('send', 'send'),
    ('accepted', 'accepted')
]


class RelationManager(models.Manager):
    def invitations_received(self, receiver):
        qs = Relation.objects.filter(receiver=receiver, status='send')
        return qs


class Relation(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=8, choices=STATUS_CHOICE)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = RelationManager()

    def __str__(self):
        return f'{self.sender} to {self.receiver}-{self.status}'
